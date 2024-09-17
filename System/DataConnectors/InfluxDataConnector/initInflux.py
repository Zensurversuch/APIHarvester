from os import getenv
from influxdb_client import InfluxDBClient, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
from commonRessources import COMPOSE_INFLUX_DB_URL, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.logger import setLoggerLevel
import time
import requests

# -------------------------- Environment Variables -----------------------------------------------------------------------------------------------------------------------------------
# Header generation for internal API calls
apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}
# InfluxDB Configs from environment variables (make sure these are set in your environment)
influxdbToken = getenv("INFLUXDB_TOKEN")
influxdbOrg = getenv("INFLUXDB_ORG")
influxAdminUser = getenv("INFLUXDB_ADMIN_USER")
influxAdminPassword = getenv("INFLUXDB_ADMIN_PASSWORD")

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
logger = setLoggerLevel("InfluxInitializer")

# Initialize InfluxDB client and influx APIs
client = InfluxDBClient(url=COMPOSE_INFLUX_DB_URL, token=influxdbToken, org=influxdbOrg)
influxWriteApi = client.write_api(write_options=SYNCHRONOUS)
influxbucketApi = client.buckets_api()
influxQueryApi = client.query_api()

def initializeInflux(bucketIds):
    """
    Initialize InfluxDB buckets. Creates new buckets if they do not already exist.

    :param bucketIds: List of the available API IDs that correspond to the bucket names.
    """
    logger.info("Initializing Influx DB")
    maxRetries = 5      # if a failure during the InfluxDB initialization occurs, the number of retries is set here
    for attempt in range(maxRetries):
        try:
            # Fetch organizations
            orgs = client.organizations_api().find_organizations()
            if not orgs:
                logger.warning("No organizations found.")
                return
            orgId = orgs[0].id
            print(f"Using org_id: {orgId}")

            # Fetch existing buckets
            existing_buckets = influxbucketApi.find_buckets_iter()
            existing_bucket_names = {bucket.name for bucket in existing_buckets}
            print(f"Existing buckets: {existing_bucket_names}")

            # Create buckets if they do not exist
            for bucket in bucketIds:
                bucketName = f"{bucket}_bucket"
                if bucketName in existing_bucket_names:
                    print(f"Bucket '{bucketName}' already exists. Skipping creation.")
                else:
                    try:
                        influxbucketApi.create_bucket(
                            bucket_name=bucketName,
                            org_id=orgId,
                            retention_rules=BucketRetentionRules(type="expire", every_seconds=3600*24*365*100)  # 100 Jahre Aufbewahrungsregel
                        )
                        print(f"Bucket '{bucketName}' created.")
                    except Exception as e:
                        print(f"Error creating bucket '{bucketName}': {e}")
            break  # Exit the retry initializing Influx loop if successful
        except Exception as e:
            logger.error(f"Error fetching org_id or existing buckets: {e}")
            logger.info(f"Retrying in 5 seconds... ({attempt + 1}/{maxRetries})")
            time.sleep(5)
    else:
        logger.warning("Max retries reached. Exiting.")

def getAvailableApiIds(apiUrl):
    """
    Fetch available API IDs from an the PostgresSQL DB.

    :param apiUrl: URL to fetch the API IDs from
    :return: List of API IDs (or empty list on failure)
    """
    maxRetries = 5
    for attempt in range(maxRetries):   # Has to be done in a loop because the PostgresSQL DB might not be ready yet
        try:
            response = requests.get(apiUrl, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            return data
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} - Error fetching available API IDs: {e}")
            time.sleep(5)  # Wait before retrying
    print("Max retries reached. Exiting.")
    return []

if __name__ == '__main__':
    availableApiIds = getAvailableApiIds(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/availableApisIds")
    initializeInflux(availableApiIds)
