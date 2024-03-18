from App.models import Course
from App.database import db

def add_Course(courseCode, courseTitle, description, level, semester, aNum):
    # Check if courseCode is already in db ie. course already added
    course = Course.query.get(courseCode)
    if course:
        return course
    else:
         #Add new Course
        newCourse = Course(courseCode, courseTitle, description, level, semester, aNum)
        db.session.add(newCourse)  #add to db
        db.session.commit()
        return newCourse
    return None        

def list_Course():
    # Get each object and return as string
    return none    