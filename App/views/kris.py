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
from ..controllers.auth import staff_required


def compile_course_data() -> List:
    course_assessment_list: list = []
    courses: list = get_all_courses()
    for course in courses:
        assessments: List[Assessment] = get_assessment_dictionary_by_course(course.code)
        if assessments and 'assessments' in assessments:
            filtered_assessments = {
                'code': assessments['code'],
                'assessments': [a for a in assessments['assessments'] if not a.get('scheduled')]
            }
            if filtered_assessments['assessments']:
                course_assessment_list.append(filtered_assessments)
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
            print("No unscheduled assessments found")
            return None

        # Log the number of assessments being scheduled
        total_assessments = sum(len(course['assessments']) for course in courses)
        print(f"Attempting to schedule {total_assessments} assessments")

        matrix: List[List[int]] = compile_class_matrix()
        phi_matrix: List[List[int]] = get_phi_matrix(matrix)

        k: int = get_semester_duration(semester.id)
        d = semester.max_assessments
        M: int = semester.constraint_value

        if k <= 0 or d <= 0 or M <= 0:
            print(f"Invalid scheduling parameters: semester duration={k} weeks, max assessments per day={d}, constraint value={M}")
            return None

        # Log scheduling constraints
        print(f"Scheduling constraints: {total_assessments} assessments over {k} weeks, max {d} per day")
        if total_assessments > (k * 5 * d):  # 5 days per week
            print(f"Warning: More assessments ({total_assessments}) than available slots ({k * 5 * d})")

        U_star, stage1_status, stage1_info = solve_stage1(courses, matrix, k, M)
        
        if not stage1_status or U_star is None:
            print(f"Stage 1 failed: Could not find valid assessment spacing.")
            print(f"This usually means either:")
            print(f"1. Too many assessments for the semester duration")
            print(f"2. Conflicting time windows between assessments")
            print(f"3. The constraint value (M={M}) is too restrictive")
            return None
            
        schedule, Y_star, probability = solve_stage2(
            courses, matrix, phi_matrix, U_star, k, d, M
        )
        
        if not schedule:
            print("Stage 2 failed: Could not generate a valid schedule.")
            print(f"This usually means either:")
            print(f"1. Maximum assessments per day (d={d}) is too low")
            print(f"2. Assessment spacing constraints cannot be satisfied")
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
        scheduled_count = 0
        failed_assessments = []
        
        for row in schedule:
            try:
                k, week, day, code, assessment_info = row
                name = assessment_info.split("-")[0]
                schedule_date = semester.start_date + timedelta(days=(k - 1))
                if schedule_assessment(semester, schedule_date, code, name):
                    scheduled_count += 1
                else:
                    print(f"Failed to schedule assessment: {code}-{name}")
                    failed_assessments.append(f"{code}-{name}")
                    success = False
            except Exception as row_error:
                print(f"Error scheduling row {row}: {str(row_error)}")
                failed_assessments.append(f"{row}")
                success = False
        
        print(f"Scheduled {scheduled_count} out of {len(schedule)} assessments")
        if failed_assessments:
            print(f"Failed to schedule {len(failed_assessments)} assessments: {', '.join(failed_assessments[:5])}")
            if len(failed_assessments) > 5:
                print(f"... and {len(failed_assessments) - 5} more")
                
        return success
        
    except Exception as e:
        import traceback
        print("Error in schedule_all_assessments:", str(e))
        print("Traceback:", traceback.format_exc())
        return False


kris_views = Blueprint("kris", __name__, template_folder="../templates")


@kris_views.route("/schedule", methods=["POST"])
@staff_required
def get_schedule_action():
    schedule = compute_schedule()
    schedule_all_assessments(schedule)
    return redirect(url_for("assessment_views.get_assessments_page"))