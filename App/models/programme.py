from App.database import db

class Programme(db.Model):
  __tablename__ = 'programme'

  p_id = db.Column(db.Integer, primary_key = True, nullable=False, autoincrement=True)
  p_name = db.Column(db.String(100), nullable = False)
  #creates reverse relationship from Programme back to Course to access courses offered in a programme
  programme_courses = db.relationship('CourseProgramme', backref='courses', lazy='joined' )

  def __init__(self, p_name):
    self.p_name = p_name

  def to_json(self):
    return {
    "p_id" : self.p_id,
    "name" : self.p_name
    } 