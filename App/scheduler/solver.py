"""
Scheduler solver module for auto-scheduling assessments.
Uses Google OR-Tools for constraint programming.
"""
import datetime
from ortools.sat.python import cp_model
from App.models.course import Course
from App.models.assessment import Assessment
from App.models.semester import Semester
from App.models.solver_config import SolverConfig
from App.database import db

class ScheduleSolver:
    """
    Solver class for auto-scheduling assessments using constraint programming.
    """
    def __init__(self, semester, courses, assessments, config=None):
        """
        Initialize the solver with the given parameters.
        
        Args:
            semester: The semester object for which to schedule assessments
            courses: List of course objects to schedule
            assessments: List of assessment types to schedule
            config: SolverConfig object or None to use default config
        """
        self.semester = semester
        self.courses = courses
        self.assessments = assessments
        
        # Get or create config
        if config is None:
            config = SolverConfig.query.order_by(SolverConfig.id.desc()).first()
            if config is None:
                config = SolverConfig()
                db.session.add(config)
                db.session.commit()
        
        self.config = config
        self.min_spacing = config.min_spacing
        self.large_m = config.large_m
        self.weekend_penalty = config.weekend_penalty
        
        # Calculate the date range for the semester
        self.start_date = semester.startDate
        self.end_date = semester.endDate
        self.num_days = (self.end_date - self.start_date).days + 1
        
        # Create a mapping of course and assessment combinations
        self.course_assessments = []
        for course in self.courses:
            for assessment in self.assessments:
                self.course_assessments.append((course, assessment))
    
    def solve(self):
        """
        Solve the scheduling problem and return the solution.
        
        Returns:
            A tuple of (schedule, U_star, probability) where:
            - schedule is a list of tuples (day, week, day_of_week, course, assessment)
            - U_star is the objective value
            - probability is the solution probability
        """
        model = cp_model.CpModel()
        
        # Create variables for each course-assessment combination
        # The variable represents the day offset from the start date
        variables = {}
        for course, assessment in self.course_assessments:
            variables[(course.id, assessment.id)] = model.NewIntVar(
                0, self.num_days - 1, f'day_offset_{course.id}_{assessment.id}'
            )
        
        # Add constraints
        
        # 1. Avoid weekends with penalty
        weekend_vars = []
        for (course_id, assessment_id), var in variables.items():
            for day in range(self.num_days):
                day_of_week = (self.start_date + datetime.timedelta(days=day)).weekday()
                if day_of_week >= 5:  # Saturday or Sunday
                    is_weekend = model.NewBoolVar(f'is_weekend_{course_id}_{assessment_id}_{day}')
                    model.Add(var == day).OnlyEnforceIf(is_weekend)
                    model.Add(var != day).OnlyEnforceIf(is_weekend.Not())
                    weekend_vars.append(is_weekend)
        
        # 2. Minimum spacing between assessments for the same course
        for course in self.courses:
            for i, assessment1 in enumerate(self.assessments):
                for assessment2 in self.assessments[i+1:]:
                    var1 = variables.get((course.id, assessment1.id))
                    var2 = variables.get((course.id, assessment2.id))
                    if var1 and var2:
                        # Either var1 is at least min_spacing days after var2
                        # or var2 is at least min_spacing days after var1
                        b1 = model.NewBoolVar(f'spacing_{course.id}_{assessment1.id}_{assessment2.id}_1')
                        b2 = model.NewBoolVar(f'spacing_{course.id}_{assessment1.id}_{assessment2.id}_2')
                        
                        model.Add(var1 - var2 >= self.min_spacing).OnlyEnforceIf(b1)
                        model.Add(var2 - var1 >= self.min_spacing).OnlyEnforceIf(b2)
                        model.Add(b1 + b2 == 1)  # Exactly one must be true
        
        # 3. Maximum assessments per day
        for day in range(self.num_days):
            day_vars = []
            for (course_id, assessment_id), var in variables.items():
                day_var = model.NewBoolVar(f'day_{day}_{course_id}_{assessment_id}')
                model.Add(var == day).OnlyEnforceIf(day_var)
                model.Add(var != day).OnlyEnforceIf(day_var.Not())
                day_vars.append(day_var)
            
            # Limit the number of assessments per day
            model.Add(sum(day_vars) <= 2)  # Default max 2 per day
        
        # Set objective: minimize weekend assessments
        if weekend_vars:
            model.Minimize(sum(weekend_vars) * int(self.weekend_penalty * 100))
        
        # Solve the model
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract the solution
            schedule = []
            for (course_id, assessment_id), var in variables.items():
                day_offset = solver.Value(var)
                date = self.start_date + datetime.timedelta(days=day_offset)
                
                # Find the course and assessment objects
                course = next(c for c in self.courses if c.id == course_id)
                assessment = next(a for a in self.assessments if a.id == assessment_id)
                
                # Calculate week number (0-indexed from semester start)
                week = day_offset // 7
                day_of_week = date.weekday()
                
                schedule.append((
                    day_offset,
                    week,
                    day_of_week,
                    course.courseCode,
                    assessment.category.value
                ))
            
            # Sort by date
            schedule.sort(key=lambda x: x[0])
            
            # Calculate objective value and probability
            U_star = 0
            if weekend_vars:
                U_star = sum(solver.Value(var) for var in weekend_vars) * self.weekend_penalty
            
            # Calculate probability (placeholder)
            probability = 1.0
            
            return schedule, U_star, probability
        
        return None, 0, 0 