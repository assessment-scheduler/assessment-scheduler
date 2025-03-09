from functools import wraps
from flask import request, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity
from App.controllers.staff import get_staff, is_course_lecturer
from App.controllers.assessment import get_assessment_by_id

def course_access_required():
    """
    A decorator that checks if the current staff member has access to the course
    associated with the assessment they're trying to modify.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the current user's ID from the JWT token
            current_user_id = get_jwt_identity()
            
            # Get the assessment ID from the URL parameters
            assessment_id = kwargs.get('id')
            
            if not assessment_id:
                flash('Assessment ID not found', 'error')
                return redirect(url_for('staff_views.get_assessments_page'))
            
            # Get the assessment to find its course code
            assessment = get_assessment_by_id(assessment_id)
            if not assessment:
                flash('Assessment not found', 'error')
                return redirect(url_for('staff_views.get_assessments_page'))
            
            # Get the course code from the assessment
            course_code = assessment.course_code
            
            # Check if the staff member has access to this course
            if not is_course_lecturer(current_user_id, course_code):
                flash('You do not have permission to modify assessments for this course', 'error')
                return redirect(url_for('staff_views.get_assessments_page'))
            
            # If they have access, proceed with the original function
            return f(*args, **kwargs)
        return decorated_function
    return decorator