from flask import Blueprint, request, jsonify, render_template
from App.database import db
from App.controllers import Lecturer
#from flask_jwt_extended import current_user as jwt_current_user
#from flask_jwt_extended import jwt_required

from App.controllers.lecturer import (
    register_lecturer
)

lect_views = Blueprint('lect_views', __name__, template_folder='../templates')

@lect_views.route('/register', methods=['POST'])
def register_lecturer_action():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    pwd = request.form['password']

    if (firstName == '' or lastName == '' or email == '' or pwd == ''):
        render_template('signup.html', message = 'Please enter required fields.')
    else:
        register_lecturer(self, fName, lName, email, pwd)
        return render_template('index.html')  