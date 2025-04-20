import unittest, logging, sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from App.database import db
from App.models.course import Course
from App.models.staff import Staff
from App.models.semester import Semester
from App.models.semester_course import SemesterCourse
from App.models.course_lecturer import CourseLecturer
from App.controllers.course import (
    get_course,
    get_all_courses,
    get_all_course_codes,
    get_course_codes,
    get_course_name,
    create_course,
    delete_course,
    update_course,
    assign_lecturer,
    assign_multiple_lecturers,
    get_course_lecturers,
    remove_lecturer,
    get_lecturer_assignments,
    get_course_lecturer_count
)
from App.main import create_app

LOGGER = logging.getLogger(__name__)

class CourseIntegrationTests(unittest.TestCase):
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
        
        self.comp1601 = Course(
            code="COMP1601",
            name="Introduction to Computer Programming I",
            level="1",
            credits=3,
            semester="1"
        )
        self.comp1602 = Course(
            code="COMP1602",
            name="Introduction to Computer Programming II",
            level="1",
            credits=3,
            semester="2"
        )
        self.info1600 = Course(
            code="INFO1600",
            name="Introduction to Information Technology Concepts",
            level="1",
            credits=3,
            semester="1"
        )
        
        db.session.add(self.comp1601)
        db.session.add(self.comp1602)
        db.session.add(self.info1600)
        
        self.staff1 = Staff(
            id="3000001",
            email="kris.manohar@sta.uwi.edu",
            password="password",
            first_name="Kris",
            last_name="Manohar",
            department="DCIT",
            faculty="FST"
        )
        self.staff2 = Staff(
            id="3000002",
            email="wayne.goodridge@sta.uwi.edu",
            password="password",
            first_name="Wayne",
            last_name="Goodridge",
            department="DCIT",
            faculty="FST"
        )
        
        db.session.add(self.staff1)
        db.session.add(self.staff2)
        
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
        
        db.session.add(self.course_lecturer1)
        
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_course(self):
        course = get_course("COMP1601")
        self.assertIsNotNone(course)
        self.assertEqual(course.code, "COMP1601")
        self.assertEqual(course.name, "Introduction to Computer Programming I")
        self.assertEqual(course.level, "1")
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.semester, "1")
        
        non_existent = get_course("COMP9999")
        self.assertIsNone(non_existent)
    
    def test_get_all_courses(self):
        courses = get_all_courses()
        self.assertEqual(len(courses), 3)
        
        course_codes = [course.code for course in courses]
        self.assertIn("COMP1601", course_codes)
        self.assertIn("COMP1602", course_codes)
        self.assertIn("INFO1600", course_codes)
    
    def test_get_all_course_codes(self):
        codes = get_all_course_codes()
        self.assertEqual(len(codes), 3)
        self.assertIn("COMP1601", codes)
        self.assertIn("COMP1602", codes)
        self.assertIn("INFO1600", codes)
    
    def test_get_course_codes(self):
        courses = get_all_courses()
        codes = get_course_codes(courses)
        self.assertEqual(len(codes), 3)
        self.assertIn("COMP1601", codes)
        self.assertIn("COMP1602", codes)
        self.assertIn("INFO1600", codes)
    
    def test_get_course_name(self):
        name = get_course_name("COMP1601")
        self.assertEqual(name, "Introduction to Computer Programming I")
        
        non_existent_name = get_course_name("COMP9999")
        self.assertIsNone(non_existent_name)
    
    def test_create_course(self):
        result = create_course(
            course_code="COMP2611",
            course_name="Data Structures",
            level="2",
            credits=3,
            semester="1"
        )
        self.assertTrue(result)
        
        course = get_course("COMP2611")
        self.assertIsNotNone(course)
        self.assertEqual(course.code, "COMP2611")
        self.assertEqual(course.name, "Data Structures")
        self.assertEqual(course.level, "2")
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.semester, "1")
        
        result = create_course(
            course_code="COMP1601",
            course_name="Duplicate Course",
            level="1",
            credits=3,
            semester="1"
        )
        self.assertFalse(result)
    
    def test_delete_course(self):
        result = delete_course("COMP1602")
        self.assertTrue(result)
        
        course = get_course("COMP1602")
        self.assertIsNone(course)
        
        result = delete_course("COMP9999")
        self.assertFalse(result)
    
    def test_update_course(self):
        result = update_course(
            course_code="COMP1601",
            new_course_code="COMP1601",
            new_course_name="Intro to Programming I - Updated",
            level="1",
            credits=4,
            semester="1"
        )
        self.assertTrue(result)
        
        course = get_course("COMP1601")
        self.assertIsNotNone(course)
        self.assertEqual(course.name, "Intro to Programming I - Updated")
        self.assertEqual(course.credits, 4)
        
        result = update_course(
            course_code="COMP9999",
            new_course_code="COMP9999",
            new_course_name="Non-existent Course",
            level="1",
            credits=3,
            semester="1"
        )
        self.assertFalse(result)
        
        result = update_course(
            course_code="INFO1600",
            new_course_code="INFO1601",
            new_course_name="Introduction to WWW Programming",
            level="1",
            credits=3,
            semester="2"
        )
        self.assertTrue(result)
        
        course = get_course("INFO1601")
        self.assertIsNotNone(course)
        old_course = get_course("INFO1600")
        self.assertIsNone(old_course)
    
    def test_assign_lecturer(self):
        result = assign_lecturer(
            lecturer_id="3000002",
            course_code="COMP1602"
        )
        self.assertTrue(result)
        
        lecturers = get_course_lecturers("COMP1602")
        self.assertEqual(len(lecturers), 1)
        self.assertEqual(str(lecturers[0].id), "3000002")
        
        result = assign_lecturer(
            lecturer_id="9999999",
            course_code="COMP1602"
        )
        self.assertFalse(result)
        
        result = assign_lecturer(
            lecturer_id="3000001",
            course_code="COMP9999"
        )
        self.assertFalse(result)
        
        result = assign_lecturer(
            lecturer_id="3000002",
            course_code="COMP1602"
        )
        self.assertTrue(result)
        
        lecturers = get_course_lecturers("COMP1602")
        self.assertEqual(len(lecturers), 1)
    
    def test_assign_multiple_lecturers(self):
        result = assign_multiple_lecturers(
            lecturer_ids=["3000001", "3000002"],
            course_code="INFO1600"
        )
        self.assertTrue(result)
        
        lecturers = get_course_lecturers("INFO1600")
        self.assertEqual(len(lecturers), 2)
        lecturer_ids = [str(lecturer.id) for lecturer in lecturers]
        self.assertIn("3000001", lecturer_ids)
        self.assertIn("3000002", lecturer_ids)
        
        result = assign_multiple_lecturers(
            lecturer_ids=["3000002"],
            course_code="INFO1600"
        )
        self.assertTrue(result)
        
        lecturers = get_course_lecturers("INFO1600")
        self.assertEqual(len(lecturers), 1)
        self.assertEqual(str(lecturers[0].id), "3000002")
        
        result = assign_multiple_lecturers(
            lecturer_ids=["3000001", "3000002"],
            course_code="COMP9999"
        )
        self.assertFalse(result)
    
    def test_get_course_lecturers(self):
        lecturer2 = CourseLecturer(
            course_code="COMP1601",
            staff_id="3000002"
        )
        db.session.add(lecturer2)
        db.session.commit()
        
        lecturers = get_course_lecturers("COMP1601")
        self.assertEqual(len(lecturers), 2)
        lecturer_ids = [str(lecturer.id) for lecturer in lecturers]
        self.assertIn("3000001", lecturer_ids)
        self.assertIn("3000002", lecturer_ids)
        
        lecturers = get_course_lecturers("INFO1600")
        self.assertEqual(len(lecturers), 0)
        
        lecturers = get_course_lecturers("COMP9999")
        self.assertIsNone(lecturers)
    
    def test_remove_lecturer(self):
        result = remove_lecturer(
            lecturer_id="3000001",
            course_code="COMP1601"
        )
        self.assertTrue(result)
        
        lecturers = get_course_lecturers("COMP1601")
        self.assertEqual(len(lecturers), 0)
        
        result = remove_lecturer(
            lecturer_id="9999999",
            course_code="COMP1601"
        )
        self.assertFalse(result)
        
        result = remove_lecturer(
            lecturer_id="3000001",
            course_code="COMP9999"
        )
        self.assertFalse(result)
        
        result = remove_lecturer(
            lecturer_id="3000002",
            course_code="COMP1602"
        )
        self.assertFalse(result)
    
    def test_get_lecturer_assignments(self):
        lecturer2 = CourseLecturer(
            course_code="INFO1600",
            staff_id="3000001"
        )
        db.session.add(lecturer2)
        db.session.commit()
        
        assignments = get_lecturer_assignments("3000001")
        self.assertEqual(len(assignments), 2)
        
        course_codes = [assignment["course_code"] for assignment in assignments]
        self.assertIn("COMP1601", course_codes)
        self.assertIn("INFO1600", course_codes)
        
        assignments = get_lecturer_assignments("3000002")
        self.assertEqual(len(assignments), 0)
        
        assignments = get_lecturer_assignments("9999999")
        self.assertEqual(len(assignments), 0)
    
    def test_get_course_lecturer_count(self):
        count = get_course_lecturer_count()
        self.assertEqual(count, 1)
        
        lecturer2 = CourseLecturer(
            course_code="INFO1600",
            staff_id="3000001"
        )
        lecturer3 = CourseLecturer(
            course_code="COMP1602",
            staff_id="3000002"
        )
        db.session.add(lecturer2)
        db.session.add(lecturer3)
        db.session.commit()
        
        count = get_course_lecturer_count()
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main() 