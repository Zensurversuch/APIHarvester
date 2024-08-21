from os import getenv
from influxdb_client import InfluxDBClient, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import requests


# InfluxDB Configs
influxdbUrl = "http://influxdb:8086"
influxdbToken = getenv("INFLUXDB_TOKEN")
influxdbOrg = getenv("INFLUXDB_ORG")
influxAdminUser = getenv("INFLUXDB_ADMIN_USER")
influxAdminPassword = getenv("INFLUXDB_ADMIN_PASSWORD")

# Influx Init
client = InfluxDBClient(url=influxdbUrl, token=influxdbToken, org=influxdbOrg)
influxWriteApi = client.write_api(write_options=SYNCHRONOUS)
influxbucketApi = client.buckets_api()
influxQueryApi = client.query_api()

def initializeInflux(bucketIds):
    print("Initializing Influx DB")
    maxRetries = 5
    for attempt in range(maxRetries):
        try:
            # Fetch organizations
            orgs = client.organizations_api().find_organizations()
            if not orgs:
                print("No organizations found.")
                return
            orgId = orgs[0].id
            print(f"Using org_id: {orgId}")

            # Fetch existing buckets
            existing_buckets = influxbucketApi.find_buckets_iter()
            existing_bucket_names = {bucket.name for bucket in existing_buckets}
            print(f"Existing buckets: {existing_bucket_names}")

            for bucket in bucketIds:
                bucketName = f"{bucket}_bucket"
                if bucketName in existing_bucket_names:
                    print(f"Bucket '{bucketName}' already exists. Skipping creation.")
                else:
                    try:
                        # Create bucket
                        influxbucketApi.create_bucket(
                            bucket_name=bucketName,
                            org_id=orgId,
                            retention_rules=BucketRetentionRules(type="expire", every_seconds=3600*24*365*100)  # 100 Jahre Aufbewahrungsregel
                        )
                        print(f"Bucket '{bucketName}' created.")
                    except Exception as e:
                        print(f"Error creating bucket '{bucketName}': {e}")
            break  # Exit loop if successful
        except Exception as e:
            print(f"Error fetching org_id or existing buckets: {e}")
            print(f"Retrying in 5 seconds... ({attempt + 1}/{maxRetries})")
            time.sleep(5)
    else:
        print("Max retries reached. Exiting.")

def getAvailableApiIds(api_url):
    maxRetries = 5
    for attempt in range(maxRetries):
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} - Error fetching available API IDs: {e}")
            time.sleep(5)  # Wait before retrying
    print("Max retries reached. Exiting.")
    return []

if __name__ == '__main__':
    availableApiIds = getAvailableApiIds("http://postgresdataconnector:5000/availableApisIds")
    initializeInflux(availableApiIds)
