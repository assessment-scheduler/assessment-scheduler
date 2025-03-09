import csv
from datetime import date, timedelta
from App.controllers.admin import create_admin
from App.database import db
from .user import create_user
from .staff import create_staff
from .course import create_course, assign_lecturer
from .assessment import create_assessment
from .courseoverlap import create_cell
from .semester import create_semester

def initialize() -> None:
    db.drop_all()
    db.create_all()

    create_admin(101101, 'admin', 'adminpass')

    with open('App/uploads/staff.csv') as staff_file:
         reader = csv.DictReader(staff_file)
         for row in reader:
              create_staff(row['id'],row['email'], row['password'], row['first_name'], row['last_name'])

    with open('App/uploads/courses.csv') as course_file:
        reader = csv.DictReader(course_file)
        for row in reader:
            create_course(row['course_code'], row['course_name'])

    with open('App/uploads/lecturerassignments.csv') as assigned_file:
         reader = csv.DictReader(assigned_file)
         for row in reader:
              assign_lecturer(row['lecturer_id'], row['course_code'])
         

    with open('App/uploads/assessments.csv') as course_file:
            reader = csv.DictReader(course_file)
            for row in reader:
                create_assessment(row['course_code'],row['assessment_name'],row['percentage'],row['start_week'],row['start_day'],row['end_week'],row['end_day'],row['proctored'])

    with open('App/uploads/cells.csv') as matrix_file:
         reader = csv.DictReader(matrix_file)
         for row in reader:
                create_cell(row['course_code'], row['course_code2'], row['overlap'])

    with open('App/uploads/semesters.csv') as semester_file:
        reader = csv.DictReader(semester_file)
        for row in reader:
             create_semester(row['start_date'], row['end_date'], row['sem_num'], row['max_assessments'], row['constraint_value'], bool(row['active']))

    with open('App/uploads/users.csv') as user_file:
        reader = csv.DictReader(user_file)
        for row in reader:
            create_user(row['id'],row['email'], row['password'])
