"""
Helper functions for the blood management system.
"""
from datetime import datetime

def format_date(date):
    """Format a date object to string."""
    return date.strftime('%Y-%m-%d')

def calculate_next_donation_date(last_donation):
    """Calculate when a donor can donate again (after 56 days)."""
    if not last_donation:
        return datetime.now()
    return last_donation + timedelta(days=56)

def is_valid_blood_type(blood_type):
    """Validate blood type."""
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_type in valid_types
