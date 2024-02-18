from App.database import db
from .user import User  ##error -> flask run to run

class Admin(User):
  __tablename__ = 'admin'
  admin_ID = db.Column(db.String, primary_key= True)

  def __init__(self, password):
    super().__init__(password)
    self.admin_ID = "A0" + str(Admin.query.count() + 1)

  def to_json(self):
	  return {
      "adminID": self.admin_ID,
      "password": self.password
  }
  
    
