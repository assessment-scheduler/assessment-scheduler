from flask import Blueprint, flash, redirect, request, render_template, url_for, make_response, session
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import logout_user
from ..controllers.auth import login_user
from ..controllers.staff import create_staff, get_staff_by_email, get_staff_by_id

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

@auth_views.route('/login', methods=['GET'])
def get_login_page():
    if request.referrer and 'register' not in request.referrer and 'signup' not in request.referrer:
        session.pop('_flashes', None)
    return render_template('login.html')
    
@auth_views.route('/login', methods=['POST'])
def login_action():
    if '_flashes' in session:
        session.pop('_flashes', None)
        
    email = request.form.get('email')          
    password = request.form.get('password')    
    response = login_user(email, password)
    if not response:
        flash('Bad email or password given', 'error') 
        return redirect(url_for('auth_views.get_login_page'))
    return response

@auth_views.route('/register', methods=['GET'])
def get_register_page():
    return render_template('register.html')

@auth_views.route('/register', methods=['POST'])
def register_action():
    try:
        staff_id = request.form.get('staff_id')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        if not all([staff_id, email, password, confirm_password, first_name, last_name]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('auth_views.get_register_page'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth_views.get_register_page'))
        
        if get_staff_by_id(staff_id):
            flash('Staff ID already registered', 'error')
            return redirect(url_for('auth_views.get_register_page'))
            
        if get_staff_by_email(email):
            flash('Email already registered', 'error')
            return redirect(url_for('auth_views.get_register_page'))
        
        success = create_staff(
            id=staff_id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            department=department,
            faculty=faculty
        )
        
        if success:
            flash('Registration successful! Please login with your new account.', 'success')
            return redirect(url_for('auth_views.get_login_page'))
        else:
            flash('Failed to create account', 'error')
            return redirect(url_for('auth_views.get_register_page'))
            
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        flash('An error occurred during registration', 'error')
        return redirect(url_for('auth_views.get_register_page'))


@auth_views.route('/logout', methods=['GET'])
@jwt_required(optional=True)
def logout():
    try:
        identity = get_jwt_identity()
        if identity:
            response = make_response(redirect(url_for('auth_views.get_login_page')))
            response.delete_cookie('access_token')
            logout_user()
            if request.path == '/logout':
                flash('You have been logged out successfully', 'success')
            return response
        else:
            return redirect(url_for('auth_views.get_login_page'))
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return redirect(url_for('auth_views.get_login_page'))
