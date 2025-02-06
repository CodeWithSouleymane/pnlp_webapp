"""
Base user models including User and Admin.
"""
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Base user model with common attributes."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, donor, patient
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        """Set hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'

    @property
    def is_donor(self):
        """Check if user is donor."""
        return self.role == 'donor'

    @property
    def is_patient(self):
        """Check if user is patient."""
        return self.role == 'patient'

    def __repr__(self):
        return f'<User {self.username}>'
