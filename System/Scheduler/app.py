from flask import Flask, jsonify
import configparser
import logging
import docker
import requests
from os import getenv
from flask_cors import CORS
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources.constants import API_MESSAGE_DESCRIPTOR

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


@app.route('/hello')
def hello():
    return 'Hello, World from Scheduler!'

@app.route('/subscribeApi/<int:userId>/<int:apiId>/<int:interval>', methods=['GET'])
def subscribeApi(userId, apiId, interval):
    global ACTIVE_WORKER_COUNTER
    try:
        response = requests.get(f'http://postgresdataconnector:5000/availableApi/{apiId}')
        logger.debug(f"response: {response}")
        response.raise_for_status()

        apiData = response.json()
        apiName = apiData.get("name")
        apiUrl = apiData.get("url")

        logger.debug(f"apiData: {apiData}")

        if not apiName or not apiUrl:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}API name or URL not found in response"}), 400

        if apiName.startswith("Finnhub"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithToken --url {apiUrl} --userid {userId} --apiid {apiId}"
        elif apiName.startswith("Weather"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithoutToken --url {apiUrl} --userid {userId} --apiid {apiId}"
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Unknown API type"}), 400

        jobName = f"job{ACTIVE_WORKER_COUNTER}"

        addJob(jobName, interval, command, "worker")
        ACTIVE_WORKER_COUNTER += 1

        # Create subscription
        subscription_response = requests.post('http://postgresdataconnector:5000/createSubscription', json={
            'userID': userId,
            'availableApiID': apiId,
            'interval': interval,
            'status': SubscriptionStatus.ACTIVE.value,
            'jobName': jobName
        })
        subscription_response.raise_for_status()

        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Job {jobName} scheduled and subscription created"}), 200

    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}{str(e)}"}), 500

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

@app.route('/unsubscribeApi/<int:subscriptionId>', methods=['GET'])
def unsubscribeApi(subscriptionId):
    try:
        response = requests.get(f'http://postgresdataconnector:5000/subscription/{subscriptionId}')
        response.raise_for_status()
        data = response.json()
        if(deleteJob(data.get('jobName'))):
            subscription_response = requests.post('http://postgresdataconnector:5000/setSubscriptionsStatus', json={
                'subscriptionID': subscriptionId,
                'subscriptionStatus': SubscriptionStatus.INACTIVE.value,
                'jobName': None
            })
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Api unsubsribed and job deleted"}), 200
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api isn't unsubscribed and job couldn't be deleted"}), 400
        # Here the counter has to be decremented in the future, but this is done during autocalling
        # The problem is that if I just decrement the counter a job which still runs could be overwritten if
        # for instance 5 jobs (job0, job1, job2, job3, job4) are running and i delete job1 then job number 5
        # would be overwritten because the counter would be decremented to 4 and the new job would be named 
        # job4 (which is already in use)
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: str(e)"}), 500

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