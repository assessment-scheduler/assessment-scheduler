from App.database import db

class LPVariable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('linear_problem.id'), nullable=False)
    name = db.Column(db.String, nullable=False) # eg x1,x2, y1, y2
    lower_bound = db.Column(db.Float, nullable=False, default = 0) # default lower bound is 0
    upper_bound = db.Column(db.Float, nullable=False, default = None)  # could go up to infinity

    problem = db.relationship('LinearProblem', back_populates='variables') # problem that it belongs to 

    def __init__(self, name, lower_bound=None, upper_bound=None):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound
        }
