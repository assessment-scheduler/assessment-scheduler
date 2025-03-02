from App.database import db
from datetime import datetime

class SolverConfig(db.Model):
    __tablename__ = 'solver_config'
    id = db.Column(db.Integer, primary_key=True)
    semester_days = db.Column(db.Integer, nullable=False, default=84)  # 12 weeks * 7 days
    min_spacing = db.Column(db.Integer, nullable=False, default=3)
    large_m = db.Column(db.Integer, nullable=False, default=1000)
    weekend_penalty = db.Column(db.Float, nullable=False, default=1.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use string reference to break circular dependency
    solutions = db.relationship('ScheduleSolution', 
        foreign_keys='ScheduleSolution.config_id',
        back_populates='config', 
        cascade='all, delete-orphan',
        lazy='dynamic')
    
    def __init__(self, semester_days=84, min_spacing=3, large_m=1000, weekend_penalty=1.5):
        self.semester_days = semester_days
        self.min_spacing = min_spacing
        self.large_m = large_m
        self.weekend_penalty = weekend_penalty
    
    def get_json(self):
        return {
            'id': self.id,
            'semester_days': self.semester_days,
            'min_spacing': self.min_spacing,
            'large_m': self.large_m,
            'weekend_penalty': self.weekend_penalty
        }