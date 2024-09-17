import redis
import docker
import configparser
from commonRessources.logger import setLoggerLevel
from os import getenv
import requests
from commonRessources import MAX_NUMBER_JOBS_PER_WORKER, MAX_NUMBER_WORKERS, REDIS_HOST, REDIS_PORT, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.interfaces import SubscriptionStatus
import re

logger = setLoggerLevel("Scalling")


redisClient = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
dockerClient = docker.from_env()

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
CONFIG_FILE = '/app/opheliaConfig/config.ini'

apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
def initializeWorkerCounter():
    """
    Initialize the number of currently active worker containers.
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        unique_workers = set()

        # Iterating through the sections and capturing the number unique worker containers
        for section in config.sections():
            if config.has_option(section, 'container'):
                container_value = config.get(section, 'container')
                if container_value.startswith('worker-'):
                    unique_workers.add(container_value)

        activeWorkerCounter = len(unique_workers)

        logger.info(f"Worker counter initialized to {activeWorkerCounter}")

        try:
            redisClient.set('ACTIVE_WORKER_CONTAINER_COUNTER', activeWorkerCounter)
        except redis.RedisError as e:
            logger.error(f"Error accessing Redis: {e}")

    except Exception as e:
        logger.error(f"Unexpected error during initializing the number of currently active worker containers: {e}")
initializeWorkerCounter()

# --------------------------- Scaling Functions -----------------------------------------------------------------------------------------------------------------------------------------
def scaleWorkers():
    """
    Scales the jobs across the worker containers.
    This is done if a new job is added.
    
    1) counts the number of jobs per worker in the ofelia config file and checks if there are any workers available.
    2) fills the first available worker with the next job.

    :return: False if no worker is available, otherwise the name of the worker container
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        jobsPerContainer = {}
        notWorkingContainers = redisClient.smembers('NOT_WORKING_CONTAINERS')

        for i in range(1, MAX_NUMBER_WORKERS + 1):
            jobsPerContainer[f"system-worker-{i}"] = 0

        for section in config.sections():
            if section.startswith('job-exec'):
                containerName = config.get(section, 'container')

                if containerName in jobsPerContainer:
                    jobsPerContainer[containerName] += 1
                else:
                    logger.error(f"Container {containerName} not found in jobsPerContainer dictionary.")

        for i in range(1, MAX_NUMBER_WORKERS + 1):
            if jobsPerContainer[f"system-worker-{i}"] < MAX_NUMBER_JOBS_PER_WORKER and f"system-worker-{i}" not in notWorkingContainers:
                return f'system-worker-{i}'

        return False        # No worker available
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during scaling worker instances: {e}")

def extractSubscriptionID(command):
    match = re.search(r'--subscriptionID (\d+)', command)
    if match:
        return match.group(1)
    return None

def balanceJobsAcrossWorkers():
    """
    Balances the jobs across the worker containers.
    This is done if a Subscribtion is desubscribed or a worker container is not working (detected by not sending a heartbeat anymore).
    
    1) Counts the number of jobs per worker in the ofelia config file
    2) Delete all the entries in the config file
    3) Fill container for container with jobs if the container is available
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        notWorkingContainers = redisClient.smembers('NOT_WORKING_CONTAINERS')

        # Initialize dictionary to track jobs for each container
        jobsPerContainer = {f"system-worker-{i}": 0 for i in range(1, MAX_NUMBER_WORKERS + 1)}
        jobSections = []

        # Collect all job sections in variable jobSections
        for section in config.sections():
            if section.startswith('job-exec'):
                jobSections.append(section)

        # Delete all container assignments in the config
        for section in jobSections:
            if config.has_option(section, 'container'):
                config.remove_option(section, 'container')

        # Distribute jobs across containers
        for section in jobSections:             # Iterate through all jobSections stored locally
            if section.startswith('job-exec'):
                containerToUse = ""
                for container in jobsPerContainer:
                    if jobsPerContainer[container] < MAX_NUMBER_JOBS_PER_WORKER and container not in notWorkingContainers:
                        containerToUse = container
                        jobsPerContainer[container] += 1
                        break

                jobName = re.search(r'job-exec\s*"(.*?)"', section).group(1)    # section contains the first line of a job entry in the config.ini file
                subscriptionID = extractSubscriptionID(config.get(section, 'command'))
                if containerToUse:          # If a container with free space was found add the job to the container
                                            # -> write to config file and set subscription status to active
                    config.set(section, 'container', containerToUse)
                    subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', json={
                        'subscriptionID': subscriptionID,
                        'subscriptionStatus': SubscriptionStatus.ACTIVE.value,
                        'jobName': jobName,
                        'container': containerToUse
                    }, headers=headers)
                    subscriptionResponse.raise_for_status()
                else:               # If no container with free space was found delete the job from the config file
                                    # -> delete the section and set subscription status to inactive
                    logger.error(f"No suitable container found for job section: {section}")
                    config.remove_section(section)
                    subscriptionResponse = requests.post(f'{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus', json={
                        'subscriptionID': subscriptionID,
                        'subscriptionStatus': SubscriptionStatus.INACTIVE.value,
                        'jobName': jobName,
                        'container': None
                    }, headers=headers)
                    subscriptionResponse.raise_for_status()

        # Save the updated configuration
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)        # Write the updated config file

    except Exception as e:
        logger.error(f"Unexpected error during job rebalancing across workers: {e}")
