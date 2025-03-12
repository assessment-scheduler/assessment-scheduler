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
    create_assessment,
    delete_assessment_by_id,
    update_assessment,
    get_assessment_by_id,
    get_assessment_dictionary_by_course,
    get_assessments_by_lecturer,
    get_assessments_by_course,
    get_num_assessments,
    get_active_semester
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
## working


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

@staff_views.route('/update_assessment_schedule', methods=['POST'])
@jwt_required()
def update_assessment_schedule():
    try:
        assessment_id = request.form.get('id')
        start_week = int(request.form.get('start_week', 0))
        start_day = int(request.form.get('start_day', 0))
        end_week = int(request.form.get('end_week', 0))
        end_day = int(request.form.get('end_day', 0))
        
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)
        
        if not assessment:
            return jsonify({'success': False, 'message': 'Assessment not found'}), 404
            
        if not is_course_lecturer(user.id, assessment.course_code):
            return jsonify({'success': False, 'message': 'You do not have permission to update this assessment'}), 403
            
        # Update only the scheduling fields
        result = update_assessment(
            assessment_id,
            assessment.name,
            assessment.percentage,
            start_week,
            start_day,
            end_week,
            end_day,
            assessment.proctored
        )
        
        if result:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to update assessment'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@staff_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    email = get_jwt_identity()
    user = get_staff_by_email(email)
    assessments = get_assessments_by_lecturer(user.email)
    return render_template('assessments.html',course_assessments = assessments)
## working

@staff_views.route('/add_assessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    email = get_jwt_identity()
    staff_courses = get_staff_courses(email)
    semester = get_active_semester()
    return render_template('add_assessment.html', courses=staff_courses, semester=semester)
## working

@staff_views.route('/add_assessment', methods=['POST'])
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
        
        assessment:bool = create_assessment(course_code,assessment_name,percentage,start_week,start_day,end_week,end_day,proctored)
        if assessment:
            flash('Assessment added successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to add assessment. Please check your inputs.', 'error')
            return redirect(url_for('staff_views.get_add_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))
## working

@staff_views.route('/update_assessment/<string:id>', methods=['GET'])
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
    
    semester = get_active_semester()
    if not semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        
    return render_template('update_assessment.html', assessment=assessment, semester=semester)
## working


@staff_views.route('/update_assessment/<string:id>', methods=['POST'])
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
        
        assessment_result = update_assessment(id, assessment_name, percentage, start_week, start_day, end_week, end_day, proctored)
        if assessment_result:
            flash('Assessment updated successfully', 'success')
            return redirect(url_for('staff_views.get_assessments_page'))
        else:
            flash('Failed to update assessment. Please check your inputs.', 'error')
            return redirect(url_for('staff_views.get_modify_assessments_page', id=id))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('staff_views.get_assessments_page'))
## working

@staff_views.route('/delete_assessment/<int:assessment_id>', methods=['POST', 'GET'])
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
## working 

@staff_views.route('/settings', methods=['GET'])
@jwt_required()
def get_settings_page():
    return render_template('settings.html')
## working


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
## working


@staff_views.route('/assessments/<course_code>', methods=['GET'])
@jwt_required()
def get_course_details(course_code):
        email = get_jwt_identity()
        user = get_user_by_email(email)
        
        if not is_course_lecturer(user.id, course_code):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('staff_views.get_account_page'))

        course = get_course(course_code)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('staff_views.get_account_page'))
        
        assessments = get_assessments_by_course(course.code)
        return render_template(
            'course_details.html',
            course=course,
            assessments=assessments,
            staff=user,
        )
## working
