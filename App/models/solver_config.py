from App.database import db
from datetime import datetime

class SolverConfig(db.Model):
    __tablename__ = 'solver_config'
    
    id = db.Column(db.Integer, primary_key=True)
    semester_days = db.Column(db.Integer, nullable=False, default=84)
    min_spacing = db.Column(db.Integer, nullable=False, default=3)
    large_m = db.Column(db.Integer, nullable=False, default=1000)
    weekend_penalty = db.Column(db.Float, nullable=False, default=1.5)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    solutions = db.relationship('ScheduleSolution',
        foreign_keys='ScheduleSolution.config_id',
        back_populates='config',
        lazy='dynamic')
    
    def __init__(self, semester_days=84, min_spacing=3, large_m=1000, weekend_penalty=1.5):
        self.semester_days = semester_days
        self.min_spacing = min_spacing
        self.large_m = large_m
        self.weekend_penalty = weekend_penalty
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_json(self):
        return {
            'id': self.id,
            'semester_days': self.semester_days,
            'min_spacing': self.min_spacing,
            'large_m': self.large_m,
            'weekend_penalty': self.weekend_penalty,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }