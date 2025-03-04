from App.database import db
from .course import Course
from .staff import Staff

class CourseStaff(db.Model):
  __tablename__ = 'courseStaff'

  id = db.Column(db.Integer, primary_key= True, autoincrement=True)
  u_id = db.Column(db.Integer, db.ForeignKey('staff.u_id'), nullable=False)
  course_code = db.Column(db.String(120), db.ForeignKey('course.course_code'), nullable=False)

def __init__(self, u_id, course_code):
  self.u_id = u_id
  self.course_code = course_code

def to_json(self):
  return{
    "u_ID":self.u_id,
    "courseCode":self.course_code,
  }

#Add new CourseStaff
def add_course_staff(self):
  db.session.add(self)
  db.session.commit()
