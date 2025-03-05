from App.models import Staff, CourseStaff
from App.database import db

def register_staff(firstName, lastName, u_ID, status, email, pwd, department, faculty):
    #Check if email is already used by another lecturer ie. lecturer already registered
    staff = db.session.query(Staff).filter(Staff.email == email).count()

    if staff == 0:
        newLect = Staff.register(firstName, lastName, u_ID, status, email, pwd, department, faculty)
        return newLect
    return None

def login_staff(email, password):
    staff = db.session.query(Staff).filter(Staff.email==email).first()
    if staff != None:
        if staff.check_password(password):
            return staff.login()
    return "Login failed"

def add_CourseStaff(u_ID, courseCode):
    existing_course_staff = CourseStaff.query.filter_by(u_ID=u_ID, courseCode=courseCode).first()
    if existing_course_staff:
        return existing_course_staff  # Return existing CourseStaff if found

    # Create a new CourseStaff object
    new_course_staff = CourseStaff(u_ID=u_ID, courseCode=courseCode)

    # Add and commit to the database
    db.session.add(new_course_staff)
    db.session.commit()

    return new_course_staff

def get_registered_courses(u_ID):
    course_listing = CourseStaff.query.filter_by(u_ID=u_ID).all()
    codes=[]
    for item in course_listing:
        codes.append(item.courseCode)
    return codes

def get_all_staff():
    """Get all staff members"""
    return Staff.get_all_staff()

def get_staff_by_id(staff_id):
    """Get a staff member by ID"""
    return Staff.get_staff_by_id(staff_id)

def update_staff(staff_id, f_name, l_name, status, department, faculty):
    """Update a staff member's details"""
    return Staff.update_staff(staff_id, f_name, l_name, status, department, faculty)

def delete_staff(staff_id):
    """Delete a staff member"""
    return Staff.delete_staff(staff_id)

def get_staff_courses(staff_id):
    """Get all courses assigned to a staff member"""
    staff = Staff.get_staff_by_id(staff_id)
    if staff:
        return staff.get_courses()
    return []

def has_access_to_course(staff_id, course_code):
    """Check if a staff member has access to a course"""
    staff = Staff.get_staff_by_id(staff_id)
    if staff:
        return staff.has_access_to_course(course_code)
    return False

def get_accessible_courses(staff_id):
    """Get all courses a staff member has access to"""
    # Get courses directly assigned to staff
    direct_courses = get_staff_courses(staff_id)
    
    # Get courses assigned through CourseStaff
    from App.models.courseStaff import CourseStaff
    from App.models.course import Course
    
    course_staff_assignments = CourseStaff.query.filter_by(u_id=staff_id).all()
    course_codes = [assignment.course_code for assignment in course_staff_assignments]
    assigned_courses = Course.query.filter(Course.course_code.in_(course_codes)).all()
    
    # Combine both lists (avoiding duplicates)
    all_courses = direct_courses.copy()
    for course in assigned_courses:
        if course not in all_courses:
            all_courses.append(course)
            
    return all_courses