from App.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def to_json(self):
        return {
            "id": self.id,
            "email": self.email
        }
        
    def __repr__(self):
        return f"Staff(id={self.id}, email={self.email})"