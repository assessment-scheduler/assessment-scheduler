"""
Linear Programming controller functions
"""
from App.database import db
from App.models.problem import LinearProblem
from App.models.solver import LPSolver

def create_sample_problem():
    """
    Creates a sample linear programming problem
    """
    # Create a simple maximization problem
    problem = LinearProblem(
        name="Sample Problem",
        description="Maximize 3x1 + 2x2 subject to constraints",
        c=[[0, 0], [0, 0]],  # Placeholder for c matrix
        phi=[[0, 0], [0, 0]],  # Placeholder for phi matrix
        objective="max",
        objective_function="3x1 + 2x2"
    )
    
    # Add variables
    from App.models.variable import LPVariable
    x1_var = LPVariable("x1", lower_bound=0)
    x2_var = LPVariable("x2", lower_bound=0)
    problem.add_variable(x1_var)
    problem.add_variable(x2_var)
    
    # Add constraints
    from App.models.constraint import LPConstraint
    constraint1 = LPConstraint("x1 + x2 <= 10", "<=")
    constraint2 = LPConstraint("2x1 + x2 <= 16", "<=")
    problem.add_constraint(constraint1)
    problem.add_constraint(constraint2)
    
    # Save to database
    db.session.add(problem)
    db.session.commit()
    
    return problem

def solve_lp_problem(problem_id=None):
    """
    Solves a linear programming problem
    
    Args:
        problem_id: ID of the problem to solve, or None to solve the latest problem
    
    Returns:
        Dictionary with solution details
    """
    # Get the problem
    if isinstance(problem_id, LinearProblem):
        problem = problem_id
    elif problem_id:
        problem = LinearProblem.query.get(problem_id)
    else:
        problem = LinearProblem.query.order_by(LinearProblem.id.desc()).first()
    
    if not problem:
        return {"error": "No problem found"}
    
    # Create solver and solve
    solver = LPSolver(problem)
    solution = solver.solve()
    
    # Update problem with solution
    problem.solution = solution
    db.session.commit()
    
    return solution 