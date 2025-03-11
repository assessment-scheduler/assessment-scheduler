from typing import List
from App.controllers.semester import get_active_semester
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database import db

from App.controllers import (
    create_staff,
    get_staff_by_email,
    get_staff_courses,
    is_course_lecturer,
    assign_course_to_staff,
    get_staff_by_id,
    get_course,
    get_user_by_email,
    create_assessment,
    delete_assessment_by_id,
    edit_assessment,
    get_assessment_by_id,
    get_assessment_dictionary_by_course,
    get_assessments_by_lecturer,
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

@staff_views.route('/account', methods=['GET'])
@jwt_required()
def get_account_page():
    email = get_jwt_identity()
    staff = get_staff_by_email(email)
    courses = get_staff_courses(email)
    return render_template('account.html', staff=staff, courses=courses)

@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    all_assessments = get_assessments_by_lecturer(user.email)
    return render_template('calendar.html', assessments=all_assessments)

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    data = request.get_json()
    return jsonify({'success': True})

@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    email = get_jwt_identity()
    user = get_staff_by_email(email)
    assessments = get_assessments_by_lecturer(user.email)
    return render_template('assessments.html',course_assessments = assessments)

@staff_views.route('/addAssessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    staff_courses = get_staff_courses(user.email)
    semester = get_active_semester()
    
    return render_template('addAssessment.html', courses=staff_courses, semester=semester)

@staff_views.route('/addAssessment', methods=['POST'])
@jwt_required()
def add_assessments_action():
    try:
        course_code = request.form.get('course_code')
        assessment_name = request.form.get('assessment_name')
        percentage = float(request.form.get('percentage')) 
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = request.form.get('proctored')


        email = get_jwt_identity()
        user = get_user_by_email(email)
        if not is_course_lecturer(user.id, course_code):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        assessment:bool =create_assessment(course_code,assessment_name,percentage,start_week,start_day,end_week,end_day,proctored)
        if assessment:
            flash('Assessment added successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to add assessment. Please check your inputs.', 'error')
            return redirect(url_for('staff_views.get_add_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))

@staff_views.route('/modifyAssessment/<string:id>', methods=['GET'])
@jwt_required()
def get_modify_assessments_page(id):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    assessment = get_assessment_by_id(id)
    
    if not assessment:
        flash('Assessment not found', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))
    
    if not is_course_lecturer(user.id, assessment.course_code):
        flash('You do not have permission to modify assessments for this course', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))
    
    # Get the active semester for date calculations
    semester = get_active_semester()
    if not semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        
    return render_template('modifyAssessment.html', assessment=assessment, semester=semester)

@staff_views.route('/modifyAssessment/<string:id>', methods=['POST'])
@jwt_required()
def modify_assessment(id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('staff_views.get_assessments_page'))
        
        if not is_course_lecturer(user.id, assessment.course_code):
            flash('You do not have permission to modify assessments for this course', 'error')
            return redirect(url_for('staff_views.get_assessments_page'))
            
        assessment_name = request.form.get('assessment_name')
        percentage = int(request.form.get('percentage')) 
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = 1 if request.form.get('proctored') is not None else 0
        
        assessment_result = edit_assessment(id, assessment_name, percentage, start_week, start_day, end_week, end_day, proctored)
        if assessment_result:
            flash('Assessment updated successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to update assessment. Please check your inputs.', 'error')
            return redirect(url_for('staff_views.get_modify_assessments_page', id=id))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))

@staff_views.route('/deleteAssessment/<int:assessment_id>', methods=['POST', 'GET'])
@jwt_required()
def delete_assessment_action(assessment_id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('staff_views.get_assessments_page'))
        
        if not is_course_lecturer(user.id, assessment.course_code):
            flash('You do not have permission to delete assessments for this course', 'error')
            return redirect(url_for('staff_views.get_assessments_page'))
            
        result = delete_assessment_by_id(int(assessment_id))
        if result:
            flash('Assessment deleted successfully', 'success')
        else:
            flash('Failed to delete assessment', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))

# Settings Routes
@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

@staff_views.route('/settings', methods=['POST'])
@jwt_required()
def update_settings():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    # Get the new password from the form
    new_password = request.form.get('password')
    
    if new_password:
        # Update the user's password
        user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully', 'success')
    else:
        flash('No password provided', 'error')
        
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
        assessments = get_assessment_dictionary_by_course(course.code)
        
        # Get staff information
        staff = get_staff_by_id(user.id)
        
        # Calculate total percentage
        
        # total_percentage = calculate_total_percentage_for_course(course.code)
        
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

@staff_views.route('/assign_test_course/<course_code>', methods=['GET'])
@jwt_required()
def assign_test_course(course_code):
    """Test route to assign a course to the current staff member"""
    try:
        email = get_jwt_identity()
        if not email:
            flash('User identity not found. Please log in again.', 'error')
            return redirect(url_for('staff_views.get_account_page'))
            
        user = get_user_by_email(email)
        
        if not user:
            flash(f'User ID not found for email: {email}. Please log in again.', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        # Assign the course to the staff member
        result = assign_course_to_staff(user.id, course_code)
        
        if result:
            flash(f'Course {course_code} assigned to you for testing', 'success')
        else:
            flash(f'Failed to assign course {course_code}', 'error')
        
        return redirect(url_for('staff_views.get_account_page'))
    except Exception as e:
        flash(f'Error assigning course: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_account_page'))

@staff_views.route('/create_test_course/<course_code>/<course_name>', methods=['GET'])
@jwt_required()
def create_test_course(course_code, course_name):
    """Test route to create a course and assign it to the current staff member"""
    try:
        from App.models.course import Course
        from ..database import db
        
        # Check if the course already exists
        existing_course = Course.query.filter_by(code=course_code).first()
        if existing_course:
            flash(f'Course {course_code} already exists', 'info')
        else:
            # Create the course
            new_course = Course(code=course_code, name=course_name)
            db.session.add(new_course)
            db.session.commit()
            flash(f'Course {course_code} created successfully', 'success')
        
        # Now assign it to the current staff member
        return redirect(url_for('staff_views.assign_test_course', course_code=course_code))
    except Exception as e:
        flash(f'Error creating course: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_account_page'))


