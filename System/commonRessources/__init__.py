import json
import os
from os import getenv

# Load constants from file in order to access them in the python code
config_path = os.path.join(os.path.dirname(__file__), 'constants.json')

def load_constants(file_path=config_path):
    with open(file_path, 'r') as file:
        return json.load(file)

config = load_constants()

API_MESSAGE_DESCRIPTOR = config['API_MESSAGE_DESCRIPTOR']
COMPOSE_POSTGRES_DATA_CONNECTOR_URL = config['POSTGRES_DATA_CONNECTOR_URL']
COMPOSE_POSTGRES_DATA_CONNECTOR_URL = config['COMPOSE_POSTGRES_DATA_CONNECTOR_URL']
COMPOSE_INFLUX_DATA_CONNECTOR_URL = config['COMPOSE_INFLUX_DATA_CONNECTOR_URL']
COMPOSE_INFLUX_DB_URL = config['COMPOSE_INFLUX_DB_URL']

# Constants for the scheduler
REDIS_HOST = config['REDIS_HOST']
REDIS_PORT = config['REDIS_PORT']

MAX_NUMBER_JOBS_PER_WORKER = config['MAX_NUMBER_JOBS_PER_WORKER']
MAX_NUMBER_WORKERS = int(getenv('MAX_NUMBER_WORKERS', '1'))