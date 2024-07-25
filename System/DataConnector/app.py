from datetime import timedelta, datetime, timezone
import hashlib
import time
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models.models import Base, User
from repositories import userRepository
from flask_cors import CORS
from os import getenv
from interfaces import UserRole, ApiStatusMessages
from influxdb_client import InfluxDBClient, Point, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client import bucket_api
from datetime import datetime

app = Flask(__name__)

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"
app.config["JWT_SECRET_KEY"] = f"{getenv('JWT_SECRET_KEY')}"
apiMessageDescriptor = "response"

# InfluxDB Configs
influxdbUrl = "http://influxdb:8086"
influxdbToken = getenv("INFLUXDB_TOKEN")
influxdbOrg = getenv("INFLUXDB_ORG")
influxAdminUser = getenv("INFLUXDB_ADMIN_USER")
influxAdminPassword = getenv("INFLUXDB_ADMIN_PASSWORD")


# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------

jwt = JWTManager(app)
CORS(app)

# Postgres Init
engine = create_engine(POSTGRES_URL)
userRepo = userRepository.UserRepository(engine)

# Influx Init
client = InfluxDBClient(url=influxdbUrl, token=influxdbToken, org=influxdbOrg)
influxWriteApi = client.write_api(write_options=SYNCHRONOUS)
influxbucketApi = client.buckets_api()
influxQueryApi = client.query_api()

def initializePostgres():
    isDatabaseReady = False
    while not isDatabaseReady:
        try:
            Base.metadata.create_all(engine)

            Session = sessionmaker(bind=engine)
            session = Session()
            isDatabaseReady = True
        except Exception as e:
            print(f"PostgreSQL is unavailable - retrying in 1 second: {e}")
            time.sleep(1)

    #add admin user during initial setup
    if session.query(User).count() == 0:
        email = getenv('USER_EMAIL')
        password = getenv('USER_PASSWORD')
        if email and password:
        # Create the admin user
            user = User(
            email = email,
            password = hashlib.sha256(password.encode('utf-8')).hexdigest(),
            lastName = 'Last1',
            firstName = 'First1',
            role=UserRole.ADMIN
            )
            session.add(user)
            session.commit()
            print("Admin user created successfully.")
        else:
            print("Environment variables USER_EMAIL or USER_PASSWORD are not set.")

    print("Database initialized.")
    session.close()

def initializeInflux(bucketIds):
    print("Initializing Influx DB")
    try:
        # Fetch organizations
        orgs = client.organizations_api().find_organizations()
        if not orgs:
            print("No organizations found.")
            return
        org_id = orgs[0].id
        print(f"Using org_id: {org_id}")

        # Fetch existing buckets
        existing_buckets = influxbucketApi.find_buckets_iter()
        existing_bucket_names = {bucket.name for bucket in existing_buckets}
        print(f"Existing buckets: {existing_bucket_names}")

        for bucket in bucketIds:
            bucket = f"{bucket}_bucket"
            if bucket in existing_bucket_names:
                print(f"Bucket '{bucket}' already exists. Skipping creation.")
            else:
                try:
                    # Create bucket
                    influxbucketApi.create_bucket(
                        bucket_name=bucket,
                        org_id=org_id,
                        retention_rules=BucketRetentionRules(type="expire", every_seconds=3600*24*365*100)  # 100 Jahre Aufbewahrungsregel
                    )
                    print(f"Bucket '{bucket}' created.")
                except Exception as e:
                    print(f"Error creating bucket '{bucket}': {e}")
    except Exception as e:
        print(f"Error fetching org_id or existing buckets: {e}")



# -------------------------- PostgreSQL User Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({apiMessageDescriptor:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    dataEmail = request.json.get('email', None)
    dataPassword = request.json.get('password', None)
    hashedPassword = hashlib.sha256(dataPassword.encode('utf-8')).hexdigest()
    if not dataEmail or not dataPassword:
        return jsonify({apiMessageDescriptor:  f"{ApiStatusMessages.ERROR}Missing email or password"}), 400
    user = userRepo.getUserByEmail(dataEmail)
    print(user)
    if user and (hashedPassword == user.password):
        access_token = create_access_token(identity=user.userID, expires_delta=timedelta(hours=1))
        userRepo.updateUserLastLogin(user.userID, datetime.now())
        return jsonify(access_token=access_token, userID = user.userID, role = user.role.value), 200
    else:
        return jsonify({apiMessageDescriptor:  f"{ApiStatusMessages.ERROR}Incorrect user name or password"}), 401

@app.route('/createUser', methods=['POST'])
def createUser():
    data = request.json
    dataEmail = data.get('email')
    dataPassword = data.get('password')
    dataLastName = data.get('lastName')
    dataFirstName = data.get('firstName')
    if not (dataEmail and dataPassword and dataLastName and dataFirstName):
        return jsonify({apiMessageDescriptor:  f"{ApiStatusMessages.ERROR}Fill in all required fields"}), 400

    if userRepo.getUserByEmail(dataEmail):
        return jsonify({apiMessageDescriptor: f"{ApiStatusMessages.ERROR}A user with the email {dataEmail} already exists"}), 500

    ret_value = userRepo.createUser(dataEmail, dataPassword, dataLastName, dataFirstName, UserRole.USER)

    if ret_value == False:
        return jsonify({apiMessageDescriptor: f"{ApiStatusMessages.ERROR}User could not be created"}), 500

    return jsonify({apiMessageDescriptor: f"{ApiStatusMessages.SUCCESS}User created successfully"}), 201

@app.route('/hello')
def hello():
    return 'Hello, World from DataConnector!'




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
    initializePostgres()
    #TO DO: Change the parameters the AvailableApiId if implemented
    initializeInflux(["1", "2"])
    app.run(host='0.0.0.0', port=5000, debug=True)