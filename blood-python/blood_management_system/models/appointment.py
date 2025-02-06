"""
Appointment model for scheduling and tracking medical appointments.
"""
from datetime import datetime, timedelta
from extensions import db

class Appointment(db.Model):
    """Medical appointment record."""
    __tablename__ = 'appointment'

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
