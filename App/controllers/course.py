from typing import List, Optional
from App.database import db
from App.models import Course, Staff

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

def create_course(course_code:str, course_name:str)-> bool:
    if get_course(course_code): 
        return False
    new_course:Course = Course(course_code, course_name)
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

def update_course(course_code: str, course_name: str, new_course_code:str, new_course_name:str) -> bool:
    course: Optional[Course] = get_course(course_code)
    if course is None:
        return False
    course.code = new_course_code
    course.name = new_course_name
    db.session.commit()
    return True    

def assign_lecturer(lecturer_id: str, course_code : str) -> bool:
        lecturer = Staff.query.filter_by(id = lecturer_id).first()
        course: Optional[Course] = get_course(course_code)
        if lecturer is None or course is None:
            print(f"could not assign lecturer {lecturer_id} to course {course_code}")
            return False
        else:
            course.lecturer_id = lecturer.id
            course.lecturer = lecturer
            db.session.commit()
            return True
