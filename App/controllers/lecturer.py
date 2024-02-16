from App.models import Lecturer
from App.database import db

def register_lecturer(fName, lName, email, password):
    staff = db.session.query(Lecturer).filter(Lecturer.email == email).count

    if staff == 0:
        #Check if email is already used by another lecturer ie. lecturer already registered
        newLect = lecturer.register(fName, lName, email, password) 
        return newLect
    return None
