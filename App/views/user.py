from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from App.models import Staff, Admin
from App.controllers.admin import login_admin
from App.controllers.staff import login_staff
from App.database import db

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/login', methods=['POST'])
def login_staff_action():
    email = request.form.get('email')
    password = request.form.get('password')
    user = db.session.query(Staff).filter(Staff.email==email).first()
    if user == None:
        user = db.session.query(Admin).filter(Admin.u_ID==email).first()
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