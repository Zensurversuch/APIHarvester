import requests
from datetime import timedelta, datetime, timezone
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from os import getenv
from influxdb_client import Point
from initInflux import influxWriteApi, influxQueryApi, influxbucketApi,influxdbOrg
from flask_cors import CORS
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources import API_MESSAGE_DESCRIPTOR, COMPOSE_POSTGRES_DATA_CONNECTOR_URL
from commonRessources.decorators import accessControlApiKey, accessControlJwtOrApiKey

app = Flask(__name__)
# -------------------------- Environment Variables -----------------------------------------------------------------------------------------------------------------------------------
apiKey = getenv('INTERNAL_API_KEY')
headers = {
    'x-api-key': apiKey
}
app.config["JWT_SECRET_KEY"] = f"{getenv('JWT_SECRET_KEY')}"

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
jwt = JWTManager(app)  # Initializes JWT manager for authentication
CORS(app)  # Enables Cross-Origin Resource Sharing for API access across different origins


# -------------------------- InfluxDB Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/influxWriteData/<int:apiId>', methods=['POST'])
@accessControlApiKey
def influxWriteData(apiId):
    """
    This route writes data into an InfluxDB bucket based on the provided API ID which represents
    the availableApiID that is stored in the PostgreSQL database.

    :param apiId: API ID to identify the associated InfluxDB bucket.
    :return: A JSON response indicating success or failure of the write operation.

    Request JSON data structure:
    {
        "subscriptionID": <str>,  # ID of the subscription
        "value": <float>,         # Value to be stored in InfluxDB
        "fetchTimestamp": <str>   # Timestamp when the data was fetched by the worker
    }

    1. Fetches the subscription data using the subscriptionID.
    2. Verifies if the subscription is valid and active.
    3. Writes data into an InfluxDB bucket.
    """
    data = request.json
    subscriptionID = data.get("subscriptionID")
    value = data.get("value")
    fetchTimestamp = data.get("fetchTimestamp")

    if not subscriptionID or not value or not fetchTimestamp:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Missing required fields in the request"}), 400

    # Check if the given subscriptionId exists
    try:
        response = requests.get(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}", headers=headers)
        response.raise_for_status()
        subscriptionData = response.json()
        if not subscriptionData:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Subscription with ID {subscriptionID} does not exist"}), 404
        elif subscriptionData.get("status") == SubscriptionStatus.INACTIVE or subscriptionData.get("status") == SubscriptionStatus.ERROR:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Subscription with ID {subscriptionID} is not active or has an error"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error fetching subscription data: {e}"}), 500

    # actual writing process
    now = datetime.now(timezone.utc)
    point = Point(apiId) \
        .tag("subscriptionID", subscriptionID) \
        .field("fetchTimestamp", fetchTimestamp) \
        .field("value", value) \
        .time(now)

    bucketName = f"{apiId}_bucket"

    try:
        influxWriteApi.write(bucket=bucketName, org=influxdbOrg, record=point)
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}Data written to InfluxDB bucket {bucketName}"}), 200
    except Exception as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Failed to write data to InfluxDB bucket {bucketName}"}), 500

@app.route('/influxGetData/<int:subscriptionID>/<int:queryTimespan>', methods=['GET'])
@accessControlJwtOrApiKey
def influxGetData(subscriptionID, queryTimespan):
    """
    This route retrieves data from an InfluxDB bucket based on the subscription ID and a timespan.

    :param subscriptionID: ID of the subscription to filter data for.
    :param queryTimespan: Time span in minutes to filter records in the past.
    :return: A JSON response containing the queried data or an error message.

    1. Fetches the subscription data using the subscriptionID.
    2. Retrieves data from the associated InfluxDB bucket for the specified time period.
    """
    # Fetch subscription data to get availableAPIID
    try:
        response = requests.get(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}", headers=headers)
        response.raise_for_status()
        subscriptionData = response.json()
        apiId = subscriptionData.get("availableApiID")
        if not apiId:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Available API ID not found in subscription data"}), 404
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error fetching subscription data: {e}"}), 500
    bucketName = f"{apiId}_bucket"

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=queryTimespan)

    # InfluxDB query for data filtering by subscriptionID and time range
    query = f'''
    from(bucket: "{bucketName}")
        |> range(start: {start.isoformat()}, stop: {now.isoformat()})
        |> filter(fn: (r) => r["subscriptionID"] == "{subscriptionID}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    try:
        tables = influxQueryApi.query(org=influxdbOrg, query=query)
        result = [record.values for table in tables for record in table.records]
    except Exception as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error querying InfluxDB: {e}"}), 500

    return jsonify(result), 200


if __name__ == '__main__':          # Only executed when using the Dockerfile.dev
                                    # Otherwise, the app is started by the WSGI server
    app.run(host='0.0.0.0', port=5000, debug=True)