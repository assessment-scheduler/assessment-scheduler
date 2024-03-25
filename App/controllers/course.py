from App.models import Course
from App.database import db

def add_Course(courseCode, courseTitle, description, level, semester, aNum):
    # Check if courseCode is already in db ie. course was already added
    course = Course.query.get(courseCode)
    if course: 
        return course
    else:
         #Add new Course
        newCourse = Course.addCourse(courseCode, courseTitle, description, level, semester, aNum)
        return newCourse
    return None        

def list_Courses():
    return Course.query.all() 

def get_course(courseCode):
    return Course.query.filter_by(courseCode=courseCode).first()

def edit_course(review, staff, is_positive, comment):
    if review.reviewer == staff:
        review.isPositive = is_positive
        review.comment = comment
        db.session.add(review)
        db.session.commit()
        return review
    return None    

def delete_Course(course):
    db.session.delete(course)
    db.session.commit()
    return True     
