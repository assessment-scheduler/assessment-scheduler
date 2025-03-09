from App.database import db
from datetime import datetime, date

class Semester(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date: date = db.Column(db.Date, nullable=False)
    end_date: date = db.Column(db.Date, nullable=False)
    sem_num:int = db.Column(db.Integer, nullable=False, default = 1)
    max_assessments: int = db.Column(db.Integer, nullable=False)
    constraint_value:int = db.Column(db.Integer, nullable = False, default = 1000)
    active: bool = db.Column(db.Boolean, nullable = False, default = False)

    def __init__(self, start_date, end_date, sem_num, max_assessments, constraint_value = 1000, active = False, course_overlap_window = 0):
        self.start_date = start_date
        self.end_date = end_date
        self.sem_num = sem_num
        self.max_assessments = max_assessments
        self.constraint_value = constraint_value
        self.active = active
        self.course_overlap_window = course_overlap_window

    def to_json(self):
        return {
            'id': self.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'sem_num': self.sem_num,
            'max_assessments': self.max_assessments,
            'constraint value': self.constraint_value,
            'active' : self.active,
        }

    def __repr__(self):
        return (f"ID: {self.id}, "
                f"Start Date: {self.start_date}, "
                f"End Date: {self.end_date}, "
                f"Semester Number: {self.sem_num}, "
                f"Max Assessments: {self.max_assessments}, "
                f"Active: {self.active}")
    
# Active is set to False to default and controller logic is uesd to ensure only one semester can be active at a time
# Semesters store dates as date objects, but conversion from Strings to Dates happens using the create_semester method in the controller.