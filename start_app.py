from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from setup_db import db


def start_app(db):
    """
start_app(db) -> Flask
This function initializes a Flask application, configure the database and returns the Flask app.
It takes a single argument db, which is an instance of SQLAlchemy.
It pushes the app context, sets the configuration for SQLAlchemy such as the database URI and disables modification tracking.
It initializes the db with the app and creates all the tables.
It also loads the environment variables using the load_dotenv() function.
It returns the Flask app instance.
Returns:
Flask: The Flask app instance.
"""
    app = Flask(__name__)
    app.app_context().push()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    load_dotenv()
    db.create_all()
    migrate = Migrate(app, db, render_as_batch=True)
    return app
