from ..database import db
from sqlalchemy.orm import mapped_column, relationship

class Course(db.Model):
    __tablename__ = 'course'
    code = db.Column(db.String(8), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    level = db.Column(db.String(1), nullable=True)
    credits = db.Column(db.Integer, nullable=True)
    semester = db.Column(db.String(10), nullable=True)
    lecturer_id = mapped_column(db.ForeignKey("staff.id"), nullable=True)   
    lecturer = relationship("Staff", back_populates="courses", lazy="joined")

    def __init__(self, code, name, level=None, credits=None, semester=None):
        self.code = code.upper()
        self.name = name
        self.level = level
        self.credits = credits
        self.semester = semester

    def __repr__(self):
        return f"{self.code} : {self.name}"
    
    def to_json(self):
        return {
            'code': self.code,
            'name': self.name,
            'level': self.level,
            'credits': self.credits,
            'semester': self.semester,
            'lecturer_id': self.lecturer_id
        }
    
    
