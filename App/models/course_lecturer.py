from ..database import db
from sqlalchemy.orm import relationship

class CourseLecturer(db.Model):
    __tablename__ = 'course_lecturers'
    course_code = db.Column(db.String(8), db.ForeignKey('course.code'), primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)
    course = relationship("Course", back_populates="lecturer_assignments")
    lecturer = relationship("Staff", back_populates="course_assignments") 