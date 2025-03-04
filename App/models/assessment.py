from App.database import db
from enum import Enum

class Category(Enum):
    EXAM = "EXAM"
    QUIZ = "QUIZ"
    PROJECT = "PROJECT"
    ASSIGNMENT = "ASSIGNMENT"

class Assessment(db.Model):
    __tablename__ = 'assessment'
    
    a_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(9), db.ForeignKey('course.course_code'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    start_week = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_week = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    proctored = db.Column(db.Boolean, nullable=False, default=False)
    category = db.Column(db.Enum(Category), nullable=False)

    # Relationship
    course = db.relationship('Course', back_populates='assessments')

    def __init__(self, course_id, name, percentage, start_week, start_day, end_week, end_day, proctored, category):
        self.course_id = course_id
        self.name = name
        self.percentage = percentage
        self.start_week = start_week
        self.start_day = start_day
        self.end_week = end_week
        self.end_day = end_day
        self.proctored = proctored
        self.category = category

    def to_json(self):
        return {
            "a_id": self.a_id,
            "course_id": self.course_id,
            "name": self.name,
            "percentage": self.percentage,
            "start_week": self.start_week,
            "start_day": self.start_day,
            "end_week": self.end_week,
            "end_day": self.end_day,
            "proctored": self.proctored,
            "category": self.category.value
        }
