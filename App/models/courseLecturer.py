from App.database import db

class courseLecturer(db.Model):
  __tablename__ = 'courseLecturer'

  u_ID = db.Column(db.Integer, db.ForeignKey('lecturer.u_ID'), primary_key= True, nullable=False)
  courseCode = db.Column(db.String(120), db.ForeignKey('course.courseCode'), primary_key= True, nullable=False)
