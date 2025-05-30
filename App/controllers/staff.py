from typing import List, Optional
from ..models import Staff, Course
from ..database import db
from ..models.course_lecturer import CourseLecturer

def create_staff(id: str, email: str, password: str, first_name: str, last_name: str, department: str = None, faculty: str = None) -> bool:
    staff: Optional[Staff] = get_staff_by_email(email)
    if staff:
        return False
    else:
        new_staff = Staff(id=id, email=email, password=password, first_name=first_name, last_name=last_name, department=department, faculty=faculty)
        db.session.add(new_staff)
        db.session.commit()
        return True

def get_staff(email:str) -> Optional[Staff]:
    return Staff.query.filter_by(email = email).first()

def get_staff_by_id(id:str) -> Optional[Staff]:
    return Staff.query.filter_by(id = id).first()

def get_all_staff() -> List[Staff]:
    return Staff.query.all()

def get_staff_by_email(email: str) -> Optional[Staff]:
    return Staff.query.filter_by(email=email).first()

def update_staff(id: str, email: str, first_name: str, last_name: str, department: str = None, faculty: str = None) -> bool:
    staff: Optional[Staff] = get_staff_by_id(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    staff.first_name = first_name
    staff.last_name = last_name
    staff.email = email
    staff.department = department
    staff.faculty = faculty
    db.session.commit()
    return True

def delete_staff(id: str) -> bool:
    staff: Optional[Staff] = get_staff_by_id(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    db.session.delete(staff)
    db.session.commit()
    return True

def get_staff_courses(staff_id_or_email: str) -> List[Course]:
    staff: Optional[Staff] = get_staff(staff_id_or_email)
    if not staff:
        staff = get_staff_by_id(staff_id_or_email)
    if not staff:
        print(f"Could not get staff courses, staff {staff_id_or_email} not found")
        return []
    
    courses = []
    for assignment in staff.course_assignments:
        try:
            course = assignment.course
            if course:
                courses.append(course)
                print(f"Added course: {course.code}, {course.name}")
            else:
                print(f"Course is None for assignment: {assignment.course_code}, {assignment.staff_id}")
        except Exception as e:
            print(f"Error retrieving course: {str(e)}")
    
    return courses

def is_course_lecturer(staff_id: str, course_code: str) -> bool:
    assignment = CourseLecturer.query.filter_by(
        staff_id=staff_id,
        course_code=course_code
    ).first()
    
    return assignment is not None

def validate_staff(email: str, password: str) -> bool:
    staff: Optional[Staff] = get_staff_by_email(email)
    if staff and staff.check_password(password):
        return True
    return False

def assign_course_to_staff(staff_id: str, course_code: str) -> bool:
    staff: Optional[Staff] = get_staff_by_id(staff_id)
    course = Course.query.filter_by(code=course_code).first()
    
    if not staff or not course:
        print(f"Could not assign course, staff {staff_id} or course {course_code} not found")
        return False
    
    course.lecturer_id = staff.id
    try:
        db.session.commit()
        print(f"Course {course_code} assigned to staff {staff_id}")
        return True
    except Exception as e:
        print(f"Error assigning course: {str(e)}")
        db.session.rollback()
        return False

def associate_with_semester(staff_id, semester_id, active=True):
    """Associate staff member with a specific semester and set participation status"""
    from ..models.staff import Staff, staff_semester
    from ..models.semester import Semester
    from ..database import db
    
    staff = Staff.query.get(staff_id)
    semester = Semester.query.get(semester_id)
    
    if not staff or not semester:
        return False
        
    exists = any(s.id == semester_id for s in staff.semesters)
    
    if not exists:
        staff.semesters.append(semester)
        
    db.session.execute(
        staff_semester.update().
        where(staff_semester.c.staff_id == staff_id).
        where(staff_semester.c.semester_id == semester_id).
        values(active=active)
    )
    
    db.session.commit()
    return True

def get_staff_courses_in_active_semester(staff_id_or_email: str) -> List[Course]:
    from .semester import get_active_semester
    
    staff = get_staff(staff_id_or_email)
    if not staff:
        staff = get_staff_by_id(staff_id_or_email)
    if not staff:
        print(f"Could not get staff courses, staff {staff_id_or_email} not found")
        return []
    
    active_semester = get_active_semester()
    if not active_semester:
        print("No active semester found")
        return []
    
    all_staff_courses = []
    for assignment in staff.course_assignments:
        try:
            course = assignment.course
            if course:
                all_staff_courses.append(course)
        except Exception as e:
            print(f"Error retrieving course: {str(e)}")
    
    semester_course_codes = [sc.course_code for sc in active_semester.course_assignments]
    active_semester_courses = [course for course in all_staff_courses if course.code in semester_course_codes]
    
    return active_semester_courses

