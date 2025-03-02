from App.database import db
import enum

class Category(enum.Enum):
    EXAM = "Exam"
    ASSIGNMENT = "Assignment"
    QUIZ = "Quiz"
    PROJECT = "Project"
    DEBATE = "Debate"
    PRESENTATION = "Presentation"
    ORALEXAM = "Oral Exam"
    PARTICIPATION = "Participation"

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    start_week = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_week = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    proctored = db.Column(db.Boolean, nullable=False, default=False)
    category = db.Column(db.Enum(Category), nullable=False)

    # Relationship
    course = db.relationship('Course', back_populates='assessments')

    def __init__(self, name, percentage, start_week, start_day, end_week, end_day, proctored=False, category=None):
        self.name = name
        self.percentage = percentage
        self.start_week = start_week
        self.start_day = start_day
        self.end_week = end_week
        self.end_day = end_day
        self.proctored = proctored
        self.category = category

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'percentage': self.percentage,
            'start_week': self.start_week,
            'start_day': self.start_day,
            'end_week': self.end_week,
            'end_day': self.end_day,
            'proctored': self.proctored,
            'category': self.category
        }
