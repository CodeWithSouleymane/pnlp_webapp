# Blood Management System

A Flask-based blood bank management system.

## Project Structure

```
blood_management_system/
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── models.py           # Database models
├── forms.py            # Form definitions
├── utils/             
│   └── helpers.py      # Helper functions
├── static/
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
├── templates/          # HTML templates
├── migrations/         # Database migrations
└── instance/          # Instance-specific files
```

## Setup and Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   flask db upgrade
   python create_admin.py
   ```

4. Run the application:
   ```
   flask run
   ```

## Features

- User authentication (admin/staff/donor)
- Blood inventory management
- Donor management
- Patient records
- Blood request handling
- Donation tracking
