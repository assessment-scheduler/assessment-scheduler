from App.models import CourseAssessment
from App.models import Assessment
from App.database import db

def add_CourseAsm(courseCode, a_ID, startDate, endDate, startTime, endTime):
    #Add new Assessment to Course
    # newAsm = addCourseAsg(courseCode, a_ID, startDate, endDate, startTime, endTime)
    # return newAsm
    newAsg = CourseAssessment(courseCode, a_ID, startDate, endDate, startTime, endTime)
    db.session.add(newAsg)  #add to db
    db.session.commit()
    return newAsg

def list_Assessments():
    return Assessment.query.all()  

def get_Assessment_id(aType):
    assessment=Assessment.query.filter_by(category=aType).first()
    return assessment.a_ID

def get_CourseAsm_id(id):
    return CourseAssessment.query.filter_by(id=id).first()   

def get_CourseAsm_code(code):
    return CourseAssessment.query.filter_by(courseCode=code).all()

def delete_CourseAsm(courseAsm):
    db.session.delete(courseAsm)
    db.session.commit()
    return True        
     