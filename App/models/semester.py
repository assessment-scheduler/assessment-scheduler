from App.database import db

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sem_num = db.Column(db.Integer, nullable=False)
    max_assessments = db.Column(db.Integer, nullable=False)

    def __init__(self, start_date, end_date, sem_num, max_assessments):
        self.start_date = start_date
        self.end_date = end_date
        self.sem_num = sem_num
        self.max_assessments = max_assessments

    def to_json(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "sem_num": self.sem_num,
            "max_assessments": self.max_assessments
        }