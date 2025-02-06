from datetime import datetime, timedelta
from extensions import db

class Donor(db.Model):
    __tablename__ = 'donor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    last_donation_date = db.Column(db.DateTime)
    total_donations = db.Column(db.Integer, default=0)
    medical_conditions = db.Column(db.Text)
    is_eligible = db.Column(db.Boolean, default=True)
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    status = db.Column(db.String(20), default='Pending')  # Pending, Active, Inactive
    
    # Health metrics
    hemoglobin_level = db.Column(db.Float)  # g/dL
    blood_pressure = db.Column(db.String(20))
    pulse_rate = db.Column(db.Integer)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('donor', uselist=False))
    donations = db.relationship('Donation', back_populates='donor', lazy=True)

    def can_donate(self):
        """Check if donor is eligible to donate based on last donation date and health criteria."""
        if not self.is_eligible or self.status != 'Active':
            return False, "Not eligible for donation"
            
        if self.last_donation_date:
            days_since_donation = (datetime.utcnow() - self.last_donation_date).days
            if days_since_donation < 56:  # Standard waiting period
                return False, f"Must wait {56 - days_since_donation} more days"

        # Check health criteria
        if self.hemoglobin_level and self.hemoglobin_level < 12.5:
            return False, "Hemoglobin level too low"
            
        if self.weight and self.weight < 50:
            return False, "Weight below minimum requirement"
            
        return True, "Eligible for donation"
    
    def __repr__(self):
        return f'<Donor {self.id}>'
