from flask import Flask
from flask_migrate import Migrate
from models.init_db import db, User  # Import your models here
from config import Config


def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints or routes
    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)