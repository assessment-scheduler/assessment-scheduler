from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy import desc
from ..models.courseoverlap import CourseOverlap
from ..models.assessment import Assessment
from ..controllers.courseoverlap import get_overlap_value
from ..controllers import get_active_semester
from ..database import db

def get_top_overlapping_courses(course_code: str, limit: int = 5) -> List[Tuple[str, int]]:
    overlaps = CourseOverlap.query.filter_by(code1=course_code).order_by(desc(CourseOverlap.student_count)).limit(limit).all()
    return [(overlap.code2, overlap.student_count) for overlap in overlaps if overlap.student_count > 0]

def get_nearest_proctored_assessment(course_code: str, target_date: datetime) -> Optional[Assessment]:
    assessments = Assessment.query.filter_by(course_code=course_code, proctored=1).all()
    if not assessments:
        return None
    
    semester = get_active_semester()
    if not semester:
        return None
    
    nearest_assessment = None
    min_days_diff = float('inf')
    
    for assessment in assessments:
        if assessment.scheduled and semester.start_date <= assessment.scheduled <= semester.end_date:
            days_diff = abs((assessment.scheduled - target_date).days)
            if days_diff < min_days_diff:
                min_days_diff = days_diff
                nearest_assessment = assessment
    
    return nearest_assessment

def calculate_assessment_clash(course_code: str, target_date: datetime) -> Tuple[float, List[Dict]]:
    top_courses = get_top_overlapping_courses(course_code)
    
    if not top_courses:
        return 0, []
    
    semester = get_active_semester()
    if not semester:
        return 0, []
    
    if target_date < semester.start_date or target_date > semester.end_date:
        return 0, []
    
    clash_details = []
    total_clash_value = 0
    valid_clash_count = 0
    highest_clash_value = 0
    
    for related_course, overlap_count in top_courses:
        nearest_assessment = get_nearest_proctored_assessment(related_course, target_date)
        
        if nearest_assessment and nearest_assessment.scheduled:
            days_diff = abs((nearest_assessment.scheduled - target_date).days)
            
            if days_diff < 3:
                day_factor = 1.5   
            elif days_diff < 7:
                day_factor = 1.0  
            elif days_diff < 14:
                day_factor = 0.7  
            elif days_diff < 21:
                day_factor = 0.4  
            else:
                day_factor = 0.2   
            
            proctored_multiplier = 1.5 if nearest_assessment.proctored else 1.0
            close_date_multiplier = 1.5 if days_diff < 3 else 1.0
            
            clash_value = (day_factor * overlap_count * proctored_multiplier * close_date_multiplier) / 30
            
            highest_clash_value = max(highest_clash_value, clash_value)
            
            clash_value = min(clash_value, 10)
            
            clash_details.append({
                'course_code': related_course,
                'overlap_count': overlap_count,
                'assessment_name': nearest_assessment.name,
                'assessment_date': nearest_assessment.scheduled,
                'days_difference': days_diff,
                'clash_value': clash_value,
                'day_factor': day_factor,
                'is_proctored': nearest_assessment.proctored
            })
            
            total_clash_value += clash_value
            valid_clash_count += 1
    
    avg_clash_value = total_clash_value / valid_clash_count if valid_clash_count > 0 else 0
    
    final_clash_value = (highest_clash_value * 0.7) + (avg_clash_value * 0.3) if valid_clash_count > 0 else 0
    
    final_clash_value = min(final_clash_value, 10)
    
    return final_clash_value, clash_details

def evaluate_assessment_date(course_code: str, target_date: datetime) -> Dict:
    clash_value, clash_details = calculate_assessment_clash(course_code, target_date)
    
    evaluation = "good"
    if clash_value <= 2.0:
        evaluation = "excellent"
    elif clash_value <= 5.0:
        evaluation = "good"
    else:
        evaluation = "poor"
    
    highest_clash = max([detail['clash_value'] for detail in clash_details]) if clash_details else 0
    if highest_clash > 4.0 and evaluation != "poor":
        evaluation = "poor"  
    elif highest_clash > 3.0 and evaluation == "excellent":
        evaluation = "good"  
    
    return {
        'average_clash_value': clash_value,
        'highest_clash_value': highest_clash,
        'evaluation': evaluation,
        'details': clash_details
    } 