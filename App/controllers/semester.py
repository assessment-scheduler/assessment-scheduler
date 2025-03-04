from App.models.semester import Semester
from App.database import db

def add_sem(start_date, end_date, sem_num, max_assessments):
    new_sem = Semester(start_date=start_date, end_date=end_date, sem_num=sem_num, max_assessments=max_assessments)
    db.session.add(new_sem)
    db.session.commit()
    return new_sem