from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, get_flashed_messages
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.middleware.auth import course_access_required
import datetime
from App.database import db

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

from App.controllers.assessment import (
    get_assessments_by_course,
    add_assessment,
    update_assessment,
    delete_assessment,
    get_assessment_by_id,
    format_assessment_for_calendar,
    calculate_total_percentage_for_course
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Authentication Routes
@staff_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

@staff_views.route('/register', methods=['POST'])
def register_staff_action():
    try:
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        u_ID = request.form.get('u_ID')
        status = request.form.get('status')
        email = request.form.get('email')
        pwd = request.form.get('password')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
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
    try:
        email = get_jwt_identity()
        if not email:
            flash('User identity not found. Please log in again.', 'error')
            return render_template('account.html')
            
        u_id = get_uid(email)
        if not u_id:
            flash(f'User ID not found for email: {email}. Please log in again.', 'error')
            return render_template('account.html')
        
        # Get staff information
        staff = get_staff_by_id(u_id)
        if not staff:
            flash(f'Staff record not found for ID: {u_id}. Please contact an administrator.', 'error')
            return render_template('account.html')
        
        all_courses = list_Courses()
        staff_courses = get_accessible_courses(u_id)
        
        # Convert course objects to JSON serializable dictionaries
        all_courses_json = [course.to_json() for course in all_courses]
        
        # For staff_courses, we need to include assessments
        staff_courses_json = []
        for course in staff_courses:
            course_json = course.to_json()
            # Add assessments to each course
            if hasattr(course, 'assessments'):
                course_json['assessments'] = [assessment.to_json() for assessment in course.assessments]
            staff_courses_json.append(course_json)
        
        staff_course_codes = [course.course_code for course in staff_courses]
        
        return render_template(
            'account.html', 
            courses=all_courses_json, 
            staff_courses=staff_courses_json,
            staff_course_codes=staff_course_codes,
            registered=staff_course_codes,
            staff=staff  # Pass staff information to the template
        )
    except Exception as e:
        flash(f'Error loading account page: {str(e)}', 'error')
        return render_template('account.html')

@staff_views.route('/account', methods=['POST'])
@jwt_required()
def update_staff_courses():
    email = get_jwt_identity()
    staff_id = get_uid(email)

    course_codes_json = request.form.get('courseCodes')
    if course_codes_json:
        import json
        course_codes = json.loads(course_codes_json)
        for code in course_codes:
            add_CourseStaff(staff_id, code)
       
    return redirect(url_for('staff_views.get_account_page'))

# Calendar Routes
@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    staff_courses = get_accessible_courses(u_id)
    course_codes = [course.course_code for course in staff_courses]
    
    assessments = []
    for course in staff_courses:
        course_assessments = get_assessments_by_course(course.course_code)
        for assessment in course_assessments:
            assessments.append(format_assessment_for_calendar(assessment))
    
    return render_template('calendar.html', assessments=assessments, courses=course_codes)

@staff_views.route('/calendar', methods=['POST'])
@jwt_required()
def update_calendar_page():
    data = request.get_json()
    return jsonify({'success': True})

@staff_views.route('/calendar/solve', methods=['POST'])
@jwt_required()
def solve_calendar_schedule():
    from App.controllers.semester import get_current_semester
    from App.models.semester import Semester
    from App.controllers.assessment import get_assessments_by_course
    from App.models.kris import solve_stage1, solve_stage2
    from App.models.solver_config import SolverConfig
    from App.models.course import Course
    from App.models.class_size import ClassSize
    
    # Get current semester
    semester = get_current_semester()
    
    if not semester:
        # Check if any semesters exist
        semesters = Semester.query.all()
        if not semesters:
            return jsonify({'success': False, 'error': 'No semesters found in the database. Please create a semester first.'})
        
        # Use the first semester if no current semester is set
        semester = semesters[0]
    
    # Get or create config and update with semester parameters
    config = SolverConfig.query.first()
    if not config:
        config = SolverConfig(
            semester_days=semester.K,
            min_spacing=semester.d,
            large_m=semester.M
        )
        db.session.add(config)
    else:
        # Always update config with current semester values
        config.semester_days = semester.K
        config.min_spacing = semester.d
        config.large_m = semester.M
    
    db.session.commit()
    
    # Get all active courses
    courses = Course.query.filter_by(active=True).all()
    
    if not courses:
        return jsonify({'success': False, 'error': 'No active courses found in database'})
    
    # Get all assessments and format data for solver
    formatted_courses = []
    course_codes = []
    
    for course in courses:
        # Use the controller method to get assessments for this course
        course_assessments = get_assessments_by_course(course.course_code)
        if not course_assessments:
            continue
            
        course_codes.append(course.course_code)
        
        # Format assessments for this course
        formatted_assessments = []
        for assessment in course_assessments:
            # Convert percentage to integer by multiplying by 100 if it's a decimal
            percentage = assessment.percentage
            if percentage < 100:  # If it's already stored as a percentage (e.g., 25 for 25%)
                percentage_int = int(percentage)
            else:  # If it's stored as a decimal (e.g., 0.25 for 25%)
                percentage_int = int(percentage * 100)
                
            formatted_assessments.append({
                'name': assessment.name,
                'percentage': percentage_int,
                'start_week': assessment.start_week,
                'start_day': assessment.start_day,
                'end_week': assessment.end_week,
                'end_day': assessment.end_day,
                'proctored': 1 if assessment.proctored else 0
            })
        
        # Add course with its assessments to the formatted list
        formatted_courses.append({
            'code': course.course_code,
            'assessments': formatted_assessments
        })
    
    if not formatted_courses:
        return jsonify({'success': False, 'error': 'No assessments found in database'})
    
    # Initialize class sizes matrix
    n = len(formatted_courses)
    c = [[0 for _ in range(n)] for _ in range(n)]
    
    # Get class sizes from database
    class_sizes = ClassSize.query.all()
    for class_size in class_sizes:
        i = next((idx for idx, code in enumerate(course_codes) if code == class_size.course_code), None)
        j = next((idx for idx, code in enumerate(course_codes) if code == class_size.other_course_code), None)
        if i is not None and j is not None:
            c[i][j] = class_size.size
    
    # Generate phi matrix
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]
    
    try:
        # Solve using semester parameters
        U_star, solver, x = solve_stage1(formatted_courses, c, 
                                       semester.K,
                                       semester.M)
        
        schedule, Y_star, probability = solve_stage2(formatted_courses, c, phi, U_star,
                                                   semester.K,
                                                   semester.d,
                                                   semester.M)
        
        # Format schedule for calendar display
        calendar_events = []
        
        # Calculate the semester start date
        semester_start = semester.start_date
        
        for day_offset, week, day_of_week, course_code, assessment_type in schedule:
            # Calculate the actual date
            assessment_date = semester_start + datetime.timedelta(days=day_offset)
            
            # Determine color based on assessment type
            colors = {
                'EXAM': '#e74c3c',      # Red
                'MIDTERM': '#f39c12',   # Orange
                'ASSIGNMENT': '#2ecc71', # Green
                'QUIZ': '#9b59b6',      # Purple
                'DEFAULT': '#3498db'    # Blue
            }
            color = colors.get(assessment_type, colors['DEFAULT'])
            
            # Create calendar event
            calendar_events.append({
                'title': f"{course_code} - {assessment_type}",
                'start': assessment_date.strftime('%Y-%m-%d'),
                'end': assessment_date.strftime('%Y-%m-%d'),
                'color': color,
                'textColor': '#ffffff',
                'extendedProps': {
                    'course_id': course_code,
                    'category': assessment_type,
                    'day_offset': day_offset,
                    'week': week,
                    'day_of_week': day_of_week
                }
            })
        
        return jsonify({
            'success': True,
            'events': calendar_events,
            'stats': {
                'u_star': U_star,
                'y_star': Y_star,
                'probability': probability,
                'min_spacing': semester.d,
                'total_courses': len(formatted_courses),
                'total_assessments': len(calendar_events)
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        })

# Assessment Routes
@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    email = get_jwt_identity()
    u_id = get_uid(email)
    
    staff_courses = get_accessible_courses(u_id)
    
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
    u_id = get_uid(email)
    
    staff_courses = get_accessible_courses(u_id)
    
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
        u_id = get_uid(email)
        if not has_access_to_course(u_id, course_id):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        assessment = add_assessment(
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
        
        assessment = update_assessment(
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
        u_id = get_uid(email)
        
        # Check if staff has access to this course
        if not has_access_to_course(u_id, course_code):
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
        staff = get_staff_by_id(u_id)
        
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


