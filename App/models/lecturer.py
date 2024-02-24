from App.database import db
from .user import User

class Lecturer(User):
  __tablename__ = 'lecturer'
  lect_ID = db.Column(db.String, primary_key= True)
  fName = db.Column(db.String(120), nullable=False)
  lName = db.Column(db.String(120), nullable=False)
  status = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), nullable=False)
  cNum = db.Column(db.Integer, nullable=False, default=0)
  #creates reverse relationship from Lecturer back to Course to access courses assigned to a specific lecturer
  coursesAssigned = db.relationship('course', backref=db.backref('courses', lazy='joined'))

  def __init__(self, fName, lName, lect_ID, status, email, password):
    super().__init__(password)
    self.lect_ID = lect_ID
    self.fName = fName
    self.lName = lName
    self.status = status
    self.email = email
    if str(Lecturer.query.count()) < 10:
      self.lect_ID = "L0" + str(Lecturer.query.count() + 1)
    else:
      self.lect_ID = "L" + str(Lecturer.query.count() + 1)

  def get_id(self):
    return self.lect_ID 

  def to_json(self):
    return {
        "staffID": self.lect_ID,
        "firstname": self.fName,
        "lastname": self.lName,
        "status": self.status,
        "email": self.email,
        "coursesNum": self.cNum,
        "coursesAssigned": [course.to_json() for course in self.coursesAssigned]
    }

  #Lecturers must register before using system
  def register(firstName, lastName, staffID, status, email, pwd):
    newLect = Lecturer(firstName, lastName, staffID, status, email, pwd)
    db.session.add(newLect)  #add to db
    db.session.commit()
    return newLect  
