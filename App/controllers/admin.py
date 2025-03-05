from App.models import Admin
from App.database import db

def get_admin_by_id(admin_id):
    """
    Get an admin by ID
    
    Args:
        admin_id: ID of the admin
        
    Returns:
        Admin object if found, None otherwise
    """
    return Admin.query.filter_by(u_ID=admin_id).first()

def login_admin(email, password):
    admin = db.session.query(Admin).filter(Admin.u_ID==email).first()
    if admin != None:
        if admin.check_password(password):
            return admin.login()
    return "Login failed"