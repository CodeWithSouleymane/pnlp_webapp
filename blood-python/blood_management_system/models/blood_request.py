from datetime import datetime
from extensions import db

class BloodRequest(db.Model):
    __tablename__ = 'blood_request'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    blood_type = db.Column(db.String(3), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Approved, Rejected, Completed
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='blood_requests')
    
    def __repr__(self):
        return f'<BloodRequest {self.id}: {self.blood_type} {self.quantity_ml}ml>'
