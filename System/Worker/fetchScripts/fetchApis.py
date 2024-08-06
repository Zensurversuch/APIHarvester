import requests
import logging
from os import getenv
import argparse

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

#python fetchApis.py fetchFinnhub --symbol AAPL
def fetchFinnhub(stockSymbol):
    baseUrl = "https://finnhub.io/api/v1/"

    params = {
        'symbol': stockSymbol,
        'token': apiTokens['FINNHUB_KEY']
    }
    try:
        response = requests.get(f"{baseUrl}/quote", params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received data for {stockSymbol}: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {stockSymbol}: {e}")

def fetchXY():
    logger.info("FETCHING XY")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run specific functions from the script.')
    parser.add_argument('function', choices=['fetchFinnhub', 'fetchXY'], help='Function to run')
    parser.add_argument('--stockSymbol', help='Stock symbol for fetchFinnhub')

    args = parser.parse_args()

    if args.function == 'fetchFinnhub':
        if args.stockSymbol:
            fetchFinnhub(args.stockSymbol)
        else:
            logger.error("For 'fetchFinnhub', --stockSymbol argument is required.")
    elif args.function == 'fetchXY':
        fetchXY()