from flask import render_template, flash, redirect, url_for, request, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, DonorForm, DonationForm, PatientForm, BloodRequestForm, DonorRegistrationForm, PatientRegistrationForm, AppointmentForm
from models import (
    db, User, Admin, Donor, Patient, 
    BloodInventory, BloodRequest, Donation, 
    Appointment
)
from datetime import datetime, timedelta
from sqlalchemy import func, extract, case
import io
import csv

def register_routes(app):
    # Initialize models
    user_model = User
    admin_model = Admin
    donor_model = Donor
    patient_model = Patient
    blood_inventory_model = BloodInventory
    blood_request_model = BloodRequest
    donation_model = Donation
    appointment_model = Appointment

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'donor':
                return redirect(url_for('donor_dashboard'))
            elif current_user.role == 'patient':
                return redirect(url_for('patient_dashboard'))
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            # Try to find user by username or email
            user = user_model.query.filter(
                (user_model.username == form.username.data) | 
                (user_model.email == form.username.data)
            ).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                
                # Redirect based on user role
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'donor':
                    return redirect(url_for('donor_dashboard'))
                elif user.role == 'patient':
                    return redirect(url_for('patient_dashboard'))
                
                return redirect(url_for('index'))
            else:
                flash('Invalid username/email or password.', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/register/donor', methods=['GET', 'POST'])
    def register_donor():
        form = DonorRegistrationForm()
        
        if form.validate_on_submit():
            try:
                # Create new donor
                donor = donor_model(
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
                user = user_model(
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

    @app.route('/register/patient', methods=['GET', 'POST'])
    def register_patient():
        form = PatientRegistrationForm()
        
        if form.validate_on_submit():
            try:
                # Create new patient
                patient = patient_model(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    date_of_birth=form.date_of_birth.data,
                    blood_type=form.blood_type.data,
                    medical_conditions=form.medical_conditions.data,
                    allergies=form.allergies.data,
                    current_medications=form.current_medications.data,
                    address=form.address.data,
                    city=form.city.data,
                    postal_code=form.postal_code.data,
                    emergency_contact_name=form.emergency_contact_name.data,
                    emergency_contact_phone=form.emergency_contact_phone.data,
                    emergency_contact_relationship=form.emergency_contact_relationship.data,
                    registration_date=datetime.now(),
                    status='Active'  # Patients start with active status
                )
                
                # Create user account for patient
                user = user_model(
                    username=form.email.data.split('@')[0],  # Use part before @ as username
                    email=form.email.data,
                    role='patient'
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.add(patient)
                db.session.commit()
                
                flash('Registration successful! You can now login with your email and password.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'danger')
                app.logger.error(f'Patient registration error: {str(e)}')
        
        return render_template('register_patient.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Redirect to appropriate dashboard based on role
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'donor':
            return redirect(url_for('donor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient_dashboard'))
        return redirect(url_for('index'))

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. This area is for administrators only.', 'danger')
            return redirect(url_for('index'))
            
        # Get statistics for the dashboard
        total_donors = donor_model.query.count()
        total_patients = patient_model.query.count()
        pending_donors = donor_model.query.filter_by(status='Pending').count()
        pending_requests = blood_request_model.query.filter_by(status='Pending').count()
        
        # Get blood inventory
        blood_inventory = blood_inventory_model.query.all()
        inventory_data = {item.blood_type: item.quantity_ml for item in blood_inventory}
        
        # Get recent donations
        recent_donations = donation_model.query.order_by(donation_model.donation_date.desc()).limit(5).all()
        
        # Get recent blood requests
        recent_requests = blood_request_model.query.order_by(blood_request_model.request_date.desc()).limit(5).all()
        
        return render_template('admin_dashboard.html',
                             total_donors=total_donors,
                             total_patients=total_patients,
                             pending_donors=pending_donors,
                             pending_requests=pending_requests,
                             inventory_data=inventory_data,
                             recent_donations=recent_donations,
                             recent_requests=recent_requests)

    @app.route('/donors', methods=['GET'])
    @login_required
    def donors():
        form = DonorForm()
        donors = donor_model.query.all()
        return render_template('donors.html', form=form, donors=donors)

    @app.route('/donors/register', methods=['POST'])
    @login_required
    def register_donor_admin():
        form = DonorForm()
        if form.validate_on_submit():
            donor = donor_model(
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
        patient = patient_model.query.get(patient_id)
        if not patient:
            flash("Patient not found", "danger")
            return redirect(url_for('patients'))
        return f"Blood request page for patient {patient_id}"

    @app.route('/request_blood', methods=['GET', 'POST'])
    @login_required
    def request_blood():
        if current_user.role != 'patient':
            return redirect(url_for('index'))

        form = BloodRequestForm()
        if form.validate_on_submit():
            request_entry = blood_request_model(
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

    @app.route('/patient/dashboard')
    @login_required
    def patient_dashboard():
        if current_user.role != 'patient':
            flash('Access denied. This area is for patients only.', 'danger')
            return redirect(url_for('index'))
            
        # Get patient information
        patient = patient_model.query.filter_by(email=current_user.email).first()
        if not patient:
            flash('Patient record not found.', 'danger')
            return redirect(url_for('index'))
            
        # Get patient's blood requests
        blood_requests = blood_request_model.query.filter_by(patient_id=patient.id).order_by(blood_request_model.request_date.desc()).all()
        
        # Get blood inventory status for patient's blood type
        compatible_types = get_compatible_blood_types(patient.blood_type)
        blood_inventory = {}
        for blood_type in compatible_types:
            inventory = blood_inventory_model.query.filter_by(blood_type=blood_type).first()
            if inventory:
                blood_inventory[blood_type] = inventory.quantity_ml
            else:
                blood_inventory[blood_type] = 0
                
        return render_template('patient_dashboard.html', 
                             patient=patient,
                             blood_requests=blood_requests,
                             blood_inventory=blood_inventory)

    def get_compatible_blood_types(patient_blood_type):
        """Return list of compatible blood types for a given patient blood type"""
        compatibility = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']
        }
        return compatibility.get(patient_blood_type, [])

    @app.route('/record_donation/<int:donor_id>', methods=['GET', 'POST'])
    @login_required
    def record_donation(donor_id):
        form = DonationForm()
        donor = donor_model.query.get_or_404(donor_id)
        
        if form.validate_on_submit():
            donation = donation_model(
                donor_id=donor.id,
                quantity_ml=form.quantity_ml.data,
                donation_date=datetime.utcnow()
            )
            db.session.add(donation)
            db.session.commit()
            flash('Donation recorded successfully!', 'success')
            return redirect(url_for('donors'))
            
        return render_template('record_donation.html', form=form, donor=donor)

    @app.route('/update_inventory', methods=['POST'])
    @login_required
    def update_inventory():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        
        try:
            blood_type = request.form.get('blood_type')
            quantity_ml = int(request.form.get('quantity_ml', 0))
            operation = request.form.get('operation', 'add')
            
            if not blood_type or quantity_ml <= 0:
                flash('Invalid input. Please check your values.', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            inventory_item = blood_inventory_model.query.filter_by(blood_type=blood_type).first()
            
            if operation == 'subtract':
                quantity_ml = -quantity_ml  # Make the quantity negative for subtraction
            
            if inventory_item:
                if operation == 'subtract' and abs(quantity_ml) > inventory_item.quantity_ml:
                    flash('Error: Cannot remove more blood than available in inventory.', 'danger')
                    return redirect(url_for('admin_dashboard'))
                
                inventory_item.quantity_ml += quantity_ml
                inventory_item.last_updated = datetime.utcnow()
            else:
                if operation == 'subtract':
                    flash('Error: Cannot remove blood from empty inventory.', 'danger')
                    return redirect(url_for('admin_dashboard'))
                
                inventory_item = blood_inventory_model(
                    blood_type=blood_type,
                    quantity_ml=quantity_ml,
                    last_updated=datetime.utcnow()
                )
                db.session.add(inventory_item)
            
            db.session.commit()
            flash(f'Successfully {"removed" if operation == "subtract" else "added"} {abs(quantity_ml)}ml of {blood_type} blood.', 'success')
            
        except ValueError:
            flash('Invalid quantity value.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating inventory: {str(e)}', 'danger')
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/appointments')
    @login_required
    def appointments():
        if current_user.role != 'admin':
            flash('Access denied. This area is for administrators only.', 'danger')
            return redirect(url_for('index'))
            
        # Get appointment counts for quick stats
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Base query for appointments
        base_query = appointment_model.query
        
        # Get various counts for dashboard
        today_count = base_query.filter(
            func.date(appointment_model.preferred_date) == today
        ).count()
        
        pending_count = base_query.filter_by(status='Pending').count()
        
        weekly_count = base_query.filter(
            appointment_model.preferred_date.between(week_start, week_end)
        ).count()
        
        # Get all appointments ordered by date
        appointments = base_query.order_by(appointment_model.preferred_date.desc()).all()
        
        return render_template('admin_appointments.html',
                             appointments=appointments,
                             today_count=today_count,
                             pending_count=pending_count,
                             weekly_count=weekly_count)

    @app.route('/calendar')
    @login_required
    def calendar_view():
        if current_user.role != 'admin':
            flash('Access denied. This area is for administrators only.', 'danger')
            return redirect(url_for('index'))
            
        # Get appointment counts for quick stats
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        base_query = appointment_model.query
        
        today_count = base_query.filter(
            func.date(appointment_model.preferred_date) == today
        ).count()
        
        pending_count = base_query.filter_by(status='Pending').count()
        
        weekly_count = base_query.filter(
            appointment_model.preferred_date.between(week_start, week_end)
        ).count()
        
        return render_template('calendar_view.html',
                             today_count=today_count,
                             pending_count=pending_count,
                             weekly_count=weekly_count)

    @app.route('/appointment/<int:appointment_id>/update-status', methods=['POST'])
    @login_required
    def update_appointment_status(appointment_id):
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status or new_status not in ['Pending', 'Approved', 'Completed', 'Cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        
        appointment = appointment_model.query.get_or_404(appointment_id)
        old_status = appointment.status
        appointment.status = new_status
        appointment.last_updated = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Return updated appointment details
            return jsonify({
                'success': True,
                'message': f'Appointment status updated from {old_status} to {new_status}',
                'appointment': {
                    'id': appointment.id,
                    'status': appointment.status,
                    'last_updated': appointment.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update status: {str(e)}'}), 500

    @app.route('/api/appointments')
    @login_required
    def get_appointments():
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        status_filter = request.args.getlist('status[]')
        
        # Base query
        query = appointment_model.query
        
        # Apply date filters if provided
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(appointment_model.preferred_date.between(start, end))
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(appointment_model.status.in_(status_filter))
        
        # Get appointments
        appointments = query.all()
        
        # Format appointments for calendar
        events = []
        for appointment in appointments:
            event = {
                'id': appointment.id,
                'title': f'Appointment: {appointment.user.username if appointment.user else "Unknown"}',
                'start': f'{appointment.preferred_date} {appointment.preferred_time}',
                'end': (datetime.strptime(f'{appointment.preferred_date} {appointment.preferred_time}', '%Y-%m-%d %H:%M') + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': appointment.status,
                'className': f'event-{appointment.status.lower()}'
            }
            events.append(event)
        
        return jsonify(events)

    @app.route('/api/appointments/export', methods=['POST'])
    @login_required
    def export_appointments():
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        export_format = data.get('format', 'csv')
        
        # Base query
        query = appointment_model.query
        
        # Apply date filters if provided
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(appointment_model.preferred_date.between(start, end))
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        appointments = query.all()
        
        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Appointment ID', 'Donor Name', 'Date', 'Status', 'Last Updated'])
            
            # Write data
            for appointment in appointments:
                writer.writerow([
                    appointment.id,
                    appointment.user.username if appointment.user else 'Unknown',
                    f'{appointment.preferred_date} {appointment.preferred_time}',
                    appointment.status,
                    appointment.updated_at.strftime('%Y-%m-%d %H:%M:%S') if appointment.updated_at else ''
                ])
            
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=appointments_{datetime.now().strftime("%Y%m%d")}.csv',
                    'Content-Type': 'text/csv'
                }
            )
        
        return jsonify({'error': 'Unsupported export format'}), 400

    @app.route('/inventory')
    def inventory():
        # Get blood inventory
        blood_inventory = blood_inventory_model.query.all()
        inventory_data = {item.blood_type: item.quantity_ml for item in blood_inventory}
        
        # Calculate total units and volume
        total_units = len(blood_inventory)
        total_quantity = sum(item.quantity_ml for item in blood_inventory)
        
        # Define thresholds for blood levels (in ml)
        CRITICAL_THRESHOLD = 1000  # 1 liter
        WARNING_THRESHOLD = 2000   # 2 liters
        
        # Prepare inventory summary with status
        inventory_summary = []
        low_stock = 0
        for blood_type in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            quantity = inventory_data.get(blood_type, 0)
            status = 'Good'
            if quantity <= CRITICAL_THRESHOLD:
                status = 'Critical'
                low_stock += 1
            elif quantity <= WARNING_THRESHOLD:
                status = 'Warning'
                low_stock += 1
                
            inventory_summary.append({
                'blood_type': blood_type,
                'quantity': quantity,
                'status': status
            })
        
        return render_template('inventory.html',
                             inventory_summary=inventory_summary,
                             total_units=total_units,
                             total_quantity=total_quantity,
                             low_stock=low_stock,
                             now=datetime.now())

    @app.route('/donor/dashboard')
    @login_required
    def donor_dashboard():
        if current_user.role != 'donor':
            flash('Access denied. This area is for donors only.', 'danger')
            return redirect(url_for('index'))
            
        # Get donor information
        donor = donor_model.query.filter_by(email=current_user.email).first()
        if not donor:
            flash('Donor record not found.', 'danger')
            return redirect(url_for('index'))
            
        # Get donor's donation history
        donations = donation_model.query.filter_by(donor_id=donor.id).order_by(donation_model.donation_date.desc()).all()
        
        # Calculate total donation volume
        total_donation_volume = sum(donation.quantity_ml for donation in donations)
        
        # Get upcoming appointments
        upcoming_appointments = appointment_model.query.filter_by(
            donor_id=donor.id,
            status='Scheduled'
        ).order_by(appointment_model.preferred_date.asc()).all()
        
        return render_template('donor_dashboard.html',
                             donor=donor,
                             donations=donations,
                             total_donation_volume=total_donation_volume,
                             upcoming_appointments=upcoming_appointments)

    @app.route('/patients', methods=['GET', 'POST'])
    @login_required
    def patients():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        
        form = PatientRegistrationForm()
        if form.validate_on_submit():
            patient = patient_model(
                username=form.email.data,  # Using email as username
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                contact=form.contact.data,
                role='patient'
            )
            patient.set_password('default123')  # Set a default password
            db.session.add(patient)
            db.session.commit()
            flash('Patient registered successfully!', 'success')
            return redirect(url_for('patients'))
            
        patients = patient_model.query.all()
        return render_template('patients.html', form=form, patients=patients)

    @app.route('/patient/<int:patient_id>')
    @login_required
    def patient_profile(patient_id):
        patient = patient_model.query.get_or_404(patient_id)
        blood_requests = blood_request_model.query.filter_by(patient_id=patient_id).all()
        return render_template('patient_profile.html', patient=patient, blood_requests=blood_requests)

    @app.route('/donor/<int:donor_id>')
    @login_required
    def donor_profile(donor_id):
        donor = donor_model.query.get_or_404(donor_id)
        donations = donation_model.query.filter_by(donor_id=donor_id).all()
        return render_template('donor_profile.html', donor=donor, donations=donations)

    @app.route('/reports')
    @login_required
    def reports():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))

        # Get date range from query parameters, default to last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get donations in date range
        donations = donation_model.query.filter(
            donation_model.donation_date.between(start_date, end_date)
        ).all()
        
        # Get blood requests in date range
        blood_requests = blood_request_model.query.filter(
            blood_request_model.request_date.between(start_date, end_date)
        ).all()
        
        # Calculate statistics
        total_donations = len(donations)
        total_donation_volume = sum(d.quantity_ml for d in donations)
        total_requests = len(blood_requests)
        total_request_volume = sum(r.quantity_ml for r in blood_requests)
        
        # Group donations by blood type
        blood_type_stats = {}
        for donation in donations:
            blood_type = donation.donor.blood_type
            if blood_type not in blood_type_stats:
                blood_type_stats[blood_type] = {
                    'donations': 0,
                    'volume': 0,
                    'requests': 0,
                    'request_volume': 0
                }
            blood_type_stats[blood_type]['donations'] += 1
            blood_type_stats[blood_type]['volume'] += donation.quantity_ml
            
        # Add request stats to blood type stats
        for request in blood_requests:
            blood_type = request.blood_type
            if blood_type not in blood_type_stats:
                blood_type_stats[blood_type] = {
                    'donations': 0,
                    'volume': 0,
                    'requests': 0,
                    'request_volume': 0
                }
            blood_type_stats[blood_type]['requests'] += 1
            blood_type_stats[blood_type]['request_volume'] += request.quantity_ml
        
        return render_template('reports.html',
                             start_date=start_date,
                             end_date=end_date,
                             total_donations=total_donations,
                             total_donation_volume=total_donation_volume,
                             total_requests=total_requests,
                             total_request_volume=total_request_volume,
                             blood_type_stats=blood_type_stats)

    @app.route('/donations')
    @login_required
    def donations():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
            
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        donations = donation_model.query.order_by(
            donation_model.donation_date.desc()
        ).paginate(page=page, per_page=per_page)
        
        return render_template('donations.html',
                             donations=donations)

    @app.route('/blood_requests')
    @login_required
    def blood_requests():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
            
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        requests = blood_request_model.query.order_by(
            blood_request_model.request_date.desc()
        ).paginate(page=page, per_page=per_page)
        
        return render_template('blood_requests.html',
                             requests=requests)

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
        print(f'Welcome email would be sent to {email} with username: {username} and password: {password}')

    return app
