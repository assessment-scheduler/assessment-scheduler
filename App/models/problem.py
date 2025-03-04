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
    __tablename__ = 'linear_problem'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    objective = db.Column(db.String(10), nullable=False)  # 'max' or 'min'
    objective_function = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    variables = db.relationship('LPVariable', back_populates='problem', cascade='all, delete-orphan')
    constraints = db.relationship('LPConstraint', back_populates='problem', cascade='all, delete-orphan')

    def __init__(self, name, description, c, phi, objective='min', objective_function=''):
        self.name = name
        self.description = description
        self.objective = objective
        self.objective_function = objective_function
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_variable(self, variable):
        """Add a variable to the problem"""
        self.variables.append(variable)
        
    def add_constraint(self, constraint):
        """Add a constraint to the problem"""
        self.constraints.append(constraint)
        
    def print_problem(self):
        """Print the problem definition"""
        print(f"Name: {self.name}")
        print(f"Description: {self.description}")
        print(f"Objective: {'Maximize' if self.objective == 'max' else 'Minimize'} {self.objective_function}")
        print("Variables:")
        for var in self.variables:
            lower_bound = f"Lower Bound: {var.lower_bound}" if var.lower_bound is not None else "Lower Bound: None"
            upper_bound = f"Upper Bound: {var.upper_bound}" if var.upper_bound is not None else "Upper Bound: None"
            print(f"  - {var.name} ({lower_bound}, {upper_bound})")
        print("Constraints:")
        for const in self.constraints:
            print(f"  - {const.expression}")

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'objective': self.objective,
            'objective_function': self.objective_function,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'variables': [var.to_json() for var in self.variables],
            'constraints': [const.to_json() for const in self.constraints]
        }
