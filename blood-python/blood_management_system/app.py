from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from datetime import datetime
import logging
from models import User, Donor, Patient, BloodInventory, BloodRequest, Donation, Appointment

def create_app():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Add context processor for current date
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Import and register routes
    from routes import register_routes
    register_routes(app)

    with app.app_context():
        try:
            # Drop all tables and recreate them
            db.drop_all()
            db.create_all()
            app.logger.info("Database tables reset successfully")
            
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@bloodbank.com',
                role='admin',
                name='Administrateur'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info("Default admin user created successfully")
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            raise e

    return app

# Create the application instance
try:
    print("Creating Flask application...")
    app = create_app()
    
    if __name__ == '__main__':
        print("Starting Flask development server...")
        app.run(debug=True)
except Exception as e:
    print(f"Error creating Flask application: {str(e)}")
    raise e
