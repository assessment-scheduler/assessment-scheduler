from App.database import db
from .user import User
from flask_login import UserMixin

class Admin(User, UserMixin):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    def __init__(self, id, password, email):
        super().__init__(id, password, email)

    def get_id(self):
        return self.id

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email
        }

    def __repr__(self):
        return f"Admin(id={self.id}, email={self.email})"