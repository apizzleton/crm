"""
Flask application entrypoint for Multifamily CRM.
Run with: python app.py
"""
from flask import Flask
from crm.db import init_db
from crm.routes import register_routes
from datetime import datetime

import os
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'crm', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'crm', 'static'))
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'  # Not needed for local-only, but Flask requires it
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
    return {'current_year': datetime.now().year}

# Register all routes
register_routes(app)

if __name__ == '__main__':
    # use_reloader=False to avoid watchdog compatibility issue with Python 3.13
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)

