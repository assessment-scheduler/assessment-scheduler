import unittest, logging, sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from App.database import db
from App.models.user import User
from App.models.staff import Staff
from App.models.admin import Admin
from App.models.course import Course
from App.models.semester import Semester
from App.models.semester_course import SemesterCourse
from App.models.course_lecturer import CourseLecturer
from App.controllers.user import (
    validate_staff,
    validate_admin,
    create_user,
    change_password,
    get_user_by_email,
    get_user_by_id,
    valdiate_user,
    get_all_users,
    get_all_users_json
)
from App.controllers.admin import (
    get_admin_by_id,
    get_admin_by_email,
    create_admin_user,
    update_admin,
    delete_admin,
    is_admin,
    validate_admin as admin_validate_admin
)
from App.controllers.staff import (
    create_staff,
    get_staff,
    get_staff_by_id,
    get_all_staff,
    get_staff_by_email,
    update_staff,
    delete_staff,
    get_staff_courses,
    is_course_lecturer,
    validate_staff as staff_validate_staff,
    assign_course_to_staff,
    associate_with_semester,
    get_staff_courses_in_active_semester
)
from App.main import create_app

LOGGER = logging.getLogger(__name__)

class UserIntegrationTests(unittest.TestCase):
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
        
        self.course1 = Course(
            code="COMP1601",
            name="Introduction to Computer Programming I",
            level="1",
            credits=3,
            semester="1"
        )
        self.course2 = Course(
            code="COMP1602",
            name="Introduction to Computer Programming II",
            level="1",
            credits=3,
            semester="2"
        )
        db.session.add(self.course1)
        db.session.add(self.course2)
        
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_and_get_user(self):
        user = create_user(id=1, email="user@test.com", password="password")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "user@test.com")
        
        retrieved_user = get_user_by_email("user@test.com")
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.id, 1)
        self.assertEqual(retrieved_user.email, "user@test.com")
        
        retrieved_user_by_id = get_user_by_id(1)
        self.assertIsNotNone(retrieved_user_by_id)
        self.assertEqual(retrieved_user_by_id.email, "user@test.com")
    
    def test_change_password(self):
        user = create_user(id=1, email="user@test.com", password="password")
        
        result = change_password(email="user@test.com", password="newpassword")
        self.assertTrue(result)
        
        self.assertTrue(user.check_password("newpassword"))
        self.assertFalse(user.check_password("password"))
        
        result = change_password(email="nonexistent@test.com", password="newpassword")
        self.assertTrue(result)
    
    def test_validate_user(self):
        create_user(id=1, email="user@test.com", password="password")
        
        user = valdiate_user(email="user@test.com", password="password")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "user@test.com")
        
        user = valdiate_user(email="user@test.com", password="wrongpassword")
        self.assertIsNone(user)
        
        user = valdiate_user(email="nonexistent@test.com", password="password")
        self.assertIsNone(user)
    
    def test_get_all_users(self):
        create_user(id=1, email="user1@test.com", password="password")
        create_user(id=2, email="user2@test.com", password="password")
        
        users = get_all_users()
        self.assertEqual(len(users), 2)
        
        user_emails = [user.email for user in users]
        self.assertIn("user1@test.com", user_emails)
        self.assertIn("user2@test.com", user_emails)
    
    def test_get_all_users_json(self):
        create_user(id=1, email="user1@test.com", password="password")
        create_user(id=2, email="user2@test.com", password="password")
        
        with self.app.test_request_context():
            response = get_all_users_json()
            data = response.get_json()
            self.assertEqual(len(data), 2)
            
            user_emails = [user["email"] for user in data]
            self.assertIn("user1@test.com", user_emails)
            self.assertIn("user2@test.com", user_emails)
    
    def test_create_and_get_admin(self):
        result = create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        self.assertTrue(result)
        
        admin = get_admin_by_email("admin@test.com")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.id, 1000001)
        
        admin_by_id = get_admin_by_id("1000001")
        self.assertIsNotNone(admin_by_id)
        self.assertEqual(admin_by_id.email, "admin@test.com")
    
    def test_update_admin(self):
        create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        
        result = update_admin(admin_id="1000001", email="newemail@test.com")
        self.assertTrue(result)
        
        admin = get_admin_by_id("1000001")
        self.assertEqual(admin.email, "newemail@test.com")
        
        result = update_admin(admin_id="1000001", password="newpassword")
        self.assertTrue(result)
        
        admin = get_admin_by_id("1000001")
        self.assertTrue(admin.check_password("newpassword"))
        
        result = update_admin(admin_id="nonexistent", email="newemail@test.com")
        self.assertFalse(result)
    
    def test_delete_admin(self):
        create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        
        result = delete_admin(admin_id="1000001")
        self.assertTrue(result)
        
        admin = get_admin_by_id("1000001")
        self.assertIsNone(admin)
        
        result = delete_admin(admin_id="nonexistent")
        self.assertFalse(result)
    
    def test_is_admin(self):
        create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        
        result = is_admin(email="admin@test.com")
        self.assertTrue(result)
        
        result = is_admin(email="nonexistent@test.com")
        self.assertFalse(result)
    
    def test_admin_validate_admin(self):
        create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        
        result = admin_validate_admin(email="admin@test.com", password="password")
        self.assertTrue(result)
        
        result = admin_validate_admin(email="admin@test.com", password="wrongpassword")
        self.assertFalse(result)
        
        result = admin_validate_admin(email="nonexistent@test.com", password="password")
        self.assertFalse(result)
    
    def test_create_and_get_staff(self):
        result = create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        self.assertTrue(result)
        
        staff = get_staff("staff@test.com")
        self.assertIsNotNone(staff)
        self.assertEqual(staff.id, 3000001)
        self.assertEqual(staff.email, "staff@test.com")
        self.assertEqual(staff.first_name, "Test")
        self.assertEqual(staff.last_name, "Staff")
        self.assertEqual(staff.department, "DCIT")
        self.assertEqual(staff.faculty, "FST")
        
        staff_by_id = get_staff_by_id("3000001")
        self.assertIsNotNone(staff_by_id)
        self.assertEqual(staff_by_id.email, "staff@test.com")
        
        staff_by_email = get_staff_by_email("staff@test.com")
        self.assertIsNotNone(staff_by_email)
        self.assertEqual(staff_by_email.id, 3000001)
        
        result = create_staff(
            id="3000002",
            email="staff@test.com",
            password="password",
            first_name="Another",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        self.assertFalse(result)
    
    def test_get_all_staff(self):
        create_staff(
            id="3000001",
            email="staff1@test.com",
            password="password",
            first_name="Test1",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        create_staff(
            id="3000002",
            email="staff2@test.com",
            password="password",
            first_name="Test2",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        staff_list = get_all_staff()
        self.assertEqual(len(staff_list), 2)
        
        staff_emails = [staff.email for staff in staff_list]
        self.assertIn("staff1@test.com", staff_emails)
        self.assertIn("staff2@test.com", staff_emails)
    
    def test_update_staff(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        result = update_staff(
            id="3000001",
            email="newemail@test.com",
            first_name="Updated",
            last_name="Staff",
            department="ECE",
            faculty="ENG"
        )
        self.assertTrue(result)
        
        staff = get_staff_by_id("3000001")
        self.assertEqual(staff.email, "newemail@test.com")
        self.assertEqual(staff.first_name, "Updated")
        self.assertEqual(staff.department, "ECE")
        self.assertEqual(staff.faculty, "ENG")
        
        result = update_staff(
            id="nonexistent",
            email="newemail@test.com",
            first_name="Updated",
            last_name="Staff"
        )
        self.assertFalse(result)
    
    def test_delete_staff(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        result = delete_staff(id="3000001")
        self.assertTrue(result)
        
        staff = get_staff_by_id("3000001")
        self.assertIsNone(staff)
        
        result = delete_staff(id="nonexistent")
        self.assertFalse(result)
    
    def test_staff_validate_staff(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        result = staff_validate_staff(email="staff@test.com", password="password")
        self.assertTrue(result)
        
        result = staff_validate_staff(email="staff@test.com", password="wrongpassword")
        self.assertFalse(result)
        
        result = staff_validate_staff(email="nonexistent@test.com", password="password")
        self.assertFalse(result)
    
    def test_is_course_lecturer(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        course_lecturer = CourseLecturer(
            course_code="COMP1601",
            staff_id="3000001"
        )
        db.session.add(course_lecturer)
        db.session.commit()
        
        result = is_course_lecturer(staff_id="3000001", course_code="COMP1601")
        self.assertTrue(result)
        
        result = is_course_lecturer(staff_id="3000001", course_code="COMP1602")
        self.assertFalse(result)
        
        result = is_course_lecturer(staff_id="nonexistent", course_code="COMP1601")
        self.assertFalse(result)
    
    def test_get_staff_courses(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        course_lecturer1 = CourseLecturer(
            course_code="COMP1601",
            staff_id="3000001"
        )
        course_lecturer2 = CourseLecturer(
            course_code="COMP1602",
            staff_id="3000001"
        )
        db.session.add(course_lecturer1)
        db.session.add(course_lecturer2)
        db.session.commit()
        
        courses = get_staff_courses("3000001")
        self.assertEqual(len(courses), 2)
        
        course_codes = [course.code for course in courses]
        self.assertIn("COMP1601", course_codes)
        self.assertIn("COMP1602", course_codes)
        
        courses = get_staff_courses("staff@test.com")
        self.assertEqual(len(courses), 2)
        
        courses = get_staff_courses("nonexistent")
        self.assertEqual(len(courses), 0)
    
    def test_associate_with_semester(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        result = associate_with_semester(staff_id="3000001", semester_id=1)
        self.assertTrue(result)
        
        staff = get_staff_by_id("3000001")
        self.assertEqual(len(staff.semesters), 1)
        self.assertEqual(staff.semesters[0].id, 1)
        
        result = associate_with_semester(staff_id="nonexistent", semester_id=1)
        self.assertFalse(result)
        
        result = associate_with_semester(staff_id="3000001", semester_id=999)
        self.assertFalse(result)
    
    def test_get_staff_courses_in_active_semester(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        course_lecturer1 = CourseLecturer(
            course_code="COMP1601",
            staff_id="3000001"
        )
        course_lecturer2 = CourseLecturer(
            course_code="COMP1602",
            staff_id="3000001"
        )
        semester_course1 = SemesterCourse(
            semester_id=1,
            course_code="COMP1601"
        )
        
        db.session.add(course_lecturer1)
        db.session.add(course_lecturer2)
        db.session.add(semester_course1)
        db.session.commit()
        
        courses = get_staff_courses_in_active_semester("3000001")
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].code, "COMP1601")
        
        courses = get_staff_courses_in_active_semester("nonexistent")
        self.assertEqual(len(courses), 0)
    
    def test_validate_staff_across_controllers(self):
        create_staff(
            id="3000001",
            email="staff@test.com",
            password="password",
            first_name="Test",
            last_name="Staff",
            department="DCIT",
            faculty="FST"
        )
        
        staff = validate_staff("staff@test.com", "password")
        self.assertIsNotNone(staff)
        self.assertEqual(staff.email, "staff@test.com")
        
        staff = validate_staff("staff@test.com", "wrongpassword")
        self.assertIsNone(staff)
        
        staff = validate_staff("nonexistent@test.com", "password")
        self.assertIsNone(staff)
    
    def test_validate_admin_across_controllers(self):
        create_admin_user(admin_id="1000001", email="admin@test.com", password="password")
        
        admin = validate_admin("admin@test.com", "password")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.email, "admin@test.com")
        
        admin = validate_admin("admin@test.com", "wrongpassword")
        self.assertIsNone(admin)
        
        admin = validate_admin("nonexistent@test.com", "password")
        self.assertIsNone(admin)


if __name__ == "__main__":
    unittest.main() 