import csv
from datetime import date, timedelta
from ..controllers.admin import create_admin_user
from ..database import db
from .user import create_user
from .staff import create_staff
from .course import create_course, assign_lecturer
from .assessment import create_assessment
from .courseoverlap import create_cell
from .semester import create_semester, add_course_to_semester
from .course_timetable import create_timetable_entry, get_day_mapping

def initialize() -> None:
    db.drop_all()
    db.create_all()

    create_admin_user(101101, 'admin', 'adminpass')

    with open('App/uploads/staff.csv') as staff_file:
         reader = csv.DictReader(staff_file)
         for row in reader:
              create_staff(row['id'], row['email'], row['password'], row['first_name'], row['last_name'], row['department'], row['faculty'])

    with open('App/uploads/courses.csv') as course_file:
        reader = csv.DictReader(course_file)
        for row in reader:
            level = row.get('level')
            credits = row.get('credits')
            semester = row.get('semester')
            
            if credits and credits.isdigit():
                credits = int(credits)
            else:
                credits = None
                
            create_course(row['course_code'], row['course_name'], level, credits, semester)

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
             create_semester(row['start_date'], row['end_date'], row['sem_num'], row['max_assessments'], row['constraint_value'], row['active'] == "1" or row['active'] == "True")

    with open('App/uploads/semester_courses.csv') as semester_courses_file:
        reader = csv.DictReader(semester_courses_file)
        for row in reader:
            add_course_to_semester(int(row['semester_id']), row['course_code'])
            
    with open('App/uploads/course_timetable.csv') as timetable_file:
        reader = csv.DictReader(timetable_file)
        print("DEBUG: Processing course_timetable.csv")
        for row in reader:
            course_code = row['CourseID']
            days_str = row['Days']
            time_slot = row['LectureTime']
            
            print(f"DEBUG: Processing {course_code} with days: {days_str}")
            
            # Process days (could be multiple, separated by semicolons)
            days = days_str.split(';')
            for day in days:
                # Explicit mapping instead of using get_day_mapping
                day_mapping = {
                    'Mon': 1, 'Monday': 1,
                    'Tue': 2, 'Tuesday': 2, 
                    'Wed': 3, 'Wednesday': 3,
                    'Thu': 4, 'Thursday': 4,
                    'Fri': 5, 'Friday': 5
                }
                day_number = day_mapping.get(day.strip(), None)
                
                if day_number:
                    print(f"DEBUG: Adding {course_code} on day {day_number} ({day.strip()})")
                    entry = create_timetable_entry(course_code, day_number, time_slot)
                    print(f"DEBUG: Created entry: {entry}")
                else:
                    print(f"ERROR: Unknown day format: '{day.strip()}' for {course_code}")

def clear() -> None:
    db.drop_all()
    db.create_all()