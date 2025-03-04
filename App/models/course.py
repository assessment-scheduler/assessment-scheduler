from App.database import db
from .class_size import ClassSize

class Course(db.Model):
    __tablename__ = 'course'
  
    course_code = db.Column(db.String(9), primary_key=True)
    course_title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    pre_reqs = db.Column(db.String(120), nullable=True)
    p_id = db.Column(db.Integer, nullable=True)
    
    # Relationships
    assessments = db.relationship('Assessment', back_populates='course')

    def __init__(self, course_code, course_title, description, level, semester, pre_reqs=None, p_id=None):
        self.course_code = course_code
        self.course_title = course_title
        self.description = description
        self.level = level
        self.semester = semester
        self.pre_reqs = pre_reqs
        self.p_id = p_id

    def to_json(self):
        return {
            "course_code": self.course_code,
            "course_title": self.course_title,
            "description": self.description,
            "level": self.level,
            "semester": self.semester,
            "pre_reqs": self.pre_reqs,
            "p_id": self.p_id,
        }

    @staticmethod
    def add_course(course_code, course_title, description, level, semester, pre_reqs=None, p_id=None):
        new_course = Course(course_code, course_title, description, level, semester, pre_reqs, p_id)
        db.session.add(new_course)  # add to db
        db.session.commit()
        return new_course