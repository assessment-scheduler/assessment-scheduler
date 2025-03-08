from App.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Course(db.Model):
    __tablename__ = 'course'
    code = db.Column(db.String(8), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    lecturer_id = mapped_column(db.ForeignKey("staff.id"), nullable=True)   
    lecturer = relationship("Staff", back_populates="courses", lazy="joined")

    def __init__(self, code, name):
        self.code = code.upper()
        self.name = name

    def __repr__(self):
        return f"{self.code} : {self.name}"