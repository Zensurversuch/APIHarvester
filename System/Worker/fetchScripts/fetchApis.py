import requests
import logging
from os import getenv
import argparse
from datetime import datetime, timezone

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



#python fetchApis.py fetchApi --url <url>
def fetchApiWithToken(url):
    try:
        response = requests.get(f"{url}&token={apiTokens['FINNHUB_KEY']}")
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received data for {url}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")


def fetchApiWithoutToken(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received data for {url}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {url}: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run specific functions from the script.')
    parser.add_argument('function', choices=['fetchApiWithToken', 'fetchApiWithoutToken'], help='Function to run')
    parser.add_argument('--url', help='the Url to fetch')

    args = parser.parse_args()

    if args.function == 'fetchApiWithToken':
        if args.url:
            fetchApiWithToken(args.url)
        else:
            logger.error("--url argument is required.")
    elif args.function == 'fetchApiWithoutToken':
        if args.url:
            fetchApiWithoutToken(args.url)
        else:
            logger.error("--url argument is required.")