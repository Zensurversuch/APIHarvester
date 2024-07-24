import time
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models.models import Base, User
from os import getenv
from interfaces import UserRole

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


app = Flask(__name__)

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
            email=email,
            password=password,
            lastName='Last1',
            firstName='First1',
            role=UserRole.ADMIN
            )
            session.add(user)
            session.commit()
            print("Admin user created successfully.")
    else:
        print("Environment variables First_USER_EMAIL or First_USER_PASSWORD are not set.")
    print("Database initialized.")
    session.close()

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)