from flask import request, jsonify, redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from App.models import Admin, Staff
from App.controllers.staff import has_access_to_course

def jwt_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                
                if role == Admin:
                    admin = Admin.query.filter_by(email=identity).first()
                    if not admin:
                        flash('Admin access required', 'error')
                        return redirect(url_for('auth_views.get_login_page'))
                elif role == Staff:
                    staff = Staff.query.filter_by(email=identity).first()
                    if not staff:
                        flash('Staff access required', 'error')
                        return redirect(url_for('auth_views.get_login_page'))
                
                return fn(*args, **kwargs)
            except Exception as e:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('auth_views.get_login_page'))
        return decorator
    
    if callable(role):
        fn = role
        role = None
        return wrapper(fn)
    return wrapper

def course_access_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                
                # Get staff from identity
                staff = Staff.query.filter_by(email=identity).first()
                if not staff:
                    flash('Staff access required', 'error')
                    return redirect(url_for('auth_views.get_login_page'))
                
                # Check if course_code is in kwargs
                course_code = kwargs.get('course_code')
                if not course_code:
                    # Try to get it from request args
                    course_code = request.args.get('course_code')
                    if not course_code:
                        # Try to get it from form data
                        course_code = request.form.get('course_code')
                
                # If we have a course code, check access
                if course_code and not has_access_to_course(staff.u_id, course_code):
                    flash('You do not have access to this course', 'error')
                    return redirect(url_for('staff_views.get_account_page'))
                
                return fn(*args, **kwargs)
            except Exception as e:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('auth_views.get_login_page'))
        return decorator
    return wrapper 