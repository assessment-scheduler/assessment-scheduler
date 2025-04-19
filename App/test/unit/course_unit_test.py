import logging, unittest
from App.models.course import Course

LOGGER: logging.Logger = logging.getLogger(__name__)

class CourseUnitTests(unittest.TestCase):
    def test_new_course(self):
        course = Course(
            code="COMP1609",
            name="Introduction to Code Testing",
            level="1",
            credits=3,
            semester="1"
        )
        
        self.assertEqual(course.code, "COMP1609")
        self.assertEqual(course.name, "Introduction to Code Testing")
        self.assertEqual(course.level, "1")
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.semester, "1")
    
    def test_repr(self):
        course = Course(
            code="COMP1609",
            name="Introduction to Code Testing"
        )
        
        expected_repr = "COMP1609 : Introduction to Code Testing"
        self.assertEqual(repr(course), expected_repr)
    
    def test_to_json(self):
        course = Course(
            code="COMP1609",
            name="Introduction to Code Testing",
            level="1",
            credits=3,
            semester="1"
        )
        
        json_data = course.to_json()
        
        self.assertEqual(json_data['code'], "COMP1609")
        self.assertEqual(json_data['name'], "Introduction to Code Testing")
        self.assertEqual(json_data['level'], "1")
        self.assertEqual(json_data['credits'], 3)
        self.assertEqual(json_data['semester'], "1")
        self.assertEqual(json_data['lecturers'], [])
        self.assertEqual(json_data['semesters'], [])
