import flask_login
from App.database import db
from .user import User
import enum
from flask_login import UserMixin

class Status(enum.Enum):
    PTINSTRUCT = "Part-Time Instructor"
    INSTRUCTOR = "Instructor"
    HOD = "Head of Department"
    LECTURER = "Lecturer"
    TA = "Teaching Assisstant"
    TUTOR = "Tutor"
    PTTUTOR = "Part-Time Tutor"

class Staff(User, UserMixin):
    __tablename__ = 'staff'

    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), primary_key=True)
    f_name = db.Column(db.String(120), nullable=False)
    l_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    courses_assigned = db.Column(db.String(120), nullable=True)

    def __init__(self, f_name, l_name, u_id, status, email, password):
        super().__init__(u_id, password, email)
        self.f_name = f_name
        self.l_name = l_name
        self.status = status
        self.courses_assigned = []

    def get_id(self):
        return self.u_id

    def to_json(self):
        return {
            "staff_ID": self.u_id,
            "firstName": self.f_name,
            "lastName": self.l_name,
            "status": self.status,
            "email": self.email,
            "coursesAssigned": self.courses_assigned
        }

    def __repr__(self):
        return f"Staff(id={self.u_id}, email={self.email})"

    @staticmethod
    def register(f_name, l_name, u_id, status, email, password):
        new_staff = Staff(f_name, l_name, u_id, status, email, password)
        db.session.add(new_staff)
        db.session.commit()
        return new_staff

    def login(self):
        return flask_login.login_user(self)

  #Lecturers must register before using system

