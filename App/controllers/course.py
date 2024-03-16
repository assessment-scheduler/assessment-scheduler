from App.models import Course
from App.database import db

def add_Course(courseCode, courseTitle, description, level, semester, aNum):
    #Check if courseCode is already in db ie. course already added
    course = db.session.query(Course).filter(Course.courseCode == courseCode).count

    if course == 0:
        newCourse = Course.addCourse(courseCode, courseTitle, description, level, semester, aNum)
        return newCourse
    return None

def list_Course():
    # Get each object and return as string
    return none    