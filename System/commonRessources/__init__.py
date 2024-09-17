import json
import os
from os import getenv

# Load constants from file in order to access them in the python code
config_path = os.path.join(os.path.dirname(__file__), 'constants.json')

def load_constants(file_path=config_path):
    with open(file_path, 'r') as file:
        return json.load(file)

constants = load_constants()

API_MESSAGE_DESCRIPTOR = constants['API_MESSAGE_DESCRIPTOR']
COMPOSE_POSTGRES_DATA_CONNECTOR_URL = constants['POSTGRES_DATA_CONNECTOR_URL']
COMPOSE_POSTGRES_DATA_CONNECTOR_URL = constants['COMPOSE_POSTGRES_DATA_CONNECTOR_URL']
COMPOSE_INFLUX_DATA_CONNECTOR_URL = constants['COMPOSE_INFLUX_DATA_CONNECTOR_URL']
COMPOSE_INFLUX_DB_URL = constants['COMPOSE_INFLUX_DB_URL']
COMPOSE_SCHEDULER_API_URL = constants['COMPOSE_SCHEDULER_API_URL']

# Constants for the scheduler
REDIS_HOST = constants['REDIS_HOST']
REDIS_PORT = constants['REDIS_PORT']

MAX_NUMBER_JOBS_PER_WORKER = constants['MAX_NUMBER_JOBS_PER_WORKER']
MAX_NUMBER_WORKERS = int(getenv('MAX_NUMBER_WORKERS', '1'))

SCHEDULER_WORKER_HEARTBEAT_INTERVAL = constants['SCHEDULER_WORKER_HEARTBEAT_INTERVAL']