import requests
import socket
from os import getenv
from datetime import datetime, timezone
import time
from commonRessources.logger import setLoggerLevel
from commonRessources import COMPOSE_SCHEDULER_API_URL, SCHEDULER_WORKER_HEARTBEAT_INTERVAL
import threading
import subprocess
import docker

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
    }

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
logger = setLoggerLevel("WorkerHeartbeats")
client = docker.from_env()


def sendHeartbeat(workerID):
    """
    Send a heartbeat to the scheduler to signal that the worker is alive.

    :param workerID: The ID of the worker"""
    try:
        heartbeat_url = f"{COMPOSE_SCHEDULER_API_URL}/heartbeatWorkers"
        data = {
            "workerID": workerID,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = requests.post(heartbeat_url, json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"Heartbeat sent for worker {workerID}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send heartbeat for worker {workerID}: {e}")

def startHeartbeat(workerID):
    """
    Start sending heartbeats at regular intervals.
    Its purpose is to call sendHeartbeat() at regular intervals.

    :param workerID: The ID of the worker
    """
    logger.info("Starting heartbeat for worker", workerID)
    while True:
        sendHeartbeat(workerID)
        time.sleep(SCHEDULER_WORKER_HEARTBEAT_INTERVAL)

def get_container_name():
    """
    Get the name of the container.
    It returns the name of the container in which the script is running instead of returning the GUID of it.
    The container name is needed because if the container crashes it's entries can be removed from the scheduler which works with the container name.

    :return: The name of the container
    """
    hostname = socket.gethostname()
    try:        # Get the container name out of the hostname which represents the containers GUID
        result = subprocess.run(
            ["docker", "ps", "--filter", f"id={hostname}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        container_name = result.stdout.strip()
        return container_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get container name: {e}")
        return None

if __name__ == "__main__":
    containerName = get_container_name()
    heartbeat_thread = threading.Thread(target=startHeartbeat, args=(containerName,))
    heartbeat_thread.daemon = False
    heartbeat_thread.start()