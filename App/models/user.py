from App.database import db
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    __tablename__ = 'user'
    __abstract__ = True

    u_ID = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, u_ID, password):
        self.u_ID = u_ID,
        self.set_password(password)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)