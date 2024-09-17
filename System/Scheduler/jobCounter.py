import redis
import logging
from os import getenv
from commonRessources import REDIS_HOST, REDIS_PORT
import configparser
from commonRessources.logger import setLoggerLevel

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
CONFIG_FILE = '/app/opheliaConfig/config.ini'
activeJobCounterName = 'ACTIVE_JOB_COUNTER'
historicalJobCounterName = 'HISTORICAL_JOB_COUNTER'

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
logger = setLoggerLevel("RedisJobCounter")

redisClient = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def initializeActiveJobCounter():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    activeJobCounter = sum(1 for section in config.sections() if section.startswith('job-exec "'))

    try:
        logger.info(f"Active Job Counter initialized to {activeJobCounter}")
        redisClient.set(activeJobCounterName, activeJobCounter)
        # AKTIVE WORKER Müssen auch in der Redis gespeichert werden und am Anfang initialisiert werden
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis during initializing the {activeJobCounterName}: {e}")
initializeActiveJobCounter()

def initializeHistoricalJobCounter():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    # search the highest job number in the config file
    maxJobNumber = 0

    for section in config.sections():
        if section.startswith('job-exec "job'):
            jobNumber = int(section.split('"job')[1].split('"')[0])
            if jobNumber > maxJobNumber:
                maxJobNumber = jobNumber
    maxJobNumber += 1

    try:
        logger.info(f"Historical Job Counter initialized to {maxJobNumber}")
        redisClient.set(historicalJobCounterName, maxJobNumber)
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis during initializing the {historicalJobCounterName}: {e}")
initializeHistoricalJobCounter()

# --------------------------- Job Counter Functions -----------------------------------------------------------------------------------------------------------------------------------------
def updateActiveJobCounter(increment: bool):
    """
    Updates the active job counter in Redis.
    :param increment: True if the counter should be incremented, False if it should be decremented
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        if increment:
            redisClient.incr(activeJobCounterName)
        else:
            redisClient.decr(activeJobCounterName)
        logger.info(f"Active Job Counter updated to {redisClient.get(activeJobCounterName)}")
    except redis.RedisError as e:
        logger.error(f"Error updating Redis counter: {e}")

def updateHistoricalJobCounter():
    """
    Updates the historical job counter in Redis.
    """
    redisClient.incr(historicalJobCounterName)
    logger.info(f"Historical Job Counter updated to {redisClient.get(historicalJobCounterName)}")

def getActiveJobCounter():
    """
    Returns the current active job counter from Redis.

    The active job counter is the number of jobs that are currently being executed.
    """
    return redisClient.get(activeJobCounterName)

def getHistoricalJobCounter():
    """
    Returns the current historical job counter from Redis.

    The historical job counter is the number of jobs that have been executed since the start of the system.
    This is needed in order to assign unique job IDs to each job.
    """
    return redisClient.get(historicalJobCounterName)