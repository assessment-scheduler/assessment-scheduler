from ..database import db
from .user import User
from sqlalchemy.orm import Mapped,mapped_column
class Staff(User):
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key = True)
    first_name = mapped_column(db.String(25), nullable = False, unique = False)
    last_name = mapped_column(db.String(25), nullable = False, unique = False)
    department = mapped_column(db.String(50), nullable = True, unique = False)
    faculty = mapped_column(db.String(50), nullable = True, unique = False)
    courses = db.relationship("Course", back_populates = "lecturer", lazy="dynamic")

    def __init__(self, id:str, email: str, password: str, first_name: str, last_name: str, department: str = None, faculty: str = None):
        super().__init__(id,email,password)
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.faculty = faculty

    def to_json(self):
        return {
            "staff_ID": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "department": self.department,
            "faculty": self.faculty,
            "courses": [course.code for course in self.courses]
        }

    def __repr__(self):
        return f"Staff(id={self.id}, email={self.email})"
