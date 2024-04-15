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
    get_CourseAsm_id,
    get_CourseAsm_code,
    add_CourseAsm,
    delete_CourseAsm,
    list_Assessments,
    get_Assessment_id,
    get_Assessment_type
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

    # Get courses for filter
    courses=[]
    allCourses=[course.courseCode for course in list_Courses()]
    myCourses=get_registered_courses(id)
    for course in allCourses:
        if course not in myCourses:
            courses.append(course)

    # Get assessments for registered courses
    all_assessments=[]
    for course in myCourses:
        all_assessments= all_assessments + get_CourseAsm_code(course)

    # Format assessments for calendar js - registered courses
    myAssessments=[]
    for item in all_assessments:
        obj=format_assessment(item)
        myAssessments.append(obj)

    # Get assessments for all other courses (for filters)
    other_assessments=[]
    for c in courses:
        other_assessments = other_assessments + get_CourseAsm_code(c)

    # Format assessments for calendar js - filters
    assessments=[]
    for item in other_assessments:
        if not item.clashDetected:
            obj=format_assessment(item)
            assessments.append(obj)


    # Ensure courses, myCourses, and assessments are not empty
    if not courses:
        courses = []
    if not myCourses:
        myCourses = []
    if not myAssessments:
        myAssessments = []
    if not assessments:
        assessments = []

    sem=Semester.query.order_by(Semester.id.desc()).first()
    semester = {'start':sem.startDate,'end':sem.endDate}

    messages=[]
    message = session.pop('message',None)
    if message:
        messages.append(message)
    return render_template('index.html', courses=courses, myCourses=myCourses, assessments=myAssessments, semester=semester, otherAssessments=assessments,messages=messages) 


def format_assessment(item):
    if item.startDate is None:
        obj={'courseCode':item.courseCode,
            'a_ID':get_Assessment_type(item.a_ID),
            'caNum':item.id,
            'startDate':item.startDate,
            'endDate':item.endDate,
            'startTime':item.startTime,
            'endTime':item.endTime,
            'clashDetected':item.clashDetected
            }
    else:    
        obj={'courseCode':item.courseCode,
            'a_ID':get_Assessment_type(item.a_ID),
            'caNum':item.id,
            'startDate':item.startDate.isoformat(),
            'endDate':item.endDate.isoformat(),
            'startTime':item.startTime.isoformat(),
            'endTime':item.endTime.isoformat(),
            'clashDetected':item.clashDetected
            }
    return obj
        

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    # Retrieve data from page
    id = request.form.get('id')
    startDate = request.form.get('startDate')
    startTime = request.form.get('startTime')
    endDate = request.form.get('endDate')
    endTime = request.form.get('endTime')

    # Get course assessment
    assessment=get_CourseAsm_id(id)
    if assessment:
        assessment.startDate=startDate
        assessment.endDate=endDate
        assessment.startTime=startTime
        assessment.endTime=endTime

        db.session.commit()
        
        clash=detect_clash(assessment.id)
        if clash:
            assessment.clashDetected = True
            db.session.commit()
            session['message'] = assessment.courseCode+" - Clash detected! The maximum amount of assessments for this level has been exceeded."
        else:
            session['message'] = "Assessment modified"
    return session['message']

def detect_clash(id):
    clash=0
    sem=Semester.query.order_by(Semester.id.desc()).first() #get the weekly max num of assessments allowed per level
    max=sem.maxAssessments
    new_assessment=get_CourseAsm_id(id)                     #get current assessment info
    compare_code=new_assessment.courseCode.replace(' ','')
    all_assessments = CourseAssessment.query.filter(not_(CourseAssessment.a_ID.in_([2, 4, 8]))).all()
    if not new_assessment.endDate: #dates not set yet
        return False
    relevant_assessments=[]
    for a in all_assessments:
        code=a.courseCode.replace(' ','')
        if (code[4]==compare_code[4]) and (a.id!=new_assessment.id): #course are in the same level
            if a.startDate is not None: #assessment has been scheduled
                relevant_assessments.append(a)

    sunday,saturday=get_week_range(new_assessment.endDate.isoformat())
    for a in relevant_assessments:
        dueDate=a.endDate
        if sunday <= dueDate <= saturday:
            clash=clash+1

    return clash>=max

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
        for assessment in get_CourseAsm_code(course):  #get assessments by course code
            if assessment.startDate is None:
                obj={'id': assessment.id,
                'courseCode': assessment.courseCode,
                'a_ID': get_Assessment_type(assessment.a_ID),   #convert a_ID to category value
                'startDate': assessment.startDate,
                'endDate': assessment.endDate,
                'startTime': assessment.startTime,
                'endTime': assessment.endTime,
                'clashDetected':assessment.clashDetected
                }
            else:
                obj={'id': assessment.id,
                    'courseCode': assessment.courseCode,
                    'a_ID': get_Assessment_type(assessment.a_ID),   #convert a_ID to category value
                    'startDate': assessment.startDate.isoformat(),
                    'endDate': assessment.endDate.isoformat(),
                    'startTime': assessment.startTime.isoformat(),
                    'endTime': assessment.endTime.isoformat(),
                    'clashDetected':assessment.clashDetected
                    }
            assessments.append(obj)     #add object to list of assessments

    return render_template('assessments.html', courses=registered_courses, assessments=assessments)      

# Gets add assessment page 
@staff_views.route('/addAssessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    id=get_uid(get_jwt_identity())  #gets u_id from email token
    registered_courses = get_registered_courses(id)
    allAsm = list_Assessments()
    return render_template('addAssessment.html', courses=registered_courses, assessments=allAsm)   

# Retrieves assessment info and creates new assessment for course
@staff_views.route('/addAssessment', methods=['POST'])
@jwt_required()
def add_assessments_action():       
    course = request.form.get('myCourses')
    asmType = request.form.get('AssessmentType')
    startDate = request.form.get('startDate')
    endDate = request.form.get('endDate')
    startTime = request.form.get('startTime')
    endTime = request.form.get('endTime')
    
    if startDate=='' or endDate=='' or startTime=='' or endTime=='':
        startDate=None
        endDate=None
        startTime=None
        endTime=None

    newAsm = add_CourseAsm(course, asmType, startDate, endDate, startTime, endTime, False)  
    if newAsm.startDate:
        clash=detect_clash(newAsm.id)
        if clash:
            newAsm.clashDetected = True
            db.session.commit()
            flash("Clash detected! The maximum amount of assessments for this level has been exceeded.")
            time.sleep(1)

    return redirect(url_for('staff_views.get_assessments_page'))   
    

# Modify selected assessment
@staff_views.route('/modifyAssessment/<string:id>', methods=['GET'])
def get_modify_assessments_page(id):
    allAsm = list_Assessments()         #get assessment types
    assessment=get_CourseAsm_id(id)     #get assessment details
    return render_template('modifyAssessment.html', assessments=allAsm, ca=assessment) 

# Gets Update assessment Page
@staff_views.route('/modifyAssessment/<string:id>', methods=['POST'])
def modify_assessment(id):
    if request.method=='POST':
        #get form details
        course = request.form.get('myCourses')
        asmType = request.form.get('AssessmentType')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')
        startTime = request.form.get('startTime')
        endTime = request.form.get('endTime')

        #update record
        assessment=get_CourseAsm_id(id)
        if assessment:
            assessment.a_ID=asmType
            if startDate!='' and endDate!='' and startTime!='' and endTime!='':
                assessment.startDate=startDate
                assessment.endDate=endDate
                assessment.startTime=startTime
                assessment.endTime=endTime

            db.session.commit()

            clash=detect_clash(assessment.id)
            if clash:
                assessment.clashDetected = True
                db.session.commit()
                flash("Clash detected! The maximum amount of assessments for this level has been exceeded.")
                time.sleep(1)

    return redirect(url_for('staff_views.get_assessments_page'))

# Delete selected assessment
@staff_views.route('/deleteAssessment/<string:caNum>', methods=['GET'])
def delete_assessment(caNum):
    courseAsm = get_CourseAsm_id(caNum) # Gets selected assessment for course
    delete_CourseAsm(courseAsm)
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