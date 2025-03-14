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
    semester = get_active_semester()
    if semester is None:
        print("No active semester found")
        return None

    courses: List = compile_course_data()
    matrix: List[List[int]] = compile_class_matrix()
    phi_matrix: List[List[int]] = get_phi_matrix(matrix)

    k: int = get_semester_duration(semester.id)
    d = semester.max_assessments
    M: int = semester.constraint_value

    U_star, _, _ = solve_stage1(courses, matrix, k, M)
    schedule, Y_star, probability = solve_stage2(
        courses, matrix, phi_matrix, U_star, k, d, M
    )
    print_schedule(schedule, U_star, d, probability)
    return schedule


def schedule_all_assessments(schedule):
    semester = get_active_semester()
    if not semester:
        print("Could not schedule assessments, no active semester")
        return
    for row in schedule:
        k, week, day, code, assessment_info = row
        name = assessment_info.split("-")[0]
        schedule_date = semester.start_date + timedelta(days=(k - 1))
        schedule_assessment(semester, schedule_date, code, name)


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