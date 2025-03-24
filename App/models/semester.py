from ..database import db
from datetime import date
from .solver_factory import get_solver
from sqlalchemy.orm import relationship

class Semester(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date: date = db.Column(db.Date, nullable=False)
    end_date: date = db.Column(db.Date, nullable=False)
    sem_num: int = db.Column(db.Integer, nullable=False, default=1)
    max_assessments: int = db.Column(db.Integer, nullable=False)
    constraint_value: int = db.Column(db.Integer, nullable=False, default=1000)
    active: bool = db.Column(db.Boolean, nullable=False, default=False)
    solver_type: str = db.Column(db.String(50), nullable=False, default='kris')
    
    course_assignments = relationship("SemesterCourse", back_populates="semester", cascade="all, delete-orphan")
    
    def __init__(self, start_date, end_date, sem_num, max_assessments, constraint_value=1000, active=False, solver_type='kris'):
        self.start_date = start_date
        self.end_date = end_date
        self.sem_num = sem_num
        self.max_assessments = max_assessments
        self.constraint_value = constraint_value
        self.active = active
        self.solver_type = solver_type

    def get_solver(self):
        return get_solver(self.solver_type)
        
    @property
    def courses(self):
        return [assignment.course for assignment in self.course_assignments]

    def to_json(self):
        return {
            'id': self.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'sem_num': self.sem_num,
            'max_assessments': self.max_assessments,
            'constraint_value': self.constraint_value,
            'active': self.active,
            'solver_type': self.solver_type,
            'courses': [assignment.course_code for assignment in self.course_assignments]
        }

    def __repr__(self):
        return (f"ID: {self.id}, "
                f"Start Date: {self.start_date}, "
                f"End Date: {self.end_date}, "
                f"Semester Number: {self.sem_num}, "
                f"Max Assessments: {self.max_assessments}, "
                f"Active: {self.active}, "
                f"Solver: {self.solver_type}")
    