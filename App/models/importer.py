"""
Data importer module for loading data from CSV files
"""
import csv
import os
from App.database import db
from App.models.course import Course
from App.models.assessment import Assessment, Category
from App.models.class_size import ClassSize
from App.models.solver_config import SolverConfig
from App.models.semester import Semester
from datetime import datetime, date

def load_courses(csv_file):
    """
    Load courses from a CSV file.
    Expected columns: course_code,course_title,description,level,semester,department,faculty,active
    """
    courses = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if course already exists
            existing_course = Course.query.filter_by(course_code=row['course_code']).first()
            if existing_course:
                # Update existing course
                existing_course.course_title = row['course_title']
                existing_course.description = row.get('description', '')
                existing_course.level = int(row['level'])
                existing_course.semester = int(row['semester'])
                existing_course.department = row.get('department', 'DCIT')  # Default to DCIT if not provided
                existing_course.faculty = row.get('faculty', 'FST')  # Default to FST if not provided
                
                # Handle active field (convert string to boolean)
                active_str = row.get('active', 'true').lower()
                existing_course.active = (active_str == 'true')
                
                db.session.commit()
                courses.append(existing_course)
            else:
                # Create new course
                # Handle active field (convert string to boolean)
                active_str = row.get('active', 'true').lower()
                active = (active_str == 'true')
                
                course = Course(
                    course_code=row['course_code'],
                    course_title=row['course_title'],
                    description=row.get('description', ''),
                    level=int(row['level']),
                    semester=int(row['semester']),
                    department=row.get('department', 'DCIT'),  # Default to DCIT if not provided
                    faculty=row.get('faculty', 'FST'),  # Default to FST if not provided
                    active=active
                )
                db.session.add(course)
                db.session.commit()
                courses.append(course)
    return courses

def load_assessments(csv_file, courses=None):
    """
    Load assessments from a CSV file.
    Expected columns: course_code,name,percentage,start_week,start_day,end_week,end_day,proctored,category
    """
    if courses is None:
        courses = Course.query.all()
    
    course_dict = {course.course_code: course for course in courses}
    assessments = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_code = row['course_code']
            if course_code not in course_dict:
                print(f"Warning: Course {course_code} not found, skipping assessment")
                continue
            
            course = course_dict[course_code]
            
            # Get category as enum
            try:
                category_value = row['category']
                category = Category[category_value]
            except KeyError:
                print(f"Warning: Invalid category {category_value} for {course_code}, skipping assessment")
                continue
            
            # Check if assessment already exists
            existing_assessment = Assessment.query.filter_by(
                course_id=course_code,
                name=row['name']
            ).first()
            
            if existing_assessment:
                # Update existing assessment
                existing_assessment.percentage = float(row['percentage'])
                existing_assessment.start_week = int(row['start_week'])
                existing_assessment.start_day = int(row['start_day'])
                existing_assessment.end_week = int(row['end_week'])
                existing_assessment.end_day = int(row['end_day'])
                existing_assessment.proctored = bool(int(row['proctored']))
                existing_assessment.category = category
                db.session.commit()
                assessments.append(existing_assessment)
            else:
                # Create new assessment
                assessment = Assessment(
                    course_id=course_code,
                    name=row['name'],
                    percentage=float(row['percentage']),
                    start_week=int(row['start_week']),
                    start_day=int(row['start_day']),
                    end_week=int(row['end_week']),
                    end_day=int(row['end_day']),
                    proctored=bool(int(row['proctored'])),
                    category=category
                )
                db.session.add(assessment)
                db.session.commit()
                assessments.append(assessment)
    
    return assessments

def load_class_sizes(csv_file, courses=None):
    """
    Load class sizes from a CSV file.
    Expected columns: course_code,other_course_code,size
    """
    if courses is None:
        courses = Course.query.all()
    
    course_dict = {course.course_code: course for course in courses}
    class_sizes = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_code = row['course_code']
            other_course_code = row['other_course_code']
            
            if course_code not in course_dict:
                print(f"Warning: Course {course_code} not found, skipping class size")
                continue
                
            if other_course_code not in course_dict:
                print(f"Warning: Other course {other_course_code} not found, skipping class size")
                continue
            
            # Check if class size already exists
            existing_class_size = ClassSize.query.filter_by(
                course_code=course_code,
                other_course_code=other_course_code
            ).first()
            
            if existing_class_size:
                # Update existing class size
                existing_class_size.size = int(row['size'])
                db.session.commit()
                class_sizes.append(existing_class_size)
            else:
                # Create new class size
                class_size = ClassSize(
                    course_code=course_code,
                    other_course_code=other_course_code,
                    size=int(row['size'])
                )
                db.session.add(class_size)
                db.session.commit()
                class_sizes.append(class_size)
    
    return class_sizes

def load_solver_config(config_dict=None):
    """
    Load solver configuration from a dictionary or create default config.
    """
    config = SolverConfig.query.first()
    
    if config is None:
        config = SolverConfig()
        db.session.add(config)
    
    if config_dict:
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    db.session.commit()
    return config

def load_semester(csv_file):
    """
    Load semester data from a CSV file.
    Expected columns: start_date,end_date,sem_num,max_assessments,K,d,M
    
    Returns:
        Semester object or None if file doesn't exist
    """
    if not os.path.exists(csv_file):
        print(f"Warning: Semester CSV file {csv_file} not found")
        return None
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse dates
            try:
                start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(row['end_date'], '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid date format in {csv_file}. Expected YYYY-MM-DD")
                continue
            
            # Parse integers
            try:
                sem_num = int(row['sem_num'])
                max_assessments = int(row['max_assessments'])
                K = int(row.get('K', 84))  # Default to 84 if not provided
                d = int(row.get('d', 3))   # Default to 3 if not provided
                M = int(row.get('M', 1000)) # Default to 1000 if not provided
            except ValueError:
                print(f"Error: Invalid numeric values in {csv_file}")
                continue
            
            # Check if semester already exists
            existing_semester = Semester.query.filter_by(sem_num=sem_num).first()
            if existing_semester:
                # Update existing semester
                existing_semester.start_date = start_date
                existing_semester.end_date = end_date
                existing_semester.max_assessments = max_assessments
                existing_semester.K = K
                existing_semester.d = d
                existing_semester.M = M
                db.session.commit()
                print(f"Updated semester {sem_num}")
                return existing_semester
            else:
                # Create new semester
                new_semester = Semester(
                    start_date=start_date,
                    end_date=end_date,
                    sem_num=sem_num,
                    max_assessments=max_assessments,
                    K=K,
                    d=d,
                    M=M
                )
                db.session.add(new_semester)
                db.session.commit()
                print(f"Created new semester {sem_num}")
                return new_semester
    
    return None
