"""
Contact routes for CRUD operations.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from crm.db import db
from crm.models import Contact, Task, Touchpoint, PropertyOwner, Property

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
                         property_ownerships=property_ownerships,
                         open_tasks=open_tasks,
                         touchpoints=touchpoints)


@contacts_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new contact."""
    # Get all properties for the dropdown
    properties = Property.query.order_by(Property.name, Property.address).all()
    
    if request.method == 'GET':
        return render_template('contacts/create.html', properties=properties)
    
    # POST - create contact
    try:
        name = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip() or None
        role_type = request.form.get('role_type', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        email = request.form.get('email', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        tags = request.form.get('tags', '').strip() or None
        
        # Get selected property IDs (multi-select)
        property_ids = request.form.getlist('properties')
        
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
        db.session.flush()  # Get the contact ID before committing
        
        # Create property ownership relationships
        for prop_id in property_ids:
            if prop_id:
                ownership = PropertyOwner(
                    property_id=int(prop_id),
                    contact_id=contact.id
                )
                db.session.add(ownership)
        
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
    
    # Get all properties for the dropdown
    properties = Property.query.order_by(Property.name, Property.address).all()
    
    # Get currently owned property IDs for pre-selecting in the form
    owned_property_ids = [po.property_id for po in contact.property_ownerships]
    
    if request.method == 'GET':
        return render_template('contacts/edit.html', 
                             contact=contact, 
                             properties=properties,
                             owned_property_ids=owned_property_ids)
    
    # POST - update contact
    try:
        contact.name = request.form.get('name', '').strip()
        contact.company = request.form.get('company', '').strip() or None
        contact.role_type = request.form.get('role_type', '').strip() or None
        contact.phone = request.form.get('phone', '').strip() or None
        contact.email = request.form.get('email', '').strip() or None
        contact.notes = request.form.get('notes', '').strip() or None
        contact.tags = request.form.get('tags', '').strip() or None
        
        # Get selected property IDs (multi-select)
        property_ids = [int(pid) for pid in request.form.getlist('properties') if pid]
        
        if not contact.name:
            flash('Name is required.', 'error')
            return redirect(url_for('contacts.edit', contact_id=contact_id))
        
        # Update property ownerships: remove old ones not in the new list
        for ownership in contact.property_ownerships[:]:
            if ownership.property_id not in property_ids:
                db.session.delete(ownership)
        
        # Add new property ownerships
        for prop_id in property_ids:
            if prop_id not in owned_property_ids:
                ownership = PropertyOwner(
                    property_id=prop_id,
                    contact_id=contact.id
                )
                db.session.add(ownership)
        
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
    
    db.session.delete(contact)
    db.session.commit()
    
    flash('Contact deleted.', 'success')
    return redirect(url_for('contacts.list_contacts'))

