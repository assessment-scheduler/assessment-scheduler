import logging, unittest
from App.models.courseoverlap import CourseOverlap

LOGGER: logging.Logger = logging.getLogger(__name__)

class CourseOverlapUnitTests(unittest.TestCase):
    def test_new_course_overlap(self):
        course_overlap = CourseOverlap(
            code1="COMP1609",
            code2="COMP1612",
            student_count=25
        )
        
        self.assertEqual(course_overlap.code1, "COMP1609")
        self.assertEqual(course_overlap.code2, "COMP1612")
        self.assertEqual(course_overlap.student_count, 25)
    
    def test_repr(self):
        course_overlap = CourseOverlap(
            code1="COMP1609",
            code2="COMP1612",
            student_count=25
        )
        
        expected_repr = "25"
        self.assertEqual(repr(course_overlap), expected_repr)
        
    def test_student_count_update(self):
        course_overlap = CourseOverlap(
            code1="COMP1609",
            code2="COMP1612",
            student_count=25
        )
        
        course_overlap.student_count = 30
        self.assertEqual(course_overlap.student_count, 30)
        self.assertEqual(repr(course_overlap), "30")
    
    def test_course_code_order(self):
        cl1 = CourseOverlap(
            code1="COMP1609",
            code2="COMP1612",
            student_count=25
        )
        
        cl2 = CourseOverlap(
            code1="COMP1612",
            code2="COMP1609",
            student_count=25
        )
        
        self.assertEqual(cl1.code1, "COMP1609")
        self.assertEqual(cl1.code2, "COMP1612")
        self.assertEqual(cl2.code1, "COMP1612")
        self.assertEqual(cl2.code2, "COMP1609") 