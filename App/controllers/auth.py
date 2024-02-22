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

# Payload is a dictionary which is passed to the function by Flask JWT
def identity(payload):
  return User.query.get(payload['identity'])

def login(payload):    
  return flask_login.login_user(user, remember=remember)

def logout(user, remember):
  return flask_login.logout_user()

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

def setup_jwt(app):
  return JWT(app, authenticate, identity)



