import requests
from datetime import timedelta, datetime, timezone
from flask import Flask, jsonify, request
from os import getenv
from influxdb_client import Point
from initInflux import influxWriteApi, influxQueryApi, influxbucketApi,influxdbOrg
from commonRessources.interfaces import ApiStatusMessages, SubscriptionStatus
from commonRessources import API_MESSAGE_DESCRIPTOR, COMPOSE_POSTGRES_DATA_CONNECTOR_URL

app = Flask(__name__)

# -------------------------- InfluxDB Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/influxWriteData/<int:apiId>', methods=['POST'])
def influxWriteData(apiId):
    data = request.json
    subscriptionID = data.get("subscriptionID")
    value = data.get("value")
    fetchTimestamp = data.get("fetchTimestamp")

    if not subscriptionID or not value or not fetchTimestamp:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Missing required fields in the request"}), 400

    # Check if the subscriptionId exists
    try:
        response = requests.get(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}")
        response.raise_for_status()
        subscriptionData = response.json()
        if not subscriptionData:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Subscription with ID {subscriptionID} does not exist"}), 404
        elif subscriptionData.get("status") == SubscriptionStatus.INACTIVE or subscriptionData.get("status") == SubscriptionStatus.ERROR:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Subscription with ID {subscriptionID} is not active or has an error"}), 400
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error fetching subscription data: {e}"}), 500

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

# timespan (minutes) is used to restrict the query to a certain time period in the past
@app.route('/influxGetData/<int:subscriptionID>/<int:queryTimespan>', methods=['GET']) 
# @jwt_required()
def influxGetData(subscriptionID, queryTimespan):
    # Fetch subscription data to get availableAPIID
    try:
        response = requests.get(f"{COMPOSE_POSTGRES_DATA_CONNECTOR_URL}/subscription/{subscriptionID}")
        response.raise_for_status()
        subscriptionData = response.json()
        apiId = subscriptionData.get("availableApiID")
        if not apiId:
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Available API ID not found in subscription data"}), 404
    except requests.RequestException as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error fetching subscription data: {e}"}), 500
    bucketName = f"{apiId}_bucket"

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=queryTimespan)         # start for query: query can be restricted in this way

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


@app.route('/influxGetBuckets', methods=['GET'])
def getBuckets():
    try:
        buckets = influxbucketApi.find_buckets_iter()
        bucketList = [bucket.name for bucket in buckets]
        return jsonify(bucketList), 200
    except Exception as e:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Error fetching buckets from InfluxDB: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)