import logging, unittest
from datetime import date
from App.models.semester import Semester

LOGGER: logging.Logger = logging.getLogger(__name__)

class SemesterUnitTests(unittest.TestCase):
    def test_new_semester(self):
        semester = Semester(
            start_date=date.fromisoformat("2024-01-15"),
            end_date=date.fromisoformat("2024-05-15"),
            sem_num=1,
            max_assessments=5,
            constraint_value=1500,
            active=True,
            solver_type='kris'
        )
        
        self.assertEqual(semester.start_date, date.fromisoformat("2024-01-15"))
        self.assertEqual(semester.end_date, date.fromisoformat("2024-05-15"))
        self.assertEqual(semester.sem_num, 1)
        self.assertEqual(semester.max_assessments, 5)
        self.assertEqual(semester.constraint_value, 1500)
        self.assertTrue(semester.active)
        self.assertEqual(semester.solver_type, 'kris')
    
    def test_get_solver(self):
        semester = Semester(
            start_date=date.fromisoformat("2024-01-15"),
            end_date=date.fromisoformat("2024-05-15"),
            sem_num=1,
            max_assessments=5
        )
        
        solver = semester.get_solver()
        self.assertIsNotNone(solver)
    
    def test_to_json(self):
        semester = Semester(
            start_date=date.fromisoformat("2024-01-15"),
            end_date=date.fromisoformat("2024-05-15"),
            sem_num=1,
            max_assessments=5,
            constraint_value=1200,
            active=True
        )
        
        semester.id = 1
        
        json_data = semester.to_json()
        
        self.assertEqual(json_data['id'], 1)
        self.assertEqual(json_data['start_date'], "2024-01-15")
        self.assertEqual(json_data['end_date'], "2024-05-15")
        self.assertEqual(json_data['sem_num'], 1)
        self.assertEqual(json_data['max_assessments'], 5)
        self.assertEqual(json_data['constraint_value'], 1200)
        self.assertTrue(json_data['active'])
        self.assertEqual(json_data['solver_type'], 'kris')
        self.assertEqual(json_data['courses'], [])
    
    def test_repr(self):
        semester = Semester(
            start_date=date.fromisoformat("2024-01-15"),
            end_date=date.fromisoformat("2024-05-15"),
            sem_num=1,
            max_assessments=5,
            active=True
        )
        
        semester.id = 1
        
        repr_string = repr(semester)
        
        self.assertIn("ID: 1", repr_string)
        self.assertIn("Start Date: 2024-01-15", repr_string)
        self.assertIn("End Date: 2024-05-15", repr_string)
        self.assertIn("Semester Number: 1", repr_string)
        self.assertIn("Max Assessments: 5", repr_string)
        self.assertIn("Active: True", repr_string)
        self.assertIn("Solver: kris", repr_string)