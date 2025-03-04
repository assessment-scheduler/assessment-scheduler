from App.database import db

class CourseProgramme(db.Model):
    __tablename__ = 'course_programme'
    
    course_code = db.Column(db.String(8), db.ForeignKey('course.course_code'), primary_key=True, nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('programme.p_id'), nullable=False)

    def __init__(self, course_code, p_id):
        self.course_code = course_code
        self.p_id = p_id
    
    def to_json(self):
        return {
            "course_code": self.course_code,
            "p_id": self.p_id
        }  