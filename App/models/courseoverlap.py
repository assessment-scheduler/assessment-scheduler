from App.database import db


class CourseOverlap(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code1: str = db.Column(db.String(8), db.ForeignKey("course.code"), nullable=False)
    code2: str = db.Column(db.String(8), db.ForeignKey("course.code"), nullable=False)
    student_count: int = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, code1, code2, student_count):
        self.code1 = code1
        self.code2 = code2
        self.student_count = student_count

    def __repr__(self):
        return f"{self.student_count}"
