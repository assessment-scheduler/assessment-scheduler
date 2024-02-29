from App.database import db

class CourseAssessment(db.Model):
    __tablename__ = 'courseAssessment'

    courseCode = db.Column(db.String(8), db.ForeignKey('course.courseCode'), primary_key= True, nullable = False)
    a_ID = db.Column(db.Integer, db.ForeignKey('assessment.a_ID'), primary_key= True, nullable = False)
    #duration should be equal to difference between startTime and endTime of assessment in minutes and hours
    duration = db.Column(db.Numeric(4, 2), nullable = False)
    details = db.Column(db.String(250), nullable = True)
    weight = db.Column(db.Integer, nullable = False)
    