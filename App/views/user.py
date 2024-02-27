from flask import Blueprint, request, jsonify, render_template
from App.database import db
from App.controllers import User

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/')
def index():
    return render_template('index.html')