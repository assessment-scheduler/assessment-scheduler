from ..database import db

class CourseTimetable(db.Model):
    __tablename__ = 'course_timetable'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String(8), db.ForeignKey('course.code'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1 = Monday, 2 = Tuesday, etc.
    time_slot = db.Column(db.String(10), nullable=False)  # Format: "HH:MM"
    
    def __init__(self, course_code, day_of_week, time_slot):
        self.course_code = course_code
        self.day_of_week = day_of_week
        self.time_slot = time_slot
    
    def to_json(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'day_of_week': self.day_of_week,
            'time_slot': self.time_slot
        }
    
    def __repr__(self):
        day_names = {
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday'
        }
        day_name = day_names.get(self.day_of_week, str(self.day_of_week))
        return f'{self.course_code} - {day_name} at {self.time_slot}' 