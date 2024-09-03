import redis
import docker
import configparser
from commonRessources.logger import setLoggerLevel

logger = setLoggerLevel("Scalling")

from commonRessources import MAX_NUMBER_JOBS_PER_WORKER, MAX_NUMBER_WORKERS, REDIS_HOST, REDIS_PORT

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
dockerClient = docker.from_env()

CONFIG_FILE = '/app/opheliaConfig/config.ini'

activeWorkerCounterName = 'ACTIVE_WORKER_CONTAINER_COUNTER'

def initializeWorkerCounter():
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
            redis_client.set(activeWorkerCounterName, activeWorkerCounter)
        except redis.RedisError as e:
            logger.error(f"Error accessing Redis: {e}")

    except Exception as e:
        logger.error(f"Unexpected error during initializing the number of currently active worker containers: {e}")
initializeWorkerCounter()

def scaleWorkers():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        jobsPerContainer = {}
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
            if jobsPerContainer[f"system-worker-{i}"] < MAX_NUMBER_JOBS_PER_WORKER:
                return f'system-worker-{i}'

        import redis
        return None
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during scaling worker instances: {e}")

def balanceJobsAcrossWorkers():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        # Initialize dictionary to track jobs for each container
        jobsPerContainer = {f"system-worker-{i}": 0 for i in range(1, MAX_NUMBER_WORKERS + 1)}
        jobSections = []

        # Collect all job sections
        for section in config.sections():
            if section.startswith('job-exec'):
                jobSections.append(section)

        # Reset all container assignments in the config
        for section in jobSections:
            if config.has_option(section, 'container'):
                config.remove_option(section, 'container')

        # Distribute jobs across containers
        for section in jobSections:
            if section.startswith('job-exec'):
                containerToUse = ""
                for container in jobsPerContainer:
                    if jobsPerContainer[container] < MAX_NUMBER_JOBS_PER_WORKER:
                        containerToUse = container
                        jobsPerContainer[container] += 1
                        break

                if containerToUse:
                    config.set(section, 'container', containerToUse)
                else:
                    logger.error("No suitable container found for job section: {section}")

        # Save the updated configuration
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    except Exception as e:
        logger.error(f"Unexpected error during job rebalancing across workers: {e}")
