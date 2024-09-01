import redis
import logging
from os import getenv
from commonRessources import REDIS_HOST, REDIS_PORT
import configparser
from commonRessources.logger import setLoggerLevel

CONFIG_FILE = '/app/opheliaConfig/config.ini'

logger = setLoggerLevel("RedisJobCounter")


redisClient = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

activeJobCounterName = 'ACTIVE_JOB_COUNTER'
historicalJobCounterName = 'HISTORICAL_JOB_COUNTER'

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

def updateActiveJobCounter(increment: bool):
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
    redisClient.incr(historicalJobCounterName)
    logger.info(f"Historical Job Counter updated to {redisClient.get(historicalJobCounterName)}")

def getActiveJobCounter():
    return redisClient.get(activeJobCounterName)

def getHistoricalJobCounter():
    return redisClient.get(historicalJobCounterName)