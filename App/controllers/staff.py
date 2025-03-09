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

def get_staff(id: str) -> Optional[Staff]:
    return Staff.query.get(id)

def get_all_staff() -> List[Staff]:
    return Staff.query.all()

def get_staff_by_email(email: str) -> Optional[Staff]:
    return Staff.query.filter_by(email=email).first()

def update_staff(id: str, email: str, first_name: str, last_name: str) -> bool:
    staff: Optional[Staff] = get_staff(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    staff.first_name = first_name
    staff.last_name = last_name
    staff.email = email
    db.session.commit()
    return True

def delete_staff(id: str) -> bool:
    staff: Optional[Staff] = get_staff(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    db.session.delete(staff)
    db.session.commit()
    return True

def get_staff_courses(staff_id: str) -> List[Course]:
    staff: Optional[Staff] = get_staff(staff_id)
    if not staff:
        print(f"Could not get staff courses, staff {staff_id} not found")
        return []
    return staff.courses

def is_course_lecturer(staff_id: str, course_code: str) -> bool:
    staff: Optional[Staff] = get_staff(staff_id)
    staff_courses: List[Course] = get_staff_courses(staff_id)
    return course_code in [course.code for course in staff_courses]

def validate_staff(email: str, password: str) -> bool:
    staff: Optional[Staff] = get_staff_by_email(email)
    if staff and staff.check_password(password):
        return True
    return False

