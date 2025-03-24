from ..database import db
from .user import User
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean

staff_semester = Table(
    'staff_semester',
    db.metadata,
    Column('staff_id', Integer, ForeignKey('staff.id'), primary_key=True),
    Column('semester_id', Integer, ForeignKey('semester.id'), primary_key=True),
    Column('active', Boolean, default=True, nullable=False)
)

class Staff(User):
    __tablename__ = 'staff'
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)
    first_name = mapped_column(db.String(25), nullable=False, unique=False)
    last_name = mapped_column(db.String(25), nullable=False, unique=False)
    department = mapped_column(db.String(50), nullable=True, unique=False)
    faculty = mapped_column(db.String(50), nullable=True, unique=False)
    course_assignments = relationship("CourseLecturer", back_populates="lecturer", cascade="all, delete-orphan")
    semesters = relationship("Semester", secondary=staff_semester, backref="staff_members")

    def __init__(self, id:str, email: str, password: str, first_name: str, last_name: str, department: str = None, faculty: str = None):
        super().__init__(id,email,password)
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.faculty = faculty

    def is_active_for_semester(self, semester_id):
        """Check if staff is active for a specific semester"""
        for semester in self.semesters:
            if semester.id == semester_id:
                assoc = db.session.query(staff_semester).filter_by(
                    staff_id=self.id, semester_id=semester_id
                ).first()
                return assoc and assoc.active
        return False

    def to_json(self):
        return {
            "staff_ID": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "department": self.department,
            "faculty": self.faculty,
            "courses": [assignment.course.code for assignment in self.course_assignments],
            "active_semesters": [s.id for s in self.semesters if self.is_active_for_semester(s.id)]
        }

    def __repr__(self):
        return f"Staff(id={self.id}, email={self.email})"
