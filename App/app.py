from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

ENV = 'DEVELOPMENT'
if ENV == 'DEVELOPMENT':
    app.debug == True
    app.config['SQLALCHEMY_DATABSE_URI'] = ' '
else:
    app.debug == True
    app.config['SQLALCHEMY_DATABSE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    

if name = '__main__':
    app.run
