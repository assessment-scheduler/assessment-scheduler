"""
Linear Programming Problem model
"""
from datetime import datetime
import json
from App.database import db

class LinearProblem(db.Model):
    """
    Model for storing linear programming problems
    """
    __tablename__ = 'linear_problems'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    objective = db.Column(db.String(500), nullable=False)
    objective_type = db.Column(db.String(10), nullable=False)  # 'max' or 'min'
    constraints = db.Column(db.Text, nullable=False)  # Stored as JSON
    variables = db.Column(db.Text, nullable=False)  # Stored as JSON
    solution = db.Column(db.Text)  # Stored as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, objective, objective_type, constraints, variables):
        self.name = name
        self.objective = objective
        self.objective_type = objective_type
        self.constraints = json.dumps(constraints)
        self.variables = json.dumps(variables)
    
    def get_constraints(self):
        """
        Returns the constraints as a list
        """
        return json.loads(self.constraints)
    
    def get_variables(self):
        """
        Returns the variables as a list
        """
        return json.loads(self.variables)
    
    def get_solution(self):
        """
        Returns the solution as a dictionary
        """
        if self.solution:
            return json.loads(self.solution)
        return None
    
    def set_solution(self, solution):
        """
        Sets the solution
        """
        self.solution = json.dumps(solution)
    
    def to_dict(self):
        """
        Returns the problem as a dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'objective': self.objective,
            'objective_type': self.objective_type,
            'constraints': self.get_constraints(),
            'variables': self.get_variables(),
            'solution': self.get_solution(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
