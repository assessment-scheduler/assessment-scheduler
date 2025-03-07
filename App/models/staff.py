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
    TA = "Teaching Assistant"
    TUTOR = "Tutor"
    PTTUTOR = "Part-Time Tutor"

class Staff(User, UserMixin):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    f_name = db.Column(db.String(120), nullable=False)
    l_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    faculty = db.Column(db.String(120), nullable=False)
    
    # Relationship with courses - one staff can have many courses
    courses = db.relationship('Course', back_populates='staff', lazy='dynamic')
    # Relationship with course staff assignments
    course_staff = db.relationship('CourseStaff', back_populates='staff_member', foreign_keys='CourseStaff.staff_id', overlaps="course_assignments")

    def __init__(self, f_name, l_name, id, status, email, password, department, faculty):
        super().__init__(id, password, email)
        self.f_name = f_name
        self.l_name = l_name
        self.status = status
        self.department = department
        self.faculty = faculty

    def get_id(self):
        return self.id

    def to_json(self):
        return {
            "staff_ID": self.id,
            "firstName": self.f_name,
            "lastName": self.l_name,
            "status": self.status,
            "email": self.email,
            "department": self.department,
            "faculty": self.faculty,
            "courses": [course.course_code for course in self.courses]
        }

    def __repr__(self):
        return f"Staff(id={self.id}, email={self.email})"

    @staticmethod
    def register(f_name, l_name, id, status, email, password, department, faculty):
        staff = Staff(f_name=f_name, l_name=l_name, id=id, status=status, email=email, password=password, department=department, faculty=faculty)
        db.session.add(staff)
        db.session.commit()
        return staff

    def login(self):
        return flask_login.login_user(self)

    def assign_course(self, course):
        """Assign a course to this staff member"""
        course.staff_id = self.id
        db.session.commit()
        return True
        
    def get_courses(self):
        """Get all courses assigned to this staff member"""
        return self.courses.all()

    def has_access_to_course(self, course_code):
        """Check if staff has access to a specific course"""
        # Direct course assignment
        if self.courses.filter_by(course_code=course_code).first():
            return True
        
        # Assignment through CourseStaff
        if self.course_staff.filter_by(course_code=course_code).first():
            return True
        
        return False

    @staticmethod
    def get_all_staff():
        return Staff.query.all()
    
    @staticmethod
    def get_staff_by_id(staff_id):
        return Staff.query.get(staff_id)
    
    @staticmethod
    def get_staff_by_email(email):
        return Staff.query.filter_by(email=email).first()
    
    @staticmethod
    def update_staff(staff_id, f_name, l_name, status, department, faculty):
        """Update a staff member's details"""
        staff = Staff.query.get(staff_id)
        if staff:
            staff.f_name = f_name
            staff.l_name = l_name
            staff.status = status
            staff.department = department
            staff.faculty = faculty
            db.session.commit()
            return staff
        return None
    
    @staticmethod
    def delete_staff(staff_id):
        """Delete a staff member"""
        staff = Staff.query.get(staff_id)
        if staff:
            db.session.delete(staff)
            db.session.commit()
            return True
        return False

  #Lecturers must register before using system

