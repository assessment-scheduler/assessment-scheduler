from typing import List, Optional
from App.database import db
from ..models.semester import Semester
from datetime import date, datetime

def parse_date(date) -> date | str:
    if isinstance(date, str):
        return datetime.fromisoformat(date).date()
    return date

def get_semester(semester_id:int) -> Optional[Semester]:
    return Semester.query.filter_by(id = semester_id).first()

def get_all_semesters() -> list[Semester]:
    return Semester.query.all()

def create_semester(start_date, end_date, sem_num:int, max_assessments:int, constraint_value:int = 1000, active:bool = False) -> bool:
    start_date: date | str = parse_date(start_date)
    end_date: date | str = parse_date(end_date)

    overlapping_semesters: Optional[Semester] = Semester.query.filter(
        (Semester.start_date < end_date) & (Semester.end_date > start_date)).first()
    if overlapping_semesters:
        print(f"Semester {start_date} - {end_date} not created. Overlaps with existing semester(s)")
        return False
    semester = Semester(start_date, end_date, sem_num, max_assessments, constraint_value, active)
    db.session.add(semester)
    db.session.commit()
    return True

def get_active_semester() -> Optional[Semester]:
    return Semester.query.filter_by(active = True).first()

def get_semester_duration(semester_id:int) -> int:
    semester: Optional[Semester] = get_semester(semester_id)
    if semester is None:
        print(f"Semester with id {semester_id} not found.")
        return -1
    return (semester.end_date - semester.start_date).days

def deactivate_all() -> None:
    semesters: List[Semester] = Semester.query.filter_by(active = True)
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
        semester.active  = True
        db.session.commit()
