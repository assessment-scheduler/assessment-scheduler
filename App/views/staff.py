from flask import Blueprint, request, jsonify, render_template
from App.controllers import Staff
#from flask_jwt_extended import current_user as jwt_current_user
#from flask_jwt_extended import jwt_required

from App.controllers.staff import (
    register_staff
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

#models need to reflect data being pulled from form!
@staff_views.route('/register', methods=['GET', 'POST'])
def register_staff_action():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        staffID = request.form['staffID']
        status = request.form['status']
        email = request.form['email']
        pwd = request.form['password']

        if (firstName == '' or lastName == '' or staffID == '' or status == '' or email == '' or pwd == ''):
            return render_template('signup.html', message = 'Please enter required fields.')
        else:
            register_staff(firstName, lastName, staffID, status, email, pwd)
            return render_template('index.html')  #landing page
    
    return render_template('signup.html')      