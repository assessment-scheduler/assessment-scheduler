from App.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    u_id = db.Column(db.Integer, unique=True, primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, u_id, password, email):
        self.u_id = u_id
        self.set_password(password)
        self.email = email

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def to_json(self):
	    return {
            "u_ID": self.u_id,
            "email": self.email
        }
        
    def __repr__(self):
        return f"Staff(id={self.u_id}, email={self.email})"