from App.models.semester import Semester
from App.models.config import Config
from App.database import db

def add_sem(start_date, end_date, sem_num, max_assessments, K=84, d=3, M=1000):
    """
    Add a new semester (legacy function)
    
    Args:
        start_date: Start date of the semester
        end_date: End date of the semester
        sem_num: Semester number
        max_assessments: Maximum number of assessments allowed per day
        K: Total days in a semester
        d: Number of days between assessments for overlapping courses
        M: Constraint constant
        
    Returns:
        Semester object
    """
    new_sem = Semester(start_date=start_date, end_date=end_date, sem_num=sem_num, max_assessments=max_assessments, K=K, d=d, M=M)
    db.session.add(new_sem)
    db.session.commit()
    return new_sem

def get_current_semester():
    """
    Get the current semester
    
    Returns:
        Current semester number
    """
    config = Config.query.first()
    if not config:
        return None
    
    semester_num = config.semester
    return Semester.query.filter_by(sem_num=semester_num).first()

def create_semester(start_date, end_date, sem_num, max_assessments, K=84, d=3, M=1000):
    """
    Create a new semester
    
    Args:
        start_date: Start date of the semester
        end_date: End date of the semester
        sem_num: Semester number
        max_assessments: Maximum number of assessments allowed per day
        K: Total days in a semester
        d: Number of days between assessments for overlapping courses
        M: Constraint constant
        
    Returns:
        Semester object
    """
    semester = Semester(start_date, end_date, sem_num, max_assessments, K, d, M)
    db.session.add(semester)
    db.session.commit()
    
    # Update current semester in config
    config = Config.query.first()
    if not config:
        config = Config(semester=sem_num)
        db.session.add(config)
    else:
        config.semester = sem_num
    db.session.commit()
    
    return semester