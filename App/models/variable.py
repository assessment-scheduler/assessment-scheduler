from App.database import db
from datetime import datetime

class LPVariable(db.Model):
    __tablename__ = 'lp_variable'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('linear_problem.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    lower_bound = db.Column(db.Float, nullable=True)
    upper_bound = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    problem = db.relationship('LinearProblem', back_populates='variables')

    def __init__(self, name, lower_bound=None, upper_bound=None):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_json(self):
        return {
            'id': self.id,
            'problem_id': self.problem_id if hasattr(self, 'problem_id') else None,
            'name': self.name,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') else None
        }
