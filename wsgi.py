from datetime import date
from typing import List
import click, pytest, sys
from flask import Flask
from flask.cli import AppGroup
from prettytable import PrettyTable
from App.main import create_app
from App.models import *
from App.controllers import *
from App.views import *
from App.controllers.kris import solve_stage1, solve_stage2
from App.controllers.courseoverlap import get_phi_matrix
from App.views.kris import compile_course_data, compile_class_matrix

app = create_app()


@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print("database intialized")

@app.cli.command("clear", help="Removes all data from the database")
def drop():
    clear()
    create_admin(101101, 'admin', 'adminpass')
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
    table.field_names = ["ID", "Email", "First Name", "Last Name", "Department", "Faculty", "Courses"]
    for staff in staff_members:
        courses = [assignment.course.code for assignment in staff.course_assignments]
        table.add_row([staff.id, staff.email, staff.first_name, staff.last_name, staff.department, staff.faculty, ", ".join(courses)])
    print(table)


@staff_cli.command("assign", help="Assigns a course to a staff member")
@click.argument("lecturer_id")
@click.argument("course_code")
def assign_course(lecturer_id: str, course_code: str):
    success = assign_lecturer(lecturer_id, course_code)
    if success:
        print(f"Course {course_code} assigned to lecturer {lecturer_id}")
    else:
        print(f"Failed to assign course {course_code} to lecturer {lecturer_id}")


@staff_cli.command("courses", help="Lists the courses belonging to a lecturer")
@click.argument("lecturer_id")
def list_courses(lecturer_id: str):
    courses = get_staff_courses(lecturer_id)
    if courses is None:
        print(f"Could not list courses for lecturer {lecturer_id}")
    else:
        table = PrettyTable()
        table.field_names = ["Course Code", "Course Name", "Level", "Credits", "Semester"]
        for course in courses:
            table.add_row([
                course.code,
                course.name,
                course.level or "N/A",
                course.credits or "N/A",
                course.semester or "N/A"
            ])
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
    table.field_names = ["Course Code", "Course Name", "Level", "Credits", "Semester", "Lecturers"]
    for course in courses:
        lecturers = [assignment.lecturer.first_name + " " + assignment.lecturer.last_name 
                    for assignment in course.lecturer_assignments]
        table.add_row([
            course.code, 
            course.name, 
            course.level or "N/A",
            course.credits or "N/A",
            course.semester or "N/A",
            ", ".join(lecturers) or "N/A"
        ])
    print(table)


@course_cli.command("lecturers", help="Lists all lecturers for a course")
@click.argument("course_code")
def list_course_lecturers(course_code: str):
    lecturers = get_course_lecturers(course_code)
    if lecturers is None:
        print(f"Could not find lecturers for course {course_code}")
    else:
        table = PrettyTable()
        table.field_names = ["ID", "First Name", "Last Name", "Email", "Department", "Faculty"]
        for lecturer in lecturers:
            table.add_row([
                lecturer.id,
                lecturer.first_name,
                lecturer.last_name,
                lecturer.email,
                lecturer.department or "N/A",
                lecturer.faculty or "N/A"
            ])
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
    ]
    for overlap in overlaps:
        table.add_row(
            [overlap.code1, overlap.code2, overlap.student_count]
        )
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
def kris_solve():
    """Solve the assessment scheduling problem using the Kris model."""
    try:
        print("\n=== Starting Kris Model Data Preparation ===")
        
        courses = compile_course_data()
        print(f"\nTotal courses with assessments: {len(courses)}")
        print("\nCourse and assessment details:")
        for course in courses:
            print(f"\n{course['code']}:")
            for assessment in course['assessments']:
                print(f"  - {assessment['name']} ({assessment['percentage']}%)")
                print(f"    Start: Week {assessment['start_week']}, Day {assessment['start_day']}")
                print(f"    End: Week {assessment['end_week']}, Day {assessment['end_day']}")
                print(f"    Proctored: {'Yes' if assessment['proctored'] else 'No'}")
        
        matrix = compile_class_matrix()
        phi_matrix = get_phi_matrix(matrix)
        print("\nCourse overlap matrix:")
        for row in matrix:
            print(row)
        
        semester = get_active_semester()
        if semester is None:
            print("No active semester found")
            return None
            
        k = get_semester_duration(semester.id)
        d = semester.max_assessments
        M = semester.constraint_value
        
        print(f"\nScheduling parameters:")
        print(f"- Semester duration (k): {k} days")
        print(f"- Maximum assessments per day (d): {d}")
        print(f"- Constraint value (M): {M}")
        
        print("\n=== Starting Kris Model Solving ===")
        
        print("\nSolving Stage 1...")
        U_star, solver, x = solve_stage1(courses, matrix, k, M)
        print(f"Stage 1 solved with U* = {U_star}")
        
        print("\nSolving Stage 2...")
        schedule, Y_star, probability = solve_stage2(courses, matrix, phi_matrix, U_star, k, d, M)
        print(f"Stage 2 solved with Y* = {Y_star}")
        print(f"Probability: {probability:.3f}")
        
        print("\n=== Kris Model Solution ===")
        print(f"Total assessments scheduled: {len(schedule)}")
        print(f"Maximum assessments per day: {d}")
        print(f"Total weeks: {k // 7}")
        print(f"First stage utility (U*): {U_star}")
        print(f"Second stage utility (Y*): {Y_star}")
        print(f"Probability: {probability:.3f}")
        
        print("\nDetailed schedule:")
        for entry in schedule:
            k, week, day, course, assessment = entry
            print(f"  Week {week}, Day {day}: {course}-{assessment}")
        
        return schedule
        
    except Exception as e:
        print(f"Error in Kris model: {str(e)}")
        raise


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

course_lecturer_cli = AppGroup("course_lecturer", help="Test CourseLecturer bridge table functionality")

@course_lecturer_cli.command("assign", help="Assign a lecturer to a course")
@click.argument("lecturer_id")
@click.argument("course_code")
def test_assign_lecturer(lecturer_id, course_code):
    result = assign_lecturer(lecturer_id, course_code)
    if result:
        print(f"Successfully assigned lecturer {lecturer_id} to course {course_code}")
    else:
        print(f"Failed to assign lecturer {lecturer_id} to course {course_code}")

@course_lecturer_cli.command("list_for_course", help="List all lecturers for a course")
@click.argument("course_code")
def test_list_lecturers_for_course(course_code):
    lecturers = get_course_lecturers(course_code)
    if not lecturers:
        print(f"No lecturers found for course {course_code}")
    else:
        table = PrettyTable()
        table.field_names = ["ID", "Email", "First Name", "Last Name", "Department"]
        for lecturer in lecturers:
            table.add_row([
                lecturer.id,
                lecturer.email,
                lecturer.first_name,
                lecturer.last_name,
                lecturer.department or "N/A"
            ])
        print(f"Lecturers for course {course_code}:")
        print(table)

@course_lecturer_cli.command("list_for_lecturer", help="List all courses for a lecturer")
@click.argument("lecturer_id")
def test_list_courses_for_lecturer(lecturer_id):
    from App.controllers.course import get_lecturer_assignments
    from App.controllers.staff import get_staff_by_id
    
    staff = get_staff_by_id(lecturer_id)
    if not staff:
        print(f"No staff found with ID {lecturer_id}")
        return
    
    assignments = get_lecturer_assignments(lecturer_id)
    
    if not assignments:
        print(f"No courses found for lecturer {lecturer_id}")
        return
    
    print(f"Courses for lecturer {staff.first_name} {staff.last_name}:")
    
    table = PrettyTable()
    table.field_names = ["Code", "Name", "Level", "Credits", "Semester"]
    
    for assignment in assignments:
        table.add_row([
            assignment['course_code'],
            assignment['course_name'],
            assignment['level'] or "N/A",
            assignment['credits'] or "N/A",
            assignment['semester'] or "N/A"
        ])
    
    print(table)

@course_lecturer_cli.command("count", help="Count course-lecturer assignments")
def count_course_lecturer_assignments():
    from App.controllers.course import get_course_lecturer_count
    
    count = get_course_lecturer_count()
    print(f"Total course-lecturer assignments: {count}")

@course_lecturer_cli.command("delete", help="Remove a lecturer from a course using the controller function")
@click.argument("lecturer_id")
@click.argument("course_code")
def remove_lecturer_command(lecturer_id, course_code):
    from App.controllers.course import remove_lecturer
    
    result = remove_lecturer(lecturer_id, course_code)
    if result:
        print(f"Successfully removed lecturer {lecturer_id} from course {course_code}")
    else:
        print(f"Failed to remove lecturer {lecturer_id} from course {course_code}")

@course_lecturer_cli.command("remove", help="Remove a lecturer from a course")
@click.argument("lecturer_id")
@click.argument("course_code")
def remove_lecturer_from_course(lecturer_id, course_code):
    from App.models.course_lecturer import CourseLecturer
    from App.models import db
    
    assignment = CourseLecturer.query.filter_by(
        staff_id=lecturer_id,
        course_code=course_code
    ).first()
    
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        print(f"Successfully removed lecturer {lecturer_id} from course {course_code}")
    else:
        print(f"No assignment found for lecturer {lecturer_id} and course {course_code}")

app.cli.add_command(course_lecturer_cli)

# The WSGI acts as test environment
