from typing import List
from App.models import Staff, CourseStaff, Course
from App.database import db

def create_staff(id,email, password, first_name, last_name) -> bool:
    staff = get_staff_by_email(email)
    if staff:
        return False
    else:
        new_staff = Staff(id = id,email=email, password=password, first_name=first_name, last_name=last_name)
        db.session.add(new_staff)
        db.session.commit()
        return True

def get_staff(id) -> Staff | None:
    return Staff.query.get(id)

def get_all_staff() -> List[Staff]:
    return Staff.query.all()

def get_staff_by_email(email)-> Staff | None:
    return Staff.query.filter_by(email=email).first()

def get_all_staff() -> List[Staff]:
    return Staff.query.all()

def update_staff(id, email, first_name, last_name) -> bool:
    staff = get_staff(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    staff.first_name = first_name
    staff.last_name = last_name
    staff.email = email
    db.session.commit()
    return True

def delete_staff(id) -> bool:
    staff: Staff | None = get_staff(id)
    if staff is None:
        print(f"Could not find staff member: {id}")
        return False
    db.session.delete(staff)
    db.session.commit()
    return True

def get_staff_courses(staff_id : str) -> List[Course]:
    staff = get_staff(staff_id)
    if not staff:
        print(f"Could not get staff courses, staff {staff_id} not found")
        return []
    return staff.courses


def is_course_lecturer(staff_id, course_code) -> bool:
    staff = get_staff(staff_id)
    if not staff:
        return False
    else :
        staff_courses = get_staff_courses(staff_id)
        return course_code in staff_courses

    default_assignments = [
        ("COMP1601", "Permanand", "Mohan"),
        ("COMP1600", "Diana", "Ragbir"),
        ("COMP1603", "Michael", "Hosein"),
        ("COMP1602", "Shareeda", "Mohammed"),
        ("INFO1600", "Phaedra", "Mohammed"),
        ("INFO1601", "Phaedra", "Mohammed"),
        ("FOUN1105", "Phaedra", "Mohammed"),
    ]
    
    results = []
    
    for course_code, first_name, last_name in default_assignments:
        # Find the staff member by name
        staff = Staff.query.filter_by(f_name=first_name, l_name=last_name).first()
        if not staff:
            results.append((course_code, f"{first_name} {last_name}", False))
            continue
            
        # Find the course
        course = Course.query.filter_by(course_code=course_code).first()
        if not course:
            results.append((course_code, f"{first_name} {last_name}", False))
            continue
            
        # Check if assignment already exists
        existing = CourseStaff.query.filter_by(staff_id=staff.id, course_code=course_code).first()
        if existing:
            results.append((course_code, f"{first_name} {last_name}", True))
            continue
            
        # Create new assignment
        try:
            new_assignment = CourseStaff(staff_id=staff.id, course_code=course_code)
            db.session.add(new_assignment)
            db.session.commit()
            results.append((course_code, f"{first_name} {last_name}", True))
        except Exception as e:
            db.session.rollback()
            results.append((course_code, f"{first_name} {last_name}", False))
    
    return results