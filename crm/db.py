"""
Database setup and initialization.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from crm.models import Contact, Property, Deal, DealContactRole, Touchpoint, Task, PropertyOwner
        
        # Create all tables
        db.create_all()
        
        # Seed initial stage values if needed
        from crm.models import seed_initial_data
        seed_initial_data()

