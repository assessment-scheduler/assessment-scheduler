from App.models import Course, Staff
from App.database import db
from flask import session

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
