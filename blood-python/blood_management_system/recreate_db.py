from app import app, db
from models import User, Donor, BloodInventory, Donation, Patient, BloodRequest

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Create initial blood inventory
        print("Creating initial blood inventory...")
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for blood_type in blood_types:
            inventory = BloodInventory(blood_type=blood_type, quantity_ml=0)
            db.session.add(inventory)
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@bloodbank.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Commit changes
        print("Committing changes...")
        db.session.commit()
        
        print("Database recreation completed successfully!")
