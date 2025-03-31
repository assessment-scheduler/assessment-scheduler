from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os,csv
from ..database import db
from ..models import Admin
from ..controllers import (
    delete_course,
    assign_lecturer,
    assign_multiple_lecturers,
    update_course,
    get_all_courses,
    create_course,
    get_course,
    get_all_staff,
    get_course_lecturers
)
from ..controllers.auth import admin_required

course_views = Blueprint('course_views', __name__, template_folder ='../templates')
@course_views.route('/courses', methods=['GET'])
@admin_required
def get_courses():
    courses = get_all_courses()
    return render_template('courses.html', courses=courses)

@course_views.route('/new_course', methods=['GET'])
@admin_required
def get_new_course():
    staff_list = get_all_staff()
    return render_template('add_course.html', staff_list=staff_list)  

@course_views.route('/new_course', methods=['POST'])
@admin_required
def add_course_action():
    course_code = request.form.get('course_code')
    title = request.form.get('title')
    level = request.form.get('level')
    credits = request.form.get('credits')
    semester = request.form.get('semester')
    
    if credits and credits.isdigit():
        credits = int(credits)
    else:
        credits = None
        
    if (get_course(course_code)):
        flash("Course already exists", "error")
        return redirect(url_for('course_views.get_new_course')) 
    result = create_course(course_code, title, level, credits, semester)
    if result:
        lecturer_ids = request.form.getlist('lecturer_ids')
        if lecturer_ids:
            assign_multiple_lecturers(lecturer_ids, course_code)
        
        flash("Course added successfully!")
        return redirect(url_for('course_views.get_courses'))
    else:
        flash("Failed to add course. Course code may already exist.")
        return redirect(url_for('course_views.get_new_course'))
    
    
@course_views.route('/update_course/<string:course_code>', methods=['GET'])
@admin_required
def get_update_course(course_code):
    course = get_course(course_code)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('course_views.get_courses'))
    staff_list = get_all_staff()
    current_lecturers = get_course_lecturers(course_code) or []
    current_lecturer_ids = [str(lecturer.id) for lecturer in current_lecturers]
    
    return render_template(
        'modify_course.html', 
        course=course, 
        staff_list=staff_list, 
        current_lecturers=current_lecturers,
        current_lecturer_ids=current_lecturer_ids
    )

@course_views.route('/update_course', methods=['POST'])
@admin_required
def update_course_action():
    try:
        old_course_code = request.form.get('old_course_code')
        new_course_code = request.form.get('new_course_code')
        new_course_name = request.form.get('title')
        level = request.form.get('level')
        credits = request.form.get('credits')
        semester = request.form.get('semester')
        lecturer_ids = request.form.getlist('lecturer_ids')
        
        if credits and credits.isdigit():
            credits = int(credits)
        else:
            credits = None
            
        print(f"Updating course: {old_course_code} -> {new_course_code}, {new_course_name}, lecturers: {lecturer_ids}")
        if not old_course_code or not new_course_code or not new_course_name:
            flash("Course code and course name are required", "error")
            return redirect(url_for('course_views.get_update_course', course_code=old_course_code))

        course_update_success = update_course(old_course_code, new_course_code, new_course_name, level, credits, semester)
        if not course_update_success:
            flash("Failed to update course details", "error")
            return redirect(url_for('course_views.get_update_course', course_code=old_course_code))

        lecturer_assign_success = assign_multiple_lecturers(lecturer_ids, new_course_code)
        if not lecturer_assign_success:
            flash("Course updated but failed to update lecturer assignments", "warning")
            return redirect(url_for('course_views.get_courses'))

        flash("Course updated successfully!", "success")
        return redirect(url_for('course_views.get_courses'))

    except Exception as e:
        print(f"Error updating course: {str(e)}")
        flash(f"An error occurred while updating the course", "error")
        return redirect(url_for('course_views.get_update_course', course_code=old_course_code))

@course_views.route('/delete_course/<string:course_code>', methods = ['POST'])
@admin_required
def delete_course_action(course_code):
    if not delete_course(course_code):
        flash("Failed to delete course")
    else:
        flash("Course deleted successfully!")
    return redirect(url_for('course_views.get_courses'))

@course_views.route('/upload_course', methods=['POST'])
@admin_required
def upload_course_file():
    
    file = request.files['file'] 
    if (file.filename == '') or not file.filename.lower().endswith('.csv'):
        return render_template('upload_files.html', message = 'Please upload a CSV file!') 

    filename = secure_filename(file.filename)
    file.save(os.path.join('App/uploads', filename)) 
    courses_added = 0
    with open(os.path.join('App/uploads', filename)) as course_file:
        reader = csv.DictReader(course_file)
        for row in reader:
            level = row.get('level')
            credits = row.get('credits')
            semester = row.get('semester')
            
            if credits and credits.isdigit():
                credits = int(credits)
            else:
                credits = None
                
            if create_course(row['course_code'], row['course_name'], level, credits, semester):
                courses_added += 1
        message = f'Success! {courses_added} courses have been added to the database.'
        return render_template('upload_files.html', message=message)

@course_views.route('/upload_lecturer_assignments', methods=['POST'])
@admin_required
def upload_lecturer_assignments():
    file = request.files['file']
    if (file.filename == '') or not file.filename.lower().endswith('.csv'):
        return render_template('upload_files.html', message='Please upload a CSV file!')
        
    filename = secure_filename(file.filename)
    file.save(os.path.join('App/uploads', filename))
    
    assignments_added = 0
    
    try:
        with open(os.path.join('App/uploads', filename)) as assignment_file:
            reader = csv.DictReader(assignment_file)
            for row in reader:
                if 'lecturer_id' in row and 'course_code' in row:
                    if assign_lecturer(row['lecturer_id'], row['course_code']):
                        assignments_added += 1
                else:
                    return render_template('upload_files.html', 
                        message='CSV file must contain lecturer_id and course_code columns.')
        
        message = f'Success! {assignments_added} lecturer assignments have been added to the database.'
        return render_template('upload_files.html', message=message)
    except Exception as e:
        return render_template('upload_files.html', 
            message=f'Error processing CSV file: {str(e)}')