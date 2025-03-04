from App.database import db
from datetime import datetime

class LPConstraint(db.Model):
    __tablename__ = 'lp_constraint'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('linear_problem.id'), nullable=False)
    expression = db.Column(db.String(500), nullable=False)
    relation_type = db.Column(db.String(10), nullable=False)  # '<=', '>=', '='
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    problem = db.relationship('LinearProblem', back_populates='constraints')

    def __init__(self, expression, relation_type):
        self.expression = expression
        self.relation_type = relation_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_json(self):
        return {
            'id': self.id,
            'problem_id': self.problem_id if hasattr(self, 'problem_id') else None,
            'expression': self.expression,
            'relation_type': self.relation_type,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') else None
        }
