from App.database import db

class Lecturer(User):
  __tablename__ = 'lecturer'
  lect_ID = db.Column(db.String, primary_key= True)
  fName = db.Column(db.String(120), nullable=False)
  lName = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), nullable=False)
  cNum = db.Column(db.Integer, nullable=False, default=0)
  #creates reverse relationship from Lecturer back to Course to access courses assigned to a specific lecturer
  coursesAssigned = db.relationship('course', backref=db.backref('courses', lazy='joined'))

  def __init__(self, fName, lName, email, password):
    super().__init__(password)
    self.fName = fName
    self.lName = lName
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
        "email": self.email,
        "coursesNum": self.cNum,
        "coursesAssigned": [course.to_json() for course in self.coursesAssigned]
    }

  #Lecturers must register before using system
  def register(self, fName, lName, email, password):
    newLect = Lecturer(self, fName, lName, email, password)
    db.session.add(newLect)  #add to db
    db.session.commit()
    return newLect  
