from App.database import db
from datetime import datetime

class ScheduleSolution(db.Model):
    __tablename__ = 'schedule_solution'
    
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('solver_config.id'), nullable=False)
    u_star = db.Column(db.Float, nullable=False)
    y_star = db.Column(db.Float, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use string references to break circular dependencies
    config = db.relationship('SolverConfig', 
        foreign_keys=[config_id],
        back_populates='solutions')
    
    assignments = db.relationship('ScheduledAssessment', 
        back_populates='solution', 
        cascade='all, delete-orphan',
        lazy='dynamic')
    
    def __init__(self, config_id, u_star, y_star, probability):
        self.config_id = config_id
        self.u_star = u_star
        self.y_star = y_star
        self.probability = probability
    
    def to_json(self):
        return {
            'id': self.id,
            'config_id': self.config_id,
            'u_star': self.u_star,
            'y_star': self.y_star,
            'probability': self.probability,
            'created_at': self.created_at.isoformat(),
            'assignments': [sa.to_json() for sa in self.assignments]
        }