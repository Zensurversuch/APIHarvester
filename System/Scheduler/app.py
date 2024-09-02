from flask import Flask, jsonify, request
import configparser
import logging
import docker
import requests
from os import getenv
from flask_cors import CORS
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources import API_MESSAGE_DESCRIPTOR, COMPOSE_POSTGRES_DATA_CONNECTOR_URL

apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}

app = Flask(__name__)
CORS(app)
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

@app.route('/subscribeApi', methods=['POST'])
def subscribeApi():
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400
    userID = request.json.get('userID')
    apiID = request.json.get('apiID')
    interval = request.json.get('interval')
    
    global ACTIVE_WORKER_COUNTER
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

        jobName = f"job{ACTIVE_WORKER_COUNTER}"

        #set the jobName, command and container in the subscription
        subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', 
                                             json={
                                                   'subscriptionID': subscriptionID,
                                                   'subscriptionStatus': SubscriptionStatus.ACTIVE.value,
                                                   'jobName': jobName,
                                                   'command': command,
                                                   'container': 'worker'
                                                   },
                                             headers=headers)

        subscriptionResponse.raise_for_status()
        addJob(jobName, interval, command, "worker")
        ACTIVE_WORKER_COUNTER += 1

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
            jobName = f"job{ACTIVE_WORKER_COUNTER}"
            addJob(jobName, str(data.get('interval')), str(data.get('command')), str(data.get('container')))
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', 
                                                 json={
                                                     'subscriptionID': subscriptionID,
                                                     'subscriptionStatus': SubscriptionStatus.ACTIVE.value,
                                                     'jobName': jobName
                                                     },
                                                 headers=headers)
            subscriptionResponse.raise_for_status()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Job {jobName} scheduled and subscription for API_ID {data.get('availableApiID')} created"}), 200
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api is already active"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: str(e)"}), 500

def addJob(jobName, interval, command, container):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName not in config:
        config.add_section(sectionName)

    config[sectionName]['schedule'] = f"@every {interval}s"  #at the moment the interval is given in seconds
    config[sectionName]['command'] = command
    config[sectionName]['container'] = container

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    refreshOfelia()

@app.route('/unsubscribeApi/<int:subscriptionID>', methods=['GET'])
def unsubscribeApi(subscriptionID):
    try:
        response = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}', headers=headers)
        response.raise_for_status()
        data = response.json()
        jobName = data.get('jobName')
        if(deleteJob(jobName)):
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}//setSubscriptionsStatus', json={
                'subscriptionID': subscriptionID,
                'subscriptionStatus': SubscriptionStatus.INACTIVE.value,
                'jobName': None
            }, headers=headers)
            subscriptionResponse.raise_for_status()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Api unsubsribed and job {jobName} deleted"}), 200
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api isn't unsubscribed and job {jobName} couldn't be deleted"}), 400
        # Here the counter has to be decremented in the future, but this is done during autocalling
        # The problem is that if I just decrement the counter a job which still runs could be overwritten if
        # for instance 5 jobs (job0, job1, job2, job3, job4) are running and i delete job1 then job number 5
        # would be overwritten because the counter would be decremented to 4 and the new job would be named 
        # job4 (which is already in use)
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: {str(e)}"}), 500

def deleteJob(jobName):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    section_name = f'job-exec "{jobName}"'
    if section_name in config:
        config.remove_section(section_name)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        refreshOfelia()
        return True
    else:
        return False

def refreshOfelia():
    try:
        container = dockerClient.containers.get('ofelia')
        container.restart()
        container.reload
        logger.info("Ofelia container has been restarted successfully.")
        return "Ofelia container has been restarted successfully."
    except docker.errors.NotFound:
        logger.error("Ofelia container not found.")
        return "Ofelia container not found."
    except docker.errors.APIError as e:
        logger.error(f"Error restarting Ofelia container: {str(e)}")
        return f"Error restarting Ofelia container: {str(e)}"

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000, debug=True)