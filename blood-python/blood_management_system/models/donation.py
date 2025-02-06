from datetime import datetime
from extensions import db

class Donation(db.Model):
    __tablename__ = 'donation'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    donor = db.relationship('Donor', back_populates='donations')
    
    def __repr__(self):
        return f'<Donation {self.id}: {self.blood_type} {self.quantity_ml}ml>'
