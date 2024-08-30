import redis
import docker
import configparser
from commonRessources.logger import setLoggerLevel

logger = setLoggerLevel("Autoscaling")

from commonRessources import MAX_NUMBER_JOBS_PER_WORKER, MAX_NUMBER_WORKERS, REDIS_HOST, REDIS_PORT

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
dockerClient = docker.from_env()

CONFIG_FILE = '/app/opheliaConfig/config.ini'

def scaleWorkers():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        jobsPerContainer = {} # Dictionary to keep track of job counts per container
        for i in range(1, MAX_NUMBER_WORKERS):
            jobsPerContainer[f"worker-{i}"] = 0
        # Iterate through all sections in the config
        for section in config.sections():
            if section.startswith('job-exec'):
                # Get the container name from the current section
                containerName = config.get(section, 'container')

                if containerName in jobsPerContainer:
                    jobsPerContainer[containerName] += 1
                else:
                    logger.error(f"Container {containerName} not found in jobsPerContainer dictionary.")

        # scaleWorkerInstances(MAX_NUMBER_WORKERS) #Test if this works

        for i in range(1, MAX_NUMBER_WORKERS):
            if jobsPerContainer[f"worker-{i}"] < MAX_NUMBER_JOBS_PER_WORKER:
                return f'worker-{i}'
            else:
                redis_client.set('ACTIVE_WORKER_COUNTER', int(redis_client.get('ACTIVE_WORKER_COUNTER')) + 1)
                return f'worker-{str(redis_client.get("ACTIVE_WORKER_COUNTER"))}'
        logger.error("No worker available to scale.")
        return None
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def scaleWorkerInstances(num_instances):
    try:
        command = f"/usr/local/bin/docker-compose up -d --no-recreate --scale worker={num_instances}"

        cli_container = dockerClient.containers.get("dockercli")
        exec_command = cli_container.exec_run(command, detach=True)

        logger.info(f"Executed command '{command}' on dockercli container.")
        logger.info(f"Command execution result: {exec_command}")
    except docker.errors.NotFound:
        logger.error("Docker CLI container not found.")
    except docker.errors.APIError as e:
        logger.error(f"Error executing command: {e}")

