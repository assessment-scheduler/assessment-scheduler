from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required
from App.database import db
from werkzeug.utils import secure_filename
import os, csv
from datetime import datetime
import uuid

from App.controllers.course import (
    add_Course,
    list_Courses,
    get_course,
    edit_course,
    delete_Course,
    assign_course_to_staff,
    get_course_staff,
    get_course_status
)

from App.controllers.semester import(
    add_sem
)

from App.controllers.courseAssessment import(
    get_course_assessment_by_id,
    get_clashes
)

from App.controllers.staff import (
    add_staff,
    get_all_staff,
    get_staff_by_id,
    update_staff,
    delete_staff,
    get_staff_courses
)

from App.controllers.courseStaff import (
    assign_staff_to_course,
    remove_staff_from_course
)

from App.controllers.admin import get_admin_by_id
from App.controllers.config import get_config
from App.controllers.class_size import get_all_class_sizes, add_class_size
from App.controllers.semester import get_current_semester, create_semester
from App.controllers.course import get_all_courses, get_course_by_code, add_course, update_course, delete_course
from App.controllers.assessment import get_all_assessments
from App.middleware.auth import Admin

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

# Gets Semester Details Page
@admin_views.route('/semester', methods=['GET'])
@jwt_required(Admin)
def get_upload_page():
    return render_template('semester.html')

@admin_views.route('/uploadFiles', methods=['GET'])
@jwt_required(Admin)
def get_uploadFiles_page():
    return render_template('uploadFiles.html')

# Gets Course Listings Page
@admin_views.route('/coursesList', methods=['GET'])
@jwt_required(Admin)
def index():
    return redirect(url_for('admin_views.get_courses'))

# Retrieves semester details and stores it in global variables 
@admin_views.route('/newSemester', methods=['POST'])
@jwt_required(Admin)
def new_semester_action():
    if request.method == 'POST':
        start_date = request.form.get('teachingBegins')
        end_date = request.form.get('teachingEnds')
        sem_num = request.form.get('semester')
        max_assessments = request.form.get('maxAssessments') #used for class detection feature
        add_sem(start_date, end_date, sem_num, max_assessments)

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
            # Retrieves course details from file and stores it in database ie. store course info 
            fpath = 'App/uploads/' + filename
            courses_added = 0
            with open(fpath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create course object
                    course = add_Course(
                        courseCode=row['course_code'], 
                        courseTitle=row['course_name'], 
                        description='', 
                        level=int(row['level']), 
                        semester=int(row['semester']), 
                        aNum=0,
                        department=row['department'],
                        faculty=row['faculty']
                    )
                    if course:
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
    courses = list_Courses()
    
    course_list = []
    for course in courses:
        staff = get_course_staff(course.course_code)
        staff_name = f"{staff.f_name} {staff.l_name}" if staff else None
        status = get_course_status(course)
        
        course_list.append({
            'courseCode': course.course_code,
            'courseTitle': course.course_title,
            'description': course.description,
            'level': course.level,
            'semester': course.semester,
            'department': course.department,
            'faculty': course.faculty,
            'staff_id': course.staff_id,
            'staff_name': staff_name,
            'status': status
        })
    
    return render_template('courses.html', courses=course_list)

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
        description = request.form.get('description')
        level = request.form.get('level')
        semester = request.form.getlist('semester')  # Get all selected semesters as a list
        numAssessments = request.form.get('numAssessments')
        programmes = request.form.get('programmes')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        status = request.form.get('status')
        staff_id = request.form.get('staff_id')
        
        # Convert status to boolean
        active = (status == 'Active')
        
        # Validate required fields
        errors = []
        if not courseCode:
            errors.append("Course code is required")
        if not title:
            errors.append("Title is required")
        if not level:
            errors.append("Level is required")
        if not semester:
            errors.append("At least one semester is required")
        if not numAssessments:
            errors.append("Number of assessments is required")
        if not programmes:
            errors.append("Programmes is required")
        if not department:
            errors.append("Department is required")
        if not faculty:
            errors.append("Faculty is required")
        if not status:
            errors.append("Status is required")
            
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('admin_views.get_new_course'))
        
        # For simplicity, we'll just use the first selected semester
        first_semester = int(semester[0])
        
        # Add course to database
        course = add_Course(courseCode, title, description, int(level), first_semester, numAssessments, department, faculty, staff_id, active)
        
        if course:
            flash("Course added successfully!")
            return redirect(url_for('admin_views.get_courses'))
        else:
            flash("Failed to add course. Please try again.")
            return redirect(url_for('admin_views.get_new_course'))
        
# Gets Update Course Page
@admin_views.route('/modifyCourse/<string:courseCode>', methods=['GET'])
@jwt_required(Admin)
def get_update_course(courseCode):
    course = get_course(courseCode)
    staff_list = Staff.query.all()
    
    # Get course status
    status = get_course_status(course)
    
    return render_template('modifyCourse.html', course=course, staff_list=staff_list, status=status)

# Selects new course details and updates existing course in database
@admin_views.route('/updateCourse', methods=['POST'])
@jwt_required(Admin)
def update_course():
    if request.method == 'POST':
        courseCode = request.form.get('course_code')
        title = request.form.get('title')
        description = request.form.get('description')
        level = request.form.get('level')
        semester = request.form.get('semester')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        status = request.form.get('status')
        staff_id = request.form.get('staff_id')
        
        # Convert status to boolean
        active = (status == 'Active')
        
        # Validate required fields
        errors = []
        if not courseCode:
            errors.append("Course code is required")
        if not title:
            errors.append("Title is required")
        if not level:
            errors.append("Level is required")
        if not semester:
            errors.append("Semester is required")
        if not department:
            errors.append("Department is required")
        if not faculty:
            errors.append("Faculty is required")
        if not status:
            errors.append("Status is required")
            
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('admin_views.get_update_course', courseCode=courseCode))
        
        # Update course in database
        updated_course = edit_course(courseCode, title, description, int(level), int(semester), department, faculty, active, staff_id)
        
        if updated_course:
            flash("Course updated successfully!")
            return redirect(url_for('admin_views.get_courses'))
        else:
            flash("Failed to update course. Please try again.")
            return redirect(url_for('admin_views.get_update_course', courseCode=courseCode))

# Selects course and removes it from database
@admin_views.route("/deleteCourse/<string:courseCode>", methods=["POST"])
@jwt_required(Admin)
def delete_course_action(courseCode):
    if request.method == 'POST':
        course = get_course(courseCode) # Gets selected course
        delete_Course(course)
        print(courseCode, " deleted")
        flash("Course Deleted Successfully!")

    # Redirect to view course listings!   
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
        f_name = request.form.get('firstName')
        l_name = request.form.get('lastName')
        status = request.form.get('status')
        email = f"{f_name.lower()}.{l_name.lower()}@sta.uwi.edu"
        password = request.form.get('password')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        # Validate data
        if not all([f_name, l_name, status, password, department, faculty]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
        
        # Auto-generate staff ID (get the highest current ID and increment by 1)
        all_staff = get_all_staff()
        if all_staff:
            # Find the highest staff ID
            highest_id = max(staff.u_id for staff in all_staff)
            u_id = highest_id + 1
        else:
            # Start from 1000 if no staff exists
            u_id = 1000
        
        # Register staff
        staff = register_staff(f_name, l_name, u_id, status, email, password, department, faculty)
        
        if staff:
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
    
    courses = get_staff_courses(staff_id)
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
    
    # Get staff already assigned to this course
    assigned_staff = get_course_staff(course_code)
    assigned_staff_ids = [staff.u_id for staff in assigned_staff]
    
    # Get unique departments for filter
    departments = sorted(list(set([staff.department for staff in all_staff])))
    
    return render_template(
        'assignStaffToCourse.html', 
        course=course, 
        staff=all_staff, 
        assigned_staff_ids=assigned_staff_ids,
        departments=departments
    )

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
    assignment = add_CourseStaff(staff_id, course_code)
    
    if assignment:
        flash(f'Staff {staff.f_name} {staff.l_name} assigned to {course.course_code}', 'success')
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
    
    # Remove staff from course
    result = remove_CourseStaff(staff_id, course_code)
    
    if result:
        flash(f'Staff {staff.f_name} {staff.l_name} removed from {course.course_code}', 'success')
    else:
        flash('Failed to remove staff from course', 'error')
    
    return redirect(url_for('admin_views.assign_staff_to_course_page', course_code=course_code))