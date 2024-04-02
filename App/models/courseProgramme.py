from App.database import db

class CourseProgramme(db.Model):
  __tablename__ = 'courseProgramme'

  courseCode = db.Column(db.String(8), db.ForeignKey('course.courseCode'), primary_key=True, nullable = False)
  p_ID = db.Column(db.Integer, db.ForeignKey('programme.p_ID'), primary_key=True, nullable = False)  

  def __init__(self, id, courseCode, p_ID):
    self.courseCode = courseCode
    self.p_ID = p_ID
    
  def to_json(self):
    return {
      "courseCode": self.courseCode,
      "programmeID": self.p_ID
    }  