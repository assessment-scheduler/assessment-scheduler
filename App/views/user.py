from flask import Blueprint, request
from ..models import Staff, Admin
from ..controllers import login_admin, login_staff
from ..database import db

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/login', methods=['POST'])
def login_staff_action():
    email = request.form.get('email')
    password = request.form.get('password')
    user = db.session.query(Staff).filter(Staff.email==email).first()
    if user == None:
        user = db.session.query(Admin).filter(Admin.email==email).first()
        if user!=None:
            if login_admin(email, password):
                return user, 'Login Successful' , 200
            else:
                return 'Login Failed' , 401
    else:
        if login_staff(email, password):
            return 'Login Successful' , 200
        else:
            return 'Login Failed' , 401