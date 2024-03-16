from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from App.controllers import Staff
from App.database import db
#from flask_jwt_extended import current_user as jwt_current_user
#from flask_jwt_extended import jwt_required

from App.controllers.staff import (
    register_staff
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Gets Signup Page
@staff_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

# Gets Login Page
@staff_views.route('/login', methods=['GET'])
def get_login_page():
    return render_template('login.html')  

# Gets Calendar Page
@staff_views.route('/calendar', methods=['GET'])
def get_calendar_page():
    return render_template('index.html')        
 
# Retrieves info and stores it in database ie. register new staff
@staff_views.route('/register', methods=['POST'])
def register_staff_action():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        staffID = request.form.get('staffID')
        status = request.form.get('status')
        email = request.form.get('email')
        pwd = request.form.get('password')
         
        # Flash message
        if (firstName == '' or lastName == '' or staffID == '' or status == '' or email == '' or pwd == ''):
            return render_template('signup.html', message = 'Please enter required fields.')
        else:
            register_staff(firstName, lastName, staffID, status, email, pwd)
            return jsonify({"message":f" {Status} registered with id {staffID}"}) # for postman
            # return render_template('index.html')  
           