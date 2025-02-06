from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, PasswordField, EmailField, DateField, FloatField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp, Optional
from wtforms import ValidationError
from datetime import datetime
from models.donor import Donor
from models.patient import Patient

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DonorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    blood_type = SelectField('Blood Type', 
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Register Donor')

class DonationForm(FlaskForm):
    donor_id = SelectField('Donor', coerce=int, validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', 
                             validators=[DataRequired(), NumberRange(min=200, max=550, 
                             message="Donation must be between 200ml and 550ml")])
    submit = SubmitField('Record Donation')

class PatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    blood_type = SelectField('Blood Type',
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Register Patient')

class BloodRequestForm(FlaskForm):
    blood_type = SelectField('Blood Type', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired(), NumberRange(min=450, max=5000)])
    urgency = SelectField('Urgency Level', choices=[
        ('Emergency', 'Emergency'),
        ('Urgent', 'Urgent'),
        ('Standard', 'Standard')
    ], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Request')

class DonorRegistrationForm(FlaskForm):
    # Personal Information
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    phone = StringField('Phone', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Please enter a valid phone number")
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(),
        lambda form, field: check_age(field.data)
    ])

    # Medical Information
    blood_type = SelectField('Blood Type', choices=[
        ('', 'Select Blood Type'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    
    weight = FloatField('Weight (kg)', validators=[
        DataRequired(),
        NumberRange(min=45, max=200, message="Weight must be between 45 and 200 kg")
    ])
    
    has_diseases = BooleanField('Has Diseases')
    diseases_details = TextAreaField('Disease Details')
    
    is_medication = BooleanField('On Medication')
    medication_details = TextAreaField('Medication Details')

    # Address Information
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[
        DataRequired(),
        Regexp(r'^\d{5}$', message="Please enter a valid 5-digit postal code")
    ])

    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Please enter a valid phone number")
    ])
    emergency_contact_relationship = StringField('Relationship', validators=[DataRequired()])

    # Consent
    consent = BooleanField('I agree to the terms', validators=[
        DataRequired(message="You must agree to the terms to register")
    ])

    def validate_email(self, field):
        if Donor.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_phone(self, field):
        if Donor.query.filter_by(phone=field.data).first():
            raise ValidationError('Phone number already registered')

def check_age(dob):
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 18:
        raise ValidationError('You must be at least 18 years old to register as a donor')
    if age > 65:
        raise ValidationError('You must be under 65 years old to register as a donor')

class PatientRegistrationForm(FlaskForm):
    # Personal Information
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    contact = StringField('Contact Number', validators=[DataRequired()])
    phone = StringField('Phone', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Please enter a valid phone number")
    ])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])

    # Medical Information
    blood_type = SelectField('Blood Type', choices=[
        ('', 'Select Blood Type'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    
    medical_conditions = TextAreaField('Medical Conditions')
    allergies = TextAreaField('Allergies')
    current_medications = TextAreaField('Current Medications')

    # Address Information
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[
        DataRequired(),
        Regexp(r'^\d{5}$', message="Please enter a valid 5-digit postal code")
    ])

    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Please enter a valid phone number")
    ])
    emergency_contact_relationship = StringField('Relationship', validators=[DataRequired()])

    # Password for account
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        Length(min=8),
        lambda form, field: check_password_match(form.password, field)
    ])

    # Consent
    consent = BooleanField('I agree to the terms', validators=[
        DataRequired(message="You must agree to the terms to register")
    ])

    def validate_email(self, field):
        if Patient.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_phone(self, field):
        pass

    def validate_contact(self, field):
        if Patient.query.filter_by(contact=field.data).first():
            raise ValidationError('This contact number is already registered.')

def check_password_match(password_field, confirm_field):
    if password_field.data != confirm_field.data:
        raise ValidationError('Passwords must match')

class AppointmentForm(FlaskForm):
    appointment_type = SelectField('Appointment Type', 
                                 choices=[('donation', 'Blood Donation'), 
                                        ('request', 'Blood Request')],
                                 validators=[DataRequired()])
    blood_type = SelectField('Blood Type',
                           choices=[('A+', 'A+'), ('A-', 'A-'), 
                                  ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'),
                                  ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    preferred_date = DateField('Preferred Date', 
                             validators=[DataRequired()],
                             format='%Y-%m-%d')
    preferred_time = SelectField('Preferred Time',
                               choices=[('09:00', '9:00 AM'), ('10:00', '10:00 AM'),
                                      ('11:00', '11:00 AM'), ('12:00', '12:00 PM'),
                                      ('14:00', '2:00 PM'), ('15:00', '3:00 PM'),
                                      ('16:00', '4:00 PM')],
                               validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Schedule Appointment')
