"""
Task routes for CRUD operations.
"""
from datetime import date, datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from crm.db import db
from crm.models import Task, TaskStatus, TaskPriority, Deal, Contact, Property

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new task."""
    if request.method == 'GET':
        # Pre-fill deal_id or contact_id from query params
        deal_id = request.args.get('deal_id', type=int) or None
        contact_id = request.args.get('contact_id', type=int) or None
        property_id = request.args.get('property_id', type=int) or None
        
        contacts = Contact.query.order_by(Contact.name).all()
        deals = Deal.query.order_by(Deal.deal_name).all()
        properties = Property.query.order_by(Property.name, Property.address).all()
        
        from datetime import date
        return render_template('tasks/create.html', 
                             deal_id=deal_id, 
                             contact_id=contact_id,
                             property_id=property_id,
                             contacts=contacts,
                             deals=deals,
                             properties=properties,
                             today=date.today())
    
    # POST - create task
    try:
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        priority = request.form.get('priority', TaskPriority.MEDIUM.value)
        deal_id = request.form.get('deal_id', type=int) or None
        contact_id = request.form.get('contact_id', type=int) or None
        property_id = request.form.get('property_id', type=int) or None
        
        if not description:
            flash('Task description is required.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        if not due_date_str:
            flash('Due date is required.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        task = Task(
            description=description,
            due_date=due_date,
            priority=priority,
            deal_id=deal_id,
            contact_id=contact_id,
            property_id=property_id,
            status=TaskStatus.OPEN.value
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully.', 'success')
        return redirect(url_for('dashboard.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating task: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'GET':
        contacts = Contact.query.order_by(Contact.name).all()
        deals = Deal.query.order_by(Deal.deal_name).all()
        properties = Property.query.order_by(Property.name, Property.address).all()
        
        return render_template('tasks/edit.html', 
                             task=task,
                             contacts=contacts,
                             deals=deals,
                             properties=properties)
    
    # POST - update task
    try:
        task.description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        task.priority = request.form.get('priority', TaskPriority.MEDIUM.value)
        task.status = request.form.get('status', task.status)
        task.deal_id = request.form.get('deal_id', type=int) or None
        task.contact_id = request.form.get('contact_id', type=int) or None
        task.property_id = request.form.get('property_id', type=int) or None
        
        if not task.description:
            flash('Task description is required.', 'error')
            return redirect(url_for('tasks.edit', task_id=task_id))
        
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return redirect(url_for('tasks.edit', task_id=task_id))
        
        db.session.commit()
        flash('Task updated successfully.', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
        return redirect(url_for('tasks.edit', task_id=task_id))


@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
def complete(task_id):
    """Mark a task as complete."""
    task = Task.query.get_or_404(task_id)
    task.status = TaskStatus.DONE.value
    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Task marked as complete.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@tasks_bp.route('/<int:task_id>/snooze', methods=['POST'])
def snooze(task_id):
    """Snooze a task (mark as snoozed)."""
    task = Task.query.get_or_404(task_id)
    task.status = TaskStatus.SNOOZED.value
    db.session.commit()
    
    flash('Task snoozed.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@tasks_bp.route('/<int:task_id>/reopen', methods=['POST'])
def reopen(task_id):
    """Reopen a snoozed task."""
    task = Task.query.get_or_404(task_id)
    task.status = TaskStatus.OPEN.value
    task.completed_at = None
    db.session.commit()
    
    flash('Task reopened.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))

