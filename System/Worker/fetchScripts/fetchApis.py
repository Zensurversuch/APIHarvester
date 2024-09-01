import requests
import logging
from os import getenv
import argparse
from datetime import datetime, timezone
import json
from commonRessources import COMPOSE_INFLUX_DATA_CONNECTOR_URL, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.interfaces import SubscriptionStatus
from commonRessources.logger import setLoggerLevel

logger = setLoggerLevel("WorkerFetchApis")

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

def logErrorToPostgres(apiID, subscriptionID, error_message):
    try:
        response = requests.post(
            f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus",
            json={
                "subscriptionID": subscriptionID,
                "subscriptionStatus": SubscriptionStatus.ERROR.value,
            }
        )
        response.raise_for_status()
        logger.info(f"Logged error to PostgreSQL for subscription ID {subscriptionID}: {error_message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to log error to PostgreSQL for subscription ID {subscriptionID}: {e}")


def writeToInfluxdb(apiID, subscriptionID, value, fetchTimestamp):
    try:
        influx_url = f"{COMPOSE_INFLUX_DATA_CONNECTOR_URL}/influxWriteData/{apiID}"
        now = datetime.now(timezone.utc)
        data = {
            "subscriptionID": subscriptionID,
            "value": value,
            "fetchTimestamp": fetchTimestamp
        }
        response = requests.post(influx_url, json=data)
        response.raise_for_status()
        logger.info(f"Successfully sent data to InfluxDB for API ID {apiID}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to InfluxDB for API ID {apiID}: {e}")


#python fetchApis.py fetchApi --url <url> --subscriptionID <subscriptionID> --apiId <apiId>
def fetchApiWithToken(url, subscriptionID, apiID):
    try:
        response = requests.get(f"{url}&token={apiTokens['FINNHUB_KEY']}")
        response.raise_for_status()
        data = response.json()
        fetchTimestamp = datetime.now().isoformat()
        logger.debug(f"Received data for {url}: {data}")
        writeToInfluxdb(apiID, subscriptionID, json.dumps(data), fetchTimestamp)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")
        logErrorToPostgres(apiID, subscriptionID, str(e))


def fetchApiWithoutToken(url, subscriptionID, apiID):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        fetchTimestamp = datetime.now().isoformat()
        logger.debug(f"Received data for {url}: {data}")
        writeToInfluxdb(apiID, subscriptionID, json.dumps(data), fetchTimestamp)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")
        logErrorToPostgres(apiID, subscriptionID, str(e))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run specific functions from the script.')
    parser.add_argument('function', choices=['fetchApiWithToken', 'fetchApiWithoutToken'], help='Function to run')
    parser.add_argument('--url', help='the Url to fetch')
    parser.add_argument('--subscriptionID', help='the Id of the subscription')
    parser.add_argument('--apiID', help='the Id of the API to fetch')

    args = parser.parse_args()

    if args.function == 'fetchApiWithToken':
        if args.url and args.subscriptionID and args.apiID:
            fetchApiWithToken(args.url, args.subscriptionID, args.apiID)
        else:
            logger.error("--url & --subscriptionID & --apiID argument is required.")
    elif args.function == 'fetchApiWithoutToken':
        if args.url and args.subscriptionID and args.apiID:
            fetchApiWithoutToken(args.url, args.subscriptionID, args.apiID)
        else:
            logger.error("--url & --subscriptionID & --apiID  argument is required.")