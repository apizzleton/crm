"""
Contact routes for CRUD operations.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from crm.db import db
from crm.models import Contact, DealContactRole, Task, Touchpoint, PropertyOwner

contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts_bp.route('/')
def list_contacts():
    """List all contacts."""
    contacts = Contact.query.order_by(Contact.name).all()
    return render_template('contacts/list.html', contacts=contacts)


@contacts_bp.route('/<int:contact_id>')
def detail(contact_id):
    """Show contact detail page."""
    contact = Contact.query.get_or_404(contact_id)
    
    # Get deals this contact is involved in
    deal_roles = DealContactRole.query.filter_by(contact_id=contact_id).all()
    
    # Get properties this contact owns
    property_ownerships = PropertyOwner.query.filter_by(contact_id=contact_id).all()
    
    # Get open tasks for this contact
    open_tasks = Task.query.filter_by(
        contact_id=contact_id,
        status='Open'
    ).order_by(Task.due_date).all()
    
    # Get recent touchpoints
    touchpoints = Touchpoint.query.filter_by(contact_id=contact_id).order_by(
        Touchpoint.occurred_at.desc()
    ).limit(20).all()
    
    return render_template('contacts/detail.html',
                         contact=contact,
                         deal_roles=deal_roles,
                         property_ownerships=property_ownerships,
                         open_tasks=open_tasks,
                         touchpoints=touchpoints)


@contacts_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new contact."""
    if request.method == 'GET':
        return render_template('contacts/create.html')
    
    # POST - create contact
    try:
        name = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip() or None
        role_type = request.form.get('role_type', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        email = request.form.get('email', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        tags = request.form.get('tags', '').strip() or None
        
        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('contacts.create'))
        
        contact = Contact(
            name=name,
            company=company,
            role_type=role_type,
            phone=phone,
            email=email,
            notes=notes,
            tags=tags
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Contact created successfully.', 'success')
        return redirect(url_for('contacts.detail', contact_id=contact.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating contact: {str(e)}', 'error')
        return redirect(url_for('contacts.create'))


@contacts_bp.route('/<int:contact_id>/edit', methods=['GET', 'POST'])
def edit(contact_id):
    """Edit an existing contact."""
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'GET':
        return render_template('contacts/edit.html', contact=contact)
    
    # POST - update contact
    try:
        contact.name = request.form.get('name', '').strip()
        contact.company = request.form.get('company', '').strip() or None
        contact.role_type = request.form.get('role_type', '').strip() or None
        contact.phone = request.form.get('phone', '').strip() or None
        contact.email = request.form.get('email', '').strip() or None
        contact.notes = request.form.get('notes', '').strip() or None
        contact.tags = request.form.get('tags', '').strip() or None
        
        if not contact.name:
            flash('Name is required.', 'error')
            return redirect(url_for('contacts.edit', contact_id=contact_id))
        
        db.session.commit()
        
        flash('Contact updated successfully.', 'success')
        return redirect(url_for('contacts.detail', contact_id=contact.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating contact: {str(e)}', 'error')
        return redirect(url_for('contacts.edit', contact_id=contact_id))


@contacts_bp.route('/<int:contact_id>/delete', methods=['POST'])
def delete(contact_id):
    """Delete a contact."""
    contact = Contact.query.get_or_404(contact_id)
    
    # Check if contact is linked to any deals
    roles = DealContactRole.query.filter_by(contact_id=contact_id).count()
    if roles > 0:
        flash('Cannot delete contact that is linked to deals. Remove relationships first.', 'error')
        return redirect(url_for('contacts.detail', contact_id=contact_id))
    
    db.session.delete(contact)
    db.session.commit()
    
    flash('Contact deleted.', 'success')
    return redirect(url_for('contacts.list_contacts'))

