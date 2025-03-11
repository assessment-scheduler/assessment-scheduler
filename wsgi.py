from datetime import date
from typing import List
import click, pytest, sys
from flask import Flask
from flask.cli import AppGroup
from prettytable import PrettyTable
from App.main import create_app
from App.controllers import (
    clear,
    create_user,
    get_all_users_json,
    get_all_users,
    initialize,
    assign_lecturer,
    create_course,
    get_all_course_codes,
    get_all_courses,
    get_course,
    get_all_staff, 
    get_staff_courses,
    get_staff_by_id,
    delete_assessment_by_id,
    get_all_assessments,
    get_assessment_dictionary_by_course,
    create_semester,
    get_all_semesters,
    get_semester,
    get_semester_duration,
    set_active,
    get_all_cells,
    get_cell,
    get_course_row,
    get_course_matrix,
    get_phi_matrix,
    create_admin
    
)
from App.views import (
    compute_schedule,
    schedule_all_assessments,
)

app = create_app()


@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print("database intialized")

@app.cli.command("clear", help="Removes all data from the database")
def drop():
    clear()
    print("database cleared")


user_cli = AppGroup("user", help="User object commands")


@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f"{username} created!")


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == "string":
        print(get_all_users())
    else:
        print(get_all_users_json())


app.cli.add_command(user_cli)

test = AppGroup("test", help="Testing commands")


@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)

staff_cli = AppGroup("staff", help="Staff related functionality")


@staff_cli.command("list", help="Lists all staff members in the database")
def cli_list_staff():
    staff_members = get_all_staff()
    table = PrettyTable()
    table.field_names = ["ID", "Email", "First Name", "Last Name"]
    for staff in staff_members:
        table.add_row([staff.id, staff.email, staff.first_name, staff.last_name])
    print(table)


@staff_cli.command("assign", help="Assigns a course to a staff member")
@click.argument("lecturer_id")
@click.argument("course_code")
def assign_course(lecturer_id: str, course_code: str):
    assign_lecturer(lecturer_id, course_code)


@staff_cli.command("assign", help="assigned a course to a lecturer")
@click.argument("lecturer_id")
@click.argument("course_code")
def assign_course(lecturer_id: str, course_code: str):
    course = get_course(course_code)
    lecturer = get_staff_by_id(lecturer_id)
    if course is None or lecturer is None:
        print(f"Could not assign course {course_code} to lecturer {lecturer_id}")
    else:
        assign_lecturer(lecturer_id, course_code)
        print(f"Course {course_code} assigned to lecturer {lecturer_id}")


@staff_cli.command("courses", help="lists the courses belonging to a lecturer")
@click.argument("lecturer_id")
def list_courses(staff_email: str):
    courses = get_staff_courses(staff_email)
    if courses is None:
        print(f"Could not list courses for lecturer {staff_email}")
    else:
        table = PrettyTable()
        table.field_names = [
            "Course Code",
            "Course Name",
            "Lecturer First Name",
            "Lecturer Last Name",
        ]
        for course in courses:
            table.add_row(
                [
                    course.code,
                    course.name,
                    course.lecturer.first_name,
                    course.lecturer.last_name,
                ]
            )
        print(table)


app.cli.add_command(staff_cli)


course_cli = AppGroup("courses", help="Course and Assessment related functionality")


@course_cli.command("create_course", help="Create a course")
@click.argument("course_code")
@click.argument("course_name")
def cli_create_course(course_code, course_name):
    create_course(course_code, course_name)
    print(f"{course_code} created!")


@course_cli.command("list", help="Lists all courses in the database")
def cli_list_courses():
    courses = get_all_courses()
    table = PrettyTable()
    table.field_names = ["Course Code", "Course Name", "Lecturer"]
    for course in courses:
        lecturer_email = course.lecturer.email if course.lecturer else "N/A"
        table.add_row([course.code, course.name, lecturer_email])
    print(table)


app.cli.add_command(course_cli)

assessment_cli = AppGroup("assessments", help="Assessment related functionality")


@assessment_cli.command("list", help="Lists all assessments for a course")
def list_all_assessments():
    assessments = get_all_assessments()
    table = PrettyTable()
    table.field_names = ["Course Code", "Assessment Name", "Weight", "Scheduled for"]
    for assessment in assessments:
        table.add_row(
            [
                assessment.course_code,
                assessment.name,
                f"{assessment.percentage}%",
                assessment.scheduled,
            ]
        )
    print(table)


@assessment_cli.command(
    "by_course", help="returns all assessments for a course in json format"
)
@click.argument("course_code")
def print_assessment_jsons(course_code):
    course = get_course(course_code)
    if course is None:
        print("Course not found")
    else:
        assessments = get_assessment_dictionary_by_course(course_code)
        if assessments is None:
            print("No assessments found")
        else:
            print(assessments)

@assessment_cli.command("delete", help="Deletes an assessment by course code and name")
@click.argument("id")
def delete_assessment_command(id):
    result = delete_assessment_by_id(id)
    if result:
        print("Assessment deleted successfully")
    else:
        print("Failed to delete assessment")



# @assessment_cli.command("compile", help = "creates a large structure containing all assessments for all courses")
# def compile_assessments():
#     print(compile_course_data())

app.cli.add_command(assessment_cli)

overlap_cli = AppGroup("overlap", help="Course Overlap related functionality")


@overlap_cli.command("list", help="Lists all course overlaps")
def list_overlaps():
    overlaps = get_all_cells()
    table = PrettyTable()
    table.field_names = [
        "Course Code 1",
        "Course Code 2",
        "Overlap",
    ]  # Adjust fields as necessary
    for overlap in overlaps:
        table.add_row(
            [overlap.code1, overlap.code2, overlap.student_count]
        )  # Fixed attribute names
    print(table)


@overlap_cli.command("row", help="section of the matrix for a particular row")
@click.argument("course_code")
def print_row(course_code: str):
    print(get_course_row(course_code))


@overlap_cli.command("get", help="section of the matrix for a particular row")
@click.argument("course_code1")
@click.argument("course_code2")
def print_row(course_code1: str, course_code2: str):
    cell = get_cell(course_code1, course_code2)
    print(cell)


@overlap_cli.command("matrix", help="prints the course matrix")
def print_class_matrix():
    course_list: List[str] = get_all_course_codes()
    print(get_course_matrix(course_list))


@overlap_cli.command("phi_matrix", help="prints the phi matrix")
def print_phi_matrix() -> None:
    course_list: List[str] = get_all_course_codes()
    matrix: List[List[int]] = get_course_matrix(course_list)
    phi_matrix: List[List[int]] = get_phi_matrix(matrix)
    print(phi_matrix)


app.cli.add_command(overlap_cli)

semester_cli = AppGroup("semester", help="Semester related functionality")


@semester_cli.command("create", help="Create a semester")
@click.argument("start_date")
@click.argument("end_date")
@click.argument("sem_num", type=int)
@click.argument("max_assessments", type=int)
def create_semester_command(
    start_date: str, end_date: str, sem_num: int, max_assessments: int
) -> None:
    iso_start_date: date = date.fromisoformat(start_date)
    iso_end_date: date = date.fromisoformat(end_date)
    success: bool = create_semester(
        iso_start_date, iso_end_date, sem_num, max_assessments
    )
    if success:
        print(
            f"Semester {sem_num} created successfully from {start_date} to {end_date}"
        )
    else:
        print(
            f"Failed to create semester {sem_num}. It may overlap with an existing semester."
        )


@semester_cli.command("list", help="List all semesters")
def list_semesters() -> None:
    semesters = get_all_semesters()
    table = PrettyTable()
    table.field_names = [
        "ID",
        "Start Date",
        "End Date",
        "Semester Number",
        "Max Assessments",
        "Constraint Value",
        "Active",
    ]
    for semester in semesters:
        table.add_row(
            [
                semester.id,
                semester.start_date,
                semester.end_date,
                semester.sem_num,
                semester.max_assessments,
                semester.constraint_value,
                semester.active,
            ]
        )
    print(table)


@semester_cli.command("duration", help="Get the duration of a semester")
@click.argument("semester_id", type=int)
def get_semester_duration_command(semester_id: int) -> None:
    duration = get_semester_duration(semester_id)
    if duration == -1:
        print(f"Semester with id {semester_id} not found.")
    else:
        print(f"The duration of semester {semester_id} is {duration} days.")


@semester_cli.command("activate", help="Activates a semester by ID")
@click.argument("semester_id", type=int)
def activate_semester(semester_id: int):

    semester = get_semester(semester_id)
    if semester is None:
        print("Semester does not exist")
        return False

    success: bool = set_active(semester.id)
    print(f"Semester {semester.id} set to active!")
    return True


app.cli.add_command(semester_cli)

kris_cli = AppGroup("kris", help="Kris related functionality")


@kris_cli.command("solve", help="Uses the kris model to schedule assessments")
def schedule_assessments_command():
    schedule = compute_schedule()
    schedule_all_assessments(schedule)


app.cli.add_command(kris_cli)

admin_cli = AppGroup("admin", help="Admin related functionality")


@admin_cli.command("create", help="Creates an admin")
@click.argument("admin_id")
@click.argument("email")
@click.argument("password")
def create_admin_command(admin_id, email, password):
    success = create_admin(admin_id, email, password)
    if success:
        print(f"Admin {admin_id} created successfully!")
    else:
        print(f"Failed to create admin {admin_id}")


@admin_cli.command("list", help="Lists all admins in the database")
def list_admins_command():
    admins = Admin.query.all()

    table = PrettyTable()
    table.field_names = ["Admin ID", "Email"]
    for admin in admins:
        table.add_row([admin.id, admin.email])
    print(table)


app.cli.add_command(admin_cli)

# The WSGI acts as test environment
