from App.models.config import Config
from App.database import db

def get_config():
    """
    Get the current configuration
    
    Returns:
        Config object if found, None otherwise
    """
    return Config.query.first()

def get_current_semester():
    """
    Get the current semester
    
    Returns:
        Current semester number
    """
    return Config.get_current_semester()

def set_semester(semester):
    """
    Set the current semester
    
    Args:
        semester: Semester number
        
    Returns:
        Config object
    """
    return Config.set_semester(semester) 