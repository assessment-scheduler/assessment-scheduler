from App.models.admin import Admin
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required
from App.database import db
from werkzeug.utils import secure_filename
import os, csv
from datetime import datetime, date
import uuid

from App.controllers.course import (
    get_course,
    get_all_courses,
    create_course,
    update_course,
    delete_course,
    assign_lecturer
)

from App.controllers.courseoverlap import (
    get_cell,
    get_overlap_value,
    get_all_cells,
    create_cell,
    get_course_row,
    fill_empty_cells,
    get_course_matrix,
    get_phi_matrix
)

from App.controllers.staff import (
    get_all_staff,
    get_staff_by_id,
    update_staff,
    delete_staff,
    get_staff_courses,
    create_staff
)

from App.controllers.admin import get_admin_by_id
from App.controllers.semester import get_all_semesters, get_semester, create_semester, set_active, deactivate_all, parse_date
from App.controllers.assessment import get_all_assessments
from App.models.staff import Staff
from App.models.semester import Semester

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

# Admin dashboard - entry point after login
@admin_views.route('/dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Gets Semester List Page
@admin_views.route('/semester', methods=['GET'])
@jwt_required(Admin)
def get_upload_page():
    semesters = get_all_semesters()
    return render_template('semester.html', semesters=semesters)

@admin_views.route('/uploadFiles', methods=['GET'])
@jwt_required(Admin)
def get_uploadFiles_page():
    return render_template('uploadFiles.html')

@admin_views.route('/courses_list', methods=['GET'])
@jwt_required(Admin)
def index():    
    return redirect(url_for('admin_views.get_courses'))

# Get form to add a new semester
@admin_views.route('/newSemesterForm', methods=['GET'])
@jwt_required(Admin)
def get_new_semester_form():
    return render_template('add_semester.html')

# Add a new semester
@admin_views.route('/addNewSemester', methods=['POST'])
@jwt_required(Admin)
def add_new_semester():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        sem_num = int(request.form.get('sem_num'))
        max_assessments = int(request.form.get('max_assessments'))
        constraint_value = int(request.form.get('constraint_value'))
        
        # Parse dates
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        # Validate dates
        if isinstance(start_date, str) or isinstance(end_date, str):
            flash(f'Invalid date format: {start_date if isinstance(start_date, str) else end_date}', 'error')
            return redirect(url_for('admin_views.get_new_semester_form'))
        
        if start_date >= end_date:
            flash('Start date must be before end date', 'error')
            return redirect(url_for('admin_views.get_new_semester_form'))
        
        # Create semester
        result = create_semester(start_date, end_date, sem_num, max_assessments, constraint_value)
        
        if result:
            flash('Semester added successfully', 'success')
        else:
            flash('Failed to add semester', 'error')
        
        return redirect(url_for('admin_views.get_upload_page'))

# Get form to edit a semester
@admin_views.route('/modifySemester/<int:semester_id>', methods=['GET'])
@jwt_required(Admin)
def get_update_semester(semester_id):
    semester = get_semester(semester_id)
    if not semester:
        flash('Semester not found', 'error')
        return redirect(url_for('admin_views.get_upload_page'))
    
    return render_template('add_semester.html', semester=semester)

# Update a semester
@admin_views.route('/updateSemester/<int:semester_id>', methods=['POST'])
@jwt_required(Admin)
def update_semester(semester_id):
    if request.method == 'POST':
        semester = get_semester(semester_id)
        if not semester:
            flash('Semester not found', 'error')
            return redirect(url_for('admin_views.get_upload_page'))
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        sem_num = int(request.form.get('sem_num'))
        max_assessments = int(request.form.get('max_assessments'))
        constraint_value = int(request.form.get('constraint_value'))
        
        # Parse dates
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        # Validate dates
        if isinstance(start_date, str) or isinstance(end_date, str):
            flash(f'Invalid date format: {start_date if isinstance(start_date, str) else end_date}', 'error')
            return redirect(url_for('admin_views.get_update_semester', semester_id=semester_id))
        
        if start_date >= end_date:
            flash('Start date must be before end date', 'error')
            return redirect(url_for('admin_views.get_update_semester', semester_id=semester_id))
        
        # Update semester
        semester.start_date = start_date
        semester.end_date = end_date
        semester.sem_num = sem_num
        semester.max_assessments = max_assessments
        semester.constraint_value = constraint_value
        
        try:
            db.session.commit()
            flash('Semester updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update semester: {str(e)}', 'error')
        
        return redirect(url_for('admin_views.get_upload_page'))

# Delete a semester
@admin_views.route('/deleteSemester/<int:semester_id>', methods=['POST'])
@jwt_required(Admin)
def delete_semester(semester_id):
    semester = get_semester(semester_id)
    if not semester:
        flash('Semester not found', 'error')
        return redirect(url_for('admin_views.get_upload_page'))
    
    try:
        db.session.delete(semester)
        db.session.commit()
        flash('Semester deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete semester: {str(e)}', 'error')
    
    return redirect(url_for('admin_views.get_upload_page'))

# Set a semester as active
@admin_views.route('/setActiveSemester/<int:semester_id>', methods=['POST'])
@jwt_required(Admin)
def set_active_semester(semester_id):
    result = set_active(semester_id)
    
    if result:
        flash('Semester set as active', 'success')
    else:
        flash('Failed to set semester as active', 'error')
    
    return redirect(url_for('admin_views.get_upload_page'))

# Retrieves semester details and stores it in global variables 
@admin_views.route('/newSemester', methods=['POST'])
@jwt_required(Admin)
def new_semester_action():
    if request.method == 'POST':
        start_date = request.form.get('teachingBegins')
        end_date = request.form.get('teachingEnds')
        sem_num = request.form.get('semester')
        max_assessments = request.form.get('maxAssessments') #used for class detection feature
        create_semester(start_date, end_date, sem_num, max_assessments)

        # Return course upload page to upload cvs file for courses offered that semester
        return render_template('uploadFiles.html')  

# Gets csv file with course listings, parses it to store course data and stores it in application
@admin_views.route('/uploadcourse', methods=['POST'])
@jwt_required(Admin)
def upload_course_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        # Check if file is present
        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('uploadFiles.html', message = message) 
        
        # Check if file is a CSV
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('uploadFiles.html', message = message)
            
        # Secure filename
        filename = secure_filename(file.filename)
    
        # Save file to uploads folder
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            # Validate CSV structure
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['course_code', 'course_name']
                
                # Check if all required columns are present
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('uploadFiles.html', message=message)
            
            # Process the file exactly like in initialize.py
            courses_added = 0
            with open(os.path.join('App/uploads', filename)) as course_file:
                reader = csv.DictReader(course_file)
                for row in reader:
                    if create_course(row['course_code'], row['course_name']):
                        courses_added += 1
            
            message = f'<strong>Success!</strong> {courses_added} courses have been added to the database.'
            return render_template('uploadFiles.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('uploadFiles.html', message=message)

@admin_views.route('/uploadclasssizes', methods=['POST'])
@jwt_required(Admin)
def upload_class_sizes_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        # Check if file is present
        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('uploadFiles.html', message = message) 
        
        # Check if file is a CSV
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('uploadFiles.html', message = message)
            
        # Secure filename
        filename = secure_filename(file.filename)
    
        # Save file to uploads folder
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            # Use controller function instead of direct model access
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip header row
                
                for row in csv_reader:
                    if len(row) >= 2:
                        course_code = row[0]
                        class_size = int(row[1])
                        add_class_size(course_code, class_size)
                        
            flash('Class sizes uploaded successfully!', 'success')
            return redirect(url_for('admin_views.get_uploadFiles_page'))
        except Exception as e:
            flash(f'<strong>Error:</strong> {str(e)}', 'error')
            return redirect(url_for('admin_views.get_uploadFiles_page'))

# Pull course list from database
@admin_views.route('/get_courses', methods=['GET'])
@jwt_required(Admin)
def get_courses():
    courses = get_all_courses()
    return render_template('courses.html', courses=courses)

# Gets Add Course Page
@admin_views.route('/newCourse', methods=['GET'])
@jwt_required(Admin)
def get_new_course():
    staff_list = Staff.query.all()
    return render_template('addCourse.html', staff_list=staff_list)  

# Retrieves course info and stores it in database ie. add new course
@admin_views.route('/addNewCourse', methods=['POST'])
@jwt_required(Admin)
def add_course_action():
    if request.method == 'POST':
        courseCode = request.form.get('course_code')
        title = request.form.get('title')
        lecturer_id = request.form.get('lecturer_id') or None
        
        # Validate required fields
        errors = []
        if not courseCode:
            errors.append("Course code is required")
        if not title:
            errors.append("Title is required")
            
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('admin_views.get_new_course'))
        
        # Add course to database
        result = create_course(courseCode, title)
        
        if result:
            # Assign lecturer if provided
            if lecturer_id:
                course = get_course(courseCode)
                if course:
                    course.lecturer_id = lecturer_id
                    try:
                        db.session.commit()
                    except Exception as e:
                        flash(f"Course added but failed to assign lecturer: {str(e)}")
            
            flash("Course added successfully!")
            return redirect(url_for('admin_views.get_courses'))
        else:
            flash("Failed to add course. Course code may already exist.")
            return redirect(url_for('admin_views.get_new_course'))

# Gets Update Course Page
@admin_views.route('/modifyCourse/<string:courseCode>', methods=['GET'])
@jwt_required(Admin)
def get_update_course(courseCode):
    course = get_course(courseCode)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('admin_views.get_courses'))
        
    staff_list = Staff.query.all()
    
    return render_template('modify_course.html', course=course, staff_list=staff_list)

# Selects new course details and updates existing course in database
@admin_views.route('/updateCourse', methods=['POST'])
@jwt_required(Admin)
def update_course_action():
    if request.method == 'POST':
        old_course_code = request.form.get('old_course_code')
        new_course_code = request.form.get('course_code')
        new_course_name = request.form.get('title')
        lecturer_id = request.form.get('lecturer_id') or None
        
        # Validate required fields
        errors = []
        if not old_course_code:
            errors.append("Original course code is required")
        if not new_course_code:
            new_course_code = old_course_code
        if not new_course_name:
            errors.append("Course name is required")
            
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('admin_views.get_update_course', courseCode=old_course_code))
        
        # Update course in database
        result = update_course(old_course_code, new_course_name, new_course_code, new_course_name)
        
        if result:
            # Update lecturer if provided
            if lecturer_id:
                course = get_course(new_course_code)
                if course:
                    course.lecturer_id = lecturer_id
                    try:
                        db.session.commit()
                    except Exception as e:
                        flash(f"Course updated but failed to assign lecturer: {str(e)}")
            
            flash("Course updated successfully!")
            return redirect(url_for('admin_views.get_courses'))
        else:
            flash("Failed to update course. Please try again.")
            return redirect(url_for('admin_views.get_update_course', courseCode=old_course_code))

# Selects course and removes it from database
@admin_views.route("/deleteCourse/<string:courseCode>", methods=["POST"])
@jwt_required(Admin)
def delete_course_action(courseCode):
    if request.method == 'POST':
        result = delete_course(courseCode)
        if result:
            flash("Course Deleted Successfully!")
        else:
            flash("Failed to delete course.")
        return redirect(url_for('admin_views.get_courses'))

# Commenting out clash-related routes
"""
@admin_views.route("/clashes", methods=["GET"])
@jwt_required(Admin)
def get_clashes_page():
    #for search
    all_assessments=CourseAssessment.query.all()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    searchResults=[]
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        for a in all_assessments:
            if start_date <= a.start_date <= end_date or start_date <= a.end_date <= end_date:
                searchResults.append(a)
    #for table
    assessments=get_clashes()
    return render_template('clashes.html',assessments=assessments,results=searchResults)

@admin_views.route('/clashes/<string:aID>', methods=['GET'])
@jwt_required(Admin)
def get_clash_page(aID):
    ca=get_course_assessment_by_id(aID)
    # ... existing code ...

@admin_views.route('/clashes/<string:aID>/resolve', methods=['POST'])
@jwt_required(Admin)
def resolve_clash(aID):
    ca=get_course_assessment_by_id(aID)
    # ... existing code ...

@admin_views.route("/acceptOverride/<int:aID>", methods=['POST'])
@jwt_required(Admin)
def accept_override(aID):
    ca=get_course_assessment_by_id(aID)
    if ca:
        ca.clash_detected=False
        db.session.commit()
        print("Accepted override.")
    return redirect(url_for('admin_views.get_clashes_page'))

@admin_views.route("/rejectOverride/<int:aID>", methods=['POST'])
@jwt_required(Admin)
def reject_override(aID):
    ca=get_course_assessment_by_id(aID)
    if ca:
        ca.clash_detected=False
        ca.start_date=None
        ca.end_date=None
        ca.start_time=None
        ca.end_time=None
        db.session.commit()
        print("Rejected override.")
    return redirect(url_for('admin_views.get_clashes_page'))
"""

# Staff Management Routes
@admin_views.route('/staffList', methods=['GET'])
@jwt_required(Admin)
def get_staff_list():
    """Get the list of all staff members"""
    staff_list = get_all_staff()
    return render_template('staff.html', staff=staff_list)

@admin_views.route('/newStaff', methods=['GET'])
@jwt_required(Admin)
def get_new_staff_page():
    """Get the page for adding a new staff member"""
    return render_template('addStaff.html')

@admin_views.route('/addNewStaff', methods=['POST'])
@jwt_required(Admin)
def add_staff_action():
    """Add a new staff member"""
    try:
        # Get form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        status = request.form.get('status')
        password = request.form.get('password')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        # Validate data
        if not all([first_name, last_name, status, password, department, faculty]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
        
        all_staff = get_all_staff()
        if all_staff:
            highest_id = max(staff.id for staff in all_staff)
            u_id = highest_id + 1
        else:
            # Start from 1000 if no staff exists
            u_id = 1000
        
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        result = create_staff(str(u_id), email, password, first_name, last_name)
        
        if result:
            flash(f'Staff member added successfully with ID: {u_id}', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Email already in use', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
    except Exception as e:
        flash(f'Error adding staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_new_staff_page'))

@admin_views.route('/modifyStaff/<int:staff_id>', methods=['GET'])
@jwt_required(Admin)
def get_update_staff_page(staff_id):
    """Get the page for updating a staff member"""
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    return render_template('updateStaff.html', staff=staff)

@admin_views.route('/updateStaff', methods=['POST'])
@jwt_required(Admin)
def update_staff_action():
    """Update a staff member"""
    try:
        # Get form data
        staff_id = request.form.get('staffID')
        f_name = request.form.get('firstName')
        l_name = request.form.get('lastName')
        status = request.form.get('status')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        # Validate data
        if not all([staff_id, f_name, l_name, status, department, faculty]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_views.get_update_staff_page', staff_id=staff_id))
        
        # Update staff
        staff = update_staff(staff_id, f_name, l_name, status, department, faculty)
        
        if staff:
            flash('Staff member updated successfully', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Staff member not found', 'error')
            return redirect(url_for('admin_views.get_staff_list'))
    except Exception as e:
        flash(f'Error updating staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_staff_list'))

@admin_views.route('/deleteStaff/<int:staff_id>', methods=['POST'])
@jwt_required(Admin)
def delete_staff_action(staff_id):
    """Delete a staff member"""
    try:
        # Delete staff
        result = delete_staff(staff_id)
        
        if result:
            flash('Staff member deleted successfully', 'success')
        else:
            flash('Staff member not found', 'error')
        
        return redirect(url_for('admin_views.get_staff_list'))
    except Exception as e:
        flash(f'Error deleting staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_staff_list'))

@admin_views.route('/staffCourses/<int:staff_id>', methods=['GET'])
@jwt_required(Admin)
def get_staff_courses_page(staff_id):
    """Get the courses assigned to a staff member"""
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    courses = get_staff_courses(staff_email) # change this whenever u uncomment
    return render_template('staffCourses.html', staff=staff, courses=courses)

@admin_views.route('/assignStaffToCourse/<course_code>', methods=['GET'])
@jwt_required(Admin)
def assign_staff_to_course_page(course_code):
    """Display page for assigning staff to a course"""
    course = get_course(course_code)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('admin_views.get_courses'))
    
    # Get all staff
    all_staff = Staff.query.all()
    
    # Temporarily comment out the get_course_staff call
    # Get staff already assigned to this course
    # assigned_staff = get_course_staff(course_code)
    # assigned_staff_ids = [staff.id for staff in assigned_staff]
    
    # For now, just use the lecturer if available
    assigned_staff_ids = []
    if course.lecturer_id:
        assigned_staff_ids.append(course.lecturer_id)
    
    # Get unique departments for filter
    departments = sorted(list(set([staff.department for staff in all_staff if staff.department])))
    
    return render_template('assignStaffToCourse.html', 
                           course=course, 
                           all_staff=all_staff, 
                           assigned_staff_ids=assigned_staff_ids,
                           departments=departments)

@admin_views.route('/assignCourseStaff/<course_code>/<int:staff_id>', methods=['POST'])
@jwt_required(Admin)
def assign_course_staff(course_code, staff_id):
    """Assign a staff member to a course"""
    course = get_course(course_code)
    staff = Staff.query.get(staff_id)
    
    if not course or not staff:
        flash('Course or staff not found', 'error')
        return redirect(url_for('admin_views.get_courses'))
    
    # Assign staff to course
    result = assign_lecturer(staff_id, course_code)
    
    if result:
        flash(f'Staff {staff.first_name} {staff.last_name} assigned to {course.code}', 'success')
    else:
        flash('Failed to assign staff to course', 'error')
    
    return redirect(url_for('admin_views.assign_staff_to_course_page', course_code=course_code))

@admin_views.route('/removeCourseStaff/<course_code>/<int:staff_id>', methods=['POST'])
@jwt_required(Admin)
def remove_course_staff(course_code, staff_id):
    """Remove a staff member from a course"""
    course = get_course(course_code)
    staff = Staff.query.get(staff_id)
    
    if not course or not staff:
        flash('Course or staff not found', 'error')
        return redirect(url_for('admin_views.get_courses'))
    
    if course.lecturer_id == staff_id:
        course.lecturer_id = None
        try:
            db.session.commit()
            result = True
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            result = False
    else:
        flash('Staff is not assigned as lecturer for this course', 'warning')
        result = False
    
    if result:
        flash(f'Staff {staff.first_name} {staff.last_name} removed from {course.code}', 'success')
    else:
        flash('Failed to remove staff from course', 'error')
    
    return redirect(url_for('admin_views.assign_staff_to_course_page', course_code=course_code))

@admin_views.route('/uploadcourseoverlap', methods=['POST'])
@jwt_required(Admin)
def upload_course_overlap_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        # Check if file is present
        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('uploadFiles.html', message = message) 
        
        # Check if file is a CSV
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('uploadFiles.html', message = message)
            
        # Secure filename
        filename = secure_filename(file.filename)
    
        # Save file to uploads folder
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            # Validate CSV structure
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['course_code', 'course_code2', 'overlap']
                
                # Check if all required columns are present
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('uploadFiles.html', message=message)
            
            # Process the file exactly like in initialize.py
            overlaps_added = 0
            with open(os.path.join('App/uploads', filename)) as matrix_file:
                reader = csv.DictReader(matrix_file)
                for row in reader:
                    if create_cell(row['course_code'], row['course_code2'], row['overlap']):
                        overlaps_added += 1
            
            message = f'<strong>Success!</strong> {overlaps_added} course overlaps have been added to the database.'
            return render_template('uploadFiles.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('uploadFiles.html', message=message)