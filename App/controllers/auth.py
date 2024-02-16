from flask_login import current_user, LoginManager, login_user
from App.database import db
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

from App.models import User, Admin, Lecturer

def jwt_authenticate(id, password):
  lect = Lecturer.query.filter_by(ID=id).first()
  if lect and lect.check_password(password):
    return create_access_token(identity=id)
  return None


def jwt_authenticate_admin(id, password):
  admin = Admin.query.filter_by(ID=id).first()
  if admin and admin.check_password(password):
    return create_access_token(identity=id)
  return None


def login(id, password):    
    return none


def setup_flask_login(app):
  login_manager = LoginManager()
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(user_id):
    lect = Lecturer.query.get(user_id)
    if lect:
      return lect

    admin = Admin.query.get(user_id)
    if admin:
      return admin
    return login_manager







