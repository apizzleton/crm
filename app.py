"""
Flask application entrypoint for Multifamily CRM.
Run with: python app.py
"""
from flask import Flask
from crm.db import init_db
from crm.routes import register_routes
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'crm', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'crm', 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - supports Supabase/Postgres if DATABASE_URL is set
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Handle postgres:// vs postgresql:// (Heroku/Vercel/Supabase often use postgres://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to local SQLite if no cloud database is configured
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Custom Jinja2 date filter for templates
@app.template_filter('date')
def date_filter(value, format_string='Y'):
    """Custom date filter for Jinja2 templates.
    Converts 'now' to current datetime, then formats it.
    Format: 'Y' = 4-digit year, 'm' = month, 'd' = day
    """
    if value == 'now':
        value = datetime.now()
    if isinstance(value, str):
        return value
    
    # Map common format codes (PHP/Django style to Python strftime)
    format_map = {
        'Y': '%Y',  # 4-digit year
        'y': '%y',  # 2-digit year
        'm': '%m',  # Month as zero-padded decimal
        'd': '%d',  # Day as zero-padded decimal
    }
    py_format = format_map.get(format_string, format_string)
    return value.strftime(py_format)

# Context processor to inject current year into all templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year, 'now': datetime.now()}

@app.template_filter('replace_underscore')
def replace_underscore_filter(s):
    if not s:
        return s
    return s.replace('_', ' ')

# Register all routes
register_routes(app)

if __name__ == '__main__':
    # use_reloader=False to avoid watchdog compatibility issue with Python 3.13
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)

