from App.database import db
class Assessment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String(8), db.ForeignKey('course.code'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    percentage = db.Column(db.Integer, nullable = False, default = 0)
    proctored = db.Column(db.Integer, nullable = False, default = 0)
    start_week = db.Column(db.Integer, nullable = True)
    start_day = db.Column(db.Integer, nullable = True)
    end_week = db.Column(db.Integer, nullable = True)
    end_day = db.Column(db.Integer, nullable = True)
    scheduled = db.Column(db.Date, nullable = True)


    def __init__(self, course_code, name, percentage, start_week, start_day, end_week, end_day, proctored):
        self.course_code = course_code
        self.name = name
        self.percentage = percentage
        self.start_week = start_week
        self.start_day = start_day
        self.end_week = end_week
        self.end_day = end_day
        self.proctored = proctored
    
    def to_json(self):
        return {
            'name': self.name,
            'percentage': self.percentage,
            'start_week': self.start_week,
            'start_day': self.start_day,
            'end_week': self.end_week,
            'end_day': self.end_day,
            'proctored': self.proctored,
            'scheduled' : self.scheduled
        }
    
    def __repr__(self):
        return f'{self.course_code} {self.name}: {self.percentage}% Scheduled for { "N/A" if self.scheduled is None else self.scheduled}'
    