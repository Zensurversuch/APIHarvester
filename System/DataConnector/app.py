from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models.models import Base, User
from os import getenv

# -------------------------- Environment Variables ------------------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://postgres:{getenv('POSTGRES_PW')}@database/postgres"



app = Flask(__name__)

@app.route('/hello')
def hello():
    return 'Hello, World from DataConnector!'


def initialize_database(postgres_pw, ip):
    POSTGRES_URL = f"postgresql://postgres:{postgres_pw}@{ip}:5432/postgres"
    engine = create_engine(POSTGRES_URL)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    #add admin user during initial setup
    if session.query(User).count() == 0:
        users = [
            User(email='user1@example.com', password='password1', lastName='Last1', firstName='First1', role='admin'),
        ]

        session.add_all(users)
        session.commit()
    print("Database initialized.")

if __name__ == '__main__':
    initialize_database("test", "database" )
    app.run(host='0.0.0.0', port=5000, debug=True)