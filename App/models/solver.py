from ortools.linear_solver import pywraplp
import re
from typing import Dict, Any, List, Tuple, Literal
from App.models.problem import LinearProblem

class LPSolver:
    def __init__(self, problem: 'LinearProblem'):
        self.problem: LinearProblem = problem
        self.solver = pywraplp.Solver.CreateSolver('GLOP')

    def _parse_expression(self, expression: str) -> List[Tuple[float, str]]:
        terms: List[Tuple[float, str]] = []
        expression = re.sub(r'\s*([\+\-])\s*', r'\1', expression)
        parts: List[str | Any] = re.split(r'([\+\-])', expression.strip())

        current_coeff = 1
        for part in parts:
            if part in ['+', '-']:
                current_coeff: Literal[1, -1] = 1 if part == '+' else -1
                continue

            if not part.strip():
                continue

            # Match patterns like "3x1", "x1", "3.5x1"
            match: re.Match[str] | None = re.match(r'^(\d*\.?\d*)?([a-zA-Z]\w*)$', part)
            if match:
                coeff_str, var = match.groups()
                coeff: float = float(coeff_str) if coeff_str else 1.0
                terms.append((current_coeff * coeff, var))
        
        return terms


    def solve(self) -> Dict[str, Any]:
        """Returns a dictionary containing the solution for the provided linear problem"""
        try:
            if not self.solver:
                return {'status': 'ERROR', 'error': 'Could not create solver'}

            var_dict = self._define_variables()
            self._set_objective(var_dict)
            self._add_constraints(var_dict)

            return self._solve_and_get_results(var_dict)

        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def _define_variables(self) -> Dict[str, pywraplp.Variable]:
        """Defines and returns the decision variables."""
        var_dict = {}
        for var in self.problem.variables:
            var_dict[var.name] = self.solver.NumVar(
                var.lower_bound if var.lower_bound is not None else -self.solver.infinity(),
                var.upper_bound if var.upper_bound is not None else self.solver.infinity(),
                var.name
            )
        return var_dict

    def _set_objective(self, var_dict: Dict[str, pywraplp.Variable]) -> None:
        """Sets the objective function."""
        objective = self.solver.Objective()
        obj_terms = self._parse_expression(self.problem.objective_function)
        
        for coeff, var_name in obj_terms:
            if var_name in var_dict:
                objective.SetCoefficient(var_dict[var_name], coeff)

        objective.SetMaximization() if self.problem.objective == 'max' else objective.SetMinimization()

    def _add_constraints(self, var_dict: Dict[str, pywraplp.Variable]) -> None:
        """Adds constraints to the solver."""
        for const in self.problem.constraints:
            lhs_terms, rhs_value, relation_type = self._parse_constraint(const.expression)
            if lhs_terms is None:
                continue  # Skip invalid constraints

            constraint = self._create_constraint(relation_type, rhs_value)

            for coeff, var_name in lhs_terms:
                if var_name in var_dict:
                    constraint.SetCoefficient(var_dict[var_name], coeff)

    def _parse_constraint(self, expression: str) -> Tuple[List[Tuple[float, str]], float, str]:
        """Parses a constraint and returns (terms, RHS value, relation type)."""
        # Find the relation operator
        relation_match = re.search(r'(<=|>=|=)', expression)
        if not relation_match:
            return None, None, None  # Invalid constraint format
        
        relation_type = relation_match.group(1)
        parts = expression.split(relation_type)
        
        if len(parts) != 2:
            return None, None, None  # Invalid constraint format
        
        lhs_expr = parts[0].strip()
        rhs_expr = parts[1].strip()
        
        try:
            rhs_value = float(rhs_expr)
            lhs_terms = self._parse_expression(lhs_expr)
            return lhs_terms, rhs_value, relation_type
        except ValueError:
            return None, None, None  # Invalid RHS value

    def _create_constraint(self, relation_type: str, rhs_value: float) -> pywraplp.Constraint:
        """Creates a constraint based on the relation type."""
        if relation_type == '<=':
            return self.solver.Constraint(-self.solver.infinity(), rhs_value)
        elif relation_type == '>=':
            return self.solver.Constraint(rhs_value, self.solver.infinity())
        else:  # relation_type == '='
            return self.solver.Constraint(rhs_value, rhs_value)

    def _solve_and_get_results(self, var_dict: Dict[str, pywraplp.Variable]) -> Dict[str, Any]:
        """Solves the problem and returns the results."""
        status = self.solver.Solve()
        result_map = {
            pywraplp.Solver.OPTIMAL: lambda: {
                'status': 'OPTIMAL',
                'objective_value': round(self.solver.Objective().Value(), 6),
                'variables': {name: round(var.solution_value(), 6) for name, var in var_dict.items()}
            },
            pywraplp.Solver.INFEASIBLE: lambda: {'status': 'INFEASIBLE', 'error': 'Problem has no feasible solution'},
            pywraplp.Solver.UNBOUNDED: lambda: {'status': 'UNBOUNDED', 'error': 'Problem is unbounded'}
        }
        return result_map.get(status, lambda: {'status': 'NOT_SOLVED', 'error': 'Could not find optimal solution'})()
