from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os, csv
from ..database import db
from ..models import Admin, Staff
from ..controllers import (
    change_password,
    create_assessment,
    get_course,
    get_all_courses,
    create_course,
    update_course,
    delete_course,
    assign_lecturer,
    create_cell,
    get_all_staff,
    get_staff_by_id,
    update_staff,
    delete_staff,
    get_staff_courses,
    create_staff,
    get_all_semesters,
    get_semester,
    create_semester,
    set_active,
    parse_date
)

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')
## working


@admin_views.route('/semester', methods=['GET'])
@jwt_required(Admin)
def get_upload_page():
    semesters = get_all_semesters()
    return render_template('semester.html', semesters=semesters)
## working


@admin_views.route('/upload_files', methods=['GET'])
@jwt_required(Admin)
def get_upload_files_page():
    return render_template('upload_files.html')
## working

@admin_views.route('/get_courses', methods=['GET'])
@jwt_required(Admin)
def get_courses():
    courses = get_all_courses()
    return render_template('courses.html', courses=courses)
## working

@admin_views.route('/new_semester', methods=['GET'])
@jwt_required(Admin)
def get_new_semester_form():
    return render_template('add_semester.html')
## working

@admin_views.route('/add_semester', methods=['POST'])
@jwt_required(Admin)
def add_new_semester():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        sem_num = int(request.form.get('sem_num'))
        max_assessments = int(request.form.get('max_assessments'))
        constraint_value = int(request.form.get('constraint_value'))
        
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        if isinstance(start_date, str) or isinstance(end_date, str):
            flash(f'Invalid date format: {start_date if isinstance(start_date, str) else end_date}', 'error')
            return redirect(url_for('admin_views.get_new_semester_form'))
        
        if start_date >= end_date:
            flash('Start date must be before end date', 'error')
            return redirect(url_for('admin_views.get_new_semester_form'))
        
        result = create_semester(start_date, end_date, sem_num, max_assessments, constraint_value)
        
        if result:
            flash('Semester added successfully', 'success')
        else:
            flash('Failed to add semester', 'error')
        
        return redirect(url_for('admin_views.get_upload_page'))
## working

@admin_views.route('/update_semester/<int:semester_id>', methods=['GET'])
@jwt_required(Admin)
def get_update_semester(semester_id):
    semester = get_semester(semester_id)
    if not semester:
        flash('Semester not found', 'error')
        return redirect(url_for('admin_views.get_upload_page'))
    
    return render_template('add_semester.html', semester=semester)
## working

@admin_views.route('/delete_semester/<int:semester_id>', methods=['POST'])
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
## working


@admin_views.route('/set_active_semester/<int:semester_id>', methods=['POST'])
@jwt_required(Admin)
def set_active_semester(semester_id):
    result = set_active(semester_id)
    
    if result:
        flash('Semester set as active', 'success')
    else:
        flash('Failed to set semester as active', 'error')
    
    return redirect(url_for('admin_views.get_upload_page'))
## working

@admin_views.route('/new_semester', methods=['POST'])
@jwt_required(Admin)
def new_semester_action():
    if request.method == 'POST':
        start_date = request.form.get('teachingBegins')
        end_date = request.form.get('teachingEnds')
        sem_num = request.form.get('semester')
        max_assessments = request.form.get('maxAssessments')
        create_semester(start_date, end_date, sem_num, max_assessments)

        return render_template('upload_files.html')  
## working

@admin_views.route('/upload_course', methods=['POST'])
@jwt_required(Admin)
def upload_course_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message = message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['course_code', 'course_name']
                
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            courses_added = 0
            with open(os.path.join('App/uploads', filename)) as course_file:
                reader = csv.DictReader(course_file)
                for row in reader:
                    if create_course(row['course_code'], row['course_name']):
                        courses_added += 1
            
            message = f'<strong>Success!</strong> {courses_added} courses have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)
## working

@admin_views.route('/new_course', methods=['GET'])
@jwt_required(Admin)
def get_new_course():
    staff_list = Staff.query.all()
    return render_template('add_course.html', staff_list=staff_list)  
## working

@admin_views.route('/new_course', methods=['POST'])
@jwt_required(Admin)
def add_course_action():
    if request.method == 'POST':
        courseCode = request.form.get('course_code')
        title = request.form.get('title')
        lecturer_id = request.form.get('lecturer_id') or None
        
        errors = []
        if not courseCode:
            errors.append("Course code is required")
        if not title:
            errors.append("Title is required")
            
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('admin_views.get_new_course'))
        
        result = create_course(courseCode, title)
        
        if result:
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
## working

@admin_views.route('/update_course/<string:courseCode>', methods=['GET'])
@jwt_required(Admin)
def get_update_course(courseCode):
    course = get_course(courseCode)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for('admin_views.get_courses'))
        
    staff_list = Staff.query.all()
    
    return render_template('modify_course.html', course=course, staff_list=staff_list)
## working


@admin_views.route('/update_course', methods=['POST'])
@jwt_required(Admin)
def update_course_action():
    if request.method == 'POST':
        old_course_code = request.form.get('old_course_code')
        new_course_code = request.form.get('course_code')
        new_course_name = request.form.get('title')
        lecturer_id = request.form.get('lecturer_id') or None
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
        
        result = update_course(old_course_code, new_course_name, new_course_code, new_course_name)
        if result:
            if lecturer_id:
                assign_lecturer(lecturer_id, new_course_code)
            flash("Course updated successfully!")
            return redirect(url_for('admin_views.get_courses'))
        else:
            flash("Failed to update course. Please try again.")
            return redirect(url_for('admin_views.get_update_course', courseCode=old_course_code))
## working

@admin_views.route("/delete_course/<string:courseCode>", methods=["POST"])
@jwt_required(Admin)
def delete_course_action(courseCode):
        result = delete_course(courseCode)
        if result:
            flash("Course Deleted Successfully!")
        else:
            flash("Failed to delete course.")
        return redirect(url_for('admin_views.get_courses'))
## working


@admin_views.route('/staff', methods=['GET'])
@jwt_required(Admin)
def get_staff_list():
    staff_list = get_all_staff()
    return render_template('staff.html', staff=staff_list)
## working


@admin_views.route('/create_staff', methods=['GET'])
@jwt_required(Admin)
def get_new_staff_page():
    return render_template('add_staff.html')
## working

@admin_views.route('/add_staff', methods=['POST'])
@jwt_required(Admin)
def add_staff_action():
    try:
        staff_id = request.form.get('id')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([staff_id,first_name, last_name, staff_id, email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
        
        if create_staff(staff_id,email,password,first_name,last_name):
            flash(f'Staff {first_name} {last_name} added successfully!', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Failed to add staff', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_new_staff_page'))
## working


@admin_views.route('/edit_staff/<int:staff_id>', methods=['GET'])
@jwt_required(Admin)
def get_update_staff_page(staff_id):
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    return render_template('update_staff.html', staff=staff)
## working

@admin_views.route('/update_staff', methods=['POST'])
@jwt_required(Admin)
def update_staff_action():
    try:
        staff_id = request.form.get('staffID')
        email = request.form.get('email')
        password = request.form.get('password')
        f_name = request.form.get('firstName')
        l_name = request.form.get('lastName')

        staff = update_staff(staff_id, email, f_name, l_name)
        change_password(email,password)

        if staff:
            flash('Staff member updated successfully', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Staff member not found', 'error')
            return redirect(url_for('admin_views.get_staff_list'))
    except Exception as e:
        flash(f'Error updating staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
## working


@admin_views.route('/delete_staff/<int:staff_id>', methods=['POST'])
@jwt_required(Admin)
def delete_staff_action(staff_id):
    try:
        result = delete_staff(staff_id)
        
        if result:
            flash('Staff member deleted successfully', 'success')
        else:
            flash('Staff member not found', 'error')
        
        return redirect(url_for('admin_views.get_staff_list'))
    except Exception as e:
        flash(f'Error deleting staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
## working


@admin_views.route('/staff_courses/<int:staff_id>', methods=['GET'])
@jwt_required(Admin)
def get_staff_courses_page(staff_id):
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    courses = get_staff_courses(staff.email)
    return render_template('staff_courses.html', staff=staff, courses=courses)
## working

@admin_views.route('/uploadassessments', methods=['POST'])
@jwt_required(Admin)
def upload_assessments_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message=message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['course_code', 'assessment_name', 'percentage', 'start_week', 'start_day', 'end_week', 'end_day', 'proctored']
                
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            assessments_added = 0
            with open(os.path.join('App/uploads', filename)) as assessments_file:
                reader = csv.DictReader(assessments_file)
                for row in reader:
                    if create_assessment(
                        row['course_code'],
                        row['assessment_name'],
                        int(row['percentage']),
                        int(row['start_week']),
                        int(row['start_day']),
                        int(row['end_week']),
                        int(row['end_day']),
                        int(row['proctored'])
                    ):
                        assessments_added += 1
            
            message = f'<strong>Success!</strong> {assessments_added} assessments have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadcells', methods=['POST'])
@jwt_required(Admin)
def upload_cells_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message = message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['course_code', 'course_code2', 'overlap']
                
                if not all(col in header for col in required_columns):  
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            # Process the cells file
            cells_added = 0
            with open(os.path.join('App/uploads', filename)) as cells_file:
                reader = csv.DictReader(cells_file)
                for row in reader:
                    if create_cell(row['course_code'], row['course_code2'], int(row['overlap'])):
                        cells_added += 1
            
            message = f'<strong>Success!</strong> {cells_added} cells have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadsemesters', methods=['POST'])
@jwt_required(Admin)
def upload_semesters_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message = message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['start_date', 'end_date', 'sem_num', 'max_assessments', 'constraint_value', 'active']
                
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            semesters_added = 0
            with open(os.path.join('App/uploads', filename)) as semesters_file:
                reader = csv.DictReader(semesters_file)
                for row in reader:
                    if create_semester(
                        row['start_date'],
                        row['end_date'],
                        int(row['sem_num']),
                        int(row['max_assessments']),
                        int(row['constraint_value']),
                        bool(row['active'])
                    ):
                        semesters_added += 1
            
            message = f'<strong>Success!</strong> {semesters_added} semesters have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadstaff', methods=['POST'])
@jwt_required(Admin)
def upload_staff_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message = message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['id', 'email', 'password', 'first_name', 'last_name']
                
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            staff_added = 0
            with open(os.path.join('App/uploads', filename)) as staff_file:
                reader = csv.DictReader(staff_file)
                for row in reader:
                    if create_staff(row['id'], row['email'], row['password'], row['first_name'], row['last_name']):
                        staff_added += 1
            
            message = f'<strong>Success!</strong> {staff_added} staff members have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadlecturerassignments', methods=['POST'])
@jwt_required(Admin)
def upload_lecturer_assignments_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('upload_files.html', message = message) 
        
        if not file.filename.lower().endswith('.csv'):
            message = 'Only CSV files are allowed!'
            return render_template('upload_files.html', message = message)
            
        filename = secure_filename(file.filename)
    
        file.save(os.path.join('App/uploads', filename)) 
        
        try:
            with open(os.path.join('App/uploads', filename), 'r') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)
                required_columns = ['lecturer_id', 'course_code']
                
                if not all(col in header for col in required_columns):
                    message = f'<strong>Error:</strong> CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            assignments_added = 0
            failed_assignments = []
            with open(os.path.join('App/uploads', filename)) as assignments_file:
                reader = csv.DictReader(assignments_file)
                for row in reader:
                    if assign_lecturer(row['lecturer_id'], row['course_code']):
                        assignments_added += 1
                    else:
                        failed_assignments.append(f"{row['lecturer_id']} to {row['course_code']}")
            
            if failed_assignments:
                message = f'<strong>Partial Success:</strong> {assignments_added} lecturer assignments have been added to the database. Failed to assign: {", ".join(failed_assignments)}'
            else:
                message = f'<strong>Success!</strong> {assignments_added} lecturer assignments have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'<strong>Error:</strong> {str(e)}'
            return render_template('upload_files.html', message=message)
