"""
Deal routes for CRUD operations and pipeline view.
"""
from datetime import date, datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from crm.db import db
from crm.models import Deal, DealStage, Property, DealContactRole, Contact, Task, Touchpoint

deals_bp = Blueprint('deals', __name__, url_prefix='/deals')


@deals_bp.route('/')
def list_deals():
    """List all deals, optionally filtered by stage."""
    stage_filter = request.args.get('stage')
    
    query = Deal.query
    if stage_filter:
        query = query.filter(Deal.stage == stage_filter)
    
    deals = query.order_by(Deal.created_at.desc()).all()
    
    # Group deals by stage for pipeline view
    deals_by_stage = {}
    for stage in DealStage:
        deals_by_stage[stage.value] = [d for d in deals if d.stage == stage.value]
    
    return render_template('deals/list.html', 
                         deals=deals,
                         deals_by_stage=deals_by_stage,
                         stages=DealStage,
                         current_stage=stage_filter)


@deals_bp.route('/<int:deal_id>')
def detail(deal_id):
    """Show deal detail page."""
    deal = Deal.query.get_or_404(deal_id)
    
    # Get related contacts
    contact_roles = DealContactRole.query.filter_by(deal_id=deal_id).all()
    
    # Get all contacts for dropdown
    all_contacts = Contact.query.order_by(Contact.name).all()
    
    # Get open tasks for this deal
    open_tasks = Task.query.filter_by(
        deal_id=deal_id,
        status='Open'
    ).order_by(Task.due_date).all()
    
    # Get touchpoints ordered by most recent
    touchpoints = Touchpoint.query.filter_by(deal_id=deal_id).order_by(
        Touchpoint.occurred_at.desc()
    ).all()
    
    return render_template('deals/detail.html',
                         deal=deal,
                         contact_roles=contact_roles,
                         all_contacts=all_contacts,
                         open_tasks=open_tasks,
                         touchpoints=touchpoints,
                         stages=DealStage)


@deals_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new deal."""
    if request.method == 'GET':
        # Get all properties for dropdown
        properties = Property.query.order_by(Property.address).all()
        return render_template('deals/create.html', properties=properties, stages=DealStage)
    
    # POST - create deal
    try:
        deal_name = request.form.get('deal_name', '').strip()
        property_id = request.form.get('property_id', type=int)
        stage = request.form.get('stage', DealStage.LEAD.value)
        target_close_str = request.form.get('target_close_date', '') or None
        asking_price_str = request.form.get('asking_price', '') or None
        links = request.form.get('links', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        
        if not deal_name:
            flash('Deal name is required.', 'error')
            return redirect(url_for('deals.create'))
        
        if not property_id:
            flash('Property is required.', 'error')
            return redirect(url_for('deals.create'))
        
        # Validate property exists
        property_obj = Property.query.get(property_id)
        if not property_obj:
            flash('Invalid property selected.', 'error')
            return redirect(url_for('deals.create'))
        
        target_close_date = None
        if target_close_str:
            try:
                target_close_date = datetime.strptime(target_close_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid target close date format.', 'error')
                return redirect(url_for('deals.create'))
        
        asking_price = None
        if asking_price_str:
            try:
                asking_price = float(asking_price_str.replace(',', '').replace('$', ''))
            except ValueError:
                flash('Invalid asking price format.', 'error')
                return redirect(url_for('deals.create'))
        
        deal = Deal(
            deal_name=deal_name,
            property_id=property_id,
            stage=stage,
            target_close_date=target_close_date,
            asking_price=asking_price,
            links=links,
            notes=notes
        )
        
        db.session.add(deal)
        db.session.commit()
        
        flash('Deal created successfully.', 'success')
        return redirect(url_for('deals.detail', deal_id=deal.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating deal: {str(e)}', 'error')
        return redirect(url_for('deals.create'))


@deals_bp.route('/<int:deal_id>/edit', methods=['GET', 'POST'])
def edit(deal_id):
    """Edit an existing deal."""
    deal = Deal.query.get_or_404(deal_id)
    
    if request.method == 'GET':
        properties = Property.query.order_by(Property.address).all()
        return render_template('deals/edit.html', deal=deal, properties=properties, stages=DealStage)
    
    # POST - update deal
    try:
        deal.deal_name = request.form.get('deal_name', '').strip()
        deal.property_id = request.form.get('property_id', type=int)
        deal.stage = request.form.get('stage', DealStage.LEAD.value)
        target_close_str = request.form.get('target_close_date', '') or None
        asking_price_str = request.form.get('asking_price', '') or None
        deal.links = request.form.get('links', '').strip() or None
        deal.notes = request.form.get('notes', '').strip() or None
        
        if not deal.deal_name:
            flash('Deal name is required.', 'error')
            return redirect(url_for('deals.edit', deal_id=deal_id))
        
        # Validate property exists
        property_obj = Property.query.get(deal.property_id)
        if not property_obj:
            flash('Invalid property selected.', 'error')
            return redirect(url_for('deals.edit', deal_id=deal_id))
        
        deal.target_close_date = None
        if target_close_str:
            try:
                deal.target_close_date = datetime.strptime(target_close_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid target close date format.', 'error')
                return redirect(url_for('deals.edit', deal_id=deal_id))
        
        deal.asking_price = None
        if asking_price_str:
            try:
                deal.asking_price = float(asking_price_str.replace(',', '').replace('$', ''))
            except ValueError:
                flash('Invalid asking price format.', 'error')
                return redirect(url_for('deals.edit', deal_id=deal_id))
        
        db.session.commit()
        
        flash('Deal updated successfully.', 'success')
        return redirect(url_for('deals.detail', deal_id=deal.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating deal: {str(e)}', 'error')
        return redirect(url_for('deals.edit', deal_id=deal_id))


@deals_bp.route('/<int:deal_id>/add_contact', methods=['POST'])
def add_contact(deal_id):
    """Add a contact to a deal with a role."""
    deal = Deal.query.get_or_404(deal_id)
    
    contact_id = request.form.get('contact_id', type=int)
    role = request.form.get('role', '').strip()
    notes = request.form.get('notes', '').strip() or None
    
    if not contact_id:
        flash('Contact is required.', 'error')
        return redirect(url_for('deals.detail', deal_id=deal_id))
    
    if not role:
        flash('Role is required.', 'error')
        return redirect(url_for('deals.detail', deal_id=deal_id))
    
    contact = Contact.query.get(contact_id)
    if not contact:
        flash('Invalid contact selected.', 'error')
        return redirect(url_for('deals.detail', deal_id=deal_id))
    
    # Check if relationship already exists
    existing = DealContactRole.query.filter_by(
        deal_id=deal_id,
        contact_id=contact_id,
        role=role
    ).first()
    
    if existing:
        flash('This contact is already linked with this role.', 'error')
        return redirect(url_for('deals.detail', deal_id=deal_id))
    
    deal_contact_role = DealContactRole(
        deal_id=deal_id,
        contact_id=contact_id,
        role=role,
        notes=notes
    )
    
    db.session.add(deal_contact_role)
    db.session.commit()
    
    flash('Contact added to deal.', 'success')
    return redirect(url_for('deals.detail', deal_id=deal_id))


@deals_bp.route('/<int:deal_id>/remove_contact/<int:role_id>', methods=['POST'])
def remove_contact(deal_id, role_id):
    """Remove a contact role from a deal."""
    deal = Deal.query.get_or_404(deal_id)
    role = DealContactRole.query.get_or_404(role_id)
    
    if role.deal_id != deal_id:
        flash('Invalid relationship.', 'error')
        return redirect(url_for('deals.detail', deal_id=deal_id))
    
    db.session.delete(role)
    db.session.commit()
    
    flash('Contact removed from deal.', 'success')
    return redirect(url_for('deals.detail', deal_id=deal_id))

