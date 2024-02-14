from App.database import db
import enum

class Category(enum.Enum):
    EXAM = "Exam"
    ASSIGNMENT = "Assignment"
    QUIZ = "Quiz"
    PROJECT = "Project"

class assessment(db.Model):
    __tablename__ = 'assessment'

    a_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column(db.Enum(Category), nullable = False,)