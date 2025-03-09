from typing import Optional
from App.models import Admin
from App.database import db

def get_admin_by_id(admin_id):
    admin: Optional[Admin] = Admin.query.filter_by(id = admin_id).first()
    return admin 

def get_admin_by_email(email:str) -> Admin | None:
    admin : Optional[Admin] = Admin.query.filter_by(u_ID=email).first()
    return admin

def create_admin(admin_id,email,password) -> bool:
    new_admin: Admin  = Admin(admin_id,email,password)
    db.session.add(new_admin)
    db.session.commit()
    return True
