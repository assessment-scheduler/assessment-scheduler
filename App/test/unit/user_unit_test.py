import logging, unittest
from App.models.user import User
from App.models.staff import Staff
from App.models.admin import Admin
from werkzeug.security import check_password_hash

LOGGER: logging.Logger = logging.getLogger(__name__)

class UserUnitTests(unittest.TestCase):
    def test_new_user(self):
        user = User(
            id=1001,
            email="test@example.com",
            password="testPassword123"
        )
        
        self.assertEqual(user.id, 1001)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(check_password_hash(user.password, "testPassword123"))
    
    def test_set_password(self):
        user = User(
            id=1002,
            email="test2@example.com",
            password="initialPassword"
        )
        
        user.set_password("newPassword123")
        self.assertTrue(user.check_password("newPassword123"))
        self.assertFalse(user.check_password("initialPassword"))
    
    def test_to_json(self):
        user = User(
            id=1003,
            email="test3@example.com",
            password="password123"
        )
        
        json_data = user.to_json()
        
        self.assertEqual(json_data['id'], 1003)
        self.assertEqual(json_data['email'], "test3@example.com")
    
    def test_repr(self):
        user = User(
            id=1004,
            email="test4@example.com",
            password="password123"
        )
        
        expected_repr = "Staff(id=1004, email=test4@example.com)"
        self.assertEqual(repr(user), expected_repr)

class StaffUnitTests(unittest.TestCase):
    def test_new_staff(self):
        staff = Staff(
            id="816000456",
            email="staff@sta.uwi.edu",
            password="staffPass123",
            first_name="John",
            last_name="Doe",
            department="DCIT",
            faculty="FST"
        )
        
        self.assertEqual(staff.id, "816000456")
        self.assertEqual(staff.email, "staff@sta.uwi.edu")
        self.assertTrue(check_password_hash(staff.password, "staffPass123"))
        self.assertEqual(staff.first_name, "John")
        self.assertEqual(staff.last_name, "Doe")
        self.assertEqual(staff.department, "DCIT")
        self.assertEqual(staff.faculty, "FST")
    
    
    def test_staff_to_json(self):
        staff = Staff(
            id="816000456",
            email="staff3@sta.uwi.edu",
            password="staffPass123",
            first_name="Bob",
            last_name="Johnson",
            department="DCIT",
            faculty="FST"
        )
        
        json_data = staff.to_json()
        
        self.assertEqual(json_data['staff_ID'], "816000456")
        self.assertEqual(json_data['firstName'], "Bob")
        self.assertEqual(json_data['lastName'], "Johnson")
        self.assertEqual(json_data['email'], "staff3@sta.uwi.edu")
        self.assertEqual(json_data['department'], "DCIT")
        self.assertEqual(json_data['faculty'], "FST")
        self.assertEqual(json_data['courses'], [])
        self.assertEqual(json_data['active_semesters'], [])
    
    def test_staff_repr(self):
        staff = Staff(
            id="816000456",
            email="staff4@sta.uwi.edu",
            password="staffPass123",
            first_name="Alice",
            last_name="Brown"
        )
        
        expected_repr = "Staff(id=816000456, email=staff4@sta.uwi.edu)"
        self.assertEqual(repr(staff), expected_repr)

class AdminUnitTests(unittest.TestCase):
    def test_new_admin(self):
        admin = Admin(
            id="816000456",
            email="admin@sta.uwi.edu",
            password="adminPass123"
        )
        
        self.assertEqual(admin.id, "816000456")
        self.assertEqual(admin.email, "admin@sta.uwi.edu")
        self.assertTrue(check_password_hash(admin.password, "adminPass123"))
    
    def test_admin_get_id(self):
        admin = Admin(
            id="816000456",
            email="admin2@sta.uwi.edu",
            password="adminPass123"
        )
        
        self.assertEqual(admin.get_id(), "816000456")
    
    def test_admin_to_json(self):
        admin = Admin(
            id="816000456",
            email="admin3@sta.uwi.edu",
            password="adminPass123"
        )
        
        json_data = admin.to_json()
        
        self.assertEqual(json_data['id'], "816000456")
        self.assertEqual(json_data['email'], "admin3@sta.uwi.edu")
    
    def test_admin_repr(self):
        admin = Admin(
            id="816000456",
            email="admin4@sta.uwi.edu",
            password="adminPass123"
        )
        
        expected_repr = "Admin(id=816000456, email=admin4@sta.uwi.edu)"
        self.assertEqual(repr(admin), expected_repr) 