from App.models import Lecturer
from App.database import db

def register_lecturer(firstName, lastName, staffID, status, email, pwd):
    #Check if email is already used by another lecturer ie. lecturer already registered
    staff = db.session.query(Lecturer).filter(Lecturer.email == email).count

    if staff == 0:
        newLect = Lecturer.register(firstName, lastName, staffID, status, email, pwd)
        return newLect
    return None
