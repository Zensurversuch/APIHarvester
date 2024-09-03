from flask import Flask, jsonify, request
import requests
from os import getenv
from flask_cors import CORS
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources import API_MESSAGE_DESCRIPTOR, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.logger import setLoggerLevel
import jobCounter, scale, manageJobs, lockConfigFile
import time

apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}

app = Flask(__name__)

CORS(app)

logger = setLoggerLevel("Scheduler")
ENV=getenv('ENV')

CONFIG_FILE = '/app/opheliaConfig/config.ini'
ACTIVE_WORKER_COUNTER = 0

def initializeCounter():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    global ACTIVE_WORKER_COUNTER
    ACTIVE_WORKER_COUNTER = sum(1 for section in config.sections() if section.startswith('job-exec "'))

initializeCounter()

if(ENV=='dev'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

dockerClient = docker.from_env()

# Change the following route to Post method
@app.route('/subscribeApi', methods=['POST'])
def subscribeApi():
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400
    userID = request.json.get('userID')
    apiID = request.json.get('apiID')
    interval = request.json.get('interval')

    try:
        response = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/availableApi/{apiID}', headers=headers)
        logger.debug(f"response: {response}")
        response.raise_for_status()

        apiData = response.json()
        apiName = apiData.get("name")
        apiUrl = apiData.get("url")

        if not apiName or not apiUrl:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}API name or URL not found in response"}), 400

        logger.debug(f"apiData: {apiData}")

        while not lockConfigFile.acquireLock():  # If the config file is locked, wait
            time.sleep(0.5)

        # Create subscription
        subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/createSubscription', 
                                             json={
                                                 'userID': userID,
                                                 'availableApiID': apiID,
                                                 'interval': interval,
                                                 'status': SubscriptionStatus.ACTIVE.value,
                                                 },
                                             headers=headers)
        subscriptionResponse.raise_for_status()


        # Create job entry string for ofelia config file
        subscriptionID = subscriptionResponse.json().get('subscriptionID')
        if apiName.startswith("Finnhub"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithToken --url {apiUrl} --subscriptionID {subscriptionID} --apiID {apiID}"
        elif apiName.startswith("Weather"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithoutToken --url {apiUrl} --subscriptionID {subscriptionID} --apiID {apiID}"
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Unknown API type"}), 400

        jobName = f"job{jobCounter.getHistoricalJobCounter()}"
        containerName = scale.scaleWorkers()

        #set the jobName, command and container in the subscription
        subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', 
                                             json={
                                                   'subscriptionID': subscriptionID,
                                                   'subscriptionStatus': SubscriptionStatus.ACTIVE.value,
                                                   'jobName': jobName,
                                                   'command': command,
                                                   'container': containerName
                                                   },
                                             headers=headers)
        subscriptionResponse.raise_for_status()

        manageJobs.addJob(jobName, interval, command, containerName)

        lockConfigFile.releaseLock()
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Job {jobName} scheduled and subscription for API {apiName}; API_ID: {apiID} created"}), 200
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}{str(e)}"}), 500

@app.route('/resubscribeApi/<int:subscriptionID>', methods=['GET'])
def resubscribeApi(subscriptionID):
    try:
        response = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}', headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == SubscriptionStatus.INACTIVE.value:
            while not lockConfigFile.acquireLock():  # If the config file is locked, wait
                time.sleep(0.5)
            jobName = f"job{jobCounter.getHistoricalJobCounter()}"
            containerName = scale.scaleWorkers()
            manageJobs.addJob(jobName, str(data.get('interval')), str(data.get('command')), containerName)
            lockConfigFile.releaseLock()

            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', 
                                                 json={
                                                     'subscriptionID': subscriptionID,
                                                     'subscriptionStatus': SubscriptionStatus.ACTIVE.value,
                                                     'jobName': jobName,
                'container': containerName
                                                     },
                                                 headers=headers)
            subscriptionResponse.raise_for_status()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Job {jobName} scheduled and subscription for API_ID {data.get('availableApiID')} reactivated"}), 200
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api is already active"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: str(e)"}), 500



@app.route('/unsubscribeApi/<int:subscriptionID>', methods=['GET'])
def unsubscribeApi(subscriptionID):
    try:
        response = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}', headers=headers)
        response.raise_for_status()
        data = response.json()
        jobName = data.get('jobName')

        while not lockConfigFile.acquireLock():  # If the config file is locked, wait
            time.sleep(0.5)

        if(manageJobs.deleteJob(jobName)):
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}//setSubscriptionsStatus', json={
                'subscriptionID': subscriptionID,
                'subscriptionStatus': SubscriptionStatus.INACTIVE.value,
                'jobName': None
            }, headers=headers)
            subscriptionResponse.raise_for_status()
            lockConfigFile.releaseLock()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Api unsubsribed and job {jobName} deleted"}), 200
        else:
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}//setSubscriptionsStatus', json={
                'subscriptionID': subscriptionID,
                'subscriptionStatus': SubscriptionStatus.ERROR.value,
                'jobName': None
            }, headers=headers)
            subscriptionResponse.raise_for_status()
            lockConfigFile.releaseLock()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api isn't unsubscribed and job {jobName} couldn't be deleted"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: {str(e)}"}), 500



if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5002, debug=True)