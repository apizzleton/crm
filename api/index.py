"""
Vercel serverless function entry point for the CRM application.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from crm.db import init_db
from crm.routes import register_routes
from datetime import datetime

# Create Flask app
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'crm', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'crm', 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - supports multiple database types
# For Vercel, use a cloud database URL from environment variable
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Handle postgres:// vs postgresql:// (Heroku/Vercel uses postgres://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Custom Jinja2 date filter for templates
@app.template_filter('date')
def date_filter(value, format_string='Y'):
    """Custom date filter for Jinja2 templates."""
    if value == 'now':
        value = datetime.now()
    if isinstance(value, str):
        return value
    format_map = {
        'Y': '%Y',
        'y': '%y',
        'm': '%m',
        'd': '%d',
    }
    py_format = format_map.get(format_string, format_string)
    return value.strftime(py_format)

# Context processor to inject current year into all templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year, 'now': datetime.now()}

# Custom filter to replace underscores with spaces (used in contacts list)
@app.template_filter('replace_underscore')
def replace_underscore_filter(s):
    """Replace underscores with spaces for display."""
    if not s:
        return s
    return s.replace('_', ' ')

# Register all routes
register_routes(app)

# Create tables on startup (for serverless, this runs on cold start)
with app.app_context():
    from crm.db import db
    try:
        db.create_all()
    except Exception as e:
        # Log error but don't fail - tables might already exist
        print(f"Database initialization note: {e}")

# Export app for Vercel
# Vercel's @vercel/python automatically handles Flask apps
