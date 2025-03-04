from App.database import db
from .user import User
from flask_login import UserMixin

class Admin(User, UserMixin):
    __tablename__ = 'admin'

    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), primary_key=True)

    def __init__(self, u_id, password, email):
        super().__init__(u_id, password, email)

    def get_id(self):
        return self.u_id

    def to_json(self):
        return {
            "admin_ID": self.u_id,
            "email": self.email
        }

    def __repr__(self):
        return f"Admin(id={self.u_id}, email={self.email})"