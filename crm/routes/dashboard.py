"""
Dashboard routes.
"""
from datetime import date, datetime
from flask import Blueprint, render_template
from crm.db import db
from crm.models import Task, TaskStatus

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard showing all open tasks."""
    today = date.today()
    
    # Get all open tasks
    tasks = Task.query.filter(
        Task.status == TaskStatus.OPEN.value
    ).order_by(Task.due_date, Task.priority.desc()).all()
    
    return render_template('dashboard.html', 
                         tasks=tasks,
                         today=today)

