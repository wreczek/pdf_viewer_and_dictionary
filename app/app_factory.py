from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from app.auth.routes import *
from app.extensions import db
from app.main.routes import *
from config import load_config

# Initialize extensions without passing the app object
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    config = load_config()

    # Application Configuration
    app.config['SECRET_KEY'] = 'your_secret_key'  # Ideally, load from environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['UPLOAD_FOLDER'] = config.upload_folder
    app.config['STATIC_FOLDER'] = config.static_folder
    app.static_folder = config.static_folder
    app.upload_folder = config.upload_folder
    # app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Add this line

    # Initialize extensions with the app object
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app
