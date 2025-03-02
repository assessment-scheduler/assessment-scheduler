"""
Controller functions for the scheduler module
"""
import datetime
from App.database import db
from App.models.course import Course
from App.models.assessment import Assessment
from App.models.semester import Semester
from App.models.solver_config import SolverConfig
from App.scheduler.solver import ScheduleSolver

def get_current_semester():
    """
    Get the current semester
    
    Returns:
        The current semester or None if no semester exists
    """
    return Semester.query.order_by(Semester.id.desc()).first()

def get_courses_for_staff(staff_id):
    """
    Get courses assigned to a staff member
    
    Args:
        staff_id: ID of the staff member
    
    Returns:
        List of Course objects
    """
    from App.models.courseStaff import CourseStaff
    
    course_staff = CourseStaff.query.filter_by(s_ID=staff_id).all()
    course_ids = [cs.c_ID for cs in course_staff]
    
    return Course.query.filter(Course.id.in_(course_ids)).all()

def get_assessment_types():
    """
    Get all assessment types
    
    Returns:
        List of Assessment objects
    """
    return Assessment.query.all()

def generate_schedule(courses, assessments, min_spacing=3, max_per_day=2, avoid_weekends=True):
    """
    Generate a schedule for the given courses and assessments
    
    Args:
        courses: List of Course objects
        assessments: List of Assessment objects
        min_spacing: Minimum days between assessments
        max_per_day: Maximum assessments per day
        avoid_weekends: Whether to avoid scheduling on weekends
    
    Returns:
        A tuple of (schedule, U_star, probability) or (None, 0, 0) if no solution is found
    """
    # Get current semester
    semester = get_current_semester()
    if not semester:
        return None, 0, 0
    
    # Create or get config
    config = SolverConfig.query.order_by(SolverConfig.id.desc()).first()
    if not config:
        config = SolverConfig(
            min_spacing=min_spacing,
            large_m=1000,
            weekend_penalty=1.5 if avoid_weekends else 1.0
        )
        db.session.add(config)
        db.session.commit()
    else:
        # Update config with new values
        config.min_spacing = min_spacing
        config.weekend_penalty = 1.5 if avoid_weekends else 1.0
        db.session.commit()
    
    # Create solver and solve
    solver = ScheduleSolver(semester, courses, assessments, config)
    return solver.solve()

def apply_schedule(schedule, courses, assessments):
    """
    Apply the generated schedule to the course assessments
    
    Args:
        schedule: List of tuples (day, week, day_of_week, course_code, assessment_name)
        courses: List of Course objects
        assessments: List of Assessment objects
    
    Returns:
        True if successful, False otherwise
    """
    from App.models.courseAssessment import CourseAssessment
    
    try:
        semester = get_current_semester()
        if not semester:
            return False
        
        # Create a mapping of course codes to Course objects
        course_map = {course.courseCode: course for course in courses}
        
        # Create a mapping of assessment names to Assessment objects
        assessment_map = {assessment.category.value: assessment for assessment in assessments}
        
        # Update course assessments
        for day, week, day_of_week, course_code, assessment_name in schedule:
            course = course_map.get(course_code)
            assessment = assessment_map.get(assessment_name)
            
            if course and assessment:
                # Calculate the date
                date = semester.startDate + datetime.timedelta(days=day)
                
                # Find the course assessment
                course_assessment = CourseAssessment.query.filter_by(
                    course_id=course.id,
                    assessment_id=assessment.id
                ).first()
                
                if course_assessment:
                    course_assessment.dueDate = date
                    db.session.add(course_assessment)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error applying schedule: {e}")
        return False 