from App.models import Staff, CourseStaff, Course
from App.database import db

def register_staff(firstName, lastName, u_ID, status, email, pwd, department, faculty):
    """
    Register a new staff member
    
    Args:
        firstName: First name of the staff member
        lastName: Last name of the staff member
        u_ID: Unique ID for the staff member
        status: Status/role of the staff member
        email: Email address of the staff member
        pwd: Password for the staff member
        department: Department the staff member belongs to
        faculty: Faculty the staff member belongs to
        
    Returns:
        The newly created staff member or None if registration fails
    """
    # Check if email is already used by another staff member
    existing_staff = Staff.get_staff_by_email(email)
    if existing_staff:
        return None
        
    # Create new staff member
    new_staff = Staff(
        f_name=firstName,
        l_name=lastName,
        u_id=u_ID,
        status=status,
        email=email,
        password=pwd,
        department=department,
        faculty=faculty
    )
    
    # Add to database
    db.session.add(new_staff)
    db.session.commit()
    
    return new_staff

def login_staff(email, password):
    """
    Authenticate a staff member
    
    Args:
        email: Email address of the staff member
        password: Password of the staff member
        
    Returns:
        The authenticated staff member or an error message
    """
    staff = Staff.get_staff_by_email(email)
    if staff and staff.check_password(password):
        return staff
    return None

def add_CourseStaff(staff_id, course_code):
    """
    Assign a staff member to a course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        The newly created CourseStaff object or the existing one
    """
    # Check if assignment already exists
    existing_course_staff = CourseStaff.query.filter_by(u_ID=staff_id, course_code=course_code).first()
    if existing_course_staff:
        return existing_course_staff
    
    # Create new assignment
    new_course_staff = CourseStaff(u_ID=staff_id, course_code=course_code)
    db.session.add(new_course_staff)
    db.session.commit()
    
    return new_course_staff

def get_registered_courses(staff_id):
    """
    Get all courses a staff member is registered for
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        List of course codes
    """
    course_assignments = CourseStaff.query.filter_by(u_ID=staff_id).all()
    return [assignment.course_code for assignment in course_assignments]

def get_all_staff():
    """
    Get all staff members
    
    Returns:
        List of all staff members
    """
    return Staff.get_all_staff()

def get_staff_by_id(staff_id):
    """
    Get a staff member by ID
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        The staff member or None if not found
    """
    return Staff.get_staff_by_id(staff_id)

def update_staff(staff_id, f_name, l_name, status, department, faculty):
    """
    Update a staff member's details
    
    Args:
        staff_id: ID of the staff member
        f_name: New first name
        l_name: New last name
        status: New status/role
        department: New department
        faculty: New faculty
        
    Returns:
        The updated staff member or None if not found
    """
    staff = get_staff_by_id(staff_id)
    if not staff:
        return None
    
    staff.f_name = f_name
    staff.l_name = l_name
    staff.status = status
    staff.department = department
    staff.faculty = faculty
    
    db.session.commit()
    return staff

def delete_staff(staff_id):
    """
    Delete a staff member
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        True if successful, False otherwise
    """
    staff = get_staff_by_id(staff_id)
    if not staff:
        return False
    
    db.session.delete(staff)
    db.session.commit()
    return True

def get_staff_courses(staff_id):
    """
    Get all courses a staff member has access to
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        List of courses
    """
    staff = get_staff_by_id(staff_id)
    if not staff:
        return []
    
    # Get courses directly assigned to staff
    direct_courses = list(staff.courses)
    
    # Get courses assigned through CourseStaff
    course_staff_assignments = staff.course_staff.all()
    course_codes = [assignment.course_code for assignment in course_staff_assignments]
    indirect_courses = Course.query.filter(Course.course_code.in_(course_codes)).all()
    
    # Combine and remove duplicates
    all_courses = direct_courses + [course for course in indirect_courses if course not in direct_courses]
    return all_courses

def has_access_to_course(staff_id, course_code):
    """
    Check if a staff member has access to a specific course
    
    Args:
        staff_id: ID of the staff member
        course_code: Code of the course
        
    Returns:
        True if the staff member has access, False otherwise
    """
    staff = get_staff_by_id(staff_id)
    if not staff:
        return False
    
    return staff.has_access_to_course(course_code)

def get_accessible_courses(staff_id):
    """
    Get all courses a staff member has access to
    
    Args:
        staff_id: ID of the staff member
        
    Returns:
        List of courses
    """
    return get_staff_courses(staff_id)