from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
from ..controllers.auth import admin_required
from ..controllers.semester import (
    get_all_semesters,
    get_semester,
    create_semester,
    update_semester,
    add_course_to_semester,
    remove_course_from_semester,
    set_active
)
from ..controllers.course import get_all_courses
from ..models.assessment import Assessment

semester_views = Blueprint('semester_views', __name__, template_folder ='../templates')

@semester_views.route('/semester')
@admin_required
def semester_list():
    semesters = get_all_semesters()
    return render_template('semester.html', semesters=semesters)

@semester_views.route('/add_course_to_semester/<int:semester_id>/<course_code>', methods=['GET', 'POST'])
@admin_required
def add_course_to_semester_route(semester_id: int, course_code: str):
    success = add_course_to_semester(semester_id, course_code)
    if success:
        flash(f"Course {course_code} was successfully added to semester {semester_id}", "success")
    else:
        flash(f"Failed to add course {course_code} to semester {semester_id}", "error")
    
    return redirect(url_for('semester_views.semester_courses_route', semester_id=semester_id))

@semester_views.route('/remove_course_from_semester/<int:semester_id>/<course_code>', methods=['POST'])
@admin_required
def remove_course_from_semester_route(semester_id: int, course_code: str):
    success = remove_course_from_semester(semester_id, course_code)
    if success:
        flash(f"Course {course_code} was successfully removed from semester {semester_id}", "success")
    else:
        flash(f"Failed to remove course {course_code} from semester {semester_id}", "error")
    
    return redirect(url_for('semester_views.semester_courses_route', semester_id=semester_id))

@semester_views.route('/update_semester/<int:semester_id>', methods=['GET', 'POST'])
@admin_required
def update_semester_route(semester_id: int):
    semester = get_semester(semester_id)
    if not semester:
        flash("Semester not found.", "error")
        return redirect(url_for('semester_views.semester_list'))
    
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            sem_num = int(request.form.get('sem_num'))
            max_assessments = int(request.form.get('max_assessments'))
            constraint_value = int(request.form.get('constraint_value'))
            active = bool(int(request.form.get('active', 0)))
            solver_type = request.form.get('solver_type')
            
            selected_courses = request.form.get('selected_courses', '')
            course_codes = selected_courses.split(',') if selected_courses else []
            
            success = update_semester(
                semester_id, start_date, end_date, sem_num,
                max_assessments, constraint_value, active, 
                solver_type, course_codes
            )
            
            if success:
                flash("Semester updated successfully!", "success")
                return redirect(url_for('semester_views.semester_list'))
            else:
                flash("Failed to update semester. The dates may overlap with another semester.", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
    
    all_courses = get_all_courses()
    return render_template('update_semester.html', semester=semester, all_courses=all_courses)

@semester_views.route('/add_course_to_semester/<int:semester_id>', methods=['POST'])
@admin_required
def add_course_from_modal(semester_id: int):
    course_code = request.form.get('course_code')
    if not course_code:
        flash("No course selected", "error")
        return redirect(url_for('semester_views.semester_courses_route', semester_id=semester_id))
        
    success = add_course_to_semester(semester_id, course_code)
    if success:
        flash(f"Course {course_code} was successfully added to semester {semester_id}", "success")
    else:
        flash(f"Failed to add course {course_code} to semester {semester_id}", "error")
    
    return redirect(url_for('semester_views.semester_courses_route', semester_id=semester_id))

@semester_views.route('/semester_courses/<int:semester_id>')
@admin_required
def semester_courses_route(semester_id: int):
    semester = get_semester(semester_id)
    if not semester:
        flash("Semester not found.", "error")
        return redirect(url_for('semester_views.semester_list'))
    
    all_courses = get_all_courses()
    return render_template('semester_courses.html', semester=semester, all_courses=all_courses)

@semester_views.route('/set_active_semester/<int:semester_id>', methods=['POST'])
@admin_required
def set_active_semester(semester_id: int):
    success = set_active(semester_id)
    if success:
        flash(f"Semester {semester_id} was successfully set as active", "success")
        
        # Get semester to check if it has courses
        semester = get_semester(semester_id)
        if semester and semester.course_assignments:
            # Check if there are any unscheduled assessments
            unscheduled_count = 0
            for assignment in semester.course_assignments:
                if assignment.course:
                    unscheduled_assessments = Assessment.query.filter_by(
                        course_code=assignment.course_code,
                        scheduled=None
                    ).count()
                    unscheduled_count += unscheduled_assessments
            
            if unscheduled_count > 0:
                flash(f"Started auto-scheduling {unscheduled_count} unscheduled assessments for {len(semester.course_assignments)} courses", "info")
                flash("This process may take a moment to complete. Check the calendar page when complete.", "info")
            else:
                flash("All assessments for this semester are already scheduled. No auto-scheduling needed.", "info")
        else:
            flash("No courses found in this semester. Please add courses to schedule assessments.", "warning")
    else:
        flash(f"Failed to set semester {semester_id} as active", "error")
    
    return redirect(url_for('semester_views.semester_list')) 