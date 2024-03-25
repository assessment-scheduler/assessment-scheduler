from App.database import db

class CourseStaff(db.Model):
  __tablename__ = 'courseStaff'

  u_ID = db.Column(db.Integer, db.ForeignKey('staff.u_ID'), primary_key= True, nullable=False)
  courseCode = db.Column(db.String(120), db.ForeignKey('course.courseCode'), primary_key= True, nullable=False)

def __init__(self,u_ID,courseCode):
  self.u_ID=u_ID
  self.courseCode=courseCode

def to_json(self):
  return{
    "u_ID":self.u_ID,
    "courseCode":self.courseCode,
  }

#Add new CourseStaff
def addCourseStaff(self):
  db.session.add(self)
  db.session.commit()
