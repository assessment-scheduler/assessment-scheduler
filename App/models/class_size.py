from App.database import db

class ClassSize(db.Model):
    __tablename__ = 'class_size'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(9), db.ForeignKey('course.course_code'), nullable=False)
    other_course_code = db.Column(db.String(9), db.ForeignKey('course.course_code'), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    
    # Relationships
    course = db.relationship('Course', foreign_keys=[course_code])
    other_course = db.relationship('Course', foreign_keys=[other_course_code])
    
    def __init__(self, course_code, other_course_code, size):
        self.course_code = course_code
        self.other_course_code = other_course_code
        self.size = size

    def to_json(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'other_course_code': self.other_course_code,
            'size': self.size
        }

    @staticmethod
    def add_class_size(course_code, other_course_code, size):
        class_size = ClassSize(course_code, other_course_code, size)
        db.session.add(class_size)
        db.session.commit()
        return class_size

    @staticmethod
    def add_reverse_class_size(new_course_code, other_course_code, size):
        reverse_size = ClassSize(new_course_code, other_course_code, size)
        db.session.add(reverse_size)
        db.session.commit()
        return reverse_size

    @classmethod
    def initialize_matrix_for_course(cls, new_course):
        """Initialize matrix entries with 0 for a new course"""
        # Get all existing courses
        from .course import Course
        existing_courses = Course.query.all()
        
        # Create entries for new course with all existing courses (including itself)
        for other_course in existing_courses:
            # Create entry for new_course -> other_course
            class_size = cls(course_code=new_course.course_code, other_course_code=other_course.course_code, size=0)
            class_size.course = new_course
            class_size.other_course = other_course
            db.session.add(class_size)
            
            # Create entry for other_course -> new_course if it's not the same course
            if other_course.course_code != new_course.course_code:
                reverse_size = cls(course_code=other_course.course_code, other_course_code=new_course.course_code, size=0)
                reverse_size.course = other_course
                reverse_size.other_course = new_course
                db.session.add(reverse_size)
        
        db.session.commit()

def get_overlapping_students(course1, course2):
    """Returns the number of students taking both courses"""
    # This is a simplified version - you'll need to implement based on your data structure
    overlap = ClassSize.query.filter(
        (ClassSize.course_code == course1.course_code) & 
        (ClassSize.other_course_code == course2.course_code)
    ).first()
    
    return overlap.size if overlap else 0