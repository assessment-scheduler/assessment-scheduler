from App.models import CourseStaff, Course, Staff
from App.database import db

def assign_staff_to_course(staff_id, course_code):
    """
    Assign a staff member to a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        CourseStaff object if successful, None otherwise
    """
    return add_CourseStaff(staff_id, course_code)

def remove_staff_from_course(staff_id, course_code):
    """
    Remove a staff member from a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        True if successful, False otherwise
    """
    return remove_CourseStaff(staff_id, course_code)

def add_CourseStaff(staff_id, course_code):
    """
    Add a staff member to a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        CourseStaff object if successful, None otherwise
    """
    return CourseStaff.assign_staff_to_course(staff_id, course_code)

def remove_CourseStaff(staff_id, course_code):
    """
    Remove a staff member from a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        True if successful, False otherwise
    """
    return CourseStaff.remove_staff_from_course(staff_id, course_code)

def get_staff_courses(staff_id):
    """
    Get all courses assigned to a staff member
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        List of Course objects
    """
    return CourseStaff.get_staff_courses(staff_id)

def get_course_staff(course_code):
    """
    Get all staff assigned to a course
    
    Args:
        course_code: Code of the course
        
    Returns:
        List of Staff objects
    """
    return CourseStaff.get_course_staff(course_code)

def is_staff_assigned_to_course(staff_id, course_code):
    """
    Check if a staff member is assigned to a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        True if assigned, False otherwise
    """
    assignment = CourseStaff.query.filter_by(u_id=staff_id, course_code=course_code).first()
    return assignment is not None 