from App.models.staff import Staff
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import timedelta
from typing import List
from ..models.assessment import Assessment
from ..controllers import (
    get_course_matrix,
    get_phi_matrix,
    print_schedule,
    solve_stage1,
    solve_stage2,
    get_assessment_dictionary_by_course,
    schedule_assessment,
    get_all_course_codes,
    get_all_courses,
    get_active_semester,
    get_semester_duration,
)


def compile_course_data() -> List:
    course_assessment_list: list = []
    courses: list = get_all_courses()
    for course in courses:
        assessments: List[Assessment] = get_assessment_dictionary_by_course(course.code)
        course_assessment_list.append(assessments)
    return course_assessment_list


def compile_class_matrix() -> List[List[int]]:
    course_list: List[str] = get_all_course_codes()
    matrix: List[List[int]] = get_course_matrix(course_list)
    return matrix


def compute_schedule():
    try:
        semester = get_active_semester()
        if semester is None:
            print("No active semester found")
            return None

        courses: List = compile_course_data()
        if not courses:
            print("No courses found")
            return None

        matrix: List[List[int]] = compile_class_matrix()
        phi_matrix: List[List[int]] = get_phi_matrix(matrix)

        k: int = get_semester_duration(semester.id)
        d = semester.max_assessments
        M: int = semester.constraint_value

        if k <= 0 or d <= 0 or M <= 0:
            print(f"Invalid parameters: k={k}, d={d}, M={M}")
            return None

        U_star, stage1_status, _ = solve_stage1(courses, matrix, k, M)
        
        if not stage1_status or U_star is None:
            print("Stage 1 failed to find an optimal solution")
            return None
            
        schedule, Y_star, probability = solve_stage2(
            courses, matrix, phi_matrix, U_star, k, d, M
        )
        
        if not schedule:
            print("Stage 2 failed to generate a schedule")
            return None
            
        print_schedule(schedule, U_star, d, probability)
        return schedule
        
    except Exception as e:
        import traceback
        print("Error in compute_schedule:", str(e))
        print("Traceback:", traceback.format_exc())
        return None


def schedule_all_assessments(schedule):
    try:
        if not schedule:
            print("No schedule provided")
            return False
            
        semester = get_active_semester()
        if not semester:
            print("Could not schedule assessments, no active semester")
            return False
            
        success = True
        for row in schedule:
            try:
                k, week, day, code, assessment_info = row
                name = assessment_info.split("-")[0]
                schedule_date = semester.start_date + timedelta(days=(k - 1))
                if not schedule_assessment(semester, schedule_date, code, name):
                    print(f"Failed to schedule assessment: {code}-{name}")
                    success = False
            except Exception as row_error:
                print(f"Error scheduling row {row}: {str(row_error)}")
                success = False
                
        return success
        
    except Exception as e:
        import traceback
        print("Error in schedule_all_assessments:", str(e))
        print("Traceback:", traceback.format_exc())
        return False


kris_views = Blueprint("kris", __name__, template_folder="../templates")


@kris_views.route("/schedule", methods=["POST"])
@jwt_required(Staff)
def get_schedule_action():
    schedule = compute_schedule()
    schedule_all_assessments(schedule)
    return redirect(url_for("assessment.assessments"))


@kris_views.route("/solve", methods=["GET", "POST"])
@jwt_required(Staff)
def solve_schedule():
    schedule = compute_schedule()
    if schedule:
        return redirect(url_for("kris.solve_done", schedule_data="solved"))
    else:
        return redirect(url_for("admin_views.get_admin_dashboard_page"))


@kris_views.route("/solve-done", methods=["GET", "POST"])
@jwt_required(Staff)
def solve_done():
    flash("Schedule solved successfully", "success")
    return redirect(url_for("admin_views.get_admin_dashboard_page"))