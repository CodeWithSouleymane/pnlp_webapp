"""
Patient model for blood transfusion management.
"""
from datetime import datetime
from extensions import db

class Patient(db.Model):
    """Patient model with medical and blood request related attributes."""
    __tablename__ = 'patient'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    
    # Medical Information
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_relation = db.Column(db.String(50))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Blood Transfusion History
    last_transfusion_date = db.Column(db.DateTime)
    total_transfusions = db.Column(db.Integer, default=0)
    transfusion_reactions = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('patient', uselist=False))
    blood_requests = db.relationship('BloodRequest', back_populates='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.id}>'
