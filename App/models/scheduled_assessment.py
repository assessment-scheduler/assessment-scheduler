from App.database import db

class ScheduledAssessment(db.Model):
    __tablename__ = 'scheduled_assignments'
    id = db.Column(db.Integer, primary_key=True)
    solution_id = db.Column(db.Integer, db.ForeignKey('schedule_solutions.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    scheduled_day = db.Column(db.Integer, nullable=False)
    scheduled_week = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    
    # Relationships with string references
    solution = db.relationship('ScheduleSolution', back_populates='assignments')
    assessment = db.relationship('Assessment')
    
    def __init__(self, solution_id, assessment_id, scheduled_day):
        self.solution_id = solution_id
        self.assessment_id = assessment_id
        self.scheduled_day = scheduled_day
        self.scheduled_week = (scheduled_day - 1) // 7 + 1
        self.day_of_week = (scheduled_day - 1) % 7 + 1
        
    def get_json(self):
        return {
            'id': self.id,
            'solution_id': self.solution_id,
            'assessment_id': self.assessment_id,
            'scheduled_day': self.scheduled_day,
            'scheduled_week': self.scheduled_week,
            'day_of_week': self.day_of_week,
            'assessment': self.assessment.get_json() if self.assessment else None
        }