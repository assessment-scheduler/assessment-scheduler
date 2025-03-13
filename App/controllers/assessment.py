from datetime import timedelta
from typing import Any, Dict, List, Optional
from ..controllers.course import get_course_codes
from ..controllers.staff import get_staff_courses
from ..models.assessment import Assessment
from ..database import db

def get_assessment(course_code, name)-> Optional[Assessment]:
    return Assessment.query.filter_by(course_code=course_code, name=name).first()

def get_assessment_by_id(id) -> Optional[Assessment]:
    return Assessment.query.get(id)

def get_all_assessments() -> List[Assessment]:
    return Assessment.query.all()

def get_num_assessments(course_code:str) -> int:
    assessments = get_assessments_by_course(course_code)
    return len(assessments)

def get_assessment_dictionary_by_course(course_code) -> Dict[str,List[Assessment]]:
    course_assessments: List[Assessment] = Assessment.query.filter_by(course_code = course_code).all()
    if course_assessments == []:
        return {'code':course_code, 'assessments':[]}
    json_list: List[dict[str, int]] = [assessment.to_json() for assessment in course_assessments]
    course_dict: dict[str, Any] = {'code' : course_code, 'assessments': json_list}
    return course_dict

def get_assessments_by_course(course_code: str) -> List[Assessment]:
    return Assessment.query.filter_by(course_code = course_code).all()

def get_assessments_by_lecturer(staff_email: str) -> List[Assessment]:
    staff_courses = get_staff_courses(staff_email)
    course_codes = get_course_codes(staff_courses)
    
    all_assessments = []
    course_assessments_map = {}
    for course_code in course_codes:
        assessments = get_assessments_by_course(course_code)
        all_assessments.extend(assessments)
    return all_assessments


def create_assessment(course_code:str, name:str, percentage:int, start_week:int, start_day:int, end_week:int, end_day:int, proctored:int)-> bool:
    assessment: Optional[Assessment] =  get_assessment(course_code,name)
    if assessment:
        return False
    newassessment = Assessment(course_code=course_code, name=name, percentage=percentage, start_week=start_week, start_day=start_day, end_week=end_week, end_day=end_day, proctored=proctored)
    db.session.add(newassessment)
    db.session.commit()
    return True

def update_assessment(id:str, name:str, percentage:int, start_week:int, start_day:int, end_week:int, end_day:int, proctored:int, scheduled:str = None)-> bool:
    assessment: Optional[Assessment] =  Assessment.query.get(id)
    if assessment is None:
        return False
    assessment.name = name
    assessment.percentage = percentage
    assessment.start_week = start_week
    assessment.start_day = start_day
    assessment.end_week = end_week
    assessment.end_day = end_day
    assessment.proctored = proctored
    if scheduled is not None:
        assessment.scheduled = scheduled
    db.session.commit()
    return True


def schedule_assessment(semester,schedule_date:int,course_code:str,name:str)-> bool:
    assessment: Optional[Assessment] = get_assessment(course_code,name)
    assessment.scheduled = schedule_date
    db.session.commit()
    return True

def delete_assessment(course_code, name) -> bool:
    assessment: Optional[Assessment] =  get_assessment(course_code,name)
    if assessment is None:
        return False
    db.session.delete(assessment)
    db.session.commit()
    return True

def delete_assessment_by_id(assessment_id) -> bool:
    assessment: Optional[Assessment] =  Assessment.query.get(int(assessment_id))
    if assessment is None:
        return False
    db.session.delete(assessment)
    db.session.commit()
    return True
