import redis
import logging
from os import getenv
from commonRessources import REDIS_HOST, REDIS_PORT
import configparser
from commonRessources.logger import setLoggerLevel

CONFIG_FILE = '/app/opheliaConfig/config.ini'

logger = setLoggerLevel("RedisWorkerCounter")


redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def initializeCounter():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    try:
        activeJobCounter = sum(1 for section in config.sections() if section.startswith('job-exec "'))
        logger.info(f"Counter initialized to {activeJobCounter}")
        redis_client.set('ACTIVE_JOB_COUNTER', activeJobCounter)
        # AKTIVE WORKER Müssen auch in der Redis gespeichert werden und am Anfang initialisiert werden
    except redis.RedisError as e:
        logger.error(f"Error accessing Redis: {e}")
initializeCounter()

def updateCounter(increment: bool):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        counterValue = int(redis_client.get('ACTIVE_JOB_COUNTER') or 0)
        if increment:
            counterValue += 1
        else:
            counterValue -= 1
        redis_client.set('ACTIVE_JOB_COUNTER', counterValue)
        logger.info(f"Counter updated to {counterValue}")
    except redis.RedisError as e:
        logger.error(f"Error updating Redis counter: {e}")
        
def getCounter():
    redis_client.get('ACTIVE_JOB_COUNTER')
    return redis_client.get('ACTIVE_JOB_COUNTER')