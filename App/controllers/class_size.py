from App.models.class_size import ClassSize
from App.database import db

def get_all_class_sizes():
    """
    Get all class sizes
    
    Returns:
        List of ClassSize objects
    """
    return ClassSize.query.all()

def add_class_size(course_code, other_course_code, size):
    """
    Add a new class size
    
    Args:
        course_code: Code of the first course
        other_course_code: Code of the second course
        size: Number of students taking both courses
        
    Returns:
        ClassSize object
    """
    return ClassSize.add_class_size(course_code, other_course_code, size)

def get_overlapping_students(course1_code, course2_code):
    """
    Get the number of students taking both courses
    
    Args:
        course1_code: Code of the first course
        course2_code: Code of the second course
        
    Returns:
        Number of students taking both courses
    """
    overlap = ClassSize.query.filter(
        (ClassSize.course_code == course1_code) & 
        (ClassSize.other_course_code == course2_code)
    ).first()
    
    return overlap.size if overlap else 0 