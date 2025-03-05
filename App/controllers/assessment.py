from App.models.assessment import Assessment
from App.models.course import Course
from App.database import db
from datetime import datetime, timedelta

def get_all_assessments():
    """
    Get all assessments
    
    Returns:
        List of Assessment objects
    """
    return Assessment.query.all()

def get_assessments_by_course(course_id):
    return Assessment.query.filter_by(course_id=course_id).all()

def get_assessments_by_courses(course_ids):
    return Assessment.query.filter(Assessment.course_id.in_(course_ids)).all()

def add_assessment(course_id, name, percentage, start_week, start_day, end_week, end_day, proctored, category):
    """
    Add a new assessment with validation for course existence and percentage range
    """
    # Validate course exists
    course = Course.query.filter_by(course_code=course_id).first()
    if not course:
        return None
    
    # Validate percentage is between 0 and 100
    if percentage < 0 or percentage > 100:
        return None
    
    assessment = Assessment(
        course_id=course_id,
        name=name,
        percentage=percentage,
        start_week=start_week,
        start_day=start_day,
        end_week=end_week,
        end_day=end_day,
        proctored=proctored,
        category=category
    )
    
    db.session.add(assessment)
    db.session.commit()
    return assessment

def update_assessment(assessment_id, name=None, percentage=None, start_week=None, 
                     start_day=None, end_week=None, end_day=None, proctored=None, category=None):
    assessment = get_assessment_by_id(assessment_id)
    if not assessment:
        return None
    
    # Validate percentage if provided
    if percentage is not None and (percentage < 0 or percentage > 100):
        return None
    
    if name:
        assessment.name = name
    if percentage is not None:
        assessment.percentage = percentage
    if start_week is not None:
        assessment.start_week = start_week
    if start_day is not None:
        assessment.start_day = start_day
    if end_week is not None:
        assessment.end_week = end_week
    if end_day is not None:
        assessment.end_day = end_day
    if proctored is not None:
        assessment.proctored = proctored
    if category:
        assessment.category = category
    
    db.session.commit()
    return assessment

def delete_assessment(assessment_id):
    assessment = get_assessment_by_id(assessment_id)
    if not assessment:
        return False
    
    db.session.delete(assessment)
    db.session.commit()
    return True

def get_assessment_by_id(assessment_id):
    return Assessment.query.get(assessment_id)

def get_assessments_by_category(category):
    return Assessment.query.filter_by(category=category).all()

def get_proctored_assessments():
    return Assessment.query.filter_by(proctored=True).all()

def calculate_total_percentage_for_course(course_id):
    """
    Calculate the total percentage of all assessments for a course
    """
    assessments = get_assessments_by_course(course_id)
    return sum(assessment.percentage for assessment in assessments)

# Commenting out clash detection
'''
def detect_assessment_clashes(assessment_id):
    """
    Detect time clashes between the target assessment and other assessments in the same course
    """
    target_assessment = get_assessment_by_id(assessment_id)
    if not target_assessment:
        return []
    
    # Get all assessments for the same course
    course_assessments = get_assessments_by_course(target_assessment.course_id)
    
    # Filter out the target assessment
    other_assessments = [a for a in course_assessments if a.a_id != target_assessment.a_id]
    
    # Check for clashes
    clashes = []
    for assessment in other_assessments:
        # Simple clash detection based on week and day
        if (target_assessment.start_week <= assessment.end_week and 
            target_assessment.end_week >= assessment.start_week):
            # Weeks overlap, check days
            if (target_assessment.start_day <= assessment.end_day and 
                target_assessment.end_day >= assessment.start_day):
                clashes.append(assessment)
    
    return clashes
'''

def format_assessment_for_calendar(assessment):
    """
    Format assessment data for calendar display with appropriate colors based on category
    """
    colors = {
        'EXAM': '#e74c3c',      # Red
        'MIDTERM': '#f39c12',   # Orange
        'ASSIGNMENT': '#2ecc71', # Green
        'QUIZ': '#9b59b6',      # Purple
        'DEFAULT': '#3498db'    # Blue
    }
    
    color = colors.get(assessment.category, colors['DEFAULT'])
    
    return {
        'id': assessment.a_id,
        'title': assessment.name,
        'start': None,  # Would need semester start date to calculate actual date
        'end': None,    # Would need semester start date to calculate actual date
        'color': color,
        'textColor': '#ffffff',
        'extendedProps': {
            'course_id': assessment.course_id,
            'percentage': assessment.percentage,
            'category': assessment.category.value if hasattr(assessment.category, 'value') else assessment.category,
            'proctored': assessment.proctored
        }
    } 