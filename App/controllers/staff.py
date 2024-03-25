from App.models import Staff
from App.database import db

def register_staff(firstName, lastName, u_ID, status, email, pwd):
    #Check if email is already used by another lecturer ie. lecturer already registered
    staff = db.session.query(Staff).filter(Staff.email == email).count()

    if staff == 0:
        newLect = Staff.register(firstName, lastName, u_ID, status, email, pwd)
        return newLect
    return None

def login_staff(email, password):
    staff = db.session.query(Staff).filter(Staff.email==email).first()
    if staff != None:
        if staff.check_password(password):
            return staff.login()
    return "Login failed"