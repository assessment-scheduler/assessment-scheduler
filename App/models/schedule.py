from App.database import db

class Schedule(db.Model):
    __tablename__ = 'schedule'

    s_ID = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.Date, nullable = False)
    endDate = db.Column(db.Date, nullable = False)
    startTime = db.Column(db.Time, nullable = False)
    endTime = db.Column(db.Time, nullable = False)