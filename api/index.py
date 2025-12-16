import os
import sys
from flask import Flask

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm.db import init_db
from crm.routes import register_routes
from datetime import datetime

# Global Flask app instance
app = None

def create_app():
    """Create and configure the Flask application."""
    global app
    if app is None:
        app = Flask(__name__,
                    template_folder=os.path.join(os.path.dirname(__file__), '..', 'crm', 'templates'),
                    static_folder=os.path.join(os.path.dirname(__file__), '..', 'crm', 'static'))

        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///crm.db')
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

    return app

# Vercel serverless function handler
def handler(event, context):
    """Vercel serverless function handler."""
    from werkzeug.wrappers import Request
    from werkzeug.wsgi import get_input_stream

    # Create Flask app if it doesn't exist
    flask_app = create_app()

    # Extract request data from Vercel event
    method = event.get('method', 'GET')
    path = event.get('path', '/')
    query_string = event.get('query', {})
    headers = event.get('headers', {})
    body = event.get('body', b'')

    # Build query string
    query_parts = []
    for key, values in query_string.items():
        if isinstance(values, list):
            for value in values:
                query_parts.append(f"{key}={value}")
        else:
            query_parts.append(f"{key}={values}")
    query_str = '&'.join(query_parts)

    # Create WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_str,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': body if isinstance(body, bytes) else body.encode('utf-8'),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add HTTP headers
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[f'HTTP_{key}'] = value

    # Response handling
    response_started = []
    response_headers = []
    response_data = []

    def start_response(status, headers, exc_info=None):
        response_started.append(status)
        response_headers.extend(headers)

    # Call Flask WSGI application
    with flask_app.app_context():
        result = flask_app(environ, start_response)

        # Collect response data
        for data in result:
            if isinstance(data, str):
                response_data.append(data.encode('utf-8'))
            else:
                response_data.append(data)

    # Build response
    status_code = int(response_started[0].split()[0])

    # Convert headers to dict
    response_headers_dict = {}
    for header_name, header_value in response_headers:
        response_headers_dict[header_name] = header_value

    # Determine if response is binary or text
    content_type = response_headers_dict.get('Content-Type', '')
    is_binary = not (content_type.startswith('text/') or content_type.startswith('application/json'))

    body_content = b''.join(response_data)
    if not is_binary:
        body_content = body_content.decode('utf-8')

    return {
        'statusCode': status_code,
        'headers': response_headers_dict,
        'body': body_content
    }
