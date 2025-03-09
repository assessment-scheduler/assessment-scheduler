from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, get_flashed_messages
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from App.database import db
from functools import wraps

from App.middleware.wrapper import course_access_required

from App.controllers.staff import (
    create_staff,
    get_staff,
    get_staff_courses,
    delete_staff,
    get_staff_courses,
    is_course_lecturer,
)

from App.controllers.course import (
    get_all_courses,
    get_course
)

from App.controllers.user import(
    get_user_by_email
)

from App.controllers.assessment import (
    create_assessment,
    edit_assessment,
    get_assessment_by_id,
    get_assessments_by_course,
    delete_assessment,
    get_assessment,
)
staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

@staff_views.route('/register', methods=['POST'])
def register_staff_action():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        id = request.form.get('id')
        email = request.form.get('email')
        password = request.form.get('password')
        
        staff = create_staff(id, email, password, first_name, last_name)
        
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
    try:
        email = get_jwt_identity()
        if not email:
            flash('User identity not found. Please log in again.', 'error')
            return render_template('account.html')
            
        user = get_user_by_email(email)
        
        if not user.id:
            flash(f'User ID not found for email: {email}. Please log in again.', 'error')
            return render_template('account.html')
        
        # Get staff information
        staff = get_staff(user.id)
        if not staff:
            flash(f'Staff record not found for ID: {user.id}. Please contact an administrator.', 'error')
            return render_template('account.html')
        
        all_courses = get_all_courses()
        staff_courses = get_staff_courses(user.id)
        
        # Convert course objects to JSON serializable dictionaries
        all_courses_json = [course.to_json() for course in all_courses]
        
        # For staff_courses, we need to include assessments
        staff_courses_json = []
        total_assessments = 0  # Track total assessments across all courses
        
        for course in staff_courses:
            course_json = course.to_json()
            # Get assessments for this course directly from the database
            course_assessments = get_assessments_by_course(course.course_code)
            
            # Add assessments to each course
            course_assessments_json = [assessment.to_json() for assessment in course_assessments]
            course_json['assessments'] = course_assessments_json
            
            # Update total assessment count
            total_assessments += len(course_assessments)
            
            staff_courses_json.append(course_json)
        
        staff_course_codes = [course.course_code for course in staff_courses]
        
        return render_template(
            'account.html', 
            courses=all_courses_json, 
            staff_courses=staff_courses_json,
            staff_course_codes=staff_course_codes,
            registered=staff_course_codes,
            staff=staff,  # Pass staff information to the template
            total_assessments=total_assessments  # Pass the total assessment count
        )
    except Exception as e:
        flash(f'Error loading account page: {str(e)}', 'error')
        return render_template('account.html')

@staff_views.route('/account', methods=['POST'])
@jwt_required()
def update_staff_courses():
    email = get_jwt_identity()
    user = get_user_by_email(email)

    course_codes_json = request.form.get('courseCodes')
    if course_codes_json:
        import json
        course_codes = json.loads(course_codes_json)
        for code in course_codes:
            add_CourseStaff(user.id, code)
       
    return redirect(url_for('staff_views.get_account_page'))

# Calendar Routes
@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    staff_courses = get_staff_courses(user.id)
    course_codes = [course.course_code for course in staff_courses]
    
    assessments = []
    for course in staff_courses:
        course_assessments = get_assessments_by_course(course.course_code)
        for assessment in course_assessments:
            assessments.append(assessment.to_json())
    
    return render_template('calendar.html', assessments=assessments, courses=course_codes)

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    data = request.get_json()
    return jsonify({'success': True})


# Assessment Routes
@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    staff_courses = get_staff_courses(user.id)
    
    # Extract course codes for the dropdown
    courses = [course.course_code for course in staff_courses]
    
    course_assessments = []
    for course in staff_courses:
        assessments = get_assessments_by_course(course.course_code)
        if assessments:
            total_percentage = calculate_total_percentage_for_course(course.course_code)
            course_assessments.append({
                'course': course.to_json(),
                'assessments': [assessment.to_json() for assessment in assessments],
                'total_percentage': total_percentage
            })
    
    return render_template('assessments.html', course_assessments=course_assessments, courses=courses)

@staff_views.route('/addAssessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    staff_courses = get_staff_courses(user.id)
    
    return render_template('addAssessment.html', courses=staff_courses)

@staff_views.route('/addAssessment', methods=['POST'])
@jwt_required()
def add_assessments_action():
    try:
        course_id = request.form.get('course_id')
        name = request.form.get('name')
        percentage = float(request.form.get('percentage'))
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = request.form.get('proctored') == 'on'
        category = request.form.get('category')
        
        email = get_jwt_identity()
        user = get_user_by_email(email)
        if not is_course_lecturer(user.id, course_id):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        assessment = create_assessment(
            course_id, name, percentage, start_week, start_day, 
            end_week, end_day, proctored, category
        )
        
        if assessment:
            flash('Assessment added successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to add assessment. Please check your inputs.', 'error')
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
        name = request.form.get('name')
        percentage = float(request.form.get('percentage'))
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = request.form.get('proctored') == 'on'
        category = request.form.get('category')
        
        assessment = edit_assessment(
            id, name, percentage, start_week, start_day, 
            end_week, end_day, proctored, category
        )
        
        if assessment:
            flash('Assessment updated successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to update assessment. Please check your inputs.', 'error')
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
def update_settings():
    flash('Settings updated successfully', 'success')
    return redirect(url_for('staff_views.get_settings_page'))

# Course Routes
@staff_views.route('/course/<course_code>', methods=['GET'])
@jwt_required()
def get_course_details(course_code):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        
        # Check if staff has access to this course
        if not is_course_lecturer(user.id, course_code):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        # Get course information
        course = get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        # Get assessments for this course
        assessments = get_assessments_by_course(course.course_code)
        
        # Get staff information
        staff = get_staff(user.id)
        
        # Calculate total percentage
        
        total_percentage = calculate_total_percentage_for_course(course.course_code)
        
        # Convert course and assessments to JSON serializable format
        course_json = course.to_json()
        assessments_json = [assessment.to_json() for assessment in assessments]
        
        # Add additional fields needed for the template
        for assessment in assessments_json:
            # Add type field based on category
            if 'category' in assessment:
                assessment['type'] = assessment['category']
            
            # Add due_date field (placeholder since we don't have actual dates)
            assessment['due_date'] = None
            
            # Add active field
            assessment['active'] = True
        
        return render_template(
            'course_details.html',
            course=course_json,
            assessments=assessments_json,
            staff=staff,
            total_percentage=total_percentage
        )
    except Exception as e:
        flash(f'Error loading course details: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_account_page'))


