"""
Blood-related models for donation and inventory management.
"""
from datetime import datetime, timedelta
from . import db

class BloodInventory(db.Model):
    """Blood inventory tracking."""
    __tablename__ = 'blood_inventory'

    id = db.Column(db.Integer, primary_key=True)
    blood_type = db.Column(db.String(3), unique=True, nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='available')
    
    # Additional tracking fields
    minimum_level = db.Column(db.Integer, default=1000)  # Minimum required level in ml
    optimal_level = db.Column(db.Integer, default=5000)  # Optimal inventory level in ml
    location = db.Column(db.String(100))  # Storage location
    temperature = db.Column(db.Float)  # Storage temperature

    @property
    def is_low(self):
        """Check if inventory is below minimum level."""
        return self.quantity_ml < self.minimum_level

    @property
    def needs_replenishment(self):
        """Check if inventory needs replenishment."""
        return self.quantity_ml < self.optimal_level

    def add_blood(self, quantity_ml):
        """Add blood to inventory."""
        self.quantity_ml += quantity_ml
        self.last_updated = datetime.utcnow()
        self.expiry_date = datetime.utcnow() + timedelta(days=42)  # Standard shelf life

    def remove_blood(self, quantity_ml):
        """Remove blood from inventory."""
        if self.quantity_ml >= quantity_ml:
            self.quantity_ml -= quantity_ml
            self.last_updated = datetime.utcnow()
            return True
        return False


class Donation(db.Model):
    """Blood donation record."""
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Health metrics at time of donation
    hemoglobin_level = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    pulse_rate = db.Column(db.Integer)
    
    # Donation details
    donation_type = db.Column(db.String(50), default='whole_blood')  # whole_blood, platelets, plasma
    status = db.Column(db.String(20), default='completed')
    screening_passed = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Donation, self).__init__(**kwargs)
        if self.status == 'completed' and self.screening_passed:
            # Update inventory
            inventory = BloodInventory.query.filter_by(
                blood_type=self.donor_profile.blood_type
            ).first()
            if inventory:
                inventory.add_blood(self.quantity_ml)


class BloodRequest(db.Model):
    """Blood request record."""
    __tablename__ = 'blood_requests'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    urgency_level = db.Column(db.String(20), default='normal')  # normal, urgent, emergency
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fulfillment_date = db.Column(db.DateTime)
    
    # Additional fields
    diagnosis = db.Column(db.String(200))
    requesting_physician = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    def fulfill_request(self):
        """Attempt to fulfill the blood request."""
        if self.status != 'pending':
            return False, "Request is not pending"
            
        inventory = BloodInventory.query.filter_by(blood_type=self.blood_type).first()
        if not inventory:
            return False, "Blood type not found in inventory"
            
        if inventory.quantity_ml < self.quantity_ml:
            return False, "Insufficient blood quantity in inventory"
            
        if inventory.remove_blood(self.quantity_ml):
            self.status = 'completed'
            self.fulfillment_date = datetime.utcnow()
            # Update patient's transfusion record
            self.patient_profile.record_transfusion(self)
            return True, "Request fulfilled successfully"
            
        return False, "Failed to remove blood from inventory"
