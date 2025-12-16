"""
Route registration for all CRM routes.
"""
from flask import Flask
from crm.routes.dashboard import dashboard_bp
from crm.routes.deals import deals_bp
from crm.routes.contacts import contacts_bp
from crm.routes.tasks import tasks_bp
from crm.routes.touchpoints import touchpoints_bp
from crm.routes.search import search_bp
from crm.routes.properties import properties_bp
from crm.routes.backup import backup_bp


def register_routes(app: Flask):
    """Register all blueprints."""
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(deals_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(touchpoints_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(backup_bp)

