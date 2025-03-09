import flask_login
from App.database import db
from .user import User
import enum
from flask_login import UserMixin
from sqlalchemy.orm import Mapped,mapped_column
class Staff(User):
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key = True)
    first_name = mapped_column(db.String(25), nullable = False, unique = False)
    last_name = mapped_column(db.String(25), nullable = False, unique = False)
    courses = db.relationship("Course", back_populates = "lecturer", lazy="dynamic")

    def __init__(self, id:str, email: str, password: str, first_name: str, last_name: str):
        super().__init__(id,email,password)
        self.first_name = first_name
        self.last_name = last_name

    def to_json(self):
        return {
            "staff_ID": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "courses": [course.course_code for course in self.courses]
        }

    def __repr__(self):
        return f"Staff(id={self.id}, email={self.email})"

    # @staticmethod
    # def register(f_name, l_name, id, status, email, password, department, faculty):
    #     staff = Staff(f_name=f_name, l_name=l_name, id=id, status=status, email=email, password=password, department=department, faculty=faculty)
    #     db.session.add(staff)
    #     db.session.commit()
    #     return staff

    # def login(self):
    #     return flask_login.login_user(self)

  #Lecturers must register before using system

