from .staff import *
from .course import *
from .courseAssessment import *
from .semester import *
from .user import *
from .auth import *
from .scheduler import *
from .assessment import *
from .admin import *
from .lp import *
from .courseStaff import *

# Add initialize function for database initialization
def initialize():
    """
    Initialize the database with required data
    """
    from App.database import db
    from App.models import User, Staff, Admin
    
    # Create tables if they don't exist
    db.create_all()
    
    # Add any initial data here if needed
    
    return True