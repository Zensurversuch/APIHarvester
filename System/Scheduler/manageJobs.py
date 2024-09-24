import jobCounter
import scale
import configparser
import docker
import time
from commonRessources.logger import setLoggerLevel

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
CONFIG_FILE = '/app/opheliaConfig/config.ini'

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
logger = setLoggerLevel("JobManager")
dockerClient = docker.from_env()

# --------------------------- Job Management Functions -----------------------------------------------------------------------------------------------------------------------------------------



def addJob(jobName, interval, command, container):
    """
    Adds a new job to the Ofelia configuration file, which looks like this:
    [job-exec "job1"]
    schedule = @every 5s
    command = python /app/fetchScripts/fetchApis.py --url https://finnhub.io/api/v1/quote?symbol=IBM --tokenRequired True --subscriptionID 319286224 --apiID 2
    container = system-worker-1

    :param jobName: Name of the job
    :param interval: Fetching interval in seconds
    :param command: Command to execute
    :param container: Container to execute the command in
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName not in config:
        config.add_section(sectionName)

    config[sectionName]['schedule'] = f"@every {interval}s"
    config[sectionName]['command'] = command
    config[sectionName]['container'] = container

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    refreshOfelia()     # Restart Ofelia to apply the new job

    jobCounter.updateHistoricalJobCounter()
    jobCounter.updateActiveJobCounter(True)

def deleteJob(jobName):
    """
    Deletes a job from the Ofelia configuration file.

    :param jobName: Name of the job to delete
    :return: True if the job was deleted, False if the job was not found
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName in config:
        config.remove_section(sectionName)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        jobCounter.updateActiveJobCounter(False)
        scale.balanceJobsAcrossWorkers()
        refreshOfelia()
        return True
    else:
        return False

def refreshOfelia():
    """
    Restarts the Ofelia container to apply the new configuration.

    :return: True if the container was restarted, False if the container was not found or an error occurred
    """
    try:
        container = dockerClient.containers.get('ofelia')
        container.restart()
        container.reload()
        logger.info("Ofelia container has been restarted successfully.")
        return True
    except docker.errors.NotFound:
        logger.error("Ofelia container not found.")
        return False
    except docker.errors.APIError as e:
        logger.error(f"Error restarting Ofelia container: {str(e)}")
        return False
