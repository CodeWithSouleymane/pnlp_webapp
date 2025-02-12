"""
Database models for the blood management system.
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'donor', or 'patient'
    name = db.Column(db.String(100), nullable=True)  # Optional name field
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    donor = db.relationship('Donor', backref='user', uselist=False)
    patient = db.relationship('Patient', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(9), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    
    # Medical Information
    has_diseases = db.Column(db.Boolean, default=False)
    diseases_details = db.Column(db.Text)
    is_medication = db.Column(db.Boolean, default=False)
    medication_details = db.Column(db.Text)
    
    # Address Information
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(9), nullable=False)
    emergency_contact_relationship = db.Column(db.String(50), nullable=False)
    
    # Donation History
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_donation_date = db.Column(db.DateTime)
    donations = db.relationship('Donation', backref='donor', lazy=True)
    
    # Status can be: 'Pending', 'Approved', 'Rejected', 'Inactive'
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
    def __repr__(self):
        return f'<Donor {self.name}>'
    
    def can_donate(self):
        """Check if donor is eligible to donate based on last donation and other criteria"""
        if self.status != 'Approved':
            return False, 'Donor is not approved'
            
        if self.last_donation_date:
            # Check if 56 days (8 weeks) have passed since last donation
            days_since_donation = (datetime.utcnow() - self.last_donation_date).days
            if days_since_donation < 56:
                return False, f'Must wait {56 - days_since_donation} more days before next donation'
        
        # Check age
        age = (datetime.now().date() - self.date_of_birth).days // 365
        if age < 18 or age > 65:
            return False, 'Age must be between 18 and 65'
        
        # Check weight
        if self.weight < 45:
            return False, 'Weight must be at least 45 kg'
            
        return True, 'Eligible to donate'
    
    def get_donation_history(self):
        """Get donor's donation history with additional statistics"""
        donations = Donation.query.filter_by(donor_id=self.id).order_by(Donation.donation_date.desc()).all()
        
        total_donations = len(donations)
        total_volume = sum(d.quantity_ml for d in donations)
        
        history = {
            'donations': donations,
            'total_donations': total_donations,
            'total_volume': total_volume,
            'last_donation': self.last_donation_date,
            'can_donate': self.can_donate()
        }
        
        return history

class Patient(db.Model):
    """Patient model for storing patient information"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(9), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    medical_conditions = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    current_medications = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(9), nullable=False)
    emergency_contact_relationship = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Active')

    # Relationships
    blood_requests = db.relationship('BloodRequest', backref='patient', lazy=True)
    user = db.relationship('User', backref=db.backref('patient', uselist=False))

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_type = db.Column(db.String(3), nullable=False, unique=True)
    quantity_ml = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Approved, Rejected, Completed
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_type = db.Column(db.String(20), nullable=False)  # 'donation' or 'request'
    blood_type = db.Column(db.String(3), nullable=False)
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reminder_sent = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='appointments')
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.appointment_type} on {self.preferred_date} at {self.preferred_time}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_type': self.appointment_type,
            'blood_type': self.blood_type,
            'preferred_date': self.preferred_date.strftime('%Y-%m-%d'),
            'preferred_time': self.preferred_time,
            'status': self.status,
            'notes': self.notes,
            'user': self.user.name if self.user else None
        }
    
    def send_reminder_email(self):
        if not self.reminder_sent and self.status == 'Approved':
            appointment_date = datetime.combine(self.preferred_date, 
                                             datetime.strptime(self.preferred_time, '%H:%M').time())
            if datetime.utcnow() + timedelta(days=1) >= appointment_date:
                # Send reminder email here
                self.reminder_sent = True
                db.session.commit()
                return True
        return False
