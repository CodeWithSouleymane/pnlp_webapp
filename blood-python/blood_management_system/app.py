from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from datetime import datetime
import logging

def create_app():
    # Configurer la journalisation
    logging.basicConfig(level=logging.DEBUG)
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser les extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Importer les modèles ici pour éviter les imports circulaires
    from models import User, Donor, Patient, BloodInventory, BloodRequest, Donation, Appointment

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ajouter un processeur de contexte pour la date actuelle
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Importer et enregistrer les routes
    from routes import register_routes
    register_routes(app)

    with app.app_context():
        try:
            # Créer les tables si elles n'existent pas
            db.create_all()
            app.logger.info("Tables de base de données créées avec succès")
            
            # Créer l'utilisateur admin par défaut s'il n'existe pas
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@bloodbank.com',
                    role='admin',
                    name='Administrateur'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Utilisateur admin par défaut créé avec succès")
        except Exception as e:
            app.logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
            raise e

    return app

# Créer l'instance de l'application
try:
    print("Création de l'application Flask...")
    app = create_app()
    
    if __name__ == '__main__':
        print("Démarrage du serveur de développement Flask...")
        app.run(debug=True)
except Exception as e:
    print(f"Erreur lors de la création de l'application Flask: {str(e)}")
    raise e
