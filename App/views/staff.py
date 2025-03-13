from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database import db
from ..models import Staff
from ..controllers import (
    create_staff,
    get_staff_by_email,
    get_staff_courses,
    is_course_lecturer,
    assign_course_to_staff,
    get_staff_by_id,
    get_course,
    get_user_by_email,
    get_num_assessments,
    get_active_semester,
    get_assessments_by_lecturer,
    get_assessment_by_id,
    update_assessment,
    get_assessments_by_course
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/account', methods=['GET'])
@jwt_required(Staff)
def get_account_page():
    email = get_jwt_identity()
    staff = get_staff_by_email(email)
    courses = get_staff_courses(email)
    num_assessments = 0
    for course in courses: 
        num_assessments  = num_assessments + get_num_assessments(course.code)
    return render_template('account.html', staff=staff, courses=courses, num_assessments = num_assessments)

@staff_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    # Get all assessments for the lecturer
    all_assessments = get_assessments_by_lecturer(user.email) or []
    
    # Separate into scheduled and unscheduled assessments
    scheduled_assessments = []
    unscheduled_assessments = []
    
    for assessment in all_assessments:
        assessment_dict = {
            'id': assessment.id,
            'name': assessment.name,
            'course_code': assessment.course_code,
            'percentage': assessment.percentage,
            'start_week': assessment.start_week,
            'start_day': assessment.start_day,
            'end_week': assessment.end_week,
            'end_day': assessment.end_day,
            'proctored': assessment.proctored,
            'scheduled': assessment.scheduled.isoformat() if assessment.scheduled else None
        }
        
        if assessment.scheduled:
            scheduled_assessments.append(assessment_dict)
        else:
            unscheduled_assessments.append(assessment_dict)
    
    staff_courses = [course.to_json() for course in get_staff_courses(email) or []]
    
    # Get active semester and ensure it exists
    active_semester = get_active_semester()
    if not active_semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        semester = {}
    else:
        semester = active_semester.to_json()
        # Ensure dates are in ISO format
        if isinstance(semester.get('start_date'), str):
            semester['start_date'] = semester['start_date'].split(' ')[0]
        if isinstance(semester.get('end_date'), str):
            semester['end_date'] = semester['end_date'].split(' ')[0]
    
    return render_template('calendar.html', 
                         scheduled_assessments=scheduled_assessments,
                         unscheduled_assessments=unscheduled_assessments,
                         staff_courses=staff_courses, 
                         semester=semester)

@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')

@staff_views.route('/settings', methods=['POST'])
@jwt_required()
def update_settings():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    new_password = request.form.get('password')
    
    if new_password:
        user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully', 'success')
    else:
        flash('No password provided', 'error')
        
    return redirect(url_for('staff_views.get_settings_page'))

@staff_views.route('/update_assessment_schedule', methods=['POST'])
@jwt_required()
def update_assessment_schedule():
    try:
        assessment_id = request.form.get('id')
        scheduled_date = request.form.get('scheduled')
        
        if not assessment_id or not scheduled_date:
            return jsonify({'error': 'Missing required fields'}), 400
        
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
            
        if not is_course_lecturer(user.id, assessment.course_code):
            return jsonify({'error': 'Unauthorized to modify this assessment'}), 403
        
        # Convert the date string to a Python date object
        from datetime import datetime
        scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
        
        # Update the assessment with the scheduled date
        assessment.scheduled = scheduled_date
        db.session.commit()
        
        return jsonify({'message': 'Assessment scheduled successfully'}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
