from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..controllers import (
    get_staff_by_email,
    get_staff_courses,
    is_course_lecturer,
    get_user_by_email,
    create_assessment,
    delete_assessment_by_id,
    update_assessment,
    get_assessment_by_id,
    get_assessments_by_lecturer,
    get_assessments_by_course,
    get_course,
    get_active_semester
)
from datetime import datetime

assessment_views = Blueprint('assessment_views', __name__, template_folder='../templates')

@assessment_views.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments_page():
    email = get_jwt_identity()
    user = get_staff_by_email(email)
    assessments = get_assessments_by_lecturer(user.email)
    return render_template('assessments.html', course_assessments=assessments)

@assessment_views.route('/add_assessment', methods=['GET'])
@jwt_required()
def get_add_assessments_page():
    email = get_jwt_identity()
    staff_courses = get_staff_courses(email)
    semester = get_active_semester()
    return render_template('add_assessment.html', courses=staff_courses, semester=semester)

@assessment_views.route('/add_assessment', methods=['POST'])
@jwt_required()
def add_assessments_action():
    try:
        course_code = request.form.get('course_code')
        assessment_name = request.form.get('name')
        percentage = float(request.form.get('percentage')) 
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = 1 if request.form.get('proctored') == 'on' else 0

        email = get_jwt_identity()
        user = get_user_by_email(email)
        if not is_course_lecturer(user.id, course_code):
            flash('You do not have access to this course', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
        
        assessment = create_assessment(course_code, assessment_name, percentage, start_week, start_day, end_week, end_day, proctored)
        if assessment:
            flash('Assessment added successfully', 'success')
            return redirect(url_for('assessment_views.get_assessments_page'))
        else:
            flash('Failed to add assessment. Please check your inputs.', 'error')
            return redirect(url_for('assessment_views.get_add_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))

@assessment_views.route('/update_assessment/<string:id>', methods=['GET'])
@jwt_required()
def get_modify_assessments_page(id):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    assessment = get_assessment_by_id(id)
    
    if not assessment:
        flash('Assessment not found', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    
    if not is_course_lecturer(user.id, assessment.course_code):
        flash('You do not have permission to modify assessments for this course', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    
    semester = get_active_semester()
    if not semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        
    return render_template('update_assessment.html', assessment=assessment, semester=semester)

@assessment_views.route('/update_assessment/<string:id>', methods=['POST'])
@jwt_required()
def modify_assessment(id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
        
        if not is_course_lecturer(user.id, assessment.course_code):
            flash('You do not have permission to modify assessments for this course', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
            
        assessment_name = request.form.get('name')
        percentage = int(request.form.get('percentage')) 
        start_week = int(request.form.get('start_week'))
        start_day = int(request.form.get('start_day'))
        end_week = int(request.form.get('end_week'))
        end_day = int(request.form.get('end_day'))
        proctored = 1 if request.form.get('proctored') is not None else 0
        
        assessment_result = update_assessment(id, assessment_name, percentage, start_week, start_day, end_week, end_day, proctored)
        if assessment_result:
            flash('Assessment updated successfully', 'success')
            return redirect(url_for('assessment_views.get_assessments_page'))
        else:
            flash('Failed to update assessment. Please check your inputs.', 'error')
            return redirect(url_for('assessment_views.get_modify_assessments_page', id=id))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))

@assessment_views.route('/delete_assessment/<int:assessment_id>', methods=['POST', 'GET'])
@jwt_required()
def delete_assessment_action(assessment_id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
        
        if not is_course_lecturer(user.id, assessment.course_code):
            flash('You do not have permission to delete assessments for this course', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
            
        result = delete_assessment_by_id(int(assessment_id))
        if result:
            flash('Assessment deleted successfully', 'success')
        else:
            flash('Failed to delete assessment', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))

@assessment_views.route('/assessments/<course_code>', methods=['GET'])
@jwt_required()
def get_course_details(course_code):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    if not is_course_lecturer(user.id, course_code):
        flash('You do not have access to this course', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))

    course = get_course(course_code)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    
    assessments = get_assessments_by_course(course.code)
    return render_template(
        'course_details.html',
        course=course,
        assessments=assessments,
        staff=user
    )

@assessment_views.route('/update_assessment_schedule', methods=['POST'])
@jwt_required()
def update_assessment_schedule():
    try:
        assessment_id = request.form.get('id')
        assessment_date = datetime.strptime(request.form.get('assessment_date'), '%Y-%m-%d').date()
        
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
            
        if not is_course_lecturer(user.id, assessment.course_code):
            flash('You do not have permission to schedule this assessment', 'error')
            return redirect(url_for('assessment_views.get_assessments_page'))
        
        # Update the assessment with the scheduled date
        result = update_assessment(
            assessment_id,
            assessment.name,
            assessment.percentage,
            assessment.start_week,
            assessment.start_day,
            assessment.end_week,
            assessment.end_day,
            assessment.proctored,
            assessment_date 
        )
        
        if result:
            flash('Assessment scheduled successfully', 'success')
        else:
            flash('Failed to schedule assessment', 'error')
        
        return redirect(url_for('assessment_views.get_assessments_page'))
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))

@assessment_views.route('/schedule_assessment/<string:id>', methods=['GET'])
@jwt_required()
def get_schedule_assessment_page(id):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    assessment = get_assessment_by_id(id)
    
    if not assessment:
        flash('Assessment not found', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    
    if not is_course_lecturer(user.id, assessment.course_code):
        flash('You do not have permission to schedule assessments for this course', 'error')
        return redirect(url_for('assessment_views.get_assessments_page'))
    
    semester = get_active_semester()
    if not semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        
    return render_template('schedule_assessment.html', assessment=assessment, semester=semester)
