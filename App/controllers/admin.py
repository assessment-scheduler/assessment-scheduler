from App.models import Admin
from App.database import db

def login_admin(email, password):
    admin = db.session.query(Admin).filter(Admin.u_ID==email).first()
    if admin != None:
        if admin.check_password(password):
            return admin.login()
    return "Login failed"