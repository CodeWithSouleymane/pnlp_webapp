from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField, SubmitField, 
    PasswordField, EmailField, DateField, FloatField, 
    BooleanField, TextAreaField
)
from wtforms.validators import (
    DataRequired, Email, Length, NumberRange, 
    Regexp, Optional, ValidationError
)
from datetime import datetime
from models import Donor, Patient

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur ou Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Connexion')

class DonorForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=100)])
    blood_type = SelectField('Groupe sanguin', 
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Enregistrer le donneur')

class DonationForm(FlaskForm):
    donor_id = SelectField('Donneur', coerce=int, validators=[DataRequired()])
    quantity_ml = IntegerField('Quantité (ml)', 
                             validators=[DataRequired(), NumberRange(min=200, max=550, 
                             message="Le don doit être entre 200ml et 550ml")])
    submit = SubmitField('Enregistrer le don')

class PatientForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=100)])
    blood_type = SelectField('Groupe sanguin',
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Enregistrer le patient')

class BloodRequestForm(FlaskForm):
    blood_type = SelectField('Groupe sanguin', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantité (ml)', validators=[DataRequired(), NumberRange(min=450, max=5000)])
    urgency = SelectField('Niveau d\'urgence', choices=[
        ('Emergency', 'Urgence extrême'),
        ('Urgent', 'Urgent'),
        ('Standard', 'Standard')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes supplémentaires', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Soumettre la demande')

class DonorRegistrationForm(FlaskForm):
    # Informations personnelles
    name = StringField('Nom complet', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Le nom doit contenir entre 2 et 100 caractères")
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message="Veuillez entrer une adresse email valide")
    ])
    phone = StringField('Téléphone', validators=[
        DataRequired(),
        Regexp(r'^\d{9}$', message="Le numéro de téléphone doit contenir exactement 9 chiffres")
    ])
    date_of_birth = DateField('Date de naissance', validators=[
        DataRequired(),
        lambda form, field: check_age(field.data)
    ])

    # Informations médicales
    blood_type = SelectField('Groupe sanguin', choices=[
        ('', 'Sélectionner le groupe sanguin'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    
    weight = FloatField('Poids (kg)', validators=[
        DataRequired(),
        NumberRange(min=45, max=200, message="Le poids doit être entre 45 et 200 kg")
    ])
    
    has_diseases = BooleanField('A des maladies')
    diseases_details = TextAreaField('Détails des maladies')
    
    is_medication = BooleanField('Sous médicaments')
    medication_details = TextAreaField('Détails des médicaments')

    # Informations d'adresse
    address = StringField('Adresse', validators=[DataRequired()])
    city = StringField('Ville', validators=[DataRequired()])
    postal_code = StringField('Code postal', validators=[
        DataRequired(),
        Regexp(r'^\d{5}$', message="Veuillez entrer un code postal valide à 5 chiffres")
    ])

    # Contact d'urgence
    emergency_contact_name = StringField('Nom du contact d\'urgence', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    emergency_contact_phone = StringField('Téléphone du contact d\'urgence', validators=[
        DataRequired(),
        Regexp(r'^\d{9}$', message="Le numéro de téléphone doit contenir exactement 9 chiffres")
    ])
    emergency_contact_relationship = StringField('Relation', validators=[DataRequired()])

    # Consentement
    consent = BooleanField('Je confirme que toutes les informations fournies sont exactes et je consens à être donneur de sang.', 
                          validators=[DataRequired(message="Vous devez accepter les conditions pour vous inscrire")])

    submit = SubmitField('S\'inscrire comme donneur')

class PatientRegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message="Veuillez entrer une adresse email valide")
    ])
    phone = StringField('Téléphone', validators=[
        DataRequired(),
        Regexp(r'^\d{9}$', message="Le numéro de téléphone doit contenir exactement 9 chiffres")
    ])
    date_of_birth = DateField('Date de naissance', validators=[DataRequired()])
    blood_type = SelectField('Groupe sanguin', choices=[
        ('', 'Sélectionner le groupe sanguin'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    medical_conditions = TextAreaField('Conditions médicales')
    allergies = TextAreaField('Allergies')
    current_medications = TextAreaField('Médicaments actuels')
    address = StringField('Adresse', validators=[DataRequired()])
    city = StringField('Ville', validators=[DataRequired()])
    postal_code = StringField('Code postal', validators=[
        DataRequired(),
        Regexp(r'^\d{5}$', message="Veuillez entrer un code postal valide à 5 chiffres")
    ])
    emergency_contact_name = StringField('Nom du contact d\'urgence', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    emergency_contact_phone = StringField('Téléphone du contact d\'urgence', validators=[
        DataRequired(),
        Regexp(r'^\d{9}$', message="Le numéro de téléphone doit contenir exactement 9 chiffres")
    ])
    emergency_contact_relationship = StringField('Relation', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères")
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        Length(min=8),
        lambda form, field: check_password_match(form.password, field)
    ])
    consent = BooleanField('J\'accepte les conditions', validators=[
        DataRequired(message="Vous devez accepter les conditions pour vous inscrire")
    ])
    submit = SubmitField('S\'inscrire comme patient')

def check_age(dob):
    """Check if donor is at least 18 years old and not more than 65 years old"""
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 18:
        raise ValidationError('Vous devez avoir au moins 18 ans pour vous inscrire comme donneur.')
    elif age > 65:
        raise ValidationError('Vous ne pouvez pas avoir plus de 65 ans pour vous inscrire comme donneur.')

def check_password_match(password_field, confirm_field):
    if password_field.data != confirm_field.data:
        raise ValidationError('Les mots de passe ne correspondent pas')

class AppointmentForm(FlaskForm):
    appointment_type = SelectField('Type de rendez-vous', 
                                 choices=[('donation', 'Don de sang'), 
                                        ('request', 'Demande de sang')],
                                 validators=[DataRequired()])
    blood_type = SelectField('Groupe sanguin',
                           choices=[('A+', 'A+'), ('A-', 'A-'), 
                                  ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'),
                                  ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    preferred_date = DateField('Date préférée', 
                             validators=[DataRequired()],
                             format='%Y-%m-%d')
    preferred_time = SelectField('Heure préférée',
                               choices=[('09:00', '9h00'), ('10:00', '10h00'),
                                      ('11:00', '11h00'), ('12:00', '12h00'),
                                      ('14:00', '14h00'), ('15:00', '15h00'),
                                      ('16:00', '16h00')],
                               validators=[DataRequired()])
    notes = TextAreaField('Notes supplémentaires')
    submit = SubmitField('Planifier le rendez-vous')
