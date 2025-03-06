import click
import pytest
import sys
from flask import Flask
from flask.cli import AppGroup
from App.database import db, get_migrate
from App.main import create_app
from App.models import User, Staff, Course, Assessment, Programme, Admin, ClassSize, SolverConfig, Semester
from App.controllers import create_user, get_all_users_json, get_all_users, initialize, Course
from App.controllers.assessment import get_assessments_by_course
from App.models.solver import LPSolver
from App.controllers.lp import create_sample_problem, solve_lp_problem
from App.models.importer import load_courses, load_assessments, load_class_sizes, load_semester
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
import os

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
    bob = Admin(id=999, email="bob@gmail.com", password="bobpass")
    db.session.add(bob)
    db.session.commit()
    print(bob)
    print('Database initialized')
    
    # Load all data from CSV files
    try:
        # Clear existing data
        ClassSize.query.delete()
        Assessment.query.delete()
        Course.query.delete()
        SolverConfig.query.delete()
        Semester.query.delete()
        db.session.commit()
        
        # Load courses first
        courses_dict = load_courses("App/data/courses.csv")
        print(f"Loaded {len(courses_dict)} courses")
        
        # Load assessments for the courses
        assessments = load_assessments("App/data/assessments.csv", courses_dict)
        print(f"Loaded {len(assessments)} assessments")
        
        # Load class sizes
        class_sizes = load_class_sizes("App/data/class_sizes.csv", courses_dict)
        print(f"Loaded {len(class_sizes)} class sizes")
        
        # Load semester data
        semester_csv_path = "App/data/semester.csv"
        semester = load_semester(semester_csv_path)
        if not semester:
            # Create default semester with specified values
            from datetime import date, timedelta
            today = date.today()
            end_date = today + timedelta(days=120)  # Approximately 4 months
            semester = Semester(
                start_date=today,
                end_date=end_date,
                sem_num=1,
                max_assessments=3,
                K=84,
                d=3,
                M=1000
            )
            db.session.add(semester)
            db.session.commit()
            print(f"Created default semester with K={semester.K}, d={semester.d}, M={semester.M}")
        
        # Set this as the current semester in Config
        from App.models.config import Config
        config = Config.query.first()
        if not config:
            config = Config(semester=semester.sem_num)
            db.session.add(config)
        else:
            config.semester = semester.sem_num
        db.session.commit()
        print(f"Set semester {semester.sem_num} as current semester")
        
        # Create solver config using semester values
        solver_config = SolverConfig(
            semester_days=semester.K,
            min_spacing=semester.d,
            large_m=semester.M
        )
        db.session.add(solver_config)
        db.session.commit()
        print(f"Created solver config with semester values: K={solver_config.semester_days}, d={solver_config.min_spacing}, M={solver_config.large_m}")
        
        # Load staff data from CSV
        staff_count = 0
        staff_csv_path = "App/data/staff.csv"
        if os.path.exists(staff_csv_path):
            with open(staff_csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Check if staff already exists
                    existing_staff = Staff.query.filter_by(id=int(row['ID'])).first()
                    if not existing_staff:
                        # Register new staff
                        Staff.register(
                            f_name=row['First Name'],
                            l_name=row['Last Name'],
                            id=int(row['ID']),
                            status=row['Status'],
                            email=row['Email'],
                            password=row['Password'],
                            department=row['Department'],
                            faculty=row['Faculty']
                        )
                        staff_count += 1
            print(f"Loaded {staff_count} staff members from CSV")
        else:
            print(f"Warning: Staff CSV file not found at {staff_csv_path}")
        
        print("Schedule data loaded successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading data: {e}")

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
    bob = Staff.query.filter_by(id=staff_ID).first()
  
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
    """Load course data from CSV files"""
    from App.models.importer import load_courses
    
    # Check if courses.csv exists
    if not os.path.exists("App/data/courses.csv"):
        print("Error: courses.csv not found in App/data directory")
        return
    
    # Load courses
    courses = load_courses("App/data/courses.csv")
    print(f"Loaded {len(courses)} courses")
    
    # Print course details
    for course in courses:
        status = "Active" if course.active else "Inactive"
        print(f"Course: {course.course_code} - {course.course_title}")
        print(f"  Level: {course.level}, Semester: {course.semester}")
        print(f"  Department: {course.department}, Faculty: {course.faculty}")
        print(f"  Status: {status}")

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
    """Solve the scheduling problem using database data"""
    # Get current semester
    from App.controllers.semester import get_current_semester
    from App.models.semester import Semester
    from App.controllers.assessment import get_assessments_by_course
    from App.models.kris import print_schedule
    
    semester = get_current_semester()
    
    if not semester:
        # Check if any semesters exist
        semesters = Semester.query.all()
        if not semesters:
            print("No semesters found in the database. Please create a semester first.")
            return
        
        # Use the first semester if no current semester is set
        semester = semesters[0]
        print(f"No current semester set. Using semester {semester.sem_num} as fallback.")
        
        # Set this as the current semester
        from App.models.config import Config
        config = Config.query.first()
        if not config:
            config = Config(semester=semester.sem_num)
            db.session.add(config)
        else:
            config.semester = semester.sem_num
        db.session.commit()
        print(f"Set semester {semester.sem_num} as current semester")
    
    print(f"Using semester {semester.sem_num} parameters:")
    print(f"  - K (total days): {semester.K}")
    print(f"  - d (min spacing): {semester.d}")
    print(f"  - M (constraint constant): {semester.M}")
    
    # Get or create config and update with semester parameters
    config = SolverConfig.query.first()
    if not config:
        config = SolverConfig(
            semester_days=semester.K,
            min_spacing=semester.d,
            large_m=semester.M
        )
        db.session.add(config)
    else:
        # Always update config with current semester values
        config.semester_days = semester.K
        config.min_spacing = semester.d
        config.large_m = semester.M
    
    db.session.commit()
    
    # Get all active courses
    courses = Course.query.filter_by(active=True).all()
    
    if not courses:
        print("No active courses found in database")
        return
    
    print(f"Found {len(courses)} active courses")
    
    # Get all assessments and format data for solver using the controller method
    formatted_courses = []
    course_codes = []
    
    for course in courses:
        # Use the controller method to get assessments for this course
        course_assessments = get_assessments_by_course(course.course_code)
        if not course_assessments:
            continue
            
        course_codes.append(course.course_code)
        
        # Format assessments for this course
        formatted_assessments = []
        for assessment in course_assessments:
            # Convert percentage to integer by multiplying by 100 if it's a decimal (e.g., 0.25 -> 25)
            percentage = assessment.percentage
            if percentage < 100:  # If it's already stored as a percentage (e.g., 25 for 25%)
                percentage_int = int(percentage)
            else:  # If it's stored as a decimal (e.g., 0.25 for 25%)
                percentage_int = int(percentage * 100)
                
            formatted_assessments.append({
                'name': assessment.name,
                'percentage': percentage_int,  # Use integer percentage
                'start_week': assessment.start_week,
                'start_day': assessment.start_day,
                'end_week': assessment.end_week,
                'end_day': assessment.end_day,
                'proctored': 1 if assessment.proctored else 0  # Convert boolean to int
            })
        
        # Add course with its assessments to the formatted list
        formatted_courses.append({
            'code': course.course_code,  # Add the course code
            'assessments': formatted_assessments
        })
    
    if not formatted_courses:
        print("No assessments found in database")
        return
    
    total_assessments = sum(len(course['assessments']) for course in formatted_courses)
    print(f"Found {total_assessments} assessments")
    
    # Initialize class sizes matrix
    n = len(formatted_courses)
    c = [[0 for _ in range(n)] for _ in range(n)]
    
    # Get class sizes from database
    class_sizes = ClassSize.query.all()
    for class_size in class_sizes:
        i = next((idx for idx, code in enumerate(course_codes) if code == class_size.course_code), None)
        j = next((idx for idx, code in enumerate(course_codes) if code == class_size.other_course_code), None)
        if i is not None and j is not None:
            c[i][j] = class_size.size
    
    # Print class sizes matrix for debugging
    print("\nClass sizes matrix:")
    for i, row in enumerate(c):
        print(f"{course_codes[i]}: {row}")
    
    # Generate phi matrix
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]
    
    try:
        # Solve using semester parameters
        print(f"\nSolving with parameters: K={semester.K}, d={semester.d}, M={semester.M}")
        U_star, solver, x = solve_stage1(formatted_courses, c, 
                                       semester.K,
                                       semester.M)
        
        schedule, Y_star, probability = solve_stage2(formatted_courses, c, phi, U_star,
                                                   semester.K,
                                                   semester.d,
                                                   semester.M)
        
        # Print schedule in the original format
        print_schedule(schedule, U_star, semester.d, probability)
        
        # Save solution
        solution = ScheduleSolution(
            config_id=config.id,
            u_star=U_star,
            y_star=Y_star,
            probability=probability
        )
        db.session.add(solution)
        db.session.commit()
        
        print(f"\nSolution saved with ID {solution.id}")
        
    except Exception as e:
        import traceback
        print(f"Error solving schedule: {str(e)}")
        traceback.print_exc()

# Commenting out the load function as it won't be used anymore
"""
@schedule_cli.command("load", help="Load scheduling data from CSV files")
@click.argument("courses_csv", default="App/data/courses.csv")
@click.argument("assessments_csv", default="App/data/assessments.csv")
@click.argument("class_sizes_csv", default="App/data/class_sizes.csv")
@click.argument("config_csv", default="App/data/config.csv")
def load_schedule_data(courses_csv, assessments_csv, class_sizes_csv, config_csv):
    # Load scheduling data from CSV files
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
        print(f"Loaded {len(class_sizes)} class size relationships")
        
        # Load config
        try:
            with open(config_csv, 'r') as f:
                reader = csv.DictReader(f)
                row = next(reader)
                config = SolverConfig(
                    semester_days=int(row.get('semester_days', 70)),
                    min_spacing=int(row.get('min_spacing', 3)),
                    large_m=int(row.get('large_m', 1000))
                )
                db.session.add(config)
                db.session.commit()
                print(f"Loaded config: K={config.semester_days}, d={config.min_spacing}, M={config.large_m}")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            # Use default config
            config = SolverConfig()
            db.session.add(config)
            db.session.commit()
            print(f"Using default config: K={config.semester_days}, d={config.min_spacing}, M={config.large_m}")
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
"""

class Importer:
    def __init__(self, app):
        self.app = app

    def import_assessments(self):
        with open('data/assessments.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                course_code, name, percentage, start_week, start_day, end_week, end_day, proctored, category = row
                
                # Convert values to appropriate types
                percentage = int(percentage)
                start_week = int(start_week)
                start_day = int(start_day)
                end_week = int(end_week)
                end_day = int(end_day)
                proctored = proctored.lower() == 'true'
                
                # Convert category string to Category enum
                from App.models.assessment import Category
                try:
                    category_enum = Category[category.strip().upper()]
                except (KeyError, ValueError):
                    category_enum = Category.ASSIGNMENT
                
                assessment = Assessment(
                    course_id=course_code,
                    name=name,
                    percentage=percentage,
                    start_week=start_week,
                    start_day=start_day,
                    end_week=end_week,
                    end_day=end_day,
                    proctored=proctored,
                    category=category_enum  # Use the enum value instead of the string
                )
                
                db.session.add(assessment)
        
        db.session.commit()

@app.cli.command("import-semester", help="Import semester data from a CSV file")
@click.argument("csv_file", default="App/data/semester.csv")
def import_semester_command(csv_file):
    """Import semester data from a CSV file"""
    try:
        semester = load_semester(csv_file)
        if semester:
            print(f"Successfully imported semester {semester.sem_num} with parameters:")
            print(f"  - Start date: {semester.start_date}")
            print(f"  - End date: {semester.end_date}")
            print(f"  - Max assessments: {semester.max_assessments}")
            print(f"  - K (total days): {semester.K}")
            print(f"  - d (min spacing): {semester.d}")
            print(f"  - M (constraint constant): {semester.M}")
            
            # Set this as the current semester
            from App.models.config import Config
            config = Config.query.first()
            if not config:
                config = Config(semester=semester.sem_num)
                db.session.add(config)
            else:
                config.semester = semester.sem_num
            db.session.commit()
            print(f"Set semester {semester.sem_num} as current semester")
            
            # Update solver config with semester parameters
            solver_config = SolverConfig.query.first()
            if not solver_config:
                solver_config = SolverConfig(
                    semester_days=semester.K,
                    min_spacing=semester.d,
                    large_m=semester.M
                )
                db.session.add(solver_config)
            else:
                solver_config.semester_days = semester.K
                solver_config.min_spacing = semester.d
                solver_config.large_m = semester.M
            db.session.commit()
            print(f"Updated solver configuration with semester parameters")
        else:
            print(f"Failed to import semester data from {csv_file}")
    except Exception as e:
        print(f"Error importing semester data: {str(e)}")

@app.cli.command("export-semester", help="Export current semester data to a CSV file")
@click.argument("csv_file", default="App/data/semester_export.csv")
def export_semester_command(csv_file):
    """Export current semester data to a CSV file"""
    from App.controllers.semester import get_current_semester
    import csv
    
    semester = get_current_semester()
    if not semester:
        print("No current semester found to export")
        return
    
    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['start_date', 'end_date', 'sem_num', 'max_assessments', 'K', 'd', 'M'])
            # Write data
            writer.writerow([
                semester.start_date.strftime('%Y-%m-%d'),
                semester.end_date.strftime('%Y-%m-%d'),
                semester.sem_num,
                semester.max_assessments,
                semester.K,
                semester.d,
                semester.M
            ])
        print(f"Successfully exported semester {semester.sem_num} data to {csv_file}")
    except Exception as e:
        print(f"Error exporting semester data: {str(e)}")

@app.cli.command("create-semester", help="Create a new semester with specified parameters")
@click.option("--start-date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", required=True, help="End date (YYYY-MM-DD)")
@click.option("--sem-num", required=True, type=int, help="Semester number")
@click.option("--max-assessments", required=True, type=int, help="Maximum assessments per level")
@click.option("--k", default=84, type=int, help="Total days in semester")
@click.option("--d", default=3, type=int, help="Days between assessments for overlapping courses")
@click.option("--m", default=1000, type=int, help="Constraint constant")
def create_semester_command(start_date, end_date, sem_num, max_assessments, k, d, m):
    """Create a new semester with specified parameters"""
    from datetime import datetime
    from App.controllers.semester import create_semester
    
    try:
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Create semester
        semester = create_semester(start_date, end_date, sem_num, max_assessments, k, d, m)
        
        print(f"Successfully created semester {semester.sem_num} with parameters:")
        print(f"  - Start date: {semester.start_date}")
        print(f"  - End date: {semester.end_date}")
        print(f"  - Max assessments: {semester.max_assessments}")
        print(f"  - K (total days): {semester.K}")
        print(f"  - d (min spacing): {semester.d}")
        print(f"  - M (constraint constant): {semester.M}")
        
        # Note: create_semester already sets this as the current semester in Config
        
        # Update solver config with semester parameters
        solver_config = SolverConfig.query.first()
        if not solver_config:
            solver_config = SolverConfig(
                semester_days=semester.K,
                min_spacing=semester.d,
                large_m=semester.M
            )
            db.session.add(solver_config)
        else:
            solver_config.semester_days = semester.K
            solver_config.min_spacing = semester.d
            solver_config.large_m = semester.M
        db.session.commit()
        print(f"Updated solver configuration with semester parameters")
    except Exception as e:
        print(f"Error creating semester: {str(e)}")

@app.cli.command("list-semesters", help="List all semesters in the database")
def list_semesters_command():
    """List all semesters in the database"""
    semesters = Semester.query.all()
    if not semesters:
        print("No semesters found in the database")
        return
    
    for semester in semesters:
        print(f"Semester {semester.sem_num}: {semester.start_date} to {semester.end_date}, Max Assessments: {semester.max_assessments}")
        print(f"  K={semester.K}, d={semester.d}, M={semester.M}")
    
    print(f"Total: {len(semesters)} semesters")
