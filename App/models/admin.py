from App.database import db

class Admin(User):
  __tablename__ = 'admin'

  def __init__(self):
    super().__init__(u_ID, password)

  
    
