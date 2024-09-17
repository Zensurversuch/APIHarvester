from datetime import timedelta, datetime, timezone
import hashlib
import time
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




# -------------------------- PostgreSQL User Routes ------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
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
                                           expires_delta=timedelta(hours=1),
                                           additional_claims={'role': user.role.value})
        userRepo.updateUserLastLogin(user.userID, datetime.now())
        return jsonify(access_token=access_token, userID = user.userID, role = user.role.value), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Incorrect user name or password"}), 401

@app.route('/createUser', methods=['POST'])
def createUser():
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


# -------------------------- PostgreSQL Subscription Routes -------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/subscriptions', methods=['GET'])
@accessControlJwtOrApiKey
def subscriptions():
    subscriptions = subscriptionRepo.getSubscriptions()
    if subscriptions is not None:
        subscriptionsDict = [subscription.toDict() for subscription in subscriptions]
        return jsonify(subscriptionsDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscriptions found"}), 404
    
@app.route('/subscription/<int:subscriptionID>', methods=['GET'])
@accessControlApiKey
def subscription(subscriptionID):
    subscription = subscriptionRepo.getSubscriptionByID(subscriptionID)
    if subscription is not None:
        return jsonify(subscription.toDict()), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscription with ID {subscriptionID} found"}), 404

@app.route('/subscriptionsByStatus/<string:subscriptionStatus>', methods=['GET'])       # NOT USED AT THE MOMENT
def subscriptionsByStatus(subscriptionStatus):
    try:
        # Attempt to match the status with the Enum
        validSubscriptionStatus = SubscriptionStatus(subscriptionStatus)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid subscriptionStatus value provided. Must be one of {[status.value for status in SubscriptionStatus]}"}), 400
    subscriptions = subscriptionRepo.getSubscriptionsByStatus(validSubscriptionStatus)
    if subscriptions is not None:
        subscriptionsDict = [subscription.toDict() for subscription in subscriptions]
        return jsonify(subscriptionsDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscriptions with Status {subscriptionStatus} found"}), 404

@app.route('/subscriptionsByUserID/<string:userID>', methods=['GET'])
@accessControlJwt
def subscriptionsByUserID(userID):
    subscriptions = subscriptionRepo.getSubscriptionsByUserID(userID)   
    if subscriptions is not None:
        subscriptionsDict = [subscription.toDict() for subscription in subscriptions]
        return jsonify(subscriptionsDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No subscriptions with userID {userID} found"}), 404

@app.route('/setSubscriptionsStatus', methods=['POST'])
@accessControlApiKey
def setSubscriptionsStatus():
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


# -------------------------- PostgreSQL AvailableApi Routes -------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/availableApis', methods=['GET'])
@accessControlJwt
def availableApis():
    availableApis = availableApiRepo.getAvailableApis()
    if availableApis is not None:
        availableApisDict = [availableApi.toDict() for availableApi in availableApis]
        return jsonify(availableApisDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApis found"}), 404

@app.route('/availableApisIds', methods=['GET'])
@accessControlApiKey
def availableApisIds():
    Ids = availableApiRepo.getAvailableApisIds()
    if Ids is not None:
        return jsonify(Ids), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApis found"}), 404

@app.route('/availableApi/<int:availableApiID>', methods=['GET'])
@accessControlApiKey
def availableApi(availableApiID):
    availableApi = availableApiRepo.getAvailableApiByID(availableApiID)
    if availableApi is not None:
        return jsonify(availableApi.toDict()), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApiID with ID {availableApiID} found"}), 404

@app.route('/availableApisBySubscriptionType/<string:subscriptionType>', methods=['GET'])       # NOT USED AT THE MOMENT
def availableApisBySubscriptionType(subscriptionType):
    try:
        # Attempt to match the status with the Enum
        validSubscriptionType = SubscriptionType(subscriptionType)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid subscriptionType value provided. Must be one of {[type.value for type in SubscriptionType]}"}), 400
    
    availableApis =  availableApiRepo.getAvailableApiBySubscriptionType(validSubscriptionType)
    if availableApis is not None:
        availableApisDict = [availableApi.toDict() for availableApi in availableApis]
        return jsonify(availableApisDict), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}No availableApis with subscriptionType {subscriptionType} found"}), 404

@app.route('/createAvailableApi', methods=['POST'])     # NOT USED AT THE MOMENT
def createAvailableApi():
    if not request.is_json:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing JSON in the request"}), 400

    dataUrl = request.json.get('url', None)
    dataName = request.json.get('name', None)
    dataDescription = request.json.get('description', None)
    dataSubscriptionType = request.json.get('subscriptionType', None)
    dataRelevantFields = request.json.get('relevantFields', None)

    if not dataUrl or not dataName or not dataDescription or not dataSubscriptionType or not dataRelevantFields:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}Missing url, name, subscriptionType or relevantFields"}), 400
    
    try:
        # Attempt to match the status with the Enum
        validSubscriptionType = SubscriptionType(dataSubscriptionType)
    except ValueError:
        return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Invalid subscriptionType value provided. Must be one of {[type.value for type in SubscriptionType]}"}), 400
    
    if availableApiRepo.createAvailableApi(dataUrl, dataName, validSubscriptionType, dataRelevantFields):
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.SUCCESS}availableApi created successfully"}), 200
    else:
        return jsonify({API_MESSAGE_DESCRIPTOR:  f"{ApiStatusMessages.ERROR}availableApi could not be created"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)