from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@database:5432/{os.getenv('POSTGRES_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    return app

app = create_app()
@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000, debug=True)