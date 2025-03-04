"""
Data importer module for loading data from CSV files
"""
import csv
import os
from App.database import db
from App.models.course import Course
from App.models.assessment import Assessment
from App.models.class_size import ClassSize
from App.models.solver_config import SolverConfig

def load_courses(csv_file):
    """
    Load courses from a CSV file
    
    Args:
        csv_file: Path to the CSV file
    
    Returns:
        Dictionary mapping course codes to Course objects
    """
    courses = {}
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course = Course(
                    course_code=row.get('course_code', row.get('courseCode')),
                    course_title=row.get('course_title', row.get('courseTitle')),
                    description=row.get('description', ''),
                    level=row.get('level', ''),
                    semester=row.get('semester', ''),
                    pre_reqs=row.get('pre_reqs', row.get('preReqs', '')),
                    p_id=row.get('p_id', row.get('p_ID', None))
                )
                db.session.add(course)
                courses[course.course_code] = course
        
        db.session.commit()
        return courses
    except Exception as e:
        db.session.rollback()
        print(f"Error loading courses: {e}")
        return {}

def load_assessments(csv_file, courses=None):
    """
    Load assessments from a CSV file
    
    Args:
        csv_file: Path to the CSV file
        courses: Dictionary mapping course codes to Course objects
    
    Returns:
        List of Assessment objects
    """
    assessments = []
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course_code = row.get('course_code', row.get('courseCode'))
                assessment = Assessment(
                    course_id=course_code,
                    name=row.get('name', ''),
                    percentage=float(row.get('percentage', 0)),
                    start_week=int(row.get('start_week', 0)),
                    start_day=int(row.get('start_day', 0)),
                    end_week=int(row.get('end_week', 0)),
                    end_day=int(row.get('end_day', 0)),
                    proctored=row.get('proctored', 'False').lower() == 'true',
                    category=row.get('category', 'EXAM').strip()
                )
                db.session.add(assessment)
                assessments.append(assessment)
        
        db.session.commit()
        return assessments
    except Exception as e:
        db.session.rollback()
        print(f"Error loading assessments: {e}")
        return []

def load_class_sizes(csv_file, courses=None):
    """
    Load class sizes from a CSV file
    
    Args:
        csv_file: Path to the CSV file
        courses: Dictionary mapping course codes to Course objects
    
    Returns:
        List of ClassSize objects
    """
    class_sizes = []
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course_code = row.get('course_code', row.get('courseCode'))
                other_course_code = row.get('other_course_code', row.get('other_courseCode'))
                
                class_size = ClassSize(
                    course_code=course_code,
                    other_course_code=other_course_code,
                    size=int(row.get('size', 0))
                )
                db.session.add(class_size)
                class_sizes.append(class_size)
        
        db.session.commit()
        return class_sizes
    except Exception as e:
        db.session.rollback()
        print(f"Error loading class sizes: {e}")
        return []

def load_solver_config(config_dict=None):
    """
    Load solver configuration
    
    Args:
        config_dict: Dictionary with configuration values
    
    Returns:
        SolverConfig object
    """
    try:
        # Use default values if no config provided
        if not config_dict:
            config_dict = {}
        
        config = SolverConfig(
            semester_days=config_dict.get('semester_days', 84),
            min_spacing=config_dict.get('min_spacing', 3),
            large_m=config_dict.get('large_m', 1000),
            weekend_penalty=config_dict.get('weekend_penalty', 1.5)
        )
        
        db.session.add(config)
        db.session.commit()
        return config
    except Exception as e:
        db.session.rollback()
        print(f"Error loading solver config: {e}")
        return None
