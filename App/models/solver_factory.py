from typing import Optional
from .solver import Solver

def get_solver(solver_type: str) -> Solver:
    if solver_type == 'kris':
        from .solvers.kris import KrisSolver
        return KrisSolver()
    
    raise ValueError(f"Unknown solver type: {solver_type}") 