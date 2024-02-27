from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from App.controllers import (
    register_lecturer
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')
     
# @auth_views.route('/login', methods=['POST'])
# def login_action():
#     data = request.form
#     token = login(data['username'], data['password'])
#     response = redirect(request.referrer)
#     if not token:
#         flash('Bad username or password given'), 401
#     else:
#         flash('Login Successful')
#         set_access_cookies(response, token) 
#     return response

# @auth_views.route('/logout', methods=['GET'])
# def logout_action():
#     response = redirect(request.referrer) 
#     flash("Logged Out!")
#     unset_jwt_cookies(response)
#     return response