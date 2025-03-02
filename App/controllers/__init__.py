from .staff import *
from .course import *
from .courseAssessment import *
from .semester import *
from .user import *
from .auth import *
from .scheduler import *

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