from commonRessources.logger import setLoggerLevel
from commonRessources import REDIS_HOST, REDIS_PORT
import redis
import time

logger = setLoggerLevel("lockConfigFile")

redisClient = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

LOCK_KEY = 'config_file_lock'
LOCK_TIMEOUT = 10  # Timeout for the lock in seconds

def acquireLock():
    try:
        result = redisClient.set(LOCK_KEY, 'locked', nx=True, ex=LOCK_TIMEOUT)
        if result == True:
            logger.info("Lock acquired.")
            return True
        else:
            logger.warning("Lock not acquired. The config file is currently locked.")
            return False
    except redis.RedisError as e:
        logger.error(f"Error acquiring lock: {e}")
        return False

def releaseLock():
    try:
        redisClient.delete(LOCK_KEY)
        logger.info("Lock released.")
        return True
    except redis.RedisError as e:
        logger.error(f"Error releasing lock: {e}")
        return False
