"""
Dashboard routes.
"""
from datetime import date, datetime
from flask import Blueprint, render_template, request
from crm.db import db
from crm.models import Task, TaskStatus, Contact, Property, Touchpoint

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard showing open tasks by default, with filtering and statistics."""
    today = date.today()
    status_filter = request.args.get('status', 'Open')
    
    # Calculate statistics for dashboard cards
    all_tasks = Task.query.all()
    open_tasks = [t for t in all_tasks if t.status == TaskStatus.OPEN.value]
    overdue_count = sum(1 for t in open_tasks if t.due_date < today)
    due_today_count = sum(1 for t in open_tasks if t.due_date == today)
    snoozed_count = sum(1 for t in all_tasks if t.status == TaskStatus.SNOOZED.value)
    completed_count = sum(1 for t in all_tasks if t.status == TaskStatus.DONE.value)
    
    # Get entity counts
    contact_count = Contact.query.count()
    property_count = Property.query.count()
    
    # Get recent touchpoints for activity feed
    recent_touchpoints = Touchpoint.query.order_by(
        Touchpoint.occurred_at.desc()
    ).limit(5).all()
    
    # Build stats dictionary
    stats = {
        'open': len(open_tasks),
        'overdue': overdue_count,
        'due_today': due_today_count,
        'snoozed': snoozed_count,
        'completed': completed_count,
        'contacts': contact_count,
        'properties': property_count,
    }
    
    # Filter tasks for display
    query = Task.query
    
    if status_filter == 'All':
        pass
    elif status_filter in [s.value for s in TaskStatus]:
        query = query.filter(Task.status == status_filter)
    else:
        query = query.filter(Task.status == TaskStatus.OPEN.value)
        status_filter = 'Open'
        
    tasks = query.order_by(Task.due_date, Task.priority.desc()).all()
    
    return render_template('dashboard.html', 
                         tasks=tasks,
                         today=today,
                         current_status=status_filter,
                         stats=stats,
                         recent_touchpoints=recent_touchpoints)
