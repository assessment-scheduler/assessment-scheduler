from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import current_user
from App.controllers import Staff
from App.controllers import Course
from App.controllers import CourseAssessment
from App.database import db
from App.send_email import send_mail
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

from App.controllers.user import(
    get_uid
)

from App.controllers.courseAssessment import(
    add_CourseAsm
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
    id=get_uid(get_jwt_identity())  #gets u_id from email token

    #get courses for filter
    courses=[]
    allCourses=[course.courseCode for course in list_Courses()]
    myCourses=get_registered_courses(id)
    for course in allCourses:
        if course not in myCourses:
            courses.append(course)

    #get assessments for registered courses
    assessments=[{'courseCode':'COMP1601','a_ID':'Assignment','caNum':'0','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1602','a_ID':'Assignment','caNum':'1','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1601','a_ID':'Exam','caNum':'2','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1602','a_ID':'Exam','caNum':'3','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'}]
   
    

    # for c in courses:
    #     print(c.courseCode)

    # Ensure courses, myCourses, and assessments are not empty
    if not courses:
        courses = []

    if not myCourses:
        myCourses = []

    if not assessments:
        assessments = []

    return render_template('index.html', courses=courses, myCourses=myCourses, assessments=assessments)        
 
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
         
        # Field Validation is on HTML Page
        staff = register_staff(firstName, lastName, staffID, status, email, pwd)
        send_mail(staff)
        return render_template('login.html')  # must login after registration to get access token
        
    
#Gets account page
@staff_views.route('/account', methods=['GET'])
@jwt_required()
def get_account_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    courses=list_Courses()
    registered_courses=get_registered_courses(id)
    return render_template('account.html', courses=courses, registered=registered_courses)      

@staff_views.route('/account', methods=['POST'])
@jwt_required()
def get_selected_courses():
    courses=list_Courses()
    id=get_uid(get_jwt_identity())  #gets u_id from email token

    if request.method == 'POST':
        course_codes_json = request.form.get('courseCodes')
        course_codes = json.loads(course_codes_json)
        for code in course_codes:
            obj=add_CourseStaff(id,code)   #add course to course-staff table
        
    return redirect(url_for('staff_views.get_account_page'))   

#Gets assessments page
@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    registered_courses=get_registered_courses(id)
    #get assessments by course code
    assessments=[{'courseCode':'COMP1601','a_ID':'Assignment','caNum':'0','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1602','a_ID':'Assignment','caNum':'1','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1601','a_ID':'Exam','caNum':'2','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'},
                {'courseCode':'COMP1602','a_ID':'Assignment','caNum':'3','startDate':'29-02-2024','endDate':'29-02-2024','startTime':'9:00','endTime':'9:00'}]
    return render_template('assessments.html', courses=registered_courses, assessments=assessments)      

# Gets add assessment page
@staff_views.route('/addAssessment', methods=['GET'])
def get_add_assessments_page():
    registered_courses=get_registered_courses(123)
    return render_template('addAssessment.html', courses=registered_courses)   

# Retrieves assessment info and creates new assessment for course
@staff_views.route('/addAssessment', methods=['POST'])
def add_assessments_action():       
    registered_courses=get_registered_courses(123)
    course = request.form.get('myCourses')
    asmType = request.form.get('AssessmentType')
    startDate = request.form.get('startDate')
    endDate = request.form.get('endDate')
    startTime = request.form.get('startTime')
    endTime = request.form.get('endTime')
    
    if course in registered_courses:
        newAsm = add_CourseAsm(courseCode, a_ID, startDate, endDate, startTime, endTime)  

    return redirect(url_for('staff_views.get_calendar_page'))   

@staff_views.route('/modifyAssessment/<string:caNum>', methods=['GET'])
def get_modify_assessments_page(caNum):
    print(caNum, ' modified')
    #if post
        #get form details
        #update record
        #redirect to /assessments
    #if get
        #get assessment details
        #pass details to frontend
    return render_template('modifyAssessment.html')  

@staff_views.route('/deleteAssessment/<string:caNum>', methods=['GET'])
def delete_assessment(caNum):
    print(caNum, ' deleted')
    #get assessment
    #delete record
    return redirect(url_for('staff_views.get_assessments_page')) 

# get settings page
@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

# route to change password of user
@staff_views.route('/settings', methods=['POST'])
@jwt_required()
def changePassword():
    
    if request.method == 'POST':
        #get new password
        newPassword = request.form.get('password')
        # print(newPassword)
        
        #get email of current user
        current_user_email = get_jwt_identity()
        # print(current_user_email)
        
        #find user by email
        user = db.session.query(Staff).filter(Staff.email == current_user_email).first()
        # print(user)
        
        if user:
            # update the password
            user.set_password(newPassword)
            
            #commit changes to DB
            db.session.commit()
    
    return render_template('settings.html')