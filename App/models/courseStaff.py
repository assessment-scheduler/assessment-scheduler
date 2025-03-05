from App.database import db
from .course import Course
from .staff import Staff

class CourseStaff(db.Model):
  __tablename__ = 'courseStaff'

  id = db.Column(db.Integer, primary_key= True, autoincrement=True)
  u_id = db.Column(db.Integer, db.ForeignKey('staff.u_id'), nullable=False)
  course_code = db.Column(db.String(120), db.ForeignKey('course.course_code'), nullable=False)
  
  # Define relationships
  staff = db.relationship('Staff', backref=db.backref('course_assignments', lazy='dynamic'))
  course = db.relationship('Course', backref=db.backref('staff_assignments', lazy='dynamic'))

  def __init__(self, u_id, course_code):
    self.u_id = u_id
    self.course_code = course_code

  def to_json(self):
    return{
      "u_ID": self.u_id,
      "courseCode": self.course_code,
    }

  #Add new CourseStaff
  def add_course_staff(self):
    db.session.add(self)
    db.session.commit()
    
  @staticmethod
  def get_staff_courses(staff_id):
    """Get all courses assigned to a staff member"""
    assignments = CourseStaff.query.filter_by(u_id=staff_id).all()
    course_codes = [assignment.course_code for assignment in assignments]
    return Course.query.filter(Course.course_code.in_(course_codes)).all()
    
  @staticmethod
  def get_course_staff(course_code):
    """Get all staff assigned to a course"""
    assignments = CourseStaff.query.filter_by(course_code=course_code).all()
    staff_ids = [assignment.u_id for assignment in assignments]
    return Staff.query.filter(Staff.u_id.in_(staff_ids)).all()
    
  @staticmethod
  def assign_staff_to_course(staff_id, course_code):
    """Assign a staff member to a course"""
    # Check if assignment already exists
    existing = CourseStaff.query.filter_by(u_id=staff_id, course_code=course_code).first()
    if existing:
      return existing
      
    # Create new assignment
    assignment = CourseStaff(u_id=staff_id, course_code=course_code)
    db.session.add(assignment)
    db.session.commit()
    return assignment
    
  @staticmethod
  def remove_staff_from_course(staff_id, course_code):
    """Remove a staff member from a course"""
    assignment = CourseStaff.query.filter_by(u_id=staff_id, course_code=course_code).first()
    if assignment:
      db.session.delete(assignment)
      db.session.commit()
      return True
    return False
