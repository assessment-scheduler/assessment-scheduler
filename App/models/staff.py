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
    department = db.Column(db.String(120), nullable=False)
    faculty = db.Column(db.String(120), nullable=False)
    
    # Relationship with courses - one staff can have many courses
    courses = db.relationship('Course', back_populates='staff', lazy='dynamic')

    def __init__(self, f_name, l_name, u_id, status, email, password, department, faculty):
        super().__init__(u_id, password, email)
        self.f_name = f_name
        self.l_name = l_name
        self.status = status
        self.department = department
        self.faculty = faculty

    def get_id(self):
        return self.u_id

    def to_json(self):
        return {
            "staff_ID": self.u_id,
            "firstName": self.f_name,
            "lastName": self.l_name,
            "status": self.status,
            "email": self.email,
            "department": self.department,
            "faculty": self.faculty,
            "courses": [course.course_code for course in self.courses]
        }

    def __repr__(self):
        return f"Staff(id={self.u_id}, email={self.email})"

    @staticmethod
    def register(f_name, l_name, u_id, status, email, password, department, faculty):
        new_staff = Staff(f_name, l_name, u_id, status, email, password, department, faculty)
        db.session.add(new_staff)
        db.session.commit()
        return new_staff

    def login(self):
        return flask_login.login_user(self)

    def assign_course(self, course):
        """Assign a course to this staff member"""
        course.staff_id = self.u_id
        db.session.commit()
        return True
        
    def get_courses(self):
        """Get all courses assigned to this staff member"""
        return self.courses.all()

    def has_access_to_course(self, course_code):
        """Check if staff member has access to a course"""
        # Check direct assignment through Course model
        direct_assignment = self.courses.filter_by(course_code=course_code).first()
        if direct_assignment:
            return True
            
        # Check assignment through CourseStaff model
        from .courseStaff import CourseStaff
        course_staff = CourseStaff.query.filter_by(u_id=self.u_id, course_code=course_code).first()
        return course_staff is not None

    @staticmethod
    def get_all_staff():
        """Get all staff members"""
        return Staff.query.all()
    
    @staticmethod
    def get_staff_by_id(staff_id):
        """Get a staff member by ID"""
        return Staff.query.get(staff_id)
    
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

