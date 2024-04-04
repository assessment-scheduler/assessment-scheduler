from App.models import Staff, CourseStaff
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

def add_CourseStaff(u_ID,courseCode):
    existing_course_staff = CourseStaff.query.filter_by(u_ID=u_ID, courseCode=courseCode).first()
    if existing_course_staff:
        return existing_course_staff  # Return existing CourseStaff if found

    # Create a new CourseStaff object
    new_course_staff = CourseStaff(u_ID=u_ID, courseCode=courseCode)

    # Add and commit to the database
    db.session.add(new_course_staff)
    db.session.commit()

    return new_course_staff

def get_registered_courses(u_ID):
    course_listing = CourseStaff.query.filter_by(u_ID=u_ID).all()
    codes=[]
    for item in course_listing:
        codes.append(item.courseCode)
    return codes