from App.database import db

class courseProgramme(db.model):
  __tablename__ = 'courseProgramme'

  courseCode = db.Column(db.String(8), db.ForeignKey('course.courseCode'), nullable = False)
  p_ID = db.Column(db.Integer, db.ForeignKey('programme.p_ID'), nullable = False)
  year = db.Column(db.year, nullable = False, default = 2024)
  