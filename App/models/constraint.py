from App.database import db

class LPConstraint(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('linear_problem.id'), nullable=False)
    expression = db.Column(db.String, nullable=False) # stores the expression as a string eg x1 + x2 <= 10
    
    problem = db.relationship('LinearProblem', back_populates='constraints') # problem that it belongs to 

    def __init__(self, expression, relation_type):  # relation_type could be '<=', '>=', '='
        self.expression = expression
        self.relation_type = relation_type
        
    def get_json(self):
        return {
            'id': self.id,
            'expression': self.expression,
            'relation_type': self.relation_type
        }
