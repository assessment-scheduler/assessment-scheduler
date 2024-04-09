from App.models import Semester
from App.database import db

def add_sem(startDate,endDate,semNum,maxAssessments):
    new_sem = Semester(startDate=startDate,endDate=endDate,semNum=semNum,maxAssessments=maxAssessments)
    db.session.add(new_sem)
    db.session.commit()
    return new_sem