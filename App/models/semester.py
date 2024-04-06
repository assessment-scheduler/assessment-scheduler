from App.database import db

class Semester(db.Model):
    __tablename__='semester'
    id = db.Column(db.Integer, primary_key= True, autoincrement=True)
    startDate = db.Column(db.Date,nullable=False)
    endDate = db.Column(db.Date,nullable=False)
    semNum = db.Column(db.Integer,nullable=False)

def __init__(self, startDate, endDate, semNum):
    self.startDate = startDate
    self.endDate = endDate
    self.semNum = semNum

def to_json(self):
    return{
        "id":self.id,
        "startDate":self.startDate,
        "endDate":self.endDate,
        "semNum":self.semNum
    }