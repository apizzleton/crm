"""
Touchpoint routes for logging interactions.
"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from crm.db import db
from crm.models import Touchpoint, TouchpointType, Task, TaskPriority, Contact

touchpoints_bp = Blueprint('touchpoints', __name__, url_prefix='/touchpoints')


@touchpoints_bp.route('/')
def index():
    """List all touchpoints."""
    # Eager load relationships for efficiency
    touchpoints = Touchpoint.query.options(
        db.joinedload(Touchpoint.contact)
    ).order_by(Touchpoint.occurred_at.desc()).all()
    
    # Get all contacts for the log touchpoint modal
    contacts = Contact.query.order_by(Contact.name).all()
    
    return render_template('touchpoints/list.html', 
                         touchpoints=touchpoints,
                         contacts=contacts)


@touchpoints_bp.route('/create', methods=['POST'])
def create():
    """Create a new touchpoint and optionally create a follow-up task."""
    try:
        contact_id = request.form.get('contact_id', type=int) or None
        touchpoint_type = request.form.get('touchpoint_type', '').strip()
        occurred_at_str = request.form.get('occurred_at', '')
        summary = request.form.get('summary', '').strip()
        next_step = request.form.get('next_step', '').strip() or None
        
        # Optional: create follow-up task
        create_task = request.form.get('create_task') == 'yes'
        task_due_date_str = request.form.get('task_due_date', '')
        task_description = request.form.get('task_description', '').strip()
        task_priority = request.form.get('task_priority', TaskPriority.MEDIUM.value)
        
        if not touchpoint_type:
            flash('Touchpoint type is required.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        if not summary:
            flash('Summary is required.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        if not contact_id:
            flash('A contact must be selected.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        # Validate contact exists
        if not Contact.query.get(contact_id):
            flash('Invalid contact selected.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        # Parse occurred_at
        occurred_at = datetime.utcnow()
        if occurred_at_str:
            try:
                occurred_at = datetime.strptime(occurred_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    occurred_at = datetime.strptime(occurred_at_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date/time format.', 'error')
                    return redirect(request.referrer or url_for('dashboard.index'))
        
        # Create touchpoint
        touchpoint = Touchpoint(
            contact_id=contact_id,
            touchpoint_type=touchpoint_type,
            occurred_at=occurred_at,
            summary=summary,
            next_step=next_step
        )
        
        db.session.add(touchpoint)
        
        # Create follow-up task if requested
        if create_task:
            if not task_due_date_str:
                flash('Task due date is required when creating a task.', 'error')
                return redirect(request.referrer or url_for('dashboard.index'))
            
            if not task_description:
                # Use next_step or summary as default
                task_description = next_step or summary[:100]
            
            try:
                task_due_date = datetime.strptime(task_due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid task due date format.', 'error')
                return redirect(request.referrer or url_for('dashboard.index'))
            
            task = Task(
                description=task_description,
                due_date=task_due_date,
                priority=task_priority,
                contact_id=contact_id,
                status='Open'
            )
            
            db.session.add(task)
        
        db.session.commit()
        
        flash('Touchpoint logged successfully.' + (' Follow-up task created.' if create_task else ''), 'success')
        return redirect(request.referrer or url_for('dashboard.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error logging touchpoint: {str(e)}', 'error')
        return redirect(request.referrer or url_for('dashboard.index'))
