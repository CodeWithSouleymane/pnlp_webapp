from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, DonorForm, DonationForm, PatientForm, BloodRequestForm, DonorRegistrationForm
from models import db, User, Donor, BloodInventory, Donation, Patient, BloodRequest
from config import Config
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import io
import csv

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Add context processor for current date
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Register all routes
    register_routes(app)

    return app

def register_routes(app):
    @app.route('/')
    def index():
        form = LoginForm()
        return render_template('index.html', form=form)

    @app.route('/admin/appointments')
    @login_required
    def admin_appointments():
        if current_user.role != 'admin':
            flash("Unauthorized access!", "danger")
            return redirect(url_for('index'))  # Redirect non-admins

        appointments = BloodRequest.query.order_by(BloodRequest.request_date).all()
        return render_template('admin_appointments.html', appointments=appointments)

    @app.route('/patients')
    @login_required
    def patients():
        form = PatientForm()
        patients = Patient.query.all()
        return render_template('patients.html', form=form, patients=patients)

    @app.route('/register_patient', methods=['GET', 'POST'])
    def register_patient():
        form = PatientForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            patient = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                role='patient'
            )
            db.session.add(patient)
            db.session.commit()
            flash('Patient registered successfully!', 'success')
            return redirect(url_for('login'))
        return render_template('register_patient.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('dashboard'))
            elif current_user.role == 'patient':
                return redirect(url_for('patient_dashboard'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Logged in successfully!', 'success')
                if user.role == 'admin':
                    return redirect(url_for('dashboard'))
                elif user.role == 'patient':
                    return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('index'))

        # Calculate statistics
        total_donations = Donation.query.count()
        total_blood_ml = db.session.query(func.sum(BloodInventory.quantity_ml)).scalar() or 0
        pending_requests = BloodRequest.query.filter_by(status='Pending').count()
        
        # Calculate critical blood types (below 1000ml)
        critical_types = BloodInventory.query.filter(BloodInventory.quantity_ml < 1000).count()
        
        # Calculate donation increase
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_month_donations = Donation.query.filter(
            extract('month', Donation.donation_date) == current_month,
            extract('year', Donation.donation_date) == current_year
        ).count()
        
        last_month_donations = Donation.query.filter(
            extract('month', Donation.donation_date) == (current_month - 1 if current_month > 1 else 12),
            extract('year', Donation.donation_date) == (current_year if current_month > 1 else current_year - 1)
        ).count()
        
        donation_increase = (
            ((current_month_donations - last_month_donations) / last_month_donations * 100)
            if last_month_donations > 0 else 0
        )

        # Get blood inventory status
        inventory = {}
        for blood_type in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            blood_stock = BloodInventory.query.filter_by(blood_type=blood_type).first()
            if blood_stock:
                quantity = blood_stock.quantity_ml
                status = 'critical' if quantity < 1000 else 'low' if quantity < 2000 else 'normal'
                percentage = min((quantity / 5000) * 100, 100)  # 5000ml as max capacity
                inventory[blood_type] = {
                    'quantity': quantity,
                    'status': status,
                    'percentage': percentage
                }
            else:
                inventory[blood_type] = {
                    'quantity': 0,
                    'status': 'critical',
                    'percentage': 0
                }

        # Get recent activity
        recent_activity = []
        
        # Add recent donations
        recent_donations = Donation.query.order_by(Donation.donation_date.desc()).limit(5)
        for donation in recent_donations:
            recent_activity.append({
                'title': 'New Blood Donation',
                'description': f'{donation.quantity_ml}ml of {donation.blood_type} blood donated',
                'time_ago': time_ago(donation.donation_date),
                'user': donation.donor.name
            })
        
        # Add recent requests
        recent_requests = BloodRequest.query.order_by(BloodRequest.request_date.desc()).limit(5)
        for request in recent_requests:
            recent_activity.append({
                'title': 'Blood Request',
                'description': f'{request.quantity_ml}ml of {request.blood_type} blood requested',
                'time_ago': time_ago(request.request_date),
                'user': request.patient.name
            })
        
        # Sort activities by time
        recent_activity.sort(key=lambda x: x['time_ago'])
        recent_activity = recent_activity[:5]

        # Prepare donation trends data (last 7 days)
        labels = []
        data = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            labels.append(date.strftime('%b %d'))
            count = Donation.query.filter(
                func.date(Donation.donation_date) == date.date()
            ).count()
            data.append(count)

        donation_trends = {
            'labels': labels,
            'data': data
        }

        # Prepare request distribution data
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        request_counts = []
        for blood_type in blood_types:
            count = BloodRequest.query.filter_by(blood_type=blood_type).count()
            request_counts.append(count)

        request_distribution = {
            'labels': blood_types,
            'data': request_counts
        }

        stats = {
            'total_donations': total_donations,
            'total_blood_ml': total_blood_ml,
            'pending_requests': pending_requests,
            'critical_types': critical_types,
            'donation_increase': round(donation_increase, 1)
        }

        return render_template('dashboard.html',
                            stats=stats,
                            inventory=inventory,
                            recent_activity=recent_activity,
                            donation_trends=donation_trends,
                            request_distribution=request_distribution)

    @app.route('/donors', methods=['GET'])
    @login_required
    def donors():
        form = DonorForm()
        donors = Donor.query.all()
        return render_template('donors.html', form=form, donors=donors)

    @app.route('/register_donor', methods=['POST'])
    @login_required
    def register_donor():
        form = DonorForm()
        if form.validate_on_submit():
            donor = Donor(
                name=form.name.data,
                blood_type=form.blood_type.data,
                contact=form.contact.data
            )
            db.session.add(donor)
            db.session.commit()
            flash('Donor registered successfully!', 'success')
            return redirect(url_for('donors'))
        return redirect(url_for('donors'))  

    @app.route('/create_request/<int:patient_id>', methods=['GET', 'POST'])
    def create_request(patient_id):
        # Example: Fetch the patient from the database (if using a database)
        patient = Patient.query.get(patient_id)  # Replace with actual ORM query
        if not patient:
            flash("Patient not found", "danger")
            return redirect(url_for('patients'))

        return f"Blood request page for patient {patient_id}"  # Replace with actual logic

    @app.route('/request_blood', methods=['GET', 'POST'])
    @login_required
    def request_blood():
        if current_user.role != 'patient':
            return redirect(url_for('index'))  # Restrict access

        form = BloodRequestForm()
        if form.validate_on_submit():
            request_entry = BloodRequest(
                patient_id=current_user.id,
                blood_type=form.blood_type.data,
                quantity_ml=form.quantity_ml.data,
                status='Pending'
            )
            db.session.add(request_entry)
            db.session.commit()
            flash('Blood request submitted successfully!', 'success')
            return redirect(url_for('patient_dashboard'))

        return render_template('request_blood.html', form=form)

    @app.route('/patient_dashboard')
    @login_required
    def patient_dashboard():
        if current_user.role != 'patient':
            return redirect(url_for('index'))  # Restrict access
        
        blood_requests = BloodRequest.query.filter_by(patient_id=current_user.id).all()
        return render_template('patient_dashboard.html', blood_requests=blood_requests)

    @app.route('/record_donation/<int:donor_id>', methods=['GET', 'POST'])
    @login_required
    def record_donation(donor_id):
        form = DonationForm()
        donor = Donor.query.get_or_404(donor_id)
        
        if form.validate_on_submit():
            donation = Donation(
                donor_id=donor.id,
                quantity_ml=form.quantity_ml.data,
                donation_date=datetime.utcnow()
            )
            
    @app.route('/update_inventory', methods=['POST'])
    def update_inventory():
        blood_type = request.form['blood_type']
        try:
            quantity_ml = int(request.form['quantity_ml'])
            if quantity_ml < 0:
                raise ValueError("Quantity must be a positive integer.")
        except ValueError:
            flash('Invalid quantity. Please enter a valid positive number.', 'danger')
            return redirect(url_for('inventory'))
        
        inventory_item = BloodInventory.query.filter_by(blood_type=blood_type).first()
        if inventory_item:
            inventory_item.quantity_ml += quantity_ml
        else:
            new_inventory = BloodInventory(blood_type=blood_type, quantity_ml=quantity_ml)
            db.session.add(new_inventory)
        
        try:
            db.session.commit()
            flash('Inventory updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating inventory: {str(e)}', 'danger')
        return redirect(url_for('inventory'))

    @app.route('/inventory', methods=['GET'])
    def inventory():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        blood_inventory = BloodInventory.query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('inventory.html', inventory=blood_inventory)

    @app.route('/appointment/<int:appointment_id>/status', methods=['POST'])
    @login_required
    def update_appointment_status(appointment_id):
        if current_user.role != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400

        appointment = BloodRequest.query.get_or_404(appointment_id)
        appointment.status = status
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/export-appointments', methods=['POST'])
    @login_required
    def export_appointments():
        if current_user.role != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        data = request.get_json()
        start_date = datetime.strptime(data.get('startDate'), '%Y-%m-%d') if data.get('startDate') else None
        end_date = datetime.strptime(data.get('endDate'), '%Y-%m-%d') if data.get('endDate') else None
        export_format = data.get('format', 'csv')

        query = BloodRequest.query

        if start_date:
            query = query.filter(BloodRequest.request_date >= start_date)
        if end_date:
            query = query.filter(BloodRequest.request_date <= end_date)

        appointments = query.all()

        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient Name', 'Blood Type', 'Quantity (ml)', 'Request Date', 'Status'])
            
            for appointment in appointments:
                writer.writerow([
                    appointment.id,
                    appointment.patient.name,
                    appointment.blood_type,
                    appointment.quantity_ml,
                    appointment.request_date.strftime('%Y-%m-%d %H:%M'),
                    appointment.status
                ])
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment;filename=appointments.csv'}
            )
        
        return jsonify({'success': False, 'message': 'Unsupported format'}), 400

    @app.route('/register/donor', methods=['GET', 'POST'])
    def register_donor():
        form = DonorRegistrationForm()
        
        if form.validate_on_submit():
            try:
                # Create new donor
                donor = Donor(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    date_of_birth=form.date_of_birth.data,
                    blood_type=form.blood_type.data,
                    weight=form.weight.data,
                    has_diseases=form.has_diseases.data,
                    diseases_details=form.diseases_details.data if form.has_diseases.data else None,
                    is_medication=form.is_medication.data,
                    medication_details=form.medication_details.data if form.is_medication.data else None,
                    address=form.address.data,
                    city=form.city.data,
                    postal_code=form.postal_code.data,
                    emergency_contact_name=form.emergency_contact_name.data,
                    emergency_contact_phone=form.emergency_contact_phone.data,
                    emergency_contact_relationship=form.emergency_contact_relationship.data,
                    registration_date=datetime.now(),
                    status='Pending'  # New donors start with pending status
                )
                
                # Create user account for donor
                user = User(
                    username=form.email.data.split('@')[0],  # Use part before @ as username
                    email=form.email.data,
                    role='donor'
                )
                user.set_password(form.phone.data[-6:])  # Use last 6 digits of phone as initial password
                
                db.session.add(user)
                db.session.add(donor)
                db.session.commit()
                
                # Send welcome email
                send_welcome_email(donor.email, user.username, form.phone.data[-6:])
                
                flash('Registration successful! Please check your email for login credentials.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'danger')
                app.logger.error(f'Donor registration error: {str(e)}')
        
        return render_template('donor_register.html', form=form)

def time_ago(date):
    """Convert datetime to '... time ago' text"""
    now = datetime.now()
    diff = now - date

    if diff.days > 365:
        return f"{diff.days // 365}y ago"
    if diff.days > 30:
        return f"{diff.days // 30}mo ago"
    if diff.days > 0:
        return f"{diff.days}d ago"
    if diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    if diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    return "just now"

def send_welcome_email(email, username, password):
    # TODO: Implement email sending functionality
    # For now, just log the credentials
    app.logger.info(f'Welcome email would be sent to {email} with username: {username} and password: {password}')

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
