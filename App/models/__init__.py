from App.database import db

# Import all models here
from .user import User
from .admin import Admin
from .staff import Staff
from .course import Course
from .assessment import Assessment, Category
from .semester import Semester