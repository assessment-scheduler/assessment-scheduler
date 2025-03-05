from App.database import db

# Import all models here
from .user import User
from .admin import Admin
from .staff import Staff
from .course import Course
from .assessment import Assessment, Category
from .courseAssessment import CourseAssessment
from .courseStaff import CourseStaff
from .semester import Semester
from .programme import Programme
from .courseProgramme import CourseProgramme
from .class_size import ClassSize
from .solver_config import SolverConfig
from .schedule_solution import ScheduleSolution
from .scheduled_assessment import ScheduledAssessment
from .config import Config

# Linear programming models
from .problem import LinearProblem
from .constraint import LPConstraint
from .variable import LPVariable
from .solver import LPSolver

__all__ = [
    'db',
    'User', 'Admin', 'Staff',
    'Course', 'Assessment', 'Category', 'CourseAssessment',
    'CourseStaff', 'Semester', 'Programme', 'CourseProgramme',
    'ClassSize', 'SolverConfig', 'ScheduleSolution', 'ScheduledAssessment',
    'LinearProblem', 'LPConstraint', 'LPVariable', 'LPSolver',
    'Config'
]