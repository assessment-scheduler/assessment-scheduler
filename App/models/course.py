from App.database import db

class Course(db.Model):
  __tablename__ = 'course'

  courseCode = db.Column(db.String(8), primary_key=True)
  courseTitle = db.Column(db.String(120), nullable=False)
  description = db.Column(db.String(120), nullable=False)
  level = db.Column(db.Integer, nullable=False)
  semester = db.Column(db.Integer, nullable=False)
  aNum = db.Column(db.Integer, nullable=False, default=0)
  #creates reverse relationship from Course back to Assessment to access assessments assigned to a specific course
  assessmentsAssigned = db.relationship('assessment', backref=db.backref('assessment', lazy='joined'))
