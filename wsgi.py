import click
import pytest
import sys
from flask import Flask
from flask.cli import AppGroup
from App.database import db, get_migrate
from App.main import create_app
from App.models import User, Staff, Course, Assessment, Programme, Admin, ClassSize, SolverConfig
from App.controllers import create_user, get_all_users_json, get_all_users, initialize, Course
from App.models.solver import LPSolver
from App.controllers.lp import create_sample_problem, solve_lp_problem
from App.models.importer import load_courses, load_assessments, load_class_sizes

from App.controllers.course import (
    add_Course
)

# Get migration instance

# This commands file allows you to create convenient CLI commands for testing controllers!
app = create_app()
migrate = get_migrate(app)

# Add this after the app is created but before the lp_cli commands
lp_cli = app.cli.group('lp', help='Linear programming commands')
schedule_cli = app.cli.group('schedule', help='Scheduling commands')

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    # db.init_app(app)
    db.create_all()
    # bob = Staff("bob", "test", 300456, "Lecturer 1", "bob@gmail.com", "bobpass")
    bob = Admin(u_ID=999, email="bob@gmail.com", password="bobpass")
    db.session.add(bob)
    db.session.commit()
    print(bob)
    print('Database initialized')

# This command retrieves all staff objects
@app.cli.command('get-users')
def get_users():
    staff = Staff.query.all()
    for s in staff:
        print(s.to_json())
    print('End of staff objects')

# This command creates all the Assessment objects
@app.cli.command("asm")
def load_Asm():
    db.create_all()
    asm1 = Assessment(category='EXAM')
    db.session.add(asm1)
    db.session.commit()

    asm2 = Assessment(category='ASSIGNMENT')
    db.session.add(asm2)
    db.session.commit()

    asm3 = Assessment(category='QUIZ')
    db.session.add(asm3)
    db.session.commit()

    asm4 = Assessment(category='PROJECT')
    db.session.add(asm4)
    db.session.commit()

    asm5 = Assessment(category='DEBATE')
    db.session.add(asm5)
    db.session.commit()

    asm6 = Assessment(category='PRESENTATION')
    db.session.add(asm6)
    db.session.commit()

    asm7 = Assessment(category='ORALEXAM')
    db.session.add(asm7)
    db.session.commit()

    asm8 = Assessment(category='PARTICIPATION')
    db.session.add(asm8)
    db.session.commit()
    print('All assessments added')

# This command creates all the Programme objects
@app.cli.command("pgr")
def load_Pgr():
    db.create_all()
    pgr1 = Programme(p_name='Computer Science Major')
    db.session.add(pgr1)
    db.session.commit()

    pgr2 = Programme(p_name='Computer Science Minor')
    db.session.add(pgr2)
    db.session.commit()

    pgr3 = Programme(p_name='Computer Science Special')
    db.session.add(pgr3)
    db.session.commit()

    pgr4 = Programme(p_name='Information Technology Major')
    db.session.add(pgr4)
    db.session.commit()

    pgr5 = Programme(p_name='Information Technology Minor')
    db.session.add(pgr5)
    db.session.commit()

    pgr6 = Programme(p_name='Information Technology Special')
    db.session.add(pgr6)
    db.session.commit()

    print('All programmes added')  

# This command assigns courses to staff
@app.cli.command("add-course")
@click.argument("staff_ID")
def assign_course(staff_ID):
    bob = Staff.query.filter_by(u_ID=staff_ID).first()
  
    if not bob:
        print(f'Staff with ID: {staff_ID} not found!')
        return
    
    bob.coursesAssigned = ["COMP1601", "COMP1602", "COMP1603"]
    db.session.add(bob)
    db.session.commit()
    print(bob)
    print('Courses added')

# Load course data from CSV file
@app.cli.command("load-courses")
def load_course_data():
    with open('courses.csv') as file:  # CSV files are used for spreadsheets
        reader = csv.DictReader(file)
        for row in reader: 
            new_course = Course(courseCode=row['courseCode'], courseTitle=row['courseTitle'], description=row['description'], 
                                level=row['level'], semester=row['semester'], preReqs=row['preReqs'], p_ID=row['p_ID'])  # Create object
            db.session.add(new_course) 
        db.session.commit()  # Save all changes OUTSIDE the loop
    print('Database initialized')

@lp_cli.command("sample_problem", help="Create and solve a sample linear problem")
def sample_problem_command():
    problem = LinearProblem(
        name="Sample Problem",
        description="Maximize 3x1 + 2x2 subject to constraints",
        objective="max",
        objective_function="3x1 + 2x2"
    )
    
    # Add variables
    x1 = LPVariable("x1", lower_bound=0)
    x2 = LPVariable("x2", lower_bound=0)
    problem.add_variable(x1)
    problem.add_variable(x2)
    
    # Add constraints with relation operators
    const1 = LPConstraint("x1 + x2 <= 10", "<=")  # Fixed: Added <= and proper RHS
    const2 = LPConstraint("2x1 + x2 <= 16", "<=")  # Fixed: Added <= and proper RHS
    problem.add_constraint(const1)
    problem.add_constraint(const2)
    
    # Create solver and solve
    solver = LPSolver(problem)
    result = solver.solve()
    
    # Print problem and solution
    print("Problem Definition:")
    problem.print_problem()
    print("\nSolution:")
    print(f"Status: {result['status']}")
    if result['status'] == 'OPTIMAL':
        print(f"Objective Value: {result['objective_value']}")
        print("Variable Values:")
        for var_name, value in result['variables'].items():
            print(f"  {var_name}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

@lp_cli.command("solve", help="Solve a linear programming problem")
def solve_problem_command():
    problem = create_sample_problem()
    result = solve_lp_problem(problem)
    
    # Print results
    print("\nProblem Definition:")
    print("=" * 50)
    problem.print_problem()
    
    print("\nSolution:")
    print("=" * 50)
    if result['status'] == 'OPTIMAL':
        print(f"Status: {result['status']}")
        print(f"Objective Value: {result['objective_value']}")
        print("\nVariable Values:")
        for var_name, value in result['variables'].items():
            print(f"  {var_name} = {value}")
    else:
        print(f"Status: {result['status']}")
        print(f"Error: {result['error']}")

@schedule_cli.command("solve", help="Solve the scheduling problem using database data")
def solve_schedule():
    # Get or create config
    config = SolverConfig.query.first() or SolverConfig()
    db.session.add(config)
    
    # Get all courses and convert to solver format
    courses = Course.query.all()
    courses_list = []
    
    for course in courses:
        course_data = {
            'assessments': [
                {
                    'name': a.name,
                    'percentage': int(a.percentage),
                    'start_week': a.start_week,
                    'start_day': a.start_day,
                    'end_week': a.end_week,
                    'end_day': a.end_day,
                    'proctored': int(a.proctored)
                } for a in course.assessments
            ]
        }
        courses_list.append(course_data)
    
    # Build class sizes matrix
    n = len(courses)
    c = [[0 for _ in range(n)] for _ in range(n)]
    
    for i, course in enumerate(courses):
        for class_size in course.class_sizes:
            j = next(idx for idx, c in enumerate(courses) 
                    if c.id == class_size.other_course_id)
            c[i][j] = class_size.size
    
    # Generate phi matrix
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]
    
    # Solve using config parameters
    U_star, solver, x = solve_stage1(courses_list, c, 
                                   config.semester_days,
                                   config.large_m)
    
    schedule, Y_star, probability = solve_stage2(courses_list, c, phi, U_star,
                                               config.semester_days,
                                               config.min_spacing,
                                               config.large_m)
    
    # Save solution
    solution = ScheduleSolution(
        config_id=config.id,
        U_star=U_star,
        Y_star=Y_star,
        probability=probability
    )
    db.session.add(solution)
    
    # Save scheduled assignments
    for day, week, day_of_week, course_name, assessment_name in schedule:
        assessment = Assessment.query.filter_by(name=assessment_name.split('-')[0]).first()
        if assessment:
            scheduled = ScheduledAssignment(
                solution_id=solution.id,
                assessment_id=assessment.id,
                scheduled_day=day
            )
            db.session.add(scheduled)
    
    db.session.commit()
    
    # Print the schedule
    print_schedule(schedule, U_star, config.min_spacing, probability)

@schedule_cli.command("load", help="Load scheduling data from CSV files")
@click.argument("courses_csv", default="data/courses.csv")
@click.argument("assessments_csv", default="data/assessments.csv")
@click.argument("class_sizes_csv", default="data/class_sizes.csv")
def load_schedule_data(courses_csv, assessments_csv, class_sizes_csv):
    # Clear existing data
    ClassSize.query.delete()
    Assessment.query.delete()
    Course.query.delete()
    db.session.commit()
    
    # Load courses first
    courses_dict = load_courses(courses_csv)
    
    # Load assessments for the courses
    load_assessments(assessments_csv, courses_dict)
    
    # Load class sizes
    load_class_sizes(class_sizes_csv, courses_dict)
    
    print("Schedule data loaded successfully")
