from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
from typing import List
import traceback
from ..controllers import (
    get_active_semester,
    get_semester_duration,
    get_staff_by_email,
    get_staff_courses,
    is_course_lecturer,
    get_user_by_email,
    create_assessment,
    delete_assessment_by_id,
    update_assessment,
    get_assessment_by_id,
    get_assessments_by_lecturer,
    get_assessments_by_course,
    get_course,
    get_all_assessments,
    staff_required
)

assessment_views = Blueprint(
    "assessment_views", __name__, template_folder="../templates"
)


@assessment_views.route("/assessments", methods=["GET"])
@staff_required
def get_assessments_page():
    email = get_jwt_identity()
    user = get_staff_by_email(email)
    assessments = get_assessments_by_lecturer(user.email)
    return render_template("assessments.html", course_assessments=assessments)


@assessment_views.route("/add_assessment", methods=["GET"])
@staff_required
def get_add_assessments_page():
    email = get_jwt_identity()
    staff_courses = get_staff_courses(email)
    semester = get_active_semester()
    
    selected_course = request.args.get('course')
    
    return render_template(
        "add_assessment.html", 
        courses=staff_courses, 
        semester=semester,
        selected_course=selected_course
    )


@assessment_views.route("/add_assessment", methods=["POST"])
@staff_required
def add_assessments_action():
    try:
        course_code = request.form.get("course_code")
        assessment_name = request.form.get("name")
        percentage = float(request.form.get("percentage"))
        start_week = int(request.form.get("start_week"))
        start_day = int(request.form.get("start_day"))
        end_week = int(request.form.get("end_week"))
        end_day = int(request.form.get("end_day"))
        proctored = 1 if request.form.get("proctored") == "on" else 0

        email = get_jwt_identity()
        user = get_user_by_email(email)
        if not is_course_lecturer(user.id, course_code):
            flash("You do not have access to this course", "error")
            return redirect(url_for("assessment_views.get_assessments_page"))

        assessment = create_assessment(
            course_code,
            assessment_name,
            percentage,
            start_week,
            start_day,
            end_week,
            end_day,
            proctored,
        )
        if assessment:
            flash("Assessment added successfully", "success")
            return redirect(url_for("assessment_views.get_assessments_page"))
        else:
            flash("Failed to add assessment. Please check your inputs.", "error")
            return redirect(url_for("assessment_views.get_add_assessments_page"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))


@assessment_views.route("/update_assessment/<string:id>", methods=["GET"])
@staff_required
def get_modify_assessments_page(id):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    assessment = get_assessment_by_id(id)

    if not assessment:
        flash("Assessment not found", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))

    if not is_course_lecturer(user.id, assessment.course_code):
        flash(
            "You do not have permission to modify assessments for this course", "error"
        )
        return redirect(url_for("assessment_views.get_assessments_page"))

    semester = get_active_semester()
    if not semester:
        flash("No active semester found. Please contact an administrator.", "warning")

    return render_template(
        "update_assessment.html", assessment=assessment, semester=semester
    )


@assessment_views.route("/update_assessment/<string:id>", methods=["POST"])
@staff_required
def modify_assessment(id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(id)

        if not assessment:
            flash("Assessment not found", "error")
            return redirect(url_for("assessment_views.get_assessments_page"))

        if not is_course_lecturer(user.id, assessment.course_code):
            flash(
                "You do not have permission to modify assessments for this course",
                "error",
            )
            return redirect(url_for("assessment_views.get_assessments_page"))

        assessment_name = request.form.get("name")
        percentage = int(request.form.get("percentage"))
        start_week = int(request.form.get("start_week"))
        start_day = int(request.form.get("start_day"))
        end_week = int(request.form.get("end_week"))
        end_day = int(request.form.get("end_day"))
        proctored = 1 if request.form.get("proctored") is not None else 0

        assessment_result = update_assessment(
            id,
            assessment_name,
            percentage,
            start_week,
            start_day,
            end_week,
            end_day,
            proctored,
        )
        if assessment_result:
            flash("Assessment updated successfully", "success")
            return redirect(url_for("assessment_views.get_assessments_page"))
        else:
            flash("Failed to update assessment. Please check your inputs.", "error")
            return redirect(
                url_for("assessment_views.get_modify_assessments_page", id=id)
            )
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))


@assessment_views.route(
    "/delete_assessment/<int:assessment_id>", methods=["POST", "GET"]
)
@staff_required
def delete_assessment_action(assessment_id):
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)

        if not assessment:
            flash("Assessment not found", "error")
            return redirect(url_for("assessment_views.get_assessments_page"))

        if not is_course_lecturer(user.id, assessment.course_code):
            flash(
                "You do not have permission to delete assessments for this course",
                "error",
            )
            return redirect(url_for("assessment_views.get_assessments_page"))

        result = delete_assessment_by_id(int(assessment_id))
        if result:
            flash("Assessment deleted successfully", "success")
        else:
            flash("Failed to delete assessment", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))


@assessment_views.route("/assessments/<course_code>", methods=["GET"])
@staff_required
def get_course_details(course_code):
    email = get_jwt_identity()
    user = get_user_by_email(email)

    if not is_course_lecturer(user.id, course_code):
        flash("You do not have access to this course", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))

    course = get_course(course_code)
    if not course:
        flash("Course not found", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))

    assessments = get_assessments_by_course(course.code)
    return render_template(
        "course_details.html", course=course, assessments=assessments, staff=user
    )


@assessment_views.route("/update_assessment_schedule", methods=["POST"])
@staff_required
def update_assessment_schedule():
    try:
        assessment_id = request.form.get("id")
        assessment_date = datetime.strptime(
            request.form.get("assessment_date"), "%Y-%m-%d"
        ).date()

        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)

        if not assessment:
            flash("Assessment not found", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

        if not is_course_lecturer(user.id, assessment.course_code):
            flash("You do not have permission to schedule assessments for this course", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

        semester = get_active_semester()
        if not semester:
            flash("No active semester found", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

        days_diff = (assessment_date - semester.start_date).days
        week = (days_diff // 7) + 1
        day = (days_diff % 7) + 1

        result = update_assessment(
            assessment_id,
            assessment.name,
            assessment.percentage,
            week,
            day,
            week,
            day,
            assessment.proctored,
            assessment_date,
        )

        if result:
            flash("Assessment scheduled successfully", "success")
            return redirect(url_for("assessment_views.get_calendar_page"))
        else:
            flash("Failed to schedule assessment", "error")
            return redirect(url_for("assessment_views.get_schedule_assessment_page", id=assessment_id))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_calendar_page"))


@assessment_views.route("/schedule_assessment/<string:id>", methods=["GET"])
@staff_required
def get_schedule_assessment_page(id):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    assessment = get_assessment_by_id(id)

    if not assessment:
        flash("Assessment not found", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))

    if not is_course_lecturer(user.id, assessment.course_code):
        flash(
            "You do not have permission to schedule assessments for this course",
            "error",
        )
        return redirect(url_for("assessment_views.get_assessments_page"))

    semester = get_active_semester()
    if not semester:
        flash("No active semester found. Please contact an administrator.", "warning")

    return render_template(
        "schedule_assessment.html", assessment=assessment, semester=semester
    )


@assessment_views.route("/calendar", methods=["GET"])
@staff_required
def get_calendar_page():
    email = get_jwt_identity()
    staff = get_staff_by_email(email)

    all_assessments = get_all_assessments() or []

    user_assessments = get_assessments_by_lecturer(staff.email) or []

    staff_exams = []
    scheduled_assessments = []
    unscheduled_assessments = []

    for assessment in all_assessments:
        try:
            assessment_dict = {
                "id": assessment.id,
                "name": assessment.name,
                "course_code": assessment.course_code,
                "percentage": assessment.percentage,
                "start_week": assessment.start_week,
                "start_day": assessment.start_day,
                "end_week": assessment.end_week,
                "end_day": assessment.end_day,
                "proctored": assessment.proctored,
                "scheduled": (
                    assessment.scheduled.isoformat() if assessment.scheduled else None
                ),
            }

            if assessment.scheduled:
                if isinstance(assessment_dict["scheduled"], str):
                    if "T" in assessment_dict["scheduled"]:
                        assessment_dict["scheduled"] = assessment_dict[
                            "scheduled"
                        ].split("T")[0]

                scheduled_assessments.append(assessment_dict)

        except Exception as e:
            print(f"Error processing assessment {assessment.id}: {str(e)}")

    for assessment in user_assessments:
        try:
            assessment_dict = {
                "id": assessment.id,
                "name": assessment.name,
                "course_code": assessment.course_code,
                "percentage": assessment.percentage,
                "start_week": assessment.start_week,
                "start_day": assessment.start_day,
                "end_week": assessment.end_week,
                "end_day": assessment.end_day,
                "proctored": assessment.proctored,
                "scheduled": (
                    assessment.scheduled.isoformat() if assessment.scheduled else None
                ),
            }

            if assessment_dict.get("scheduled") and isinstance(
                assessment_dict["scheduled"], str
            ):
                if "T" in assessment_dict["scheduled"]:
                    assessment_dict["scheduled"] = assessment_dict["scheduled"].split(
                        "T"
                    )[0]

            staff_exams.append(assessment_dict)

            if not assessment.scheduled:
                unscheduled_assessments.append(assessment_dict)
        except Exception as e:
            print(f"Error processing user assessment {assessment.id}: {str(e)}")

    staff_course_objects = get_staff_courses(email) or []
    staff_courses = []

    for course in staff_course_objects:
        try:
            course_dict = {
                "code": course.code,
                "name": course.name,
                "level": course.code[4] if len(course.code) > 4 else "",
            }
            staff_courses.append(course_dict)
        except Exception as e:
            print(f"Error processing course {course.code}: {str(e)}")

    courses = staff_courses
    other_exams = staff_exams

    active_semester = get_active_semester()
    if not active_semester:
        flash("No active semester found. Please contact an administrator.", "warning")
        semester = {}
    else:
        semester = {
            "id": active_semester.id,
            "start_date": active_semester.start_date.isoformat(),
            "end_date": active_semester.end_date.isoformat(),
            "sem_num": active_semester.sem_num,
            "max_assessments": active_semester.max_assessments,
            "constraint_value": active_semester.constraint_value,
            "active": active_semester.active,
        }

        if isinstance(semester.get("start_date"), str):
            semester["start_date"] = semester["start_date"].split("T")[0]
        if isinstance(semester.get("end_date"), str):
            semester["end_date"] = semester["end_date"].split("T")[0]

    return render_template(
        "calendar.html",
        staff_exams=staff_exams,
        other_exams=other_exams,
        staff_courses=staff_courses,
        courses=courses,
        semester=semester,
        scheduled_assessments=scheduled_assessments,
        unscheduled_assessments=unscheduled_assessments
    )


@assessment_views.route("/autoschedule", methods=["POST"])
@staff_required
def autoschedule_assessments():
    try:
        active_semester = get_active_semester()
        if not active_semester:
            flash("No active semester found. Please set an active semester first.", "error")
            return redirect(url_for('assessment_views.get_calendar_page'))

        all_assessments = get_all_assessments()
        unscheduled = [a for a in all_assessments if not a.scheduled]
        
        if not unscheduled:
            flash("No unscheduled assessments found to schedule.", "info")
            return redirect(url_for('assessment_views.get_calendar_page'))

        semester_weeks = get_semester_duration(active_semester.id)
        max_slots = semester_weeks * 5 * active_semester.max_assessments
        
        if len(unscheduled) > max_slots:
            flash(f"Too many assessments ({len(unscheduled)}) for available slots ({max_slots}).", "error")
            flash(f"Please try one of the following:", "error")
            flash(f"1. Increase the maximum assessments per day (currently {active_semester.max_assessments})", "error")
            flash(f"2. Reduce the number of assessments by scheduling some manually", "error")
            flash(f"3. Extend the semester duration (currently {semester_weeks} weeks)", "error")
            return redirect(url_for('assessment_views.get_calendar_page'))
        
        if len(unscheduled) > 100:
            flash(f"Attempting to schedule {len(unscheduled)} assessments. This may take a while...", "warning")

        # Use the new solver framework instead of the old functions
        solver = active_semester.get_solver()
        schedule = solver.solve()
        
        if not schedule:
            flash("Could not find a valid schedule. This could be due to:", "error")
            flash("1. Too many assessments for the semester duration", "error")
            flash("2. Maximum assessments per day is too restrictive", "error")
            flash("3. Conflicting assessment time windows", "error")
            flash("Try adjusting these parameters or reducing the number of assessments.", "error")
            return redirect(url_for('assessment_views.get_calendar_page'))

        flash("Successfully scheduled all assessments! The calendar has been updated.", "success")
        return redirect(url_for('assessment_views.get_calendar_page'))

    except Exception as e:
        print(f"Error in autoschedule: {str(e)}")
        traceback.print_exc()
        flash(f"An unexpected error occurred while scheduling assessments: {str(e)}", "error")
        flash(f"Please try again with fewer assessments or contact support if the problem persists.", "error")
        return redirect(url_for('assessment_views.get_calendar_page'))


@assessment_views.route("/unschedule_assessment", methods=["POST"])
@staff_required
def unschedule_assessment():
    try:
        assessment_id = request.form.get("id")
        email = get_jwt_identity()
        user = get_user_by_email(email)
        assessment = get_assessment_by_id(assessment_id)

        if not assessment:
            flash("Assessment not found", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

        if not is_course_lecturer(user.id, assessment.course_code):
            flash("You do not have permission to unschedule assessments for this course", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

        result = update_assessment(
            assessment_id,
            assessment.name,
            assessment.percentage,
            assessment.start_week,
            assessment.start_day,
            assessment.end_week,
            assessment.end_day,
            assessment.proctored,
            None 
        )

        if result:
            flash("Assessment unscheduled successfully", "success")
            return redirect(url_for("assessment_views.get_calendar_page"))
        else:
            flash("Failed to unschedule assessment", "error")
            return redirect(url_for("assessment_views.get_calendar_page"))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_calendar_page"))


@assessment_views.route("/unschedule_all_assessments", methods=["POST"])
@staff_required
def unschedule_all_assessments():
    try:
        email = get_jwt_identity()
        user = get_user_by_email(email)
        
        assessments = get_assessments_by_lecturer(user.email)
        
        scheduled_count = 0
        
        if isinstance(assessments, dict):
            for course_code, course_assessments in assessments.items():
                for assessment in course_assessments:
                    if assessment.scheduled:
                        scheduled_count += 1
                        update_assessment(
                            assessment.id,
                            assessment.name,
                            assessment.percentage,
                            assessment.start_week,
                            assessment.start_day,
                            assessment.end_week,
                            assessment.end_day,
                            assessment.proctored,
                            None
                        )
        else:
            for assessment in assessments:
                if assessment.scheduled:
                    scheduled_count += 1
                    update_assessment(
                        assessment.id,
                        assessment.name,
                        assessment.percentage,
                        assessment.start_week,
                        assessment.start_day,
                        assessment.end_week,
                        assessment.end_day,
                        assessment.proctored,
                        None
                    )
        
        if scheduled_count > 0:
            flash(f"Successfully unscheduled {scheduled_count} assessments", "success")
        else:
            flash("No scheduled assessments found", "info")
            
        return redirect(url_for("assessment_views.get_calendar_page"))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_calendar_page"))


@assessment_views.route("/unschedule_all_system_assessments", methods=["POST"])
@staff_required
def unschedule_all_system_assessments():
    try:
        assessments = get_all_assessments()
        scheduled_count = 0
        
        for assessment in assessments:
            if assessment.scheduled:
                scheduled_count += 1
                update_assessment(
                    assessment.id,
                    assessment.name,
                    assessment.percentage,
                    assessment.start_week,
                    assessment.start_day,
                    assessment.end_week,
                    assessment.end_day,
                    assessment.proctored,
                    None
                )
        
        if scheduled_count > 0:
            flash(f"Successfully unscheduled {scheduled_count} assessments across all courses", "success")
        else:
            flash("No scheduled assessments found in the system", "info")
            
        return redirect(url_for("assessment_views.get_calendar_page"))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("assessment_views.get_calendar_page"))