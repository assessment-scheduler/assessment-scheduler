from flask import Blueprint, request, jsonify, render_template
from App.database import db
from App.models import Staff, Course, Assessment, Programme, Admin, Semester, CourseStaff, CourseAssessment

index_views = Blueprint('index_views', __name__, template_folder='../templates')

# Gets Landing Page
@index_views.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()

    #create admin
    bob = Admin(u_ID=999, email="bob@gmail.com", password="bobpass")
    db.session.add(bob)

    #create semester
    sem = Semester(startDate='01-02-2024', endDate='01-05-2024', semNum=1, maxAssessments=3)
    db.session.add(sem)

    #create courses
    c1 = Course(courseCode='COMP1700', courseTitle='Introduction to C++', description='C++ basics', level=1, semester=1, aNum=3)
    c2 = Course(courseCode='COMP1701', courseTitle='Introduction to Web Development', description='Web development basics', level=1, semester=1, aNum=3)
    c3 = Course(courseCode='COMP2700', courseTitle='Advanced C++', description='Advanced C++', level=2, semester=1, aNum=3)
    c4 = Course(courseCode='COMP2701', courseTitle='Advanced Web Development', description='Advanced web development', level=2, semester=1, aNum=3)
    c5 = Course(courseCode='COMP3700', courseTitle='Data Science Fundamentals', description='Introduction to python and datasets', level=3, semester=1, aNum=3)
    c6 = Course(courseCode='COMP3701', courseTitle='Advanced Data Science', description='Analyzing Big Data with Python', level=3, semester=1, aNum=3)
    db.session.add(c1)
    db.session.add(c2)
    db.session.add(c3)
    db.session.add(c4)
    db.session.add(c5)
    db.session.add(c6)

    #create staff
    staff = Staff.register(firstName='Jane', lastName='Doe', u_ID=11111111, status='Lecturer', email='jane@mail.com', password='password')

    #assign staff to courses
    cs1 = CourseStaff(u_ID=11111111, courseCode='COMP1700')
    cs2 = CourseStaff(u_ID=11111111, courseCode='COMP2700')
    cs3 = CourseStaff(u_ID=11111111, courseCode='COMP3700')
    db.session.add(cs1)
    db.session.add(cs2)
    db.session.add(cs3)

    #create assessments
    asm1 = Assessment(category='EXAM')
    db.session.add(asm1)
    asm2 = Assessment(category='ASSIGNMENT')
    db.session.add(asm2)
    asm3 = Assessment(category='QUIZ')
    db.session.add(asm3)
    asm4 = Assessment(category='PROJECT')
    db.session.add(asm4)
    asm5 = Assessment(category='DEBATE')
    db.session.add(asm5)
    asm6 = Assessment(category='PRESENTATION')
    db.session.add(asm6)
    asm7 = Assessment(category='ORALEXAM')
    db.session.add(asm7)
    asm8 = Assessment(category='PARTICIPATION')
    db.session.add(asm8)
    
    #create course assessments
    ca1 = CourseAssessment(courseCode='COMP1700', a_ID=1, startDate='2024-04-08', endDate='2024-04-08', startTime='08:00:00', endTime='10:00:00', clashDetected=False)
    ca2 = CourseAssessment(courseCode='COMP1700', a_ID=3, startDate='2024-04-09', endDate='2024-04-09', startTime='00:00:00', endTime='23:59:00', clashDetected=False)
    ca3 = CourseAssessment(courseCode='COMP1700', a_ID=6, startDate='2024-04-10', endDate='2024-04-10', startTime='09:00:00', endTime='12:00:00', clashDetected=False)
    ca4 = CourseAssessment(courseCode='COMP2700', a_ID=1, startDate='2024-04-15', endDate='2024-04-15', startTime='08:00:00', endTime='10:00:00', clashDetected=False)
    ca5 = CourseAssessment(courseCode='COMP2700', a_ID=3, startDate='2024-04-16', endDate='2024-04-16', startTime='00:00:00', endTime='23:59:00', clashDetected=False)
    ca6 = CourseAssessment(courseCode='COMP2700', a_ID=6, startDate='2024-04-17', endDate='2024-04-17', startTime='09:00:00', endTime='12:00:00', clashDetected=False)
    ca7 = CourseAssessment(courseCode='COMP3700', a_ID=1, startDate='2024-04-22', endDate='2024-04-22', startTime='08:00:00', endTime='10:00:00', clashDetected=False)
    ca8 = CourseAssessment(courseCode='COMP3700', a_ID=3, startDate='2024-04-23', endDate='2024-04-23', startTime='00:00:00', endTime='23:59:00', clashDetected=False)
    ca9 = CourseAssessment(courseCode='COMP3700', a_ID=6, startDate='2024-04-24', endDate='2024-04-24', startTime='09:00:00', endTime='12:00:00', clashDetected=False)
    db.session.add(ca1)
    db.session.add(ca2)
    db.session.add(ca3)
    db.session.add(ca4)
    db.session.add(ca5)
    db.session.add(ca6)
    db.session.add(ca7)
    db.session.add(ca8)
    db.session.add(ca9)

    db.session.commit()
    return {'message':'Objects created'}