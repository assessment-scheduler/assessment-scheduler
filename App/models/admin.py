from App.database import db
from .user import User
from sqlalchemy.orm import mapped_column, MappedColumn
class Admin(User):
    id: MappedColumn[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)

    def __init__(self, id, email, password):
        super().__init__(id = id, email=email, password=password)

    def get_id(self):
        return self.id

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email
        }

    def __repr__(self):
        return f"Admin(id={self.id}, email={self.email})"