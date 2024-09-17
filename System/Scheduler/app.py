from flask import Flask, jsonify, request
import requests
from os import getenv
from flask_cors import CORS
import configparser
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources import API_MESSAGE_DESCRIPTOR, COMPOSE_POSTGRES_DATA_CONNECTOR_URL, SCHEDULER_WORKER_HEARTBEAT_INTERVAL, REDIS_HOST, REDIS_PORT
from commonRessources.logger import setLoggerLevel
from commonRessources.decorators import accessControlApiKey, accessControlJwt
from flask_jwt_extended import JWTManager
import jobCounter, scale, manageJobs, lockConfigFile
import time
from datetime import datetime, timezone
import threading
import redis


# ------------------------------ Environment Variables ------------------------------
apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = f"{getenv('JWT_SECRET_KEY')}"

CONFIG_FILE = '/app/opheliaConfig/config.ini'
ACTIVE_WORKER_COUNTER = 0

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
def initializeCounter():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    global ACTIVE_WORKER_COUNTER
    ACTIVE_WORKER_COUNTER = sum(1 for section in config.sections() if section.startswith('job-exec "'))

initializeCounter()

redisClient = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
redisClient.delete('heartbeats')

jwt = JWTManager(app)
CORS(app)

logger = setLoggerLevel("Scheduler")
ENV=getenv('ENV')

# --------------------------- API Routes -----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/subscribeApi', methods=['POST'])
@accessControlJwt
def subscribeApi():
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400
    userID = request.json.get('userID')
    apiID = request.json.get('apiID')
    interval = request.json.get('interval')

    try:
        availableApiResponse = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/availableApi/{apiID}', headers=headers)
        logger.debug(f"response: {availableApiResponse}")
        availableApiResponse.raise_for_status()

        apiData = availableApiResponse.json()
        apiName = apiData.get("name")
        apiUrl = apiData.get("url")
        apiTokenRequired = apiData.get("apiTokenRequired")

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
        if apiTokenRequired:
            command = f"python /app/fetchScripts/fetchApis.py --url {apiUrl} --tokenRequired {apiTokenRequired} --subscriptionID {subscriptionID} --apiID {apiID}"
        else:
            command = f"python /app/fetchScripts/fetchApis.py --url {apiUrl} --tokenRequired {apiTokenRequired} --subscriptionID {subscriptionID} --apiID {apiID}"

        jobName = f"job{jobCounter.getHistoricalJobCounter()}"
        containerName = scale.scaleWorkers()

        if not containerName:
            lockConfigFile.releaseLock()
            deleteSubscriptionResponse = requests.delete(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/deleteSubscription/{subscriptionID}', headers=headers)
            deleteSubscriptionResponse.raise_for_status()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}No worker container available"}), 400

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
@accessControlJwt
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
@accessControlJwt
def unsubscribeApi(subscriptionID):
    try:
        response = requests.get(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}', headers=headers)
        response.raise_for_status()
        data = response.json()
        jobName = data.get('jobName')

        while not lockConfigFile.acquireLock():  # If the config file is locked, wait
            time.sleep(0.5)

        if(manageJobs.deleteJob(jobName)):
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', json={
                'subscriptionID': subscriptionID,
                'subscriptionStatus': SubscriptionStatus.INACTIVE.value,
                'jobName': None,
                'container': None
            }, headers=headers)
            subscriptionResponse.raise_for_status()
            lockConfigFile.releaseLock()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Api unsubsribed and job {jobName} deleted"}), 200
        else:
            subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', json={
                'subscriptionID': subscriptionID,
                'subscriptionStatus': SubscriptionStatus.ERROR.value,
                'jobName': None,
                'container': None
            }, headers=headers)
            subscriptionResponse.raise_for_status()
            lockConfigFile.releaseLock()
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Api isn't unsubscribed and job {jobName} couldn't be deleted"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}: {str(e)}"}), 500

################################ Heartbeat ################################
@app.route('/heartbeatWorkers', methods=['POST'])
@accessControlApiKey
def receive_heartbeat():
    """Receive heartbeat from a worker."""
    data = request.get_json()
    workerID = data.get('workerID')
    timestamp = data.get('timestamp')

    if workerID and timestamp:
        # Speichere den Heartbeat in Redis
        redisClient.hset('heartbeats', workerID, timestamp)
        logger.info(f"Received heartbeat from worker {workerID} at {timestamp}")
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Heartbeat successfully"}), 200
    else:
        logger.error("Invalid heartbeat data")
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid heartbeat data"}), 400

def check_heartbeats():
    """Periodically check if all workers are sending heartbeats within the expected time."""
    while True:
        now = datetime.now(timezone.utc)
        heartbeats = redisClient.hgetall('heartbeats')

        for workerID, lastHeartbeat in heartbeats.items():
            lastHeartbeat = datetime.fromisoformat(lastHeartbeat)
            if (now - lastHeartbeat).total_seconds() > (SCHEDULER_WORKER_HEARTBEAT_INTERVAL * 2):
                logger.error(f"Worker {workerID} missed heartbeat! Last seen at {lastHeartbeat}")
                redisClient.sadd("NOT_WORKING_CONTAINERS", workerID)
                scale.balanceJobsAcrossWorkers()
            else:
                # if the worker is in NOT_WORKING_CONTAINERS but is sending heartbeats again, remove it from the set
                if workerID.encode('utf-8') in redisClient.smembers("NOT_WORKING_CONTAINERS"):
                    redisClient.srem("NOT_WORKING_CONTAINERS", workerID)
                logger.info(f"{now.time()}: Worker {workerID} is alive (last seen {lastHeartbeat})")

        # Sleep for the interval before checking again
        time.sleep(SCHEDULER_WORKER_HEARTBEAT_INTERVAL)


# Create a new thread for the check_heartbeats function
heartbeat_thread = threading.Thread(target=check_heartbeats)
heartbeat_thread.daemon = False
heartbeat_thread.start()

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5002, debug=True)