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
    __tablename__ = 'assessment'

    a_ID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    category = db.Column(db.Enum(Category), nullable=False)

    def __init__(self, category):
        self.category = category

    def to_json(self):
        return {
        "a_ID" : self.a_ID,
        "category" : self.category
        }     
