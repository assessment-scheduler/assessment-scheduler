from typing import List, Optional
from ..database import db
from ..models.course import Course
from ..models.staff import Staff
from ..models.course_lecturer import CourseLecturer

def get_course(course_code:str) -> Optional[Course]:
    return Course.query.filter_by(code=course_code).first()

def get_all_courses() -> List[Course]: 
    return Course.query.all()

def get_all_course_codes() -> List[str]:
    return get_course_codes(get_all_courses())

def get_course_codes(courses :List[Course]) -> List[str]:
    return [course.code for course in courses]

def get_course_name(course_code) -> str | None:
    course: Optional[Course] = get_course(course_code)
    return None if course is None else course.name

def create_course(course_code:str, course_name:str, level:str=None, credits:int=None, semester:str=None)-> bool:
    if get_course(course_code): 
        return False
    new_course:Course = Course(course_code, course_name, level, credits, semester)
    db.session.add(new_course)
    db.session.commit()
    return True

def delete_course(course_code: str) -> bool:
    course: Optional[Course] = get_course(course_code)
    if course is None:
        return False
    db.session.delete(get_course(course_code))
    db.session.commit()
    return True

def update_course(course_code: str, new_course_code:str, new_course_name:str, level:str=None, credits:int=None, semester:str=None) -> bool:
    course: Optional[Course] = get_course(course_code)
    if course is None:
        return False
    course.code = new_course_code
    course.name = new_course_name
    course.level = level
    course.credits = credits
    course.semester = semester
    db.session.commit()
    return True    

def assign_lecturer(lecturer_id: str, course_code: str) -> bool:
    lecturer = Staff.query.filter_by(id=lecturer_id).first()
    course = get_course(course_code)
    if lecturer is None or course is None:
        print(f"could not assign lecturer {lecturer_id} to course {course_code}")
        return False
        
    existing = CourseLecturer.query.filter_by(course_code=course_code, staff_id=lecturer_id).first()
    if existing:
        return True
        
    try:
        assignment = CourseLecturer(course_code=course_code, staff_id=lecturer_id)
        db.session.add(assignment)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def assign_multiple_lecturers(lecturer_ids: List[str], course_code: str) -> bool:
    course = get_course(course_code)
    if course is None:
        print(f"Course {course_code} not found")
        return False
    
    try:
        existing_assignments = CourseLecturer.query.filter_by(course_code=course_code).all()
        for assignment in existing_assignments:
            if str(assignment.staff_id) not in lecturer_ids:
                db.session.delete(assignment)
        
        for lecturer_id in lecturer_ids:
            if not lecturer_id:  
                continue
                
            lecturer = Staff.query.filter_by(id=lecturer_id).first()
            if not lecturer:
                print(f"Lecturer {lecturer_id} not found")
                continue
                
            existing = CourseLecturer.query.filter_by(
                course_code=course_code, 
                staff_id=lecturer_id
            ).first()
            
            if not existing:
                new_assignment = CourseLecturer(course_code=course_code, staff_id=lecturer_id)
                db.session.add(new_assignment)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error assigning lecturers to course: {str(e)}")
        db.session.rollback()
        return False

def get_course_lecturers(course_code: str) -> list[Staff]:
    course = Course.query.filter_by(code=course_code).first()
    if course is None:
        print(f"Course {course_code} not found")
        return None
    
    assignments = course.lecturer_assignments
    print(f"Found {len(assignments)} lecturer assignments for course {course_code}")
    
    lecturers = []
    for assignment in assignments:
        try:
            lecturer = assignment.lecturer
            if lecturer:
                lecturers.append(lecturer)
                print(f"Added lecturer: {lecturer.id}, {lecturer.first_name} {lecturer.last_name}")
            else:
                print(f"Lecturer is None for assignment: {assignment.course_code}, {assignment.staff_id}")
        except Exception as e:
            print(f"Error retrieving lecturer: {str(e)}")
    
    return lecturers

def remove_lecturer(lecturer_id: str, course_code: str) -> bool:
    course = Course.query.filter_by(code=course_code).first()
    if course is None:
        return False
        
    lecturer = Staff.query.filter_by(id=lecturer_id).first()
    if lecturer is None:
        return False
        
    assignment = CourseLecturer.query.filter_by(course_code=course_code, staff_id=lecturer_id).first()
    if assignment is None:
        return False
        
    try:
        db.session.delete(assignment)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def get_lecturer_assignments(lecturer_id: str) -> List[dict]:
    staff = Staff.query.filter_by(id=lecturer_id).first()
    if not staff:
        return []
    
    assignments = []
    for cl in staff.course_assignments:
        course = Course.query.filter_by(code=cl.course_code).first()
        if course:
            assignments.append({
                "course_code": course.code,
                "staff_id": staff.id,
                "course_name": course.name,
                "level": course.level,
                "credits": course.credits,
                "semester": course.semester
            })
    
    return assignments

def get_course_lecturer_count() -> int:
    return CourseLecturer.query.count()
