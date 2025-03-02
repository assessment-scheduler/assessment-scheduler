from App.database import db
from .class_size import ClassSize

class Course(db.Model):
    __tablename__ = 'course'
  
    course_code = db.Column(db.String(9), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    a_num = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, course_code, name, description, level, semester, a_num):
        self.course_code = course_code
        self.name = name
        self.description = description
        self.level = level
        self.semester = semester
        self.a_num = a_num

    def to_json(self):
        return {
            "course_code": self.course_code,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "semester": self.semester,
            "a_num": self.a_num,
        }

    @staticmethod
    def add_course(course_code, name, description, level, semester, a_num):
        new_course = Course(course_code, name, description, level, semester, a_num)
        db.session.add(new_course)  # add to db
        db.session.commit()
        return new_course