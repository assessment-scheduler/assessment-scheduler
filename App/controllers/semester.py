from App.models import Semester
from App.database import db

def add_sem(startDate,endDate,semNum):
    new_sem = Semester(startDate=startDate,endDate=endDate,semNum=semNum)
    db.session.add(new_sem)
    db.session.commit()
    return new_sem