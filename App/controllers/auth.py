from App.controllers.staff import validate_staff
from flask import Blueprint, flash, redirect, request, jsonify, render_template, url_for, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request, JWTManager
import flask_login
from flask_login import logout_user
from App.models import User, Admin, Staff
from App.controllers.admin import validate_admin
from functools import wraps

# def authenticate(email, password):
#   user = User.query.filter_by(email=email).first()
#   if user and user.check_password(password):
#     return user
#   return None

def setup_jwt(app):
  jwt = JWTManager(app)

  # @jwt.user_identity_loader
  # def user_identity_lookup(identity):
  #   user = User.query.filter_by(User.email == identity).one_or_none()
  #   if user:
  #     return user.id
  # return None

  # @jwt.user_lookup_loader
  # def user_lookup_callback(_jwt_header, jwt_data):
  #   identity = jwt_data["sub"]
  # return User.query.get(identity)

def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated = is_authenticated, current_user = current_user)

# # Payload is a dictionary which is passed to the function by Flask JWT
# def identity(payload):
#   return User.query.get(payload['identity'])

# def login(payload):
#   return flask_login.login_user(user)

def login_user(email, password):

    if validate_admin(email, password):
        response = make_response(redirect(url_for('admin_views.get_upload_page')))    
        token = create_access_token(identity=email)
        response.set_cookie('access_token', token)
        return response
    
    if validate_staff(email, password):
        response = make_response(redirect(url_for('staff_views.get_account_page')))
        token = create_access_token(identity=email)
        response.set_cookie('access_token', token)
        return response
    
    return None


def logout(user, remember):
  return flask_login.logout_user()

def setup_flask_login(app):
  login_manager = flask_login.LoginManager()
  login_manager = flask_login.LoginManager()
  login_manager.init_app(app)
  login_manager.login_view = 'login'

  @login_manager.user_loader
  def load_user(user_id):
    staff = Staff.query.get(user_id)
    if staff:
      return staff
    staff = Staff.query.get(user_id)
    if staff:
      return staff

    admin = Admin.query.get(user_id)
    if admin:
      return admin
    return None

def login_required(required_class):

  def wrapper(f):

    @wraps(f)
    @jwt_required()  # Ensure JWT authentication
    def decorated_function(*args, **kwargs):
      user = required_class.query.filter_by(
          username=get_jwt_identity()).first()
      print(user.__class__, required_class, user.__class__ == required_class)
      if user.__class__ != required_class:  # Check class equality
        return jsonify(error='Invalid user role'), 403
      return f(*args, **kwargs)

    return decorated_function

  return wrapper