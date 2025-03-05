from App.models import CourseAssessment
from App.models import Assessment
from App.models import Course
from App.database import db

def add_course_assessment(course_code, a_id, start_date, end_date, start_time, end_time, clash_detected):
    #Add new Assessment to Course
    # newAsm = add_course_asg(course_code, a_id, start_date, end_date, start_time, end_time)
    # return newAsm
    new_asg = CourseAssessment(course_code, a_id, start_date, end_date, start_time, end_time, clash_detected)
    db.session.add(new_asg)  #add to db
    db.session.commit()
    return new_asg

def list_assessments():
    return Assessment.query.all()  

def get_assessment_id(a_type):
    assessment = Assessment.query.filter_by(category=a_type).first()
    return assessment.a_id

def get_assessment_type(id):
    assessment = Assessment.query.filter_by(a_id=id).first()
    return assessment.category.name

def get_course_assessment_by_id(id):
    return CourseAssessment.query.filter_by(id=id).first()   

def get_course_assessment_by_code(code):
    return CourseAssessment.query.filter_by(course_code=code).all()

def get_course_assessment_by_level(level):
    courses = Course.query.filter_by(level=level).all()
    assessments = []
    for c in courses:
        assessments = assessments + get_course_assessment_by_code(c.course_code)
    return assessments

def delete_course_assessment(course_asm):
    db.session.delete(course_asm)
    db.session.commit()
    return True        
     
# Commenting out clash detection
'''
def get_clashes():
    return CourseAssessment.query.filter_by(clash_detected=True).all()
'''
