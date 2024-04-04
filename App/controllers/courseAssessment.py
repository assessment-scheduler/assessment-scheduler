from App.models import CourseAssessment
from App.models import Assessment
from App.database import db

def add_CourseAsm(courseCode, courseTitle, description, level, semester, aNum):
    #Add new Assessment to Course
    newAsm = addCourseAsg(courseCode, a_ID, startDate, endDate, startTime, endTime)
    return newAsm

def list_Assessments():
    return Assessment.query.all()  

def get_CourseAsm(id):
    return CourseAssessment.query.filter_by(id=id).first()   

def delete_CourseAsm(courseAsm):
    db.session.delete(courseAsm)
    db.session.commit()
    return True        
     