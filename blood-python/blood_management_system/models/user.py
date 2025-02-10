"""
Modèles de base des utilisateurs, y compris Utilisateur et Administrateur.
"""
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Modèle de base des utilisateurs avec les attributs communs."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, donneur, patient
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        """Définir le mot de passe haché."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifier si le mot de passe correspond."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Vérifier si l'utilisateur est administrateur."""
        return self.role == 'admin'

    @property
    def is_donor(self):
        """Vérifier si l'utilisateur est donneur."""
        return self.role == 'donor'

    @property
    def is_patient(self):
        """Vérifier si l'utilisateur est patient."""
        return self.role == 'patient'

    def __repr__(self):
        return f'<Utilisateur {self.username}>'
