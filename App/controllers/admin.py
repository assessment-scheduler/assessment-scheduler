from typing import Optional
from ..models import Admin
from ..database import db

def get_admin_by_id(admin_id) -> Optional[Admin]:
    admin: Optional[Admin] = Admin.query.filter_by(id = admin_id).first()
    return admin 

def get_admin_by_email(email:str) -> Optional[Admin]:
    admin : Optional[Admin] = Admin.query.filter_by(email=email).first()
    return admin

def create_admin(admin_id,email,password) -> bool:
    new_admin: Admin  = Admin(admin_id,email,password)
    db.session.add(new_admin)
    db.session.commit()
    return True

def is_admin(email:str) -> bool:
    return Admin.query.filter_by(email=email).first() is not None

def validate_admin(email:str,password:str) -> bool:
    admin: Optional[Admin] = get_admin_by_email(email)
    if admin and admin.check_password(password):
        return True
    return False    
