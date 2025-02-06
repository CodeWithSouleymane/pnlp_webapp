from app import app, db, Donor, Patient, BloodInventory, Donation, BloodRequest
from datetime import datetime, timedelta

def add_sample_data():
    with app.app_context():
        # Add sample donors
        donors = [
            Donor(name='John Smith', blood_type='A+', contact='123-456-7890'),
            Donor(name='Mary Johnson', blood_type='O-', contact='234-567-8901'),
            Donor(name='David Wilson', blood_type='B+', contact='345-678-9012'),
            Donor(name='Sarah Brown', blood_type='AB+', contact='456-789-0123')
        ]
        
        # Add sample patients
        patients = [
            Patient(name='James Anderson', blood_type='A+', contact='567-890-1234'),
            Patient(name='Emma Davis', blood_type='O+', contact='678-901-2345'),
            Patient(name='Michael Clark', blood_type='B-', contact='789-012-3456')
        ]
        
        # Add blood inventory
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        inventory = []
        for blood_type in blood_types:
            inventory.append(BloodInventory(
                blood_type=blood_type,
                quantity_ml=500 * (blood_types.index(blood_type) + 2),  # Different quantities for each type
                expiry_date=datetime.now() + timedelta(days=42)  # Blood typically expires in 42 days
            ))
        
        # Add sample donations
        donations = []
        for donor in donors:
            donations.append(Donation(
                donor=donor,
                quantity_ml=450,  # Standard blood donation is about 450ml
                donation_date=datetime.now() - timedelta(days=donors.index(donor))
            ))
        
        # Add sample blood requests
        requests = [
            BloodRequest(
                patient=patients[0],
                blood_type='A+',
                quantity_ml=300,
                status='Pending',
                request_date=datetime.now() - timedelta(hours=12)
            ),
            BloodRequest(
                patient=patients[1],
                blood_type='O+',
                quantity_ml=450,
                status='Approved',
                request_date=datetime.now() - timedelta(hours=24)
            ),
            BloodRequest(
                patient=patients[2],
                blood_type='B-',
                quantity_ml=250,
                status='Completed',
                request_date=datetime.now() - timedelta(days=1)
            )
        ]
        
        try:
            # Add all sample data to database
            db.session.add_all(donors)
            db.session.add_all(patients)
            db.session.add_all(inventory)
            db.session.add_all(donations)
            db.session.add_all(requests)
            
            # Commit the changes
            db.session.commit()
            print("Sample data added successfully!")
            
        except Exception as e:
            print(f"Error adding sample data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_data()
