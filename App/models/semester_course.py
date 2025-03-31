from ..database import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class SemesterCourse(db.Model):
    __tablename__ = 'semester_course'
    
    semester_id = Column(Integer, ForeignKey('semester.id'), primary_key=True)
    course_code = Column(String(8), ForeignKey('course.code'), primary_key=True)
    
    semester = relationship("Semester", back_populates="course_assignments")
    course = relationship("Course", back_populates="semester_assignments") 