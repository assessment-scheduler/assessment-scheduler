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
from App.middleware.auth import course_access_required

from App.controllers.staff import (
    register_staff,
    login_staff,
    add_CourseStaff,
    get_registered_courses,
    get_all_staff,
    get_staff_by_id,
    update_staff,
    delete_staff,
    get_staff_courses,
    has_access_to_course,
    get_accessible_courses
)

from App.controllers.course import (
    list_Courses,
    get_course
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

from App.controllers.assessment import (
    get_assessments_by_course,
    add_assessment,
    update_assessment,
    delete_assessment,
    get_assessment_by_id
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Authentication Routes
@staff_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

@staff_views.route('/register', methods=['POST'])
def register_staff_action():
    try:
        # Get form data
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        u_ID = request.form.get('u_ID')
        status = request.form.get('status')
        email = request.form.get('email')
        pwd = request.form.get('password')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        # Register staff
        staff = register_staff(firstName, lastName, u_ID, status, email, pwd, department, faculty)
        
        if staff:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth_views.get_login_page'))
        else:
            flash('Registration failed. Email may already be in use.', 'error')
            return redirect(url_for('staff_views.get_signup_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_signup_page'))

# Account Routes
@staff_views.route('/account', methods=['GET'])
@jwt_required()
def get_account_page():
    # Get the current user
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    # Get all courses
    all_courses = list_Courses()
    
    # Get courses assigned to this staff member
    staff_courses = get_accessible_courses(u_id)
    staff_course_codes = [course.course_code for course in staff_courses]
    
    return render_template(
        'account.html', 
        courses=all_courses, 
        staff_courses=staff_courses,
        staff_course_codes=staff_course_codes
    )

@staff_views.route('/account', methods=['POST'])
@jwt_required()
def get_selected_courses():
    id = get_uid(get_jwt_identity())  # gets u_id from email token

    if request.method == 'POST':
        course_codes_json = request.form.get('courseCodes')
        course_codes = json.loads(course_codes_json)
        for code in course_codes:
            obj = add_CourseStaff(id, code)   # add course to course-staff table
       
    return redirect(url_for('staff_views.get_account_page'))

# Calendar Routes
@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    # Get the current user
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    # Get courses assigned to this staff member
    staff_courses = get_accessible_courses(u_id)
    
    # Get assessments for these courses
    assessments = []
    for course in staff_courses:
        course_assessments = get_assessments_by_course(course.course_code)
        for assessment in course_assessments:
            assessments.append(format_assessment(assessment))
    
    return render_template('calendar.html', assessments=assessments)

def format_assessment(item):
    # Format assessment data for calendar display
    assessment_data = {
        'id': item.a_id,
        'title': item.name,
        'start': None,
        'end': None,
        'color': '#3498db',  # Default color
        'textColor': '#ffffff',
        'extendedProps': {
            'course_id': item.course_id,
            'percentage': item.percentage,
            'category': item.category.value if hasattr(item.category, 'value') else item.category,
            'proctored': item.proctored
        }
    }
    
    # Set colors based on assessment type
    if item.category == 'EXAM':
        assessment_data['color'] = '#e74c3c'  # Red for exams
    elif item.category == 'MIDTERM':
        assessment_data['color'] = '#f39c12'  # Orange for midterms
    elif item.category == 'ASSIGNMENT':
        assessment_data['color'] = '#2ecc71'  # Green for assignments
    elif item.category == 'QUIZ':
        assessment_data['color'] = '#9b59b6'  # Purple for quizzes
    
    return assessment_data

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    # Retrieve data from page
    data = request.get_json()
    
    # Process data and update assessments
    # ...
    
    return jsonify({'success': True})

# Assessment Routes
@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    # Get the current user
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    # Get courses assigned to this staff member
    staff_courses = get_accessible_courses(u_id)
    
    # Get assessments for these courses
    course_assessments = []
    for course in staff_courses:
        assessments = get_assessments_by_course(course.course_code)
        if assessments:
            course_assessments.append({
                'course': course,
                'assessments': assessments
            })
    
    return render_template('assessments.html', course_assessments=course_assessments)

@staff_views.route('/addAssessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    # Get the current user
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    # Get courses assigned to this staff member
    staff_courses = get_accessible_courses(u_id)
    
    return render_template('addAssessment.html', courses=staff_courses)

@staff_views.route('/addAssessment', methods=['POST'])
@jwt_required()
def add_assessments_action():
    try:
        # Get form data
        course_id = request.form.get('course_id')
        name = request.form.get('name')
        percentage = float(request.form.get('percentage'))
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = request.form.get('proctored') == 'on'
        category = request.form.get('category')
        
        # Check if user has access to this course
        email = get_jwt_identity()
        u_id = get_uid(email)
        if not has_access_to_course(u_id, course_id):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        # Add assessment
        assessment = add_assessment(
            course_id, name, percentage, start_week, start_day, 
            end_week, end_day, proctored, category
        )
        
        if assessment:
            flash('Assessment added successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to add assessment', 'error')
            return redirect(url_for('staff_views.get_add_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_add_assessments_page'))

@staff_views.route('/modifyAssessment/<string:id>', methods=['GET'])
@jwt_required()
@course_access_required()
def get_modify_assessments_page(id):
    assessment = get_assessment_by_id(id)
    return render_template('modifyAssessment.html', assessment=assessment)

@staff_views.route('/modifyAssessment/<string:id>', methods=['POST'])
@jwt_required()
@course_access_required()
def modify_assessment(id):
    try:
        # Get form data
        name = request.form.get('name')
        percentage = float(request.form.get('percentage'))
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = request.form.get('proctored') == 'on'
        category = request.form.get('category')
        
        # Update assessment
        assessment = update_assessment(
            id, name, percentage, start_week, start_day, 
            end_week, end_day, proctored, category
        )
        
        if assessment:
            flash('Assessment updated successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to update assessment', 'error')
            return redirect(url_for('staff_views.get_modify_assessments_page', id=id))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_modify_assessments_page', id=id))

@staff_views.route('/deleteAssessment/<string:caNum>', methods=['GET'])
@jwt_required()
@course_access_required()
def delete_assessment_action(caNum):
    result = delete_assessment(caNum)
    if result:
        flash('Assessment deleted successfully', 'success')
    else:
        flash('Failed to delete assessment', 'error')
    return redirect(url_for('staff_views.get_assessments_page'))

# Settings Routes
@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

@staff_views.route('/settings', methods=['POST'])
@jwt_required()
def change_password():
    # Process password change
    # ...
    return redirect(url_for('staff_views.get_settings_page'))

# Email Routes
@staff_views.route('/send_email', methods=['GET', 'POST'])
@jwt_required()
def send_email():
    # Process email sending
    # ...
    return render_template('email.html')

# Helper Functions
def detect_clash(id):
    # Detect assessment clashes
    # ...
    return False

def get_week_range(iso_date_str):
    # Get week range for a date
    # ...
    return None, None


