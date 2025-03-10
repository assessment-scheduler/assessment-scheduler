from flask import  redirect, jsonify, url_for, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request, JWTManager
import flask_login
from flask_login import logout_user
from ..models import User, Admin, Staff
from ..controllers.staff import validate_staff
from ..controllers.admin import validate_admin
from functools import wraps

def setup_jwt(app):
  jwt = JWTManager(app)

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