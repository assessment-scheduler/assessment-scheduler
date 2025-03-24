from typing import List, Optional, Union
from ..database import db
from ..models.semester import Semester
from ..models.semester_course import SemesterCourse
from datetime import date, datetime

def parse_date(date_value: Union[str, date]) -> date:
    if isinstance(date_value, str):
        return datetime.fromisoformat(date_value).date()
    return date_value

def get_semester(semester_id: int) -> Optional[Semester]:
    return Semester.query.filter_by(id=semester_id).first()

def get_all_semesters() -> List[Semester]:
    return Semester.query.all()

def create_semester(
    start_date: Union[str, date], 
    end_date: Union[str, date], 
    sem_num: int, 
    max_assessments: int, 
    constraint_value: int = 1000, 
    active: bool = False, 
    solver_type: str = 'kris',
    course_codes: Optional[List[str]] = None
) -> bool:
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    overlapping_semesters = Semester.query.filter(
        (Semester.start_date < end_date) & (Semester.end_date > start_date)).first()
    if overlapping_semesters:
        print(f"Semester {start_date} - {end_date} not created. Overlaps with existing semester(s)")
        return False
        
    semester = Semester(start_date, end_date, sem_num, max_assessments, 
                        constraint_value, active, solver_type)
    db.session.add(semester)
    db.session.commit() 
    
    if course_codes:
        for code in course_codes:
            semester_course = SemesterCourse(semester_id=semester.id, course_code=code)
            db.session.add(semester_course)
        db.session.commit()
    
    return True

def update_semester(
    semester_id: int, 
    start_date: Union[str, date], 
    end_date: Union[str, date], 
    sem_num: int, 
    max_assessments: int, 
    constraint_value: int = 1000, 
    active: bool = False, 
    solver_type: str = 'kris',
    course_codes: Optional[List[str]] = None
) -> bool:
    semester = get_semester(semester_id)
    if not semester:
        return False
        
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    
    overlapping_semesters = Semester.query.filter(
        (Semester.start_date < end_date) & 
        (Semester.end_date > start_date) & 
        (Semester.id != semester_id)
    ).first()
    
    if overlapping_semesters:
        print(f"Semester {start_date} - {end_date} not updated. Overlaps with existing semester(s)")
        return False
    
    semester.start_date = start_date
    semester.end_date = end_date
    semester.sem_num = sem_num
    semester.max_assessments = max_assessments
    semester.constraint_value = constraint_value
    semester.solver_type = solver_type
    
    if active and not semester.active:
        deactivate_all()
        semester.active = True
    
    if course_codes is not None:
        SemesterCourse.query.filter_by(semester_id=semester.id).delete()
        
        for code in course_codes:
            semester_course = SemesterCourse(semester_id=semester.id, course_code=code)
            db.session.add(semester_course)
    
    db.session.commit()
    return True

def get_active_semester() -> Optional[Semester]:
    return Semester.query.filter_by(active=True).first()

def get_semester_duration(semester_id: int) -> int:
    semester: Optional[Semester] = get_semester(semester_id)
    if semester is None:
        print(f"Semester with id {semester_id} not found.")
        return -1
    return (semester.end_date - semester.start_date).days + 1

def deactivate_all() -> None:
    semesters: List[Semester] = Semester.query.filter_by(active=True)
    for semester in semesters:
        semester.active = False
    db.session.commit()

def set_active(semester_id: int) -> bool:
    semester: Optional[Semester] = get_semester(semester_id)
    if semester is None:
        print(f"Could not activate semester: {semester_id} does not exist")
        return False 
    else:
        deactivate_all()
        semester.active = True
        db.session.commit()
        return True

def add_course_to_semester(semester_id: int, course_code: str) -> bool:
    try:
        semester_course = SemesterCourse(semester_id=semester_id, course_code=course_code)
        db.session.add(semester_course)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding course {course_code} to semester {semester_id}: {str(e)}")
        db.session.rollback()
        return False

def remove_course_from_semester(semester_id: int, course_code: str) -> bool:
    try:
        SemesterCourse.query.filter_by(
            semester_id=semester_id, course_code=course_code
        ).delete()
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error removing course {course_code} from semester {semester_id}: {str(e)}")
        db.session.rollback()
        return False
