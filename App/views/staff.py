from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import current_user
from App.controllers import Staff
from App.controllers import Course
from App.database import db
import json
from flask_jwt_extended import current_user as jwt_current_user, get_jwt_identity
from flask_jwt_extended import jwt_required

from App.controllers.staff import (
    register_staff,
    login_staff,
    add_CourseStaff,
    get_registered_courses,
)


from App.controllers.course import (
    list_Courses
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Gets Signup Page
@staff_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

# Gets Calendar Page
@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
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
            return render_template('login.html')  

          
            # return jsonify({"message":f" {status} registered with id {staffID}"}), 200 # for postman
    
#Gets account page
@staff_views.route('/account', methods=['GET'])
@jwt_required()
def get_account_page():
    value=get_jwt_identity()

    courses=list_Courses()
    registered_courses=get_registered_courses(123)
    return render_template('account.html', courses=courses, registered=registered_courses, email=value)      

@staff_views.route('/account', methods=['POST'])
def get_selected_courses():
    courses=list_Courses()

    if request.method == 'POST':
        course_codes_json = request.form.get('courseCodes')
        course_codes = json.loads(course_codes_json)
        for code in course_codes:
            obj=add_CourseStaff(123,code)   #add course to course-staff table
            print(obj.courseCode, " added")
        
    return redirect(url_for('staff_views.get_account_page'))   

#Gets assessments page
@staff_views.route('/assessments', methods=['GET'])
def get_assessments_page():
    registered_courses=get_registered_courses(123)
    return render_template('assessments.html', courses=registered_courses)      

@staff_views.route('/addAssessment', methods=['GET'])
def get_add_assessments_page():
    registered_courses=get_registered_courses(123)
    return render_template('addAssessment.html', courses=registered_courses)   

@staff_views.route('/modifyAssessment/<string:course_code>', methods=['GET'])
def get_modify_assessments_page(course_code):
    print(course_code)
    return render_template('modifyAssessment.html')  

@staff_views.route('/deleteAssessment/<string:course_code>', methods=['GET'])
def delete_assessment(course_code):
    print(course_code)
    return render_template('assessments.html')  

@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

@staff_views.route('/settings', methods=['POST'])
@jwt_required()
def changePassword():

    if request.method == 'POST':
        newPassword = request.form.get('password')
        current_user_email = get_jwt_identity()
        print(current_user_email)
        print(newPassword)
    
    return render_template('settings.html')