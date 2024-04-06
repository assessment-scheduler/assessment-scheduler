from App.database import db

class CourseAssessment(db.Model):
    __tablename__ = 'courseAssessment'

    id = db.Column(db.Integer, primary_key= True, autoincrement=True)
    courseCode = db.Column(db.String(8), db.ForeignKey('course.courseCode'), nullable = False)
    a_ID = db.Column(db.Integer, db.ForeignKey('assessment.a_ID'), nullable = False)
    startDate = db.Column(db.Date, nullable = True)
    endDate = db.Column(db.Date, nullable = True)
    startTime = db.Column(db.Time, nullable = True)
    endTime = db.Column(db.Time, nullable = True)
    
    # More features to add for possible extension
    # duration = db.Column(db.Numeric(4, 2), nullable = False)
    # details = db.Column(db.String(250), nullable = True)
    # weight = db.Column(db.Integer, nullable = False)

    def __init__(self, courseCode, a_ID, startDate, endDate, startTime, endTime):
        self.courseCode = courseCode
        self.a_ID = a_ID
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime

    def to_json(self):
        return {
            "assessmentNo": self.id,
            "courseCode" : self.courseCode,
            "a_ID" : self.a_ID,
            "startDate" : self.startDate,
            "endDate" : self.endDate,
            "startTime" : self.startTime,
            "endTime" : self.endTime
        }

    #Add new assessment to course
    def addCourseAsg(self, courseCode, a_ID, startDate, endDate, startTime, endTime):
        newAsg = CourseAssessment(courseCode, a_ID, startDate, endDate, startTime, endTime)
        db.session.add(newAsg)  #add to db
        db.session.commit()
        return newCourse