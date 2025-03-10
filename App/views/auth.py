from flask import Blueprint, flash, redirect, request, render_template, url_for, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import logout_user
from ..controllers.auth import login_user

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

@auth_views.route('/login', methods=['GET'])
def get_login_page():
    return render_template('login.html')
    
@auth_views.route('/login', methods=['POST'])
def login_action():
    email = request.form.get('email')          
    password = request.form.get('password')    
    response = login_user(email, password)
    if not response:
        flash('Bad email or password given', 'error') 
        return redirect(url_for('auth_views.get_login_page'))
    return response


@auth_views.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    email=get_jwt_identity()
    print(email)
    logout_user()
    return render_template('login.html')
