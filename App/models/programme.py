from App.database import db

class programme(db.model):
  __tablename__ = 'Programme'

  p_ID = db.Column(db.Integer, primary_key = True)
  p_name = db.Column(db.String(100), nullable = False)
  programmeCourses = db.relationship('coursePrograme', backref = 'programme' )