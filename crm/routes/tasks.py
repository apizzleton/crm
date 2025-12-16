"""
Task routes for CRUD operations.
"""
from datetime import date, datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from crm.db import db
from crm.models import Task, TaskStatus, TaskPriority, Contact

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new task."""
    if request.method == 'GET':
        # Pre-fill deal_id or contact_id from query params
        deal_id = request.args.get('deal_id', type=int) or None
        contact_id = request.args.get('contact_id', type=int) or None
        from datetime import date
        return render_template('tasks/create.html', 
                             deal_id=deal_id, 
                             contact_id=contact_id,
                             today=date.today())
    
    # POST - create task
    try:
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        priority = request.form.get('priority', TaskPriority.MEDIUM.value)
        deal_id = request.form.get('deal_id', type=int) or None
        contact_id = request.form.get('contact_id', type=int) or None
        
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
        
        # Validate contact exists if provided
        if contact_id and not Contact.query.get(contact_id):
            flash('Invalid contact selected.', 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        
        task = Task(
            description=description,
            due_date=due_date,
            priority=priority,
            deal_id=deal_id,
            contact_id=contact_id,
            status=TaskStatus.OPEN.value
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully.', 'success')
        return redirect(request.referrer or url_for('dashboard.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating task: {str(e)}', 'error')
        return redirect(request.referrer or url_for('dashboard.index'))


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

