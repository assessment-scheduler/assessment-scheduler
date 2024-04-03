from App.database import db
from .user import User  
from flask_login import UserMixin, login_user
import flask_login
from flask_login import UserMixin, login_user
import flask_login

class Admin(User,UserMixin):
  __tablename__ = 'admin'

  def login(self):
      return flask_login.login_user(self)
  
  def __init__(self, u_ID, password, email):
    super().__init__(u_ID, password, email)