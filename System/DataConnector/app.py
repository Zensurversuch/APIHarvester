from datetime import timedelta, datetime
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

app = Flask(__name__)

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"
app.config["JWT_SECRET_KEY"] = f"{getenv('JWT_SECRET_KEY')}"
apiMessageDescriptor = "response"
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

jwt = JWTManager(app)
CORS(app)

engine = create_engine(POSTGRES_URL)
userRepo = userRepository.UserRepository(engine)

# -------------------------- User Routes ------------------------------------------------------------------------------------------------------------------------------------------
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


def initialize_database():
    isDatabaseReady = False
    while not isDatabaseReady:
        try:
            engine = create_engine(POSTGRES_URL)

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

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)