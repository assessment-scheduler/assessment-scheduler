from App.database import db

class ClassSize(db.Model):
    __tablename__ = 'class_sizes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    other_course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    
    # Relationships
    course = db.relationship('Course', 
        foreign_keys=[course_id],
        back_populates='class_sizes')
    other_course = db.relationship('Course',
        foreign_keys=[other_course_id])
    
    def __init__(self, size):
        self.size = size
        
    def get_json(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'other_course_id': self.other_course_id,
            'size': self.size
        } 

    @classmethod
    def initialize_matrix_for_course(cls, new_course):
        """Initialize matrix entries with 0 for a new course"""
        # Get all existing courses
        from .course import Course
        existing_courses = Course.query.all()
        
        # Create entries for new course with all existing courses (including itself)
        for other_course in existing_courses:
            # Create entry for new_course -> other_course
            class_size = cls(size=0)
            class_size.course = new_course
            class_size.other_course_id = other_course.id
            db.session.add(class_size)
            
            # Create entry for other_course -> new_course if it's not the same course
            if other_course.id != new_course.id:
                reverse_size = cls(size=0)
                reverse_size.course = other_course
                reverse_size.other_course_id = new_course.id
                db.session.add(reverse_size)
        
        db.session.commit()

def get_overlapping_students(course1, course2):
    """Returns the number of students taking both courses"""
    # This is a simplified version - you'll need to implement based on your data structure
    overlap = ClassSize.query.filter(
        (ClassSize.course_id == course1.id) & 
        (ClassSize.student_id.in_(
            ClassSize.query.with_entities(ClassSize.student_id)
            .filter(ClassSize.course_id == course2.id)
        ))
    ).count()
    return overlap