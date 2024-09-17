from datetime import timedelta, datetime
import hashlib
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from os import getenv
from commonRessources.interfaces import UserRole, ApiStatusMessages, SubscriptionStatus, SubscriptionType
from commonRessources import API_MESSAGE_DESCRIPTOR
from commonRessources.decorators import accessControlApiKey, accessControlJwtOrApiKey, accessControlJwt
from initPostgres import userRepo, subscriptionRepo, availableApiRepo

app = Flask(__name__)

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"
app.config["JWT_SECRET_KEY"] = f"{getenv('JWT_SECRET_KEY')}"


# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
jwt = JWTManager(app)
CORS(app)


# -------------------------- PostgreSQL User API Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JWT access token if the credentials are valid.

    :return: The access token if the user is authenticated.

    Request JSON data structure:
    {
        "email": <str>,     # User email
        "password": <str>   # User password
    }
    """
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    dataEmail = request.json.get('email', None)
    dataPassword = request.json.get('password', None)
    hashedPassword = hashlib.sha256(dataPassword.encode('utf-8')).hexdigest()

    if not dataEmail or not dataPassword:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing email or password"}), 400

    user = userRepo.getUserByEmail(dataEmail)
    if user and (hashedPassword == user.password):
        access_token = create_access_token(identity=user.userID,
                                           expires_delta=timedelta(hours=1),            # set the token expiry time here
                                           additional_claims={'role': user.role.value}) # add the user role to the token for later access control
        userRepo.updateUserLastLogin(user.userID, datetime.now())
        return jsonify(access_token=access_token, userID = user.userID, role = user.role.value), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Incorrect user name or password"}), 401

@app.route('/createUser', methods=['POST'])
def createUser():
    """
    Creates a new user in the database.

    Request JSON data structure:
    {
        "email": <str>,         # User email
        "password": <str>,      # User password
        "lastName": <str>,      # User last name
        "firstName": <str>,     # User first name
        "role": <str>           # User role
    }
    """
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    data = request.json
    dataEmail = data.get('email')
    dataPassword = data.get('password')
    dataLastName = data.get('lastName')
    dataFirstName = data.get('firstName')
    dataRole = data.get('role')

    if not (dataEmail and dataPassword and dataLastName and dataFirstName and dataRole):
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Fill in all required fields"}), 400

    if userRepo.getUserByEmail(dataEmail):
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}A user with the email {dataEmail} already exists"}), 500

    try:
        # Attempt to match the status with the Enum
        validUserRole = UserRole(dataRole)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid userRole value provided. Must be one of {[role.value for role in UserRole]}"}), 400
    
    retValue = userRepo.createUser(dataEmail, dataPassword, dataLastName, dataFirstName, validUserRole)

    if retValue == False:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}User could not be created"}), 500

    return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.SUCCESS}User created successfully"}), 201


# -------------------------- PostgreSQL Subscription API Routes -------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/subscriptions', methods=['GET'])
@accessControlJwtOrApiKey
def subscriptions():
    """
    Fetches all subscriptions from the database.

    :return: A JSON list of all subscriptions in the database.
    """
    subscriptions = subscriptionRepo.getSubscriptions()
    if subscriptions is not None:
        subscriptionsDict = [subscription.toDict() for subscription in subscriptions]
        return jsonify(subscriptionsDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscriptions found"}), 404

@app.route('/subscription/<int:subscriptionID>', methods=['GET'])
@accessControlApiKey
def subscription(subscriptionID):
    """
    Fetches a subscription by its ID from the database.

    :param subscriptionID: The ID of the subscription to fetch.
    :return: A JSON object of the subscription with the given ID.
    """
    subscription = subscriptionRepo.getSubscriptionByID(subscriptionID)
    if subscription is not None:
        return jsonify(subscription.toDict()), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscription with ID {subscriptionID} found"}), 404

@app.route('/subscriptionsByUserID/<string:userID>', methods=['GET'])
@accessControlJwt
def subscriptionsByUserID(userID):
    """
    Fetches all subscriptions of a user by the user's ID from the database.

    :param userID: The ID of the user whose subscriptions to fetch.
    :return: A JSON list of all subscriptions of the user with the given ID.
    """
    subscriptions = subscriptionRepo.getSubscriptionsByUserID(userID)
    if subscriptions is not None:
        subscriptionsDict = [subscription.toDict() for subscription in subscriptions]
        return jsonify(subscriptionsDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscriptions with userID {userID} found"}), 404

@app.route('/setSubscriptionsStatus', methods=['POST'])
@accessControlApiKey
def setSubscriptionsStatus():
    """
    Updates the status of a subscription in the database.

    Request JSON data structure:
    {
        "subscriptionID": <int>,            # The ID of the subscription to update
        "subscriptionStatus": <str>,        # The new status of the subscription
        "jobName": <str>,                   # The name of the job
        "command": <str (optional)>,        # The command to execute
        "container": <str>                  # The container to use
    }
    """
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    dataSubscriptionID = request.json.get('subscriptionID', None)
    dataSubscriptionStatus = request.json.get('subscriptionStatus', None)
    dataJobName = request.json.get('jobName', None)
    dataCommand = request.json.get('command', None)
    dataContainer = request.json.get('container', None)

    if not dataSubscriptionID or not dataSubscriptionStatus:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing subscriptionID or subscriptionStatus"}), 400

    try:
        # Attempt to match the status with the Enum
        validSubscriptionStatus = SubscriptionStatus(dataSubscriptionStatus)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid subscriptionStatus value provided. Must be one of {[status.value for status in SubscriptionStatus]}"}), 400

    if subscriptionRepo.setSubsriptionStatus(dataSubscriptionID, validSubscriptionStatus, dataJobName, dataCommand, dataContainer):
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.SUCCESS}subscriptionStatus updated successfully"}), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}subscriptionStatus could not be updated"}), 500

@app.route('/createSubscription', methods=['POST'])
@accessControlApiKey
def createSubscription():
    """
    Creates a new subscription in the database.

    Request JSON data structure:
    {
        "userID": <str>,                # The ID of the user who creates the subscription
        "availableApiID": <int>,        # The ID of the available API to subscribe to
        "interval": <int>,              # The interval in seconds at which the API is called
        "status": <str>,                # The status of the subscription
        "jobName": <str>                # The name of the job
    }

    :return: The ID of the created subscription.
    """
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    dataUserID = request.json.get('userID', None)
    dataAvailableApiID = request.json.get('availableApiID', None)
    dataInterval = request.json.get('interval', None)
    dataStatus = request.json.get('status', None)
    dataJobName = request.json.get('jobName', None)

    if not dataUserID or not dataAvailableApiID or not dataInterval or not dataStatus:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing userID, availableApiID, interval, status or jobName"}), 400

    try:
        # Attempt to match the status with the Enum
        validSubscriptionStatus = SubscriptionStatus(dataStatus)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid subscriptionStatus value provided. Must be one of {[status.value for status in SubscriptionStatus]}"}), 400

    success, subscriptionID = subscriptionRepo.createSubscription(
        dataUserID,
        dataAvailableApiID,
        dataInterval,
        validSubscriptionStatus.value,
        dataJobName
    )

    if success:
        return jsonify(subscriptionID = subscriptionID), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}subscription could not be created"}), 500


# -------------------------- PostgreSQL AvailableApi API Routes -------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/availableApis', methods=['GET'])
@accessControlJwt
def availableApis():
    """
    Fetches all availableApis from the database.

    :return: A JSON list of all availableApis in the database.
    """
    availableApis = availableApiRepo.getAvailableApis()
    if availableApis is not None:
        availableApisDict = [availableApi.toDict() for availableApi in availableApis]
        return jsonify(availableApisDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApis found"}), 404

@app.route('/availableApisIds', methods=['GET'])
@accessControlApiKey
def availableApisIds():
    """
    Fetches all availableApis IDs from the database.

    :return: A JSON list of all availableApis IDs in the database.
    """
    Ids = availableApiRepo.getAvailableApisIds()
    if Ids is not None:
        return jsonify(Ids), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApis found"}), 404

@app.route('/availableApi/<int:availableApiID>', methods=['GET'])
@accessControlApiKey
def availableApi(availableApiID):
    """
    Fetches an availableApi by its ID from the database.

    :param availableApiID: The ID of the availableApi to fetch.
    :return: A JSON object of the availableApi with the given ID
    """
    availableApi = availableApiRepo.getAvailableApiByID(availableApiID)
    if availableApi is not None:
        return jsonify(availableApi.toDict()), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApiID with ID {availableApiID} found"}), 404


if __name__ == '__main__':      # Only executed when using the Dockerfile.dev
                                # Otherwise, the app is started by the WSGI server
    app.run(host='0.0.0.0', port=5000, debug=True)