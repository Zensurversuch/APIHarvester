import jobCounter
import scale
import lockConfigFile
import configparser
import docker
import time
from commonRessources.logger import setLoggerLevel

logger = setLoggerLevel("JobManager")

CONFIG_FILE = '/app/opheliaConfig/config.ini'
dockerClient = docker.from_env()

def addJob(jobName, interval, command, container):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName not in config:
        config.add_section(sectionName)

    config[sectionName]['schedule'] = f"@every {interval}s"  # Interval in seconds
    config[sectionName]['command'] = command
    config[sectionName]['container'] = container

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    refreshOfelia()

    jobCounter.updateHistoricalJobCounter()
    jobCounter.updateActiveJobCounter(True)

def deleteJob(jobName):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName in config:
        config.remove_section(sectionName)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        refreshOfelia()
        jobCounter.updateActiveJobCounter(False)
        scale.balanceJobsAcrossWorkers()
        return True
    else:
        return False

def refreshOfelia():
    try:
        container = dockerClient.containers.get('ofelia')
        container.restart()
        container.reload()
        logger.info("Ofelia container has been restarted successfully.")
        return "Ofelia container has been restarted successfully."
    except docker.errors.NotFound:
        logger.error("Ofelia container not found.")
        return "Ofelia container not found."
    except docker.errors.APIError as e:
        logger.error(f"Error restarting Ofelia container: {str(e)}")
        return f"Error restarting Ofelia container: {str(e)}"
