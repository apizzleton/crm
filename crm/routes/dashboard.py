"""
Dashboard routes.
"""
from datetime import date, datetime
from flask import Blueprint, render_template, request
from crm.db import db
from crm.models import Task, TaskStatus

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard showing open tasks by default, with filtering."""
    today = date.today()
    status_filter = request.args.get('status', 'Open')
    
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
                         current_status=status_filter)
