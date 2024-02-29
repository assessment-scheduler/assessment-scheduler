from App.database import db

class CourseStaff(db.Model):
  __tablename__ = 'courseStaff'

  u_ID = db.Column(db.Integer, db.ForeignKey('staff.u_ID'), primary_key= True, nullable=False)
  courseCode = db.Column(db.String(120), db.ForeignKey('course.courseCode'), primary_key= True, nullable=False)
