from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from App.controllers import Course, CourseAssessment
from App.models import Admin, Staff, Config
from App.database import db
from werkzeug.utils import secure_filename
import os, csv
from datetime import datetime

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
    get_clashes,
    get_course_assessment_by_id
)

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
        else:
            # Secure filename
            filename = secure_filename(file.filename)
        
            # Save file to uploads folder
            file.save(os.path.join('App/uploads', filename)) 
            
            # Retrieves course details from file and stores it in database ie. store course info 
            fpath = 'App/uploads/' + filename
            with open(fpath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    #create object
                    course = add_Course(courseCode=row['Course Code'], courseTitle=row['Course Title'], description=row['Course Description'], level=int(row['Level']), semester=int(row['Semester']), aNum=int(row['Assessment No.']))

            # Redirect to view course listings!   
            return redirect(url_for('admin_views.get_courses'))    
            
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