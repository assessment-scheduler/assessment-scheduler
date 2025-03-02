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
        objective="3x + 4y",
        objective_type="max",
        constraints=[
            "x + y <= 10",
            "2x + y <= 15",
            "x >= 0",
            "y >= 0"
        ],
        variables=["x", "y"]
    )
    
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
    if problem_id:
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