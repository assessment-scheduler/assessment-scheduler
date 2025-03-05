from App.models.assessment import Assessment
from App.database import db

def get_assessments_by_course(course_id):
    """Get all assessments for a specific course"""
    return Assessment.query.filter_by(course_id=course_id).all()

def add_assessment(course_id, name, percentage, start_week, start_day, end_week, end_day, proctored, category):
    """Add a new assessment"""
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
    """Update an existing assessment"""
    assessment = get_assessment_by_id(assessment_id)
    if not assessment:
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
    """Delete an assessment"""
    assessment = get_assessment_by_id(assessment_id)
    if not assessment:
        return False
    
    db.session.delete(assessment)
    db.session.commit()
    return True

def get_assessment_by_id(assessment_id):
    """Get an assessment by ID"""
    return Assessment.query.get(assessment_id) 