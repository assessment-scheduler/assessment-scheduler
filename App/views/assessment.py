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
    get_active_semester,
    get_num_assessments,
    get_all_assessments
)
from datetime import datetime
import json

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
            return jsonify({'success': False, 'message': 'Assessment not found'}), 404
            
        if not is_course_lecturer(user.id, assessment.course_code):
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
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
            # Get the updated assessment
            updated_assessment = get_assessment_by_id(assessment_id)
            return jsonify({
                'success': True, 
                'message': 'Assessment scheduled successfully',
                'assessment': {
                    'id': updated_assessment.id,
                    'name': updated_assessment.name,
                    'course_code': updated_assessment.course_code,
                    'percentage': updated_assessment.percentage,
                    'scheduled': updated_assessment.scheduled.isoformat() if updated_assessment.scheduled else None,
                    'proctored': updated_assessment.proctored
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to schedule assessment'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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

@assessment_views.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_page():
    email = get_jwt_identity()
    user = get_user_by_email(email)
    
    # CRITICAL SECTION: Retrieve ALL assessments across the system
    all_assessments = get_all_assessments() or []
    print(f"Total assessments retrieved: {len(all_assessments)}")
    
    # Get user's assessments (for unscheduled list)
    user_assessments = get_assessments_by_lecturer(user.email) or []
    
    # Lists to be passed to the template
    staff_exams = []  # Current user's assessments
    scheduled_assessments = []  # All scheduled assessments for calendar display
    unscheduled_assessments = []  # Current user's unscheduled assessments
    
    # Process all assessments for the calendar
    for assessment in all_assessments:
        # Handle assessments with scheduled dates
        try:
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
            
            # If it's scheduled, add to scheduled list
            if assessment.scheduled:
                if isinstance(assessment_dict['scheduled'], str):
                    if 'T' in assessment_dict['scheduled']:
                        assessment_dict['scheduled'] = assessment_dict['scheduled'].split('T')[0]
                
                scheduled_assessments.append(assessment_dict)
                print(f"Added to calendar: {assessment.course_code}-{assessment.name} on {assessment_dict['scheduled']}")
                
        except Exception as e:
            print(f"Error processing assessment {assessment.id}: {str(e)}")
    
    # Process user's assessments for the unscheduled list
    for assessment in user_assessments:
        try:
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
            
            # Format dates consistently
            if assessment_dict.get('scheduled') and isinstance(assessment_dict['scheduled'], str):
                if 'T' in assessment_dict['scheduled']:
                    assessment_dict['scheduled'] = assessment_dict['scheduled'].split('T')[0]
            
            staff_exams.append(assessment_dict)
            
            # Add to unscheduled list if not scheduled
            if not assessment.scheduled:
                unscheduled_assessments.append(assessment_dict)
        except Exception as e:
            print(f"Error processing user assessment {assessment.id}: {str(e)}")
    
    # Get staff courses
    staff_course_objects = get_staff_courses(email) or []
    staff_courses = []
    
    for course in staff_course_objects:
        try:
            course_dict = {
                'code': course.code,  # Changed from course.id to course.code
                'name': course.name,
                'level': course.code[4] if len(course.code) > 4 else ''  # Extract level from course code
            }
            staff_courses.append(course_dict)
        except Exception as e:
            print(f"Error processing course {course.code}: {str(e)}")  # Changed from course.id to course.code
    
    # For backwards compatibility
    courses = staff_courses
    other_exams = staff_exams
    
    # Get active semester
    active_semester = get_active_semester()
    if not active_semester:
        flash('No active semester found. Please contact an administrator.', 'warning')
        semester = {}
    else:
        semester = {
            'id': active_semester.id,
            'start_date': active_semester.start_date.isoformat(),
            'end_date': active_semester.end_date.isoformat(),
            'sem_num': active_semester.sem_num,
            'max_assessments': active_semester.max_assessments,
            'constraint_value': active_semester.constraint_value,
            'active': active_semester.active
        }
        
        # Ensure dates are in ISO format
        if isinstance(semester.get('start_date'), str):
            semester['start_date'] = semester['start_date'].split('T')[0]
        if isinstance(semester.get('end_date'), str):
            semester['start_date'].split('T')[0]
            semester['end_date'] = semester['end_date'].split('T')[0]
    
    # Important debug information
    print(f"Calendar: Passing {len(scheduled_assessments)} scheduled assessments to template")
    for idx, assessment in enumerate(scheduled_assessments[:10]):  # Print first 10
        print(f"  {idx+1}. ID: {assessment.get('id')}, Name: {assessment.get('name')}, Date: {assessment.get('scheduled')}, Course: {assessment.get('course_code')}")
    
    # Write to a debug file to inspect the data
    with open('calendar_debug.json', 'w') as f:
        f.write(json.dumps({
            'scheduled_count': len(scheduled_assessments),
            'scheduled_sample': scheduled_assessments[:10] if scheduled_assessments else []
        }, indent=2))
    
    return render_template('calendar.html', 
                          staff_exams=staff_exams,
                          other_exams=other_exams,
                          staff_courses=staff_courses,
                          courses=courses,
                          semester=semester,
                          scheduled_assessments=scheduled_assessments,
                          unscheduled_assessments=unscheduled_assessments)
