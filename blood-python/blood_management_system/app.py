from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from datetime import datetime
import logging

def create_app():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        # Import models after app context
        from models import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Add context processor for current date
        @app.context_processor
        def inject_now():
            return {'now': datetime.utcnow()}

        # Import routes here to avoid circular imports
        from routes import register_routes
        register_routes(app)

        try:
            # Create tables if they don't exist
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Create default admin user if it doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@bloodbank.com',
                    role='admin',
                    name='Admin User'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Default admin user created successfully")
        except Exception as e:
            app.logger.error(f"Error during database initialization: {str(e)}")
            raise e

    return app

# Create the app instance
try:
    print("Creating Flask application...")
    app = create_app()
    
    if __name__ == '__main__':
        print("Starting Flask development server...")
        app.run(debug=True)
except Exception as e:
    print(f"Error creating Flask application: {str(e)}")
    raise e
