from App.database import db

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sem_num = db.Column(db.Integer, nullable=False)
    max_assessments = db.Column(db.Integer, nullable=False)
    K = db.Column(db.Integer, nullable=False)  # Total days in a semester
    d = db.Column(db.Integer, nullable=False)  # Number of days between assessments for overlapping courses
    M = db.Column(db.Integer, nullable=False)  # Constraint constant

    def __init__(self, start_date, end_date, sem_num, max_assessments, K=84, d=3, M=1000):
        self.start_date = start_date
        self.end_date = end_date
        self.sem_num = sem_num
        self.max_assessments = max_assessments
        self.K = K
        self.d = d
        self.M = M

    def to_json(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "sem_num": self.sem_num,
            "max_assessments": self.max_assessments,
            "K": self.K,
            "d": self.d,
            "M": self.M
        }