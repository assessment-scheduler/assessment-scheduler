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
    get_active_semester
)
from ..controllers.auth import staff_required

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
        department = request.form.get('department', 'DCIT') 
        faculty = request.form.get('faculty', 'FST')  
        
        staff = create_staff(id, email, password, first_name, last_name, department, faculty)
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
@staff_required
def get_account_page():
    email = get_jwt_identity()
    staff = get_staff_by_email(email)
    courses = get_staff_courses(email)
    num_assessments = 0
    for course in courses: 
        num_assessments  = num_assessments + get_num_assessments(course.code)
    return render_template('account.html', staff=staff, courses=courses, num_assessments = num_assessments)

@staff_views.route('/settings', methods=['GET'])
@staff_required
def get_settings_page():
    return render_template('settings.html')

@staff_views.route('/settings', methods=['POST'])
@staff_required
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