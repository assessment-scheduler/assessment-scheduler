import flask_login
from App.database import db
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from App.models import User, Admin, Staff, user


def authenticate(email, password):
  user = User.query.filter_by(email=email).first()
  if user and user.check_password(password):
    return user
  return None


# Payload is a dictionary which is passed to the function by Flask JWT
def identity(payload):
  return User.query.get(payload['identity'])

def login(payload):    
  return flask_login.login_user(user)

def logout(user, remember):
  return flask_login.logout_user()

def setup_flask_login(app):
  login_manager = flask_login.LoginManager()
  login_manager.init_app(app)
  #login_manager.login_view = 'login

  @login_manager.user_loader
  def load_user(user_id):
    staff = Staff.query.get(user_id)
    if staff:
      return staff

    admin = Admin.query.get(user_id)
    if admin:
      return admin
    return None

# def setup_jwt(app):
#   return JWT(app, authenticate, identity)



