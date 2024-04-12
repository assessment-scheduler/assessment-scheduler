from App.models import CourseAssessment
from App.models import Assessment
from App.models import Course
from App.database import db

def add_CourseAsm(courseCode, a_ID, startDate, endDate, startTime, endTime, clashDetected):
    #Add new Assessment to Course
    # newAsm = addCourseAsg(courseCode, a_ID, startDate, endDate, startTime, endTime)
    # return newAsm
    newAsg = CourseAssessment(courseCode, a_ID, startDate, endDate, startTime, endTime, clashDetected)
    db.session.add(newAsg)  #add to db
    db.session.commit()
    return newAsg

def list_Assessments():
    return Assessment.query.all()  

def get_Assessment_id(aType):
    assessment=Assessment.query.filter_by(category=aType).first()
    return assessment.a_ID

def get_Assessment_type(id):
    assessment=Assessment.query.filter_by(a_ID=id).first()
    return assessment.category.name

def get_CourseAsm_id(id):
    return CourseAssessment.query.filter_by(id=id).first()   

def get_CourseAsm_code(code):
    return CourseAssessment.query.filter_by(courseCode=code).all()

def get_CourseAsm_level(level):
    courses = Course.query(level=level).all()
    assessments=[]
    for c in courses:
        assessments = assessments + get_CourseAsm_code(c)
    return assessments

def delete_CourseAsm(courseAsm):
    db.session.delete(courseAsm)
    db.session.commit()
    return True        
     
def get_clashes():
    return CourseAssessment.query.filter_by(clashDetected=True).all()
