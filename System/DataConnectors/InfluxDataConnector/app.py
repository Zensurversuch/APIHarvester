from datetime import timedelta, datetime, timezone
from flask import Flask, jsonify, request
from os import getenv
from influxdb_client import InfluxDBClient, Point
from initInflux import influxWriteApi, influxQueryApi, influxbucketApi,influxdbOrg

app = Flask(__name__)

# -------------------------- InfluxDB Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/influxWriteData/<apiId>', methods=['POST'])
def influxWriteData(apiId):
    data = request.json
    userId = data.get("userID")
    value = data.get("value")
    fetchTimestamp = data.get("fetchTimestamp")

    now = datetime.now(timezone.utc)
    point = Point(apiId) \
        .tag("userId", userId) \
        .field("fetchTimestamp", fetchTimestamp) \
        .field("value", value) \
        .time(now)

    bucketName = f"{apiId}_bucket"
    influxWriteApi.write(bucket=bucketName, org=influxdbOrg, record=point)

    return jsonify({"message": f"Data written to InfluxDB bucket {bucketName}"}), 200

@app.route('/influxGetData/<apiId>/<userId>', methods=['GET'])
# @jwt_required()
def influxGetData(apiId, userId):
    bucketName = f"{apiId}_bucket"

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=1)         # start for query: query can be restricted in this way

    query = f'''
    from(bucket: "{bucketName}")
        |> range(start: {start.isoformat()}, stop: {now.isoformat()})
        |> filter(fn: (r) => r["userId"] == "{userId}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    try:
        tables = influxQueryApi.query(org=influxdbOrg, query=query)
        result = [record.values for table in tables for record in table.records]
    except Exception as e:
        return jsonify({"message": f"Error querying InfluxDB: {e}"}), 500

    return jsonify(result), 200


@app.route('/influxGetBuckets', methods=['GET'])
def getBuckets():
    try:
        buckets = influxbucketApi.find_buckets_iter()
        bucketList = [bucket.name for bucket in buckets]
        return jsonify(bucketList), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching buckets from InfluxDB: {e}"}), 500


if __name__ == '__main__':
    #TO DO: Change the parameters the AvailableApiId if implemented
    app.run(host='0.0.0.0', port=5000, debug=True)