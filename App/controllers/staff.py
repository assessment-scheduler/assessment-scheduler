from typing import List, Optional
from App.models import Staff, Course
from App.database import db

def create_staff(id: str, email: str, password: str, first_name: str, last_name: str) -> bool:
    staff: Optional[Staff] = get_staff_by_email(email)
    if staff:
        return False
    else:
        new_staff = Staff(id=id, email=email, password=password, first_name=first_name, last_name=last_name)
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

def update_staff(id: str, email: str, first_name: str, last_name: str) -> bool:
    staff: Optional[Staff] = get_staff_by_id(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    staff.first_name = first_name
    staff.last_name = last_name
    staff.email = email
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

def get_staff_courses(staff_email: str) -> List[Course]:
    staff: Optional[Staff] = get_staff(staff_email)
    if not staff:
        print(f"Could not get staff courses, staff {staff_email} not found")
        return []
    return staff.courses.all()

def is_course_lecturer(staff_id: str, course_code: str) -> bool:
    staff: Optional[Staff] = get_staff_by_id(staff_id)
    if not staff:
        return False
    staff_courses: List[Course] = get_staff_courses(staff.email)
    return course_code in [course.code for course in staff_courses]

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

