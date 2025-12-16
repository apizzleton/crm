"""
Property routes for CRUD operations.
"""
from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, render_template, redirect, url_for, flash
from crm.db import db
from crm.models import Property, Contact, PropertyOwner

properties_bp = Blueprint('properties', __name__, url_prefix='/properties')


@properties_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new property."""
    if request.method == 'GET':
        return render_template('properties/create.html')
    
    # POST - create property
    try:
        name = request.form.get('name', '').strip() or None
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip() or None
        state = request.form.get('state', '').strip() or None
        zip_code = request.form.get('zip_code', '').strip() or None
        units_str = request.form.get('units', '') or None
        year_built_str = request.form.get('year_built', '') or None
        property_class = request.form.get('property_class', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        
        if not address:
            flash('Address is required.', 'error')
            return redirect(url_for('properties.create'))
        # Default name to address if not provided to avoid blank display
        if not name:
            name = address
        
        units = None
        if units_str:
            try:
                units = int(units_str)
            except ValueError:
                flash('Invalid units format.', 'error')
                return redirect(url_for('properties.create'))
        
        year_built = None
        if year_built_str:
            try:
                year_built = int(year_built_str)
            except ValueError:
                flash('Invalid year built format.', 'error')
                return redirect(url_for('properties.create'))
        
        property_obj = Property(
            name=name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            units=units,
            year_built=year_built,
            property_class=property_class,
            notes=notes
        )
        
        db.session.add(property_obj)
        db.session.commit()
        
        flash('Property created successfully.', 'success')
        return redirect(request.referrer or url_for('deals.create'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating property: {str(e)}', 'error')
        return redirect(url_for('properties.create'))


@properties_bp.route('/')
def list_properties():
    """List all properties."""
    city = request.args.get('city', '').strip()
    min_units_str = request.args.get('min_units', '').strip()
    max_units_str = request.args.get('max_units', '').strip()

    query = Property.query

    # Apply city filter (case-insensitive partial match)
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))

    min_units = None
    max_units = None
    if min_units_str:
        try:
            min_units = int(min_units_str)
        except ValueError:
            flash('Min units must be a number.', 'error')

    if max_units_str:
        try:
            max_units = int(max_units_str)
        except ValueError:
            flash('Max units must be a number.', 'error')

    # If both bounds are present, ensure they make sense; drop the filter if not.
    if min_units is not None and max_units is not None and max_units < min_units:
        flash('Max units must be greater than or equal to min units.', 'error')
        min_units = None
        max_units = None

    if min_units is not None:
        query = query.filter(Property.units >= min_units)
    if max_units is not None:
        query = query.filter(Property.units <= max_units)

    properties = query.order_by(Property.created_at.desc()).all()
    filters = {
        'city': city,
        'min_units': min_units_str,
        'max_units': max_units_str
    }
    return render_template('properties/list.html', properties=properties, filters=filters)


@properties_bp.route('/<int:property_id>')
def detail(property_id):
    """Show property detail page."""
    property_obj = Property.query.get_or_404(property_id)

    # Get related deals
    deals = property_obj.deals

    # Get owners and all contacts for dropdown
    owners = property_obj.owners
    all_contacts = Contact.query.order_by(Contact.name).all()

    return render_template('properties/detail.html',
                         property=property_obj,
                         deals=deals,
                         owners=owners,
                         all_contacts=all_contacts)


@properties_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
def edit(property_id):
    """Edit an existing property."""
    property_obj = Property.query.get_or_404(property_id)

    if request.method == 'GET':
        return render_template('properties/edit.html', property=property_obj)

    # POST - update property
    try:
        name = request.form.get('name', '').strip() or None
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip() or None
        state = request.form.get('state', '').strip() or None
        zip_code = request.form.get('zip_code', '').strip() or None
        units_str = request.form.get('units', '') or None
        year_built_str = request.form.get('year_built', '') or None
        property_class = request.form.get('property_class', '').strip() or None
        notes = request.form.get('notes', '').strip() or None

        if not address:
            flash('Address is required.', 'error')
            return redirect(url_for('properties.edit', property_id=property_id))
        if not name:
            name = address

        units = None
        if units_str:
            try:
                units = int(units_str)
            except ValueError:
                flash('Invalid units format.', 'error')
                return redirect(url_for('properties.edit', property_id=property_id))

        year_built = None
        if year_built_str:
            try:
                year_built = int(year_built_str)
            except ValueError:
                flash('Invalid year built format.', 'error')
                return redirect(url_for('properties.edit', property_id=property_id))

        # Update property
        property_obj.name = name
        property_obj.address = address
        property_obj.city = city
        property_obj.state = state
        property_obj.zip_code = zip_code
        property_obj.units = units
        property_obj.year_built = year_built
        property_obj.property_class = property_class
        property_obj.notes = notes

        db.session.commit()

        flash('Property updated successfully.', 'success')
        return redirect(url_for('properties.detail', property_id=property_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating property: {str(e)}', 'error')
        return redirect(url_for('properties.edit', property_id=property_id))


@properties_bp.route('/<int:property_id>/delete', methods=['POST'])
def delete(property_id):
    """Delete a property."""
    property_obj = Property.query.get_or_404(property_id)

    try:
        # Check if property has associated deals
        if property_obj.deals:
            flash('Cannot delete property that has associated deals.', 'error')
            return redirect(url_for('properties.detail', property_id=property_id))

        db.session.delete(property_obj)
        db.session.commit()

        flash('Property deleted successfully.', 'success')
        return redirect(url_for('properties.list_properties'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting property: {str(e)}', 'error')
        return redirect(url_for('properties.detail', property_id=property_id))


@properties_bp.route('/<int:property_id>/add_owner', methods=['POST'])
def add_owner(property_id):
    """Add an owner to a property."""
    property_obj = Property.query.get_or_404(property_id)

    try:
        contact_id = request.form.get('contact_id')
        ownership_pct_str = request.form.get('ownership_percentage', '').strip()
        notes = request.form.get('notes', '').strip() or None

        if not contact_id:
            flash('Please select a contact.', 'error')
            return redirect(url_for('properties.detail', property_id=property_id))

        # Check if this owner is already linked
        existing = PropertyOwner.query.filter_by(
            property_id=property_id,
            contact_id=int(contact_id)
        ).first()

        if existing:
            flash('This contact is already an owner of this property.', 'error')
            return redirect(url_for('properties.detail', property_id=property_id))

        # Parse ownership percentage
        ownership_pct = None
        if ownership_pct_str:
            try:
                ownership_pct = Decimal(ownership_pct_str)
                if ownership_pct < 0 or ownership_pct > 100:
                    flash('Ownership percentage must be between 0 and 100.', 'error')
                    return redirect(url_for('properties.detail', property_id=property_id))
            except InvalidOperation:
                flash('Invalid ownership percentage format.', 'error')
                return redirect(url_for('properties.detail', property_id=property_id))

        owner = PropertyOwner(
            property_id=property_id,
            contact_id=int(contact_id),
            ownership_percentage=ownership_pct,
            notes=notes
        )

        db.session.add(owner)
        db.session.commit()

        flash('Owner added successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding owner: {str(e)}', 'error')

    return redirect(url_for('properties.detail', property_id=property_id))


@properties_bp.route('/<int:property_id>/remove_owner/<int:owner_id>', methods=['POST'])
def remove_owner(property_id, owner_id):
    """Remove an owner from a property."""
    owner = PropertyOwner.query.get_or_404(owner_id)

    # Verify the owner belongs to this property
    if owner.property_id != property_id:
        flash('Invalid owner.', 'error')
        return redirect(url_for('properties.detail', property_id=property_id))

    try:
        db.session.delete(owner)
        db.session.commit()

        flash('Owner removed successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error removing owner: {str(e)}', 'error')

    return redirect(url_for('properties.detail', property_id=property_id))
