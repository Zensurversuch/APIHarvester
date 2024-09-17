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

logger = setLoggerLevel("WorkerHeartbeats")

client = docker.from_env()

apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
    }

# containerName = getenv('HOSTNAME')

def sendHeartbeat(workerID):
    """Send a heartbeat to the scheduler to signal that the worker is alive."""
    print("Sending heartbeat for worker", workerID)
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
    """Start sending heartbeats at regular intervals."""
    print("Starting heartbeat for worker", workerID)
    logger.error(f"Starting heartbeat for worker {workerID}")
    while True:
        sendHeartbeat(workerID)
        time.sleep(SCHEDULER_WORKER_HEARTBEAT_INTERVAL)

def get_container_name():
    hostname = socket.gethostname()
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"id={hostname}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.error(f"Container name: {result.stdout.strip()}")
        container_name = result.stdout.strip()
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen des Docker-Befehls: {e}")
        return None

if __name__ == "__main__":
    containerName = get_container_name()
    heartbeat_thread = threading.Thread(target=startHeartbeat, args=(containerName,))
    heartbeat_thread.daemon = False
    heartbeat_thread.start()