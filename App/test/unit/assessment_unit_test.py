import logging, unittest
from App.models.assessment import Assessment
from datetime import date

LOGGER: logging.Logger = logging.getLogger(__name__)

class AssessmentUnitTests(unittest.TestCase):
    def test_new_assessment(self):
        assessment = Assessment(
            course_code="COMP1601",
            name="Midterm Exam",
            percentage=20,
            start_week=5,
            start_day=2,
            end_week=5,
            end_day=2,
            proctored=1
        )
        
        self.assertEqual(assessment.course_code, "COMP1601")
        self.assertEqual(assessment.name, "Midterm Exam")
        self.assertEqual(assessment.percentage, 20)
        self.assertEqual(assessment.start_week, 5)
        self.assertEqual(assessment.start_day, 2)
        self.assertEqual(assessment.end_week, 5)
        self.assertEqual(assessment.end_day, 2)
        self.assertEqual(assessment.proctored, 1)
        self.assertIsNone(assessment.scheduled)
        
    def test_to_json(self):
        assessment = Assessment(
            course_code="COMP1602",
            name="Final Exam",
            percentage=40,
            start_week=12,
            start_day=5,
            end_week=12,
            end_day=5,
            proctored=1
        )
        
        json_data = assessment.to_json()
        
        self.assertEqual(json_data['course_code'], "COMP1602")
        self.assertEqual(json_data['name'], "Final Exam")
        self.assertEqual(json_data['percentage'], 40)
        self.assertEqual(json_data['start_week'], 12)
        self.assertEqual(json_data['start_day'], 5)
        self.assertEqual(json_data['end_week'], 12)
        self.assertEqual(json_data['end_day'], 5)
        self.assertEqual(json_data['proctored'], 1)
        self.assertEqual(json_data['scheduled'], None)
    
    def test_repr_no_schedule(self):
        assessment = Assessment(
            course_code="COMP1603",
            name="Assignment 1",
            percentage=15,
            start_week=3,
            start_day=1,
            end_week=4,
            end_day=5,
            proctored=0
        )
        
        expected_repr = "COMP1603 Assignment 1: 15% Scheduled for N/A"
        self.assertEqual(repr(assessment), expected_repr)
    
    def test_repr_with_schedule(self):
        assessment = Assessment(
            course_code="COMP1603",
            name="Assignment 2",
            percentage=15,
            start_week=8,
            start_day=1,
            end_week=9,
            end_day=5,
            proctored=0
        )
        
        test_date = date(2023, 11, 15)
        assessment.scheduled = test_date
        
        expected_repr = f"COMP1603 Assignment 2: 15% Scheduled for {test_date}"
        self.assertEqual(repr(assessment), expected_repr)
    
    def test_proctored_assessment(self):
        proctored = Assessment(
            course_code="COMP1604",
            name="Midterm Exam",
            percentage=30,
            start_week=6,
            start_day=3,
            end_week=6,
            end_day=3,
            proctored=1
        )
        
        not_proctored = Assessment(
            course_code="COMP1604",
            name="Lab Assignment",
            percentage=10,
            start_week=7,
            start_day=1,
            end_week=7,
            end_day=5,
            proctored=0
        )
        
        self.assertEqual(proctored.proctored, 1)
        self.assertEqual(not_proctored.proctored, 0)
    
    def test_assessment_date_range(self):
        single_day = Assessment(
            course_code="COMP1605",
            name="Quiz 1",
            percentage=5,
            start_week=4,
            start_day=2,
            end_week=4,
            end_day=2,
            proctored=1
        )
        
        multi_day = Assessment(
            course_code="COMP1605",
            name="Project",
            percentage=25,
            start_week=9,
            start_day=1,
            end_week=10,
            end_day=5,
            proctored=0
        )
        
        self.assertEqual(single_day.start_week, single_day.end_week)
        self.assertEqual(single_day.start_day, single_day.end_day)
        self.assertLess(multi_day.start_week, multi_day.end_week)
        self.assertLessEqual(multi_day.start_day, 7)
        self.assertLessEqual(multi_day.end_day, 7) 