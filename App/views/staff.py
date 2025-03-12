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
    
    staff_exams = get_assessments_by_lecturer(user.email) or []
    staff_courses = [course.to_json() for course in get_staff_courses(email) or []]
    semester = get_active_semester().to_json() if get_active_semester() else {}
    other_exams = get_assessments_by_lecturer(user.email) or []
    
    return render_template('calendar.html', staff_exams=staff_exams, staff_courses=staff_courses, semester=semester, other_exams=other_exams)

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
