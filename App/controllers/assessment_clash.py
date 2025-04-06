from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy import desc
from ..models.courseoverlap import CourseOverlap
from ..models.assessment import Assessment
from ..controllers.courseoverlap import get_overlap_value
from ..database import db

def get_top_overlapping_courses(course_code: str, limit: int = 5) -> List[Tuple[str, int]]:
    overlaps = CourseOverlap.query.filter_by(code1=course_code).order_by(desc(CourseOverlap.student_count)).limit(limit).all()
    return [(overlap.code2, overlap.student_count) for overlap in overlaps if overlap.student_count > 0]

def get_nearest_proctored_assessment(course_code: str, target_date: datetime) -> Optional[Assessment]:
    assessments = Assessment.query.filter_by(course_code=course_code, proctored=1).all()
    if not assessments:
        return None
    
    nearest_assessment = None
    min_days_diff = float('inf')
    
    for assessment in assessments:
        if assessment.scheduled:
            days_diff = abs((assessment.scheduled - target_date).days)
            if days_diff < min_days_diff:
                min_days_diff = days_diff
                nearest_assessment = assessment
    
    return nearest_assessment

def calculate_assessment_clash(course_code: str, target_date: datetime) -> Tuple[float, List[Dict]]:
    top_courses = get_top_overlapping_courses(course_code)
    
    if not top_courses:
        return 0, []
    
    clash_details = []
    total_clash_value = 0
    valid_clash_count = 0
    
    for related_course, overlap_count in top_courses:
        nearest_assessment = get_nearest_proctored_assessment(related_course, target_date)
        
        if nearest_assessment and nearest_assessment.scheduled:
            days_diff = abs((nearest_assessment.scheduled - target_date).days)
            clash_value = days_diff * overlap_count
            
            clash_details.append({
                'course_code': related_course,
                'overlap_count': overlap_count,
                'assessment_name': nearest_assessment.name,
                'assessment_date': nearest_assessment.scheduled,
                'days_difference': days_diff,
                'clash_value': clash_value
            })
            
            total_clash_value += clash_value
            valid_clash_count += 1
    
    avg_clash_value = total_clash_value / valid_clash_count if valid_clash_count > 0 else 0
    
    return avg_clash_value, clash_details

def evaluate_assessment_date(course_code: str, target_date: datetime) -> Dict:
    avg_clash_value, clash_details = calculate_assessment_clash(course_code, target_date)
    
    evaluation = "good"
    if avg_clash_value <= 7:
        evaluation = "excellent"
    elif avg_clash_value <= 14:
        evaluation = "good"
    elif avg_clash_value <= 21:
        evaluation = "fair"
    else:
        evaluation = "poor"
    
    return {
        'average_clash_value': avg_clash_value,
        'evaluation': evaluation,
        'details': clash_details
    } 