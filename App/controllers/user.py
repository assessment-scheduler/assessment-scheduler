from App.models import User, Admin, Staff
from App.database import db

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
    user = validate_staff(email, password)
    if user is not None:
        return user
    user = validate_admin(email, password)
    if user is not None:
        return user
    return None

def get_user_id(email): return Staff.query.filter_by(email=email).first().u_ID

def get_uid(id):
    """
    Returns the user ID for a given ID
    """
    from App.models.user import User
    user = User.query.filter_by(id=id).first()
    if user:
        return user.id
    return None

def create_user(username, password, u_ID, role, email):
    """
    Creates a new user with the given parameters
    """
    try:
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None
        
        # Create new user based on role
        if role.lower() == 'admin':
            new_user = Admin(u_ID=u_ID, email=email, password=password)
        else:
            new_user = Staff(username=username, password=password, u_ID=u_ID, 
                            role=role, email=email)
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        print(f"Error creating user: {e}")
        db.session.rollback()
        return None

def get_all_users():
    """
    Returns all users in the database
    """
    staff = Staff.query.all()
    admins = Admin.query.all()
    return staff + admins

def get_all_users_json():
    """
    Returns all users in JSON format
    """
    users = get_all_users()
    if not users:
        return []
    return [user.to_json() for user in users]