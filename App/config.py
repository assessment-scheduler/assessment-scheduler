import os
import importlib
from datetime import timedelta
from flask_cors import CORS

# must be updated to inlude addtional secrets/ api keys & use a gitignored custom-config file instad
def load_config():
    config = {'ENV': os.environ.get('ENV', 'DEVELOPMENT')}
    delta = 7
    if config['ENV'] == "DEVELOPMENT":
        from .default_config import JWT_ACCESS_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, SECRET_KEY
        config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 
        config['SECRET_KEY'] = SECRET_KEY
        delta = JWT_ACCESS_TOKEN_EXPIRES
    else:
        config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        config['DEBUG'] = config['ENV'].upper() != 'PRODUCTION'

        delta = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 7))

    config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(delta))
    config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config['TEMPLATES_AUTO_RELOAD'] = True
    config['SEVER_NAME'] = '0.0.0.0'
    config['PREFERRED_URL_SCHEME'] = 'https'
    config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    config['MAIL_SERVER'] = 'smtp.gmail.com'
    config['MAIL_PORT'] = 465
    config['MAIL_USERNAME'] = 'assessment.scheduler.emails@gmail.com'
    config['MAIL_PASSWORD'] = 'mygl qlni lqrz naxm' # App Password used 
    config['MAIL_USE_TLS'] = True 
    config['MAIL_DEFAULT_SENDER'] = 'assessment.scheduler.emails@gmail.com'
    config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    config["JWT_COOKIE_SECURE"] = True
    config["JWT_COOKIE_CSRF_PROTECT"] = False
    config['SOLVER_TIMEOUT'] = int(os.environ.get('SOLVER_TIMEOUT', 300))  # 5 minutes default timeout
    return config

config = load_config()