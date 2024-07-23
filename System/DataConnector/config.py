# config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://postgres:test@"
        f"localhost:5432/"
        f"postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')  # Example for additional configuration
