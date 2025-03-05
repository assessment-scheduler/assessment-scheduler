from App.models import Course, Staff
from App.database import db
from flask import session

def get_all_courses():
    """
    Get all courses
    
    Returns:
        List of Course objects
    """
    return list_Courses()

def get_course_by_code(course_code):
    """
    Get a course by code
    
    Args:
        course_code: Code of the course
        
    Returns:
        Course object if found, None otherwise
    """
    return get_course(course_code)

def add_course(course_code, course_title, description, level, semester, department, faculty, staff_id=None, active=True):
    """
    Add a new course
    
    Args:
        course_code: Code of the course
        course_title: Title of the course
        description: Description of the course
        level: Level of the course
        semester: Semester the course is offered in
        department: Department the course belongs to
        faculty: Faculty the course belongs to
        staff_id: ID of the staff member assigned to the course
        active: Whether the course is active
        
    Returns:
        Course object
    """
    return add_Course(course_code, course_title, description, level, semester, 0, department, faculty, staff_id, active)

def update_course(course_code, course_title, description, level, semester, department, faculty, active=True, staff_id=None):
    """
    Update a course
    
    Args:
        course_code: Code of the course
        course_title: Title of the course
        description: Description of the course
        level: Level of the course
        semester: Semester the course is offered in
        department: Department the course belongs to
        faculty: Faculty the course belongs to
        active: Whether the course is active
        staff_id: ID of the staff member assigned to the course
        
    Returns:
        Course object if found, None otherwise
    """
    return edit_course(course_code, course_title, description, level, semester, department, faculty, active, staff_id)

def delete_course(course_code):
    """
    Delete a course
    
    Args:
        course_code: Code of the course
        
    Returns:
        True if successful, False otherwise
    """
    course = get_course(course_code)
    if course:
        return delete_Course(course)
    return False

def add_Course(courseCode, courseTitle, description, level, semester, aNum, department, faculty, staff_id=None, active=True):
    # Check if courseCode is already in db ie. course was already added
    course = get_course(courseCode)
    if course:
        return course
    
    # Create new course
    course = Course.add_course(courseCode, courseTitle, description, level, semester, department, faculty, staff_id=staff_id, active=active)
    return course

def list_Courses():
    return Course.query.all()

def get_course(courseCode):
    return Course.query.filter_by(course_code=courseCode).first()

def edit_course(courseCode, courseTitle, description, level, semester, department, faculty, active=True, staff_id=None):
    course = get_course(courseCode)
    if course:
        course.course_title = courseTitle
        course.description = description
        course.level = level
        course.semester = semester
        course.department = department
        course.faculty = faculty
        course.active = active
        if staff_id:
            course.staff_id = staff_id
        db.session.commit()
        return course
    return None    

def delete_Course(course):
    db.session.delete(course)
    db.session.commit()
    return True     

def assign_course_to_staff(course_code, staff_id):
    """Assign a course to a staff member"""
    course = get_course(course_code)
    staff = Staff.query.get(staff_id)
    
    if course and staff:
        course.staff_id = staff_id
        db.session.commit()
        return True
    return False

def get_staff_courses(staff_id):
    """Get all courses assigned to a staff member"""
    staff = Staff.query.get(staff_id)
    if staff:
        return staff.get_courses()
    return []

def get_course_staff(course_code):
    """Get the staff member assigned to a course"""
    course = get_course(course_code)
    if course and course.staff_id:
        return Staff.query.get(course.staff_id)
    return None

def get_course_status(course):
    """Get the status of a course based on its active field"""
    return "Active" if course.active else "Inactive"
