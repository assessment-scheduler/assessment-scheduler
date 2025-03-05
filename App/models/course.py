from App.database import db
from .class_size import ClassSize

class Course(db.Model):
    __tablename__ = 'course'
  
    course_code = db.Column(db.String(9), primary_key=True)
    course_title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(120), nullable=False)
    faculty = db.Column(db.String(120), nullable=False)
    pre_reqs = db.Column(db.String(120), nullable=True)
    p_id = db.Column(db.Integer, nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.u_id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    assessments = db.relationship('Assessment', back_populates='course')
    staff = db.relationship('Staff', back_populates='courses')

    def __init__(self, course_code, course_title, description, level, semester, department, faculty, pre_reqs=None, p_id=None, staff_id=None, active=True):
        self.course_code = course_code
        self.course_title = course_title
        self.description = description
        self.level = level
        self.semester = semester
        self.department = department
        self.faculty = faculty
        self.pre_reqs = pre_reqs
        self.p_id = p_id
        self.staff_id = staff_id
        self.active = active

    def to_json(self):
        return {
            'course_code': self.course_code,
            'course_title': self.course_title,
            'description': self.description,
            'level': self.level,
            'semester': self.semester,
            'department': self.department,
            'faculty': self.faculty,
            'pre_reqs': self.pre_reqs,
            'p_id': self.p_id,
            'staff_id': self.staff_id,
            'active': self.active
        }

    @staticmethod
    def add_course(course_code, course_title, description, level, semester, department, faculty, pre_reqs=None, p_id=None, staff_id=None, active=True):
        course = Course(
            course_code=course_code,
            course_title=course_title,
            description=description,
            level=level,
            semester=semester,
            department=department,
            faculty=faculty,
            pre_reqs=pre_reqs,
            p_id=p_id,
            staff_id=staff_id,
            active=active
        )
        db.session.add(course)
        db.session.commit()
        return course