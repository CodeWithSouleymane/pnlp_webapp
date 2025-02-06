"""
Database models for the blood management system.
"""
from extensions import db

# Import models after db is defined
from .user import User
from .admin import Admin
from .donor import Donor
from .patient import Patient
from .blood_inventory import BloodInventory
from .blood_request import BloodRequest
from .donation import Donation
from .appointment import Appointment

__all__ = [
    'db',
    'User',
    'Admin',
    'Donor',
    'Patient',
    'BloodInventory',
    'BloodRequest',
    'Donation',
    'Appointment'
]
