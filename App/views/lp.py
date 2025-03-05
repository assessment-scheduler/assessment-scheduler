from flask import Blueprint, render_template, request, jsonify
from typing import Any, Dict
from App.models.problem import LinearProblem
from App.models.variable import LPVariable
from App.models.constraint import LPConstraint
from App.models.solver import LPSolver

lp = Blueprint('lp', __name__)

def create_sample_problem() -> LinearProblem:
    """Creates a sample linear programming problem"""

    problem = LinearProblem(
        name="Sample Problem",
        description="Maximize 3x1 + 2x2 subject to constraints",
        objective="max",
        objective_function="3x1 + 2x2"
    )
    
    problem.add_variable(LPVariable(name="x1", lower_bound=0))
    problem.add_variable(LPVariable(name="x2", lower_bound=0))
    
    problem.add_constraint(LPConstraint(expression="x1 + x2 <= 10", relation_type="<="))
    problem.add_constraint(LPConstraint(expression="2x1 + x2 <= 16", relation_type="<="))
    
    return problem

def solve_lp_problem(problem: LinearProblem) -> Dict[str, Any]:
    """Solves a linear programming problem and returns the result"""
    solver = LPSolver(problem)
    return solver.solve()

@lp.route('/lp', methods=['GET'])
def lp_form():
    return render_template('lp_form.html')

@lp.route('/lp/solve', methods=['POST'])
def solve_lp():
    data = request.get_json()
    problem = LinearProblem(
        name=data.get('name', 'Custom Problem'),
        description=data.get('description', ''),
        objective=data.get('objective', 'max'),
        objective_function=data.get('objective_function', '')
    )
    
    # Add variables
    for var_data in data.get('variables', []):
        var = LPVariable(
            name=var_data['name'],
            lower_bound=var_data.get('lower_bound', 0)
        )
        problem.add_variable(var)
    
    # Add constraints
    for const_data in data.get('constraints', []):
        const = LPConstraint(
            expression=const_data['expression'],
            relation_type=const_data['relation_type']
        )
        problem.add_constraint(const)
    
    # Solve problem
    result = solve_lp_problem(problem)
    return jsonify(result)
