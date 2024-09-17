import requests
import logging
from os import getenv
import argparse
from datetime import datetime, timezone
import json
from commonRessources import COMPOSE_INFLUX_DATA_CONNECTOR_URL, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.interfaces import SubscriptionStatus

apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
    }
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
        response = requests.post(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/setSubscriptionsStatus",
            json={
                "subscriptionID": subscriptionID,
                "subscriptionStatus": SubscriptionStatus.ERROR.value,
            },
            headers=headers)
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
        response = requests.post(influx_url, json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully sent data to InfluxDB for API ID {apiID}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to InfluxDB for API ID {apiID}: {e}")


def fetchApi(url, subscriptionID, apiID, tokenRequired):
    try:
        if tokenRequired:
            availableApiResponse = requests.get(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/availableApi/{apiID}", headers=headers)
            availableApiResponse.raise_for_status()
            availableApiName = availableApiResponse.json().get('name').split(' ')[0].upper()
            apiToken = apiTokens[availableApiName + '_KEY']
            if availableApiName == 'FINNHUB':
                response = requests.get(f"{url}&token={apiToken}")
            elif availableApiName == 'ALPHAVANTAGE':
                response = requests.get(f"{url}&apikey={apiToken}")
            else:
                logger.error(f"API {availableApiName} not supported")
                logErrorToPostgres(apiID, subscriptionID, f"API {availableApiName} not supported")
        else:
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
    parser.add_argument('--url', help='the Url to fetch')
    parser.add_argument('--tokenRequired', help='is an API token required to fetch the API')
    parser.add_argument('--subscriptionID', help='the Id of the subscription')
    parser.add_argument('--apiID', help='the Id of the API to fetch')

    args = parser.parse_args()

    if args.url and args.tokenRequired and args.subscriptionID and args.apiID:
        fetchApi(args.url, args.subscriptionID, args.apiID, args.tokenRequired)
    else:
        logger.error("--url & --tokenRequired & --subscriptionID & --apiID argument is required.")