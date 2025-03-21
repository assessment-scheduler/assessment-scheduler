from flask import Blueprint, flash, redirect, request, render_template, url_for, make_response, session
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import logout_user
from ..controllers.auth import login_user

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

@auth_views.route('/login', methods=['GET'])
def get_login_page():
    if request.referrer and 'logout' not in request.referrer:
        session.pop('_flashes', None)
    return render_template('login.html')
    
@auth_views.route('/login', methods=['POST'])
def login_action():
    if '_flashes' in session:
        session.pop('_flashes', None)
        
    email = request.form.get('email')          
    password = request.form.get('password')    
    response = login_user(email, password)
    if not response:
        flash('Bad email or password given', 'error') 
        return redirect(url_for('auth_views.get_login_page'))
    return response


@auth_views.route('/logout', methods=['GET'])
@jwt_required(optional=True)
def logout():
    try:
        identity = get_jwt_identity()
        if identity:
            response = make_response(redirect(url_for('auth_views.get_login_page')))
            response.delete_cookie('access_token')
            logout_user()
            if request.path == '/logout':
                flash('You have been logged out successfully', 'success')
            return response
        else:
            return redirect(url_for('auth_views.get_login_page'))
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return redirect(url_for('auth_views.get_login_page'))
