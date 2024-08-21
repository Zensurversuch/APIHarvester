import requests
import logging
from os import getenv
import argparse
from datetime import datetime, timezone
import json

ENV = getenv('ENV')

if ENV == 'dev':
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def loadApiTokens(file_path):
    api_tokens = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                api_tokens[key] = value
    except FileNotFoundError:
        logger.error(f"Secrets file {file_path} not found")
    except Exception as e:
        logger.error(f"Error reading secrets file: {e}")
    return api_tokens

apiTokens = loadApiTokens('/run/secrets/apikeys')

def writeToInfluxdb(apiId, userId, value, fetchTimestamp):
    try:
        influx_url = f"http://influxdataconnector:5000/influxWriteData/{apiId}"
        now = datetime.now(timezone.utc)
        data = {
            "userID": userId,
            "value": value,
            "fetchTimestamp": fetchTimestamp
        }
        response = requests.post(influx_url, json=data)
        response.raise_for_status()
        logger.info(f"Successfully sent data to InfluxDB for API ID {apiId}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to InfluxDB for API ID {apiId}: {e}")


#python fetchApis.py fetchApi --url <url>
def fetchApiWithToken(url, userId, apiId):
    try:
        response = requests.get(f"{url}&token={apiTokens['FINNHUB_KEY']}")
        response.raise_for_status()
        data = response.json()
        fetchTimestamp = datetime.now().isoformat()
        logger.debug(f"Received data for {url}: {data}")
        writeToInfluxdb(apiId, userId, json.dumps(data), fetchTimestamp)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")


def fetchApiWithoutToken(url, userId, apiId):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        fetchTimestamp = datetime.now().isoformat()
        logger.debug(f"Received data for {url}: {data}")
        writeToInfluxdb(apiId, userId, json.dumps(data), fetchTimestamp)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run specific functions from the script.')
    parser.add_argument('function', choices=['fetchApiWithToken', 'fetchApiWithoutToken'], help='Function to run')
    parser.add_argument('--url', help='the Url to fetch')
    parser.add_argument('--userid', help='the Id of the user which wants to fetch the API')
    parser.add_argument('--apiid', help='the Id of the API to fetch')
    
    

    args = parser.parse_args()

    if args.function == 'fetchApiWithToken':
        if args.url and args.userid and args.apiid:
            fetchApiWithToken(args.url, args.userid, args.apiid)
        else:
            logger.error("--url & --userid & --apiid argument is required.")
    elif args.function == 'fetchApiWithoutToken':
        if args.url and args.userid and args.apiid:
            fetchApiWithoutToken(args.url, args.userid, args.apiid)
        else:
            logger.error("--url & --userid & --apiid  argument is required.")