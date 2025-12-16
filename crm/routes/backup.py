"""
Backup and export routes.
"""
from flask import Blueprint, send_file, Response
from crm.db import db
import os
import csv
from io import StringIO
from crm.models import Deal, Contact, Property, Task, Touchpoint

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


@backup_bp.route('/export_csv')
def export_csv():
    """Export all data as CSV files in a zip archive."""
    # For simplicity, we'll export deals, contacts, and properties as separate CSV downloads
    # In a production app, you'd zip these together
    
    # Export deals
    deals = Deal.query.all()
    deals_csv = StringIO()
    writer = csv.writer(deals_csv)
    writer.writerow(['ID', 'Deal Name', 'Property Address', 'Stage', 'Asking Price', 'Target Close', 'Created'])
    for deal in deals:
        property_addr = deal.property.address if deal.property else ''
        writer.writerow([
            deal.id,
            deal.deal_name,
            property_addr,
            deal.stage,
            deal.asking_price or '',
            deal.target_close_date.strftime('%Y-%m-%d') if deal.target_close_date else '',
            deal.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return Response(
        deals_csv.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=deals_export.csv'}
    )


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

