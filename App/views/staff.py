from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, get_flashed_messages, session
from flask_login import current_user
from flask import current_app as app
from flask_mail import Mail, Message
from sqlalchemy import not_
from App.controllers import Staff
from App.controllers import Course, Semester
from App.controllers import CourseAssessment
from App.database import db
from App.models.assessment import Assessment
import json
from flask_jwt_extended import current_user as jwt_current_user, get_jwt_identity
from flask_jwt_extended import jwt_required
from datetime import date, timedelta
import time
import datetime

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
    get_course_assessment_by_id,
    get_course_assessment_by_code,
    add_course_assessment,
    delete_course_assessment,
    list_assessments,
    get_assessment_id,
    get_assessment_type
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
    # Get the current user
    current_user = get_jwt_identity()
    staff = Staff.query.filter_by(email=current_user).first()
    
    # Get all courses
    courses = Course.query.all()
    
    # Get courses assigned to this staff
    my_courses = []
    if staff:
        my_courses = get_registered_courses(staff.u_ID)
    
    # Get assessments for this staff's courses
    my_assessments = []
    if my_courses:
        for course in my_courses:
            assessments = get_course_assessment_by_code(course)
            for assessment in assessments:
                my_assessments.append(assessment)
    
    # Get assessments for all other courses
    assessments = []
    for course in courses:
        if course not in my_courses:
            course_assessments = get_course_assessment_by_code(course)
            for assessment in course_assessments:
                assessments.append(assessment)
    
    if not my_courses:
        my_courses = []
    if not my_assessments:
        my_assessments = []
    if not assessments:
        assessments = []

    sem = Semester.query.order_by(Semester.id.desc()).first()
    if sem:
        semester = {'start': sem.start_date, 'end': sem.end_date}
    else:
        # Default to current year if no semester exists
        current_year = datetime.date.today().year
        semester = {
            'start': datetime.date(current_year, 1, 1),
            'end': datetime.date(current_year, 12, 31)
        }

    messages = []
    message = session.pop('message', None)
    if message:
        messages.append(message)
    return render_template('index.html', courses=courses, myCourses=my_courses, assessments=my_assessments, semester=semester, otherAssessments=assessments, messages=messages)


def format_assessment(item):
    if item.start_date is None:
        obj={'courseCode':item.course_code,
            'a_ID':get_assessment_type(item.a_id),
            'caNum':item.id,
            'startDate':item.start_date,
            'endDate':item.end_date,
            'startTime':item.start_time,
            'endTime':item.end_time,
            'clashDetected':item.clash_detected
            }
    else:    
        obj={'courseCode':item.course_code,
            'a_ID':get_assessment_type(item.a_id),
            'caNum':item.id,
            'startDate':item.start_date.isoformat(),
            'endDate':item.end_date.isoformat(),
            'startTime':item.start_time.isoformat(),
            'endTime':item.end_time.isoformat(),
            'clashDetected':item.clash_detected
            }
    return obj
        

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    # Retrieve data from page
    id = request.form.get('id')
    start_date = request.form.get('startDate')
    start_time = request.form.get('startTime')
    end_date = request.form.get('endDate')
    end_time = request.form.get('endTime')

    # Get course assessment
    assessment=get_course_assessment_by_id(id)
    if assessment:
        assessment.start_date=start_date
        assessment.end_date=end_date
        assessment.start_time=start_time
        assessment.end_time=end_time

        db.session.commit()
        
        clash=detect_clash(assessment.id)
        if clash:
            assessment.clash_detected = True
            db.session.commit()
            session['message'] = assessment.course_code+" - Clash detected! The maximum amount of assessments for this level has been exceeded."
        else:
            session['message'] = "Assessment modified"
    return session['message']

def detect_clash(id):
    clash = 0
    sem = Semester.query.order_by(Semester.id.desc()).first() # get the weekly max num of assessments allowed per level
    if sem:
        max_assessments = sem.max_assessments
    else:
        max_assessments = 3  # Default value if no semester exists
    
    new_assessment = get_course_assessment_by_id(id)  # get current assessment info
    compare_code = new_assessment.course_code.replace(' ','')
    all_assessments = CourseAssessment.query.filter(not_(CourseAssessment.a_id.in_([2, 4, 8]))).all()
    if not new_assessment.end_date: #dates not set yet
        return False
    relevant_assessments=[]
    for a in all_assessments:
        code=a.course_code.replace(' ','')
        if (code[4]==compare_code[4]) and (a.id!=new_assessment.id): #course are in the same level
            if a.start_date is not None: #assessment has been scheduled
                relevant_assessments.append(a)

    sunday,saturday=get_week_range(new_assessment.end_date.isoformat())
    for a in relevant_assessments:
        due_date=a.end_date
        if sunday <= due_date <= saturday:
            clash=clash+1

    return clash>=max_assessments

def get_week_range(iso_date_str):
    date_obj = date.fromisoformat(iso_date_str)
    day_of_week = date_obj.weekday()

    if day_of_week != 6:
        days_to_subtract = (day_of_week + 1) % 7 
    else:
        days_to_subtract = 0

    sunday_date = date_obj - timedelta(days=days_to_subtract) #get sunday's date
    saturday_date = sunday_date + timedelta(days=6) #get saturday's date
    return sunday_date, saturday_date

# Sends confirmation email to staff upon registering
@staff_views.route('/send_email', methods=['GET','POST'])
def send_email():
    mail = Mail(app) # Create mail instance

    subject = 'Test Email!'
    receiver = request.form.get('email')
    body = 'Successful Registration'
    
    msg = Message(subject, recipients=[receiver], html=body)
    mail.send(msg)
    return render_template('login.html')  

# Retrieves staff info and stores it in database ie. register new staff
@staff_views.route('/register', methods=['POST'])
def register_staff_action():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        staffID = request.form.get('staffID')
        status = request.form.get('status')
        email = request.form.get('email')
        pwd = request.form.get('password')
         
        # Field Validation is on HTML Page!
        register_staff(firstName, lastName, staffID, status, email, pwd)
        return render_template('login.html')  
        # return redirect(url_for('staff_views.send_email'))  
    
# Gets account page
@staff_views.route('/account', methods=['GET'])
@jwt_required()
def get_account_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    courses=list_Courses()
    registered_courses=get_registered_courses(id)
    return render_template('account.html', courses=courses, registered=registered_courses)      

# Assign course to staff
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

# Gets assessments page
@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    registered_courses=get_registered_courses(id)  #get staff's courses
    
    assessments=[]
    for course in registered_courses:
        for assessment in get_course_assessment_by_code(course):  #get assessments by course code
            if assessment.start_date is None:
                obj={'id': assessment.id,
                'courseCode': assessment.course_code,
                'a_ID': get_assessment_type(assessment.a_id),   #convert a_ID to category value
                'startDate': assessment.start_date,
                'endDate': assessment.end_date,
                'startTime': assessment.start_time,
                'endTime': assessment.end_time,
                'clashDetected':assessment.clash_detected
                }
            else:
                obj={'id': assessment.id,
                    'courseCode': assessment.course_code,
                    'a_ID': get_assessment_type(assessment.a_id),   #convert a_ID to category value
                    'startDate': assessment.start_date.isoformat(),
                    'endDate': assessment.end_date.isoformat(),
                    'startTime': assessment.start_time.isoformat(),
                    'endTime': assessment.end_time.isoformat(),
                    'clashDetected':assessment.clash_detected
                    }
            assessments.append(obj)     #add object to list of assessments

    return render_template('assessments.html', courses=registered_courses, assessments=assessments)      

# Gets add assessment page 
@staff_views.route('/addAssessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    registered_courses = get_registered_courses(id)
    allAsm = list_assessments()
    return render_template('addAssessment.html', courses=registered_courses, assessments=allAsm)   

# Retrieves assessment info and creates new assessment for course
@staff_views.route('/addAssessment', methods=['POST'])
@jwt_required()
def add_assessments_action():       
    course = request.form.get('course')
    asmType = request.form.get('asmType')
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')
    start_time = request.form.get('startTime')
    end_time = request.form.get('endTime')

    if start_date=='' or end_date=='' or start_time=='' or end_time=='':
        start_date=None
        end_date=None
        start_time=None
        end_time=None

    newAsm = add_course_assessment(course, asmType, start_date, end_date, start_time, end_time, False)  
    if newAsm.start_date:
        clash=detect_clash(newAsm.id)
        if clash:
            newAsm.clash_detected = True
            db.session.commit()
    
    return redirect(url_for('staff_views.get_assessments_page'))   
    

# Modify selected assessment
@staff_views.route('/modifyAssessment/<string:id>', methods=['GET'])
def get_modify_assessments_page(id):
    allAsm = list_assessments()         #get assessment types
    assessment=get_course_assessment_by_id(id)     #get assessment details
    return render_template('modifyAssessment.html', assessments=allAsm, ca=assessment) 

# Gets Update assessment Page
@staff_views.route('/modifyAssessment/<string:id>', methods=['POST'])
def modify_assessment(id):
    if request.method == 'POST':
        asmType = request.form.get('asmType')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')

        #update record
        assessment=get_course_assessment_by_id(id)
        if assessment:
            assessment.a_id=asmType
            if start_date!='' and end_date!='' and start_time!='' and end_time!='':
                assessment.start_date=start_date
                assessment.end_date=end_date
                assessment.start_time=start_time
                assessment.end_time=end_time
                db.session.commit()
                
                clash=detect_clash(assessment.id)
                if clash:
                    assessment.clash_detected = True
                    db.session.commit()
                    flash("Clash detected! The maximum amount of assessments for this level has been exceeded.")
                    time.sleep(1)
    
    return redirect(url_for('staff_views.get_assessments_page'))

# Delete selected assessment
@staff_views.route('/deleteAssessment/<string:caNum>', methods=['GET'])
def delete_assessment(caNum):
    courseAsm = get_course_assessment_by_id(caNum) # Gets selected assessment for course
    delete_course_assessment(courseAsm)
    print(caNum, ' deleted')
    return redirect(url_for('staff_views.get_assessments_page')) 

# Get settings page
@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

# Route to change password of user
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


