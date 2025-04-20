import unittest, logging, sys, os
from datetime import date, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from App.database import db
from App.models.assessment import Assessment
from App.models.course import Course
from App.models.staff import Staff
from App.models.semester import Semester
from App.models.semester_course import SemesterCourse
from App.models.course_lecturer import CourseLecturer
from App.controllers.assessment import (
    get_assessment,
    get_assessment_by_id,
    get_all_assessments,
    get_num_assessments,
    get_assessment_dictionary_by_course,
    get_assessments_by_course,
    get_assessments_by_lecturer,
    get_semester_lecturer_assessments,
    create_assessment,
    update_assessment,
    schedule_assessment,
    delete_assessment,
    delete_assessment_by_id,
    unschedule_assessment_only,
    reset_assessment_constraints,
    reset_all_assessment_constraints
)
from App.main import create_app

LOGGER = logging.getLogger(__name__)

class AssessmentIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        self.semester = Semester(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=105),
            sem_num=1,
            max_assessments=3,
            constraint_value=1000,
            active=True,
            solver_type='kris'
        )
        db.session.add(self.semester)
        
        self.course1 = Course(code="COMP1601", name="Computer Programming 1")
        self.course2 = Course(code="COMP1602", name="Computer Programming 2")
        db.session.add(self.course1)
        db.session.add(self.course2)
        
        self.staff = Staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        db.session.add(self.staff)
        
        self.semester_course1 = SemesterCourse(
            semester_id=1,
            course_code="COMP1601"
        )
        self.semester_course2 = SemesterCourse(
            semester_id=1,
            course_code="COMP1602"
        )
        db.session.add(self.semester_course1)
        db.session.add(self.semester_course2)
        
        self.course_lecturer1 = CourseLecturer(
            course_code="COMP1601",
            staff_id="3000001"
        )
        self.course_lecturer2 = CourseLecturer(
            course_code="COMP1602",
            staff_id="3000001"
        )
        db.session.add(self.course_lecturer1)
        db.session.add(self.course_lecturer2)
        
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_and_get_assessment(self):
        result = create_assessment(
            course_code="COMP1601",
            name="A1",
            percentage=6,
            start_week=2,
            start_day=1,
            end_week=4,
            end_day=7,
            proctored=0
        )
        
        self.assertTrue(result)
        
        assessment = get_assessment("COMP1601", "A1")
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.course_code, "COMP1601")
        self.assertEqual(assessment.name, "A1")
        self.assertEqual(assessment.percentage, 6)
        self.assertEqual(assessment.start_week, 2)
        self.assertEqual(assessment.start_day, 1)
        self.assertEqual(assessment.end_week, 4)
        self.assertEqual(assessment.end_day, 7)
        self.assertEqual(assessment.proctored, 0)
    
    def test_get_assessment_by_id(self):
        create_assessment(
            course_code="COMP1601",
            name="CW1",
            percentage=10,
            start_week=6,
            start_day=1,
            end_week=7,
            end_day=7,
            proctored=1
        )
        
        assessment = get_assessment("COMP1601", "CW1")
        assessment_by_id = get_assessment_by_id(assessment.id)
        
        self.assertIsNotNone(assessment_by_id)
        self.assertEqual(assessment_by_id.name, "CW1")
        self.assertEqual(assessment_by_id.course_code, "COMP1601")
    
    def test_get_all_assessments(self):
        create_assessment(
            course_code="COMP1601",
            name="A1",
            percentage=6,
            start_week=2,
            start_day=1,
            end_week=4,
            end_day=7,
            proctored=0
        )
        
        create_assessment(
            course_code="COMP1602",
            name="A1",
            percentage=15,
            start_week=2,
            start_day=1,
            end_week=5,
            end_day=7,
            proctored=0
        )
        
        assessments = get_all_assessments()
        self.assertEqual(len(assessments), 2)
        
    def test_get_num_assessments(self):
        create_assessment(
            course_code="COMP1601",
            name="A1",
            percentage=6,
            start_week=2,
            start_day=1,
            end_week=4,
            end_day=7,
            proctored=0
        )
        
        create_assessment(
            course_code="COMP1601",
            name="CW1",
            percentage=10,
            start_week=6,
            start_day=1,
            end_week=7,
            end_day=7,
            proctored=1
        )
        
        count = get_num_assessments("COMP1601")
        self.assertEqual(count, 2)
        
        count = get_num_assessments("COMP1602")
        self.assertEqual(count, 0)
    
    def test_get_assessment_dictionary_by_course(self):
        create_assessment(
            course_code="COMP1602",
            name="A1",
            percentage=15,
            start_week=2,
            start_day=1,
            end_week=5,
            end_day=7,
            proctored=0
        )
        
        course_dict = get_assessment_dictionary_by_course("COMP1602")
        self.assertEqual(course_dict["code"], "COMP1602")
        self.assertEqual(len(course_dict["assessments"]), 1)
        self.assertEqual(course_dict["assessments"][0]["name"], "A1")
        
        empty_dict = get_assessment_dictionary_by_course("COMP1601")
        self.assertEqual(empty_dict["code"], "COMP1601")
        self.assertEqual(len(empty_dict["assessments"]), 0)
    
    def test_get_assessments_by_course(self):
        create_assessment(
            course_code="COMP1601",
            name="A1",
            percentage=6,
            start_week=2,
            start_day=1,
            end_week=4,
            end_day=7,
            proctored=0
        )
        
        create_assessment(
            course_code="COMP1601",
            name="A2",
            percentage=6,
            start_week=6,
            start_day=1,
            end_week=7,
            end_day=7,
            proctored=0
        )
        
        assessments = get_assessments_by_course("COMP1601")
        self.assertEqual(len(assessments), 2)
        self.assertEqual(assessments[0].course_code, "COMP1601")
        self.assertEqual(assessments[1].course_code, "COMP1601")
    
    def test_get_assessments_by_lecturer(self):
        create_assessment(
            course_code="COMP1601",
            name="CW1",
            percentage=10,
            start_week=6,
            start_day=1,
            end_week=7,
            end_day=7,
            proctored=1
        )
        
        create_assessment(
            course_code="COMP1602",
            name="CW1",
            percentage=20,
            start_week=8,
            start_day=1,
            end_week=11,
            end_day=7,
            proctored=1
        )
        
        assessments = get_assessments_by_lecturer("staff@test.com")
        self.assertEqual(len(assessments), 2)
    
    def test_get_semester_lecturer_assessments(self):
        create_assessment(
            course_code="COMP1601",
            name="A3",
            percentage=8,
            start_week=9,
            start_day=1,
            end_week=10,
            end_day=7,
            proctored=0
        )
        
        assessments = get_semester_lecturer_assessments("staff@test.com", 1)
        self.assertEqual(len(assessments), 1)
        self.assertEqual(assessments[0].name, "A3")
    
    def test_update_assessment(self):
        create_assessment(
            course_code="COMP1602",
            name="A2",
            percentage=15,
            start_week=6,
            start_day=1,
            end_week=9,
            end_day=7,
            proctored=0
        )
        
        assessment = get_assessment("COMP1602", "A2")
        
        result = update_assessment(
            id=assessment.id,
            name="A2-Updated",
            percentage=20,
            start_week=5,
            start_day=1,
            end_week=8,
            end_day=7,
            proctored=0
        )
        
        self.assertTrue(result)
        
        updated = get_assessment_by_id(assessment.id)
        self.assertEqual(updated.name, "A2-Updated")
        self.assertEqual(updated.percentage, 20)
        self.assertEqual(updated.start_week, 5)
        self.assertEqual(updated.end_week, 8)
    
    def test_schedule_assessment(self):
        create_assessment(
            course_code="COMP1601",
            name="CW2",
            percentage=20,
            start_week=10,
            start_day=1,
            end_week=12,
            end_day=7,
            proctored=1
        )
        
        schedule_date = self.semester.start_date + timedelta(days=21)  
        
        result = schedule_assessment(
            semester=self.semester,
            schedule_date=schedule_date,
            course_code="COMP1601",
            name="CW2"
        )
        
        self.assertTrue(result)
        
        assessment = get_assessment("COMP1601", "CW2")
        self.assertEqual(assessment.scheduled, schedule_date)
        self.assertEqual(assessment.start_week, 4)
        self.assertEqual(assessment.start_day, 1)
    
    def test_delete_assessment(self):
        create_assessment(
            course_code="COMP1602",
            name="A2",
            percentage=15,
            start_week=6,
            start_day=1,
            end_week=9,
            end_day=7,
            proctored=0
        )
        
        result = delete_assessment("COMP1602", "A2")
        self.assertTrue(result)
        
        assessment = get_assessment("COMP1602", "A2")
        self.assertIsNone(assessment)
    
    def test_delete_assessment_by_id(self):
        create_assessment(
            course_code="COMP1601",
            name="A3",
            percentage=8,
            start_week=9,
            start_day=1,
            end_week=10,
            end_day=7,
            proctored=0
        )
        
        assessment = get_assessment("COMP1601", "A3")
        
        result = delete_assessment_by_id(assessment.id)
        self.assertTrue(result)
        
        deleted = get_assessment_by_id(assessment.id)
        self.assertIsNone(deleted)
    
    def test_unschedule_assessment_only(self):
        create_assessment(
            course_code="COMP1602",
            name="CW1",
            percentage=20,
            start_week=8,
            start_day=1,
            end_week=11,
            end_day=7,
            proctored=1
        )
        
        assessment = get_assessment("COMP1602", "CW1")
        
        schedule_date = self.semester.start_date + timedelta(days=70)  
        schedule_assessment(
            semester=self.semester,
            schedule_date=schedule_date,
            course_code="COMP1602",
            name="CW1"
        )
        
        assessment = get_assessment("COMP1602", "CW1")
        self.assertIsNotNone(assessment.scheduled)
        
        result = unschedule_assessment_only(assessment.id)
        self.assertTrue(result)
        
        assessment = get_assessment_by_id(assessment.id)
        self.assertIsNone(assessment.scheduled)
    
    def test_reset_assessment_constraints(self):
        create_assessment(
            course_code="COMP1601",
            name="CW1",
            percentage=10,
            start_week=6,
            start_day=1,
            end_week=7,
            end_day=7,
            proctored=1
        )
        
        assessment = get_assessment("COMP1601", "CW1")
        
        schedule_date = self.semester.start_date + timedelta(days=42)  
        schedule_assessment(
            semester=self.semester,
            schedule_date=schedule_date,
            course_code="COMP1601",
            name="CW1"
        )
        
        result = reset_assessment_constraints(
            assessment_id=assessment.id,
            original_start_week=2,
            original_start_day=1,
            original_end_week=5,
            original_end_day=7
        )
        
        self.assertTrue(result)
        
        assessment = get_assessment_by_id(assessment.id)
        self.assertEqual(assessment.start_week, 2)
        self.assertEqual(assessment.start_day, 1)
        self.assertEqual(assessment.end_week, 5)
        self.assertEqual(assessment.end_day, 7)
        self.assertIsNone(assessment.scheduled)
    
    def test_reset_all_assessment_constraints(self):
        create_assessment(
            course_code="COMP1601",
            name="A1",
            percentage=6,
            start_week=2,
            start_day=1,
            end_week=4,
            end_day=7,
            proctored=0
        )
        
        create_assessment(
            course_code="COMP1602",
            name="A1",
            percentage=15,
            start_week=2,
            start_day=1,
            end_week=5,
            end_day=7,
            proctored=0
        )
        
        count = reset_all_assessment_constraints()
        self.assertEqual(count, 2)
        
        assessments = get_all_assessments()
        for assessment in assessments:
            self.assertEqual(assessment.start_week, 1)
            self.assertEqual(assessment.start_day, 1)
            self.assertEqual(assessment.end_week, 15)
            self.assertEqual(assessment.end_day, 5)


if __name__ == "__main__":
    unittest.main()
