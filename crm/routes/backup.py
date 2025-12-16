"""
Backup and export routes.
"""
from flask import Blueprint, send_file, Response
from crm.db import db
import os
import csv
from io import StringIO
from crm.models import Contact, Property, Task, Touchpoint

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')


@backup_bp.route('/download_db')
def download_db():
    """Download the SQLite database file as a backup."""
    # Get the project root directory (where app.py is located)
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / 'crm.db'
    if db_path.exists():
        return send_file(str(db_path), as_attachment=True, download_name='crm_backup.db')
    return "Database file not found", 404


@backup_bp.route('/export_contacts')
def export_contacts():
    """Export contacts as CSV."""
    contacts = Contact.query.all()
    contacts_csv = StringIO()
    writer = csv.writer(contacts_csv)
    writer.writerow(['ID', 'Name', 'Company', 'Role', 'Phone', 'Email', 'Tags', 'Created'])
    for contact in contacts:
        writer.writerow([
            contact.id,
            contact.name,
            contact.company or '',
            contact.role_type or '',
            contact.phone or '',
            contact.email or '',
            contact.tags or '',
            contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return Response(
        contacts_csv.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=contacts_export.csv'}
    )


@backup_bp.route('/export_properties')
def export_properties():
    """Export properties as CSV."""
    properties = Property.query.all()
    properties_csv = StringIO()
    writer = csv.writer(properties_csv)
    writer.writerow(['ID', 'Name', 'Address', 'City', 'State', 'Zip', 'Units', 'Year Built', 'Class', 'Est. Value Min', 'Est. Value Max', 'Created'])
    for prop in properties:
        writer.writerow([
            prop.id,
            prop.name or '',
            prop.address or '',
            prop.city or '',
            prop.state or '',
            prop.zip_code or '',
            prop.units or '',
            prop.year_built or '',
            prop.property_class or '',
            prop.estimated_value_min or '',
            prop.estimated_value_max or '',
            prop.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return Response(
        properties_csv.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=properties_export.csv'}
    )

