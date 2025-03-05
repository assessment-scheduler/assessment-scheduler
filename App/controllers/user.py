from App.models import User, Admin, Staff
from App.database import db
from flask import jsonify

def validate_staff(email, password):
    staff = Staff.query.filter_by(email=email).first()
    if staff and staff.check_password(password):
        return staff
    return None

def validate_admin(email, password):
    admin = Admin.query.filter_by(email=email).first()
    if admin and admin.check_password(password):
        return admin
    return None

def get_user(email, password):
    """
    Returns the user object if the email and password are correct
    """
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None

def get_user_id(email): 
    return Staff.query.filter_by(email=email).first().id

def get_uid(id):
    """
    Returns the user ID for a given ID
    """
    from App.models.user import User
    user = User.query.filter_by(id=id).first()
    if user:
        return user.id
    return None

def create_user(username, password, id, role, email):
    """
    Creates a new user with the given parameters
    """
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None
    
    # Create new user based on role
    if role == 'admin':
        new_user = Admin(id=id, password=password, email=email)
    elif role == 'staff':
        new_user = Staff(f_name=username, l_name="", id=id, status="", email=email, password=password, department="", faculty="")
    else:
        return None
    
    # Add to database
    db.session.add(new_user)
    db.session.commit()
    
    return new_user

def get_all_users():
    """
    Returns all users in the database
    """
    return User.query.all()

def get_all_users_json():
    """
    Returns all users in the database as a JSON response
    """
    users = User.query.all()
    if not users:
        return jsonify([])
    users_json = [user.to_json() for user in users]
    return jsonify(users_json)