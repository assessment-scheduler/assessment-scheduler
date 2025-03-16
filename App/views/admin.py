from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os, csv
from ..database import db
from ..models import Admin, Staff, Course, Assessment
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
from ..controllers.auth import admin_required

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    # Gather statistics for the dashboard
    try:
        # Get count of all courses
        courses_count = db.session.query(Course).count()
        
        # Get count of all staff
        staff_count = db.session.query(Staff).count()
        
        # Get count of all assessments
        assessments_count = db.session.query(Assessment).count()
        
        # Get count of scheduled assessments
        scheduled_count = db.session.query(Assessment).filter(Assessment.scheduled.isnot(None)).count()
        
        stats = {
            'courses': courses_count,
            'staff': staff_count,
            'assessments': assessments_count,
            'scheduled': scheduled_count
        }
    except Exception as e:
        print(f"Error gathering dashboard statistics: {str(e)}")
        stats = {
            'courses': 0,
            'staff': 0,
            'assessments': 0,
            'scheduled': 0
        }
    
    return render_template('admin_dashboard.html', stats=stats)

@admin_views.route('/semester', methods=['GET'])
@admin_required
def get_upload_page():
    semesters = get_all_semesters()
    return render_template('semester.html', semesters=semesters)

@admin_views.route('/upload_files', methods=['GET'])
@admin_required
def get_upload_files_page():
    return render_template('upload_files.html')

@admin_views.route('/new_semester', methods=['GET'])
@admin_required
def get_new_semester_form():
    return render_template('add_semester.html')

@admin_views.route('/add_semester', methods=['POST'])
@admin_required
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

@admin_views.route('/update_semester/<int:semester_id>', methods=['GET'])
@admin_required
def get_update_semester(semester_id):
    semester = get_semester(semester_id)
    if not semester:
        flash('Semester not found', 'error')
        return redirect(url_for('admin_views.get_upload_page'))
    
    return render_template('add_semester.html', semester=semester)

@admin_views.route('/delete_semester/<int:semester_id>', methods=['POST'])
@admin_required
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

@admin_views.route('/set_active_semester/<int:semester_id>', methods=['POST'])
@admin_required
def set_active_semester(semester_id):
    result = set_active(semester_id)
    
    if result:
        flash('Semester set as active', 'success')
    else:
        flash('Failed to set semester as active', 'error')
    
    return redirect(url_for('admin_views.get_upload_page'))

@admin_views.route('/new_semester', methods=['POST'])
@admin_required
def new_semester_action():
    if request.method == 'POST':
        start_date = request.form.get('teachingBegins')
        end_date = request.form.get('teachingEnds')
        sem_num = request.form.get('semester')
        max_assessments = request.form.get('maxAssessments')
        create_semester(start_date, end_date, sem_num, max_assessments)

        return render_template('upload_files.html')  

@admin_views.route('/staff', methods=['GET'])
@admin_required
def get_staff_list():
    staff_list = get_all_staff()
    return render_template('staff.html', staff=staff_list)

@admin_views.route('/new_staff', methods=['GET'])
@admin_views.route('/create_staff', methods=['GET'])
@admin_required
def get_new_staff_page():
    return render_template('add_staff.html')

@admin_views.route('/add_staff', methods=['POST'])
@admin_required
def add_staff_action():
    try:
        staff_id = request.form.get('id')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        faculty = request.form.get('faculty')
        
        if not all([staff_id,first_name, last_name, staff_id, email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
        
        if create_staff(staff_id, email, password, first_name, last_name, department, faculty):
            flash(f'Staff {first_name} {last_name} added successfully!', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Failed to add staff', 'error')
            return redirect(url_for('admin_views.get_new_staff_page'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_new_staff_page'))

@admin_views.route('/edit_staff/<int:staff_id>', methods=['GET'])
@admin_required
def get_update_staff_page(staff_id):
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    return render_template('update_staff.html', staff=staff)

@admin_views.route('/update_staff', methods=['POST'])
@admin_required
def update_staff_action():
    try:
        staff_id = request.form.get('staffID')
        email = request.form.get('email')
        password = request.form.get('password')
        f_name = request.form.get('firstName')
        l_name = request.form.get('lastName')
        department = request.form.get('department')
        faculty = request.form.get('faculty')

        staff = update_staff(staff_id, email, f_name, l_name, department, faculty)
        if password:
            change_password(email, password)

        if staff:
            flash('Staff member updated successfully', 'success')
            return redirect(url_for('admin_views.get_staff_list'))
        else:
            flash('Staff member not found', 'error')
            return redirect(url_for('admin_views.get_staff_list'))
    except Exception as e:
        flash(f'Error updating staff member: {str(e)}', 'error')
        return redirect(url_for('admin_views.get_staff_list'))

@admin_views.route('/delete_staff/<int:staff_id>', methods=['POST'])
@admin_required
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

@admin_views.route('/staff_courses/<int:staff_id>', methods=['GET'])
@admin_required
def get_staff_courses_page(staff_id):
    staff = get_staff_by_id(staff_id)
    if not staff:
        flash('Staff member not found', 'error')
        return redirect(url_for('admin_views.get_staff_list'))
    
    courses = get_staff_courses(staff.email)
    return render_template('staff_courses.html', staff=staff, courses=courses)

@admin_views.route('/uploadassessments', methods=['POST'])
@admin_required
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
                    message = f'Error: CSV file must contain the following columns: {", ".join(required_columns)}'
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
            
            message = f'Success! {assessments_added} assessments have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'Error: {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadcells', methods=['POST'])
@admin_required
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
                    message = f'Error: CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            # Process the cells file
            cells_added = 0
            with open(os.path.join('App/uploads', filename)) as cells_file:
                reader = csv.DictReader(cells_file)
                for row in reader:
                    if create_cell(row['course_code'], row['course_code2'], int(row['overlap'])):
                        cells_added += 1
            
            message = f'Success! {cells_added} cells have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'Error: {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadsemesters', methods=['POST'])
@admin_required
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
                    message = f'Error: CSV file must contain the following columns: {", ".join(required_columns)}'
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
            
            message = f'Success! {semesters_added} semesters have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'Error: {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadstaff', methods=['POST'])
@admin_required
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
                    message = f'Error: CSV file must contain the following columns: {", ".join(required_columns)}'
                    return render_template('upload_files.html', message=message)
            
            staff_added = 0
            with open(os.path.join('App/uploads', filename)) as staff_file:
                reader = csv.DictReader(staff_file)
                for row in reader:
                    if create_staff(row['id'], row['email'], row['password'], row['first_name'], row['last_name']):
                        staff_added += 1
            
            message = f'Success! {staff_added} staff members have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'Error: {str(e)}'
            return render_template('upload_files.html', message=message)

@admin_views.route('/uploadlecturerassignments', methods=['POST'])
@admin_required
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
                    message = f'Error: CSV file must contain the following columns: {", ".join(required_columns)}'
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
                message = f'Partial Success: {assignments_added} lecturer assignments have been added to the database. Failed to assign: {", ".join(failed_assignments)}'
            else:
                message = f'Success! {assignments_added} lecturer assignments have been added to the database.'
            return render_template('upload_files.html', message=message)
        except Exception as e:
            message = f'Error: {str(e)}'
            return render_template('upload_files.html', message=message)
