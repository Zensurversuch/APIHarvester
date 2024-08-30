from os import getenv
import logging

def setLoggerLevel(loggerName):
    ENV=getenv('ENV')
    if ENV == 'dev':
        # logging.basicConfig(level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    return logging.getLogger(loggerName)