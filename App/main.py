import os
from flask import Flask
from flask_login import LoginManager, current_user
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import timedelta
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required as flask_jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from App.controllers.auth import setup_flask_login, setup_jwt
from App.database import init_db
from App.config import config

from App.views import views

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def configure_app(app, config, overrides):
    for key, value in config.items():
        if key in overrides:
            app.config[key] = overrides[key]
        else:
            app.config[key] = config[key]

def create_app(config_overrides={}):
    app = Flask(__name__, static_url_path='/static')
    configure_app(app, config, config_overrides)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEVER_NAME'] = '0.0.0.0'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOAD_FOLDER'] = 'App/uploads'  
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'assessment.scheduler.emails@gmail.com'
    app.config['MAIL_PASSWORD'] = 'mygl qlni lqrz naxm' 
    app.config['MAIL_USE_TLS'] = True 
    app.config['MAIL_DEFAULT_SENDER'] = 'assessment.scheduler.emails@gmail.com'
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['DEBUG'] = True
    
    # Initialize CORS
    CORS(app)
    
    # Initialize database
    init_db(app)
    
    # Setup authentication
    setup_flask_login(app)
    setup_jwt(app)
    
    # Register views
    add_views(app)
    
    return app