from flask import Flask, request, jsonify
import configparser
import logging
import docker
import requests
from os import getenv
from interfaces import UserRole, ApiStatusMessages, SubscriptionStatus, SubscriptionType


app = Flask(__name__)
ENV=getenv('ENV')

COUNTER = 0

if(ENV=='dev'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

dockerClient = docker.from_env()

CONFIG_FILE = '/app/opheliaConfig/config.ini'

@app.route('/hello')
def hello():
    return 'Hello, World from Scheduler!'

@app.route('/subscribeApi/<int:userId>/<int:apiId>/<int:interval>', methods=['GET'])
def subscribeApi(userId, apiId, interval):
    global COUNTER
    try:
        response = requests.get(f'http://postgresdataconnector:5000/availableApi/{apiId}')
        logger.debug(f"response: {response}")
        response.raise_for_status()

        apiData = response.json()
        apiName = apiData.get("name")
        apiUrl = apiData.get("url")

        logger.debug(f"apiData: {apiData}")

        if not apiName or not apiUrl:
            return jsonify({"error": "API name or URL not found in response"}), 400

        if apiName.startswith("Finnhub"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithToken --url {apiUrl}"
        elif apiName.startswith("Weather"):
            command = f"python /app/fetchScripts/fetchApis.py fetchApiWithoutToken --url {apiUrl}"
        else:
            return jsonify({"error": "Unknown API type"}), 400

        jobName = f"job{COUNTER}"

        addJob(jobName, interval, command, "worker")
        COUNTER += 1

        # Create subscription
        subscription_response = requests.post('http://postgresdataconnector:5000/createSubscription', json={
            'userID': userId,
            'availableApiID': apiId,
            'interval': interval,
            'status': SubscriptionStatus.ACTIVE.value,
            'jobName': jobName
        })
        subscription_response.raise_for_status()

        return jsonify({"message": f"Job {jobName} scheduled and subscription created"}), 200

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

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
    return jsonify({"message": "Job added"}), 200

@app.route('/unsubscribeApi/<int:subscriptionId>', methods=['GET'])
def unsubscribeApi(subscriptionId):
    try:
        response = requests.get(f'http://postgresdataconnector:5000/subscription/{subscriptionId}')
        response.raise_for_status()
        data = response.json()
        deleteJob(data.get('jobName'))
        subscription_response = requests.post('http://postgresdataconnector:5000/setSubscriptionsStatus', json={
                'subscriptionID': subscriptionId,
                'subscriptionStatus': SubscriptionStatus.INACTIVE.value
        })
        return jsonify({"message": "Api unsubsribed and job deleted"}), 200
        
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

def deleteJob(jobName):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    section_name = f'job-exec "{jobName}"'
    if section_name in config:
        config.remove_section(section_name)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        refreshOfelia()
        return jsonify({"message": "Job deleted"}), 200
    else:
        return jsonify({"message": "Job not found"}), 404

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