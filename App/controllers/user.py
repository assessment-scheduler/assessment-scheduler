from ..models import User, Admin, Staff
from ..database import db
from typing import Any, Optional
from flask import jsonify

def validate_staff(email, password) -> Any | None:
    staff = Staff.query.filter_by(email=email).first()
    if staff and staff.check_password(password):
        return staff
    return None

def validate_admin(email, password):
    admin = Admin.query.filter_by(email=email).first()
    if admin and admin.check_password(password):
        return admin
    return None

def create_user(id, email, password) -> User:
    newuser = User(id=id, email=email, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser


def change_password(email:str, password:str) -> bool:
    user: Optional[User] = get_user_by_email(email)
    if user is None:
        print("user could not be found")
        return True
    else:
        user.set_password(password)
        db.session.commit()
        return True

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()
 

def get_user_by_id(id):
    return User.query.filter_by(id=id).first()

def valdiate_user(email,password) -> Optional[User]:
    user = get_user_by_email(email)
    if user and user.check_password(password):
        return user
    return None

# def get_user_id(email): 
#     staff = Staff.query.filter_by(email=email).first()
#     if staff:
#         return staff.id
#     return None


def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return jsonify([])
    users_json = [user.to_json() for user in users]
    return jsonify(users_json)