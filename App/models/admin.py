from App.database import db
from .user import User  

class Admin(User):
  __tablename__ = 'admin'

  def __init__(self, u_ID, password):
    super().__init__(u_ID, password)

  def to_json(self):
	  return {
      "admin_ID": self.u_ID,
      "password": self.password
  }
  
    
