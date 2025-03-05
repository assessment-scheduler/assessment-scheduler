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
from App.models.problem import LinearProblem
from App.models.constraint import LPConstraint
from App.models.variable import LPVariable
from App.models.kris import solve_stage1, solve_stage2, print_schedule
from App.controllers.course import (
    add_Course
)
from App.models.schedule_solution import ScheduleSolution
from App.models.scheduled_assessment import ScheduledAssessment
import csv

# Get migration instance

# This commands file allows you to create convenient CLI commands for testing controllers!
app = create_app()
migrate = get_migrate(app)

# Add this after the app is created but before the lp_cli commands
lp_cli = AppGroup('lp', help='Linear programming commands')
schedule_cli = AppGroup('schedule', help='Scheduling commands')

app.cli.add_command(lp_cli)
app.cli.add_command(schedule_cli)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    # db.init_app(app)
    db.create_all()
    # bob = Staff("bob", "test", 300456, "Lecturer 1", "bob@gmail.com", "bobpass")
    bob = Admin(u_id=999, email="bob@gmail.com", password="bobpass")
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
    db.session.add(problem)
    db.session.commit()
    
    # Add variables
    x1 = LPVariable("x1", lower_bound=0)
    x2 = LPVariable("x2", lower_bound=0)
    x1.problem_id = problem.id
    x2.problem_id = problem.id
    db.session.add(x1)
    db.session.add(x2)
    db.session.commit()
    
    # Add constraints with relation operators
    const1 = LPConstraint("x1 + x2 <= 10", "<=")
    const2 = LPConstraint("2x1 + x2 <= 16", "<=")
    const1.problem_id = problem.id
    const2.problem_id = problem.id
    db.session.add(const1)
    db.session.add(const2)
    db.session.commit()
    
    # Create solver and solve
    solver = LPSolver(problem)
    result = solver.solve()
    
    # Print problem and solution
    print("Problem Definition:")
    problem.print_problem()
    print("\nSolution:")
    print(result)

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
        for var_name, value in sorted(result['variables'].items()):
            print(f"  {var_name} = {value}")
    else:
        print(f"Status: {result['status']}")
        print(f"Error: {result.get('error', 'Unknown error')}")

@schedule_cli.command("solve", help="Solve the scheduling problem using database data")
def solve_schedule():
    # Get or create config
    config = SolverConfig.query.first() or SolverConfig()
    db.session.add(config)
    
    # Get all courses and convert to solver format
    courses = Course.query.all()
    courses_list = []
    
    # Print debug info
    print("Courses and assessments loaded from database:")
    for course in courses:
        print(f"Course: {course.course_code}")
        for a in course.assessments:
            print(f"  - {a.name} ({a.percentage}%) - Week {a.start_week}-{a.end_week}, Proctored: {a.proctored}")
    
    # Format courses in the exact format expected by kris.py
    for i, course in enumerate(courses):
        assessments_list = []
        for a in course.assessments:
            assessments_list.append({
                'name': a.name,
                'percentage': int(a.percentage),
                'start_week': a.start_week,
                'start_day': a.start_day,
                'end_week': a.end_week,
                'end_day': a.end_day,
                'proctored': int(a.proctored)
            })
        
        # Note: kris.py expects courses without 'name' field, it generates course names as C160{i+1}
        course_data = {
            'assessments': assessments_list
        }
        courses_list.append(course_data)
    
    # Build class sizes matrix
    n = len(courses)
    c = [[0 for _ in range(n)] for _ in range(n)]
    
    # Get class sizes from database
    class_sizes = ClassSize.query.all()
    for class_size in class_sizes:
        i = next((idx for idx, course in enumerate(courses) if course.course_code == class_size.course_code), None)
        j = next((idx for idx, course in enumerate(courses) if course.course_code == class_size.other_course_code), None)
        if i is not None and j is not None:
            c[i][j] = class_size.size
    
    # Print class sizes matrix for debugging
    print("\nClass sizes matrix:")
    for i, row in enumerate(c):
        print(f"{courses[i].course_code}: {row}")
    
    # Generate phi matrix
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]
    
    try:
        # Solve using config parameters
        print(f"\nSolving with parameters: K={config.semester_days}, d={config.min_spacing}, M={config.large_m}")
        U_star, solver, x = solve_stage1(courses_list, c, 
                                       config.semester_days,
                                       config.large_m)
        
        schedule, Y_star, probability = solve_stage2(courses_list, c, phi, U_star,
                                                   config.semester_days,
                                                   config.min_spacing,
                                                   config.large_m)
        
        # Print schedule details for debugging
        print("\nSchedule details:")
        for k, week, day, course, assessment in schedule:
            print(f"Day {k}, Week {week}, Day {day}: {course}-{assessment}")
        
        # Save solution
        solution = ScheduleSolution(
            config_id=config.id,
            u_star=U_star,
            y_star=Y_star,
            probability=probability
        )
        db.session.add(solution)
        db.session.commit()
        
        # Let kris.py handle the printing of the schedule
        print_schedule(schedule, U_star, config.min_spacing, probability)
    except Exception as e:
        print(f"Error solving schedule: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

@schedule_cli.command("load", help="Load scheduling data from CSV files")
@click.argument("courses_csv", default="App/data/courses.csv")
@click.argument("assessments_csv", default="App/data/assessments.csv")
@click.argument("class_sizes_csv", default="App/data/class_sizes.csv")
@click.argument("config_csv", default="App/data/config.csv")
def load_schedule_data(courses_csv, assessments_csv, class_sizes_csv, config_csv):
    """Load scheduling data from CSV files"""
    try:
        # Clear existing data
        ClassSize.query.delete()
        Assessment.query.delete()
        Course.query.delete()
        SolverConfig.query.delete()
        db.session.commit()
        
        # Load courses first
        courses_dict = load_courses(courses_csv)
        print(f"Loaded {len(courses_dict)} courses")
        
        # Load assessments for the courses
        assessments = load_assessments(assessments_csv, courses_dict)
        print(f"Loaded {len(assessments)} assessments")
        
        # Load class sizes
        class_sizes = load_class_sizes(class_sizes_csv, courses_dict)
        print(f"Loaded {len(class_sizes)} class sizes")
        
        # Load config if available
        try:
            with open(config_csv, 'r') as file:
                reader = csv.DictReader(file)
                config_data = next(reader)
                config = SolverConfig(
                    semester_days=int(config_data.get('time_horizon', 84)),
                    min_spacing=int(config_data.get('min_spacing', 3)),
                    large_m=int(config_data.get('big_m', 1000)),
                    weekend_penalty=float(config_data.get('weekend_penalty', 1.5))
                )
                db.session.add(config)
                db.session.commit()
                print(f"Loaded config: K={config.semester_days}, d={config.min_spacing}, M={config.large_m}")
        except Exception as e:
            # Create default config if loading fails
            config = SolverConfig()
            db.session.add(config)
            db.session.commit()
            print(f"Created default config: K={config.semester_days}, d={config.min_spacing}, M={config.large_m}")
        
        print("Schedule data loaded successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading schedule data: {e}")
