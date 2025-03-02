from App.database import db
from datetime import datetime

class ScheduleSolution(db.Model):
    __tablename__ = 'schedule_solutions'
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('solver_config.id'), nullable=False)
    U_star = db.Column(db.Float, nullable=False)
    Y_star = db.Column(db.Float, nullable=False)
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
    
    def __init__(self, config_id, U_star, Y_star, probability):
        self.config_id = config_id
        self.U_star = U_star
        self.Y_star = Y_star
        self.probability = probability
    
    def get_json(self):
        return {
            'id': self.id,
            'config_id': self.config_id,
            'U_star': self.U_star,
            'Y_star': self.Y_star,
            'probability': self.probability,
            'created_at': self.created_at.isoformat(),
            'assignments': [sa.get_json() for sa in self.assignments]
        }