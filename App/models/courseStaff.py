from App.database import db
from .course import Course
from .staff import Staff

class CourseStaff(db.Model):
  __tablename__ = 'courseStaff'

  id = db.Column(db.Integer, primary_key= True, autoincrement=True)
  u_ID = db.Column(db.Integer, db.ForeignKey('staff.u_ID'), nullable=False)
  courseCode = db.Column(db.String(120), db.ForeignKey('course.courseCode'), nullable=False)

def __init__(self, u_ID, courseCode):
  self.u_ID = u_ID
  self.courseCode = courseCode

def to_json(self):
  return{
    "u_ID":self.u_ID,
    "courseCode":self.courseCode,
  }

#Add new CourseStaff
def addCourseStaff(self):
  db.session.add(self)
  db.session.commit()
