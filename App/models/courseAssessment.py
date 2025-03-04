from App.database import db

class CourseAssessment(db.Model):
    __tablename__ = 'courseAssessment'

    id = db.Column(db.Integer, primary_key= True, autoincrement=True)
    course_code = db.Column(db.String(9), db.ForeignKey('course.course_code'), nullable = False)
    a_id = db.Column(db.Integer, db.ForeignKey('assessment.a_id'), nullable = False)
    start_date = db.Column(db.Date, nullable = True)
    end_date = db.Column(db.Date, nullable = True)
    start_time = db.Column(db.Time, nullable = True)
    end_time = db.Column(db.Time, nullable = True)
    clash_detected = db.Column(db.Boolean, default = False)

    # More features to add for possible extension
    # duration = db.Column(db.Numeric(4, 2), nullable = False)
    # details = db.Column(db.String(250), nullable = True)
    # weight = db.Column(db.Integer, nullable = False)

    def __init__(self, course_code, a_id, start_date, end_date, start_time, end_time, clash_detected):
        self.course_code = course_code
        self.a_id = a_id
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.clash_detected = clash_detected

    def to_json(self):
        return {
            "assessmentNo": self.id,
            "courseCode" : self.course_code,
            "a_ID" : self.a_id,
            "startDate" : self.start_date,
            "endDate" : self.end_date,
            "startTime" : self.start_time,
            "endTime" : self.end_time,
            "clashDetected" : self.clash_detected
        }

    #Add new assessment to course
    def add_course_asg(self, course_code, a_id, start_date, end_date, start_time, end_time, clash_detected):
        new_asg = CourseAssessment(course_code, a_id, start_date, end_date, start_time, end_time, clash_detected)
        db.session.add(new_asg)  #add to db
        db.session.commit()
        return new_asg