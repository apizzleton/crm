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
    """Main dashboard showing today's tasks and overdue items."""
    today = date.today()
    
    # Get today's tasks
    today_tasks = Task.query.filter(
        Task.due_date == today,
        Task.status == TaskStatus.OPEN.value
    ).order_by(Task.priority.desc(), Task.due_date).all()
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        Task.due_date < today,
        Task.status == TaskStatus.OPEN.value
    ).order_by(Task.due_date, Task.priority.desc()).all()
    
    # Get upcoming tasks (next 7 days)
    from datetime import timedelta
    next_week = today + timedelta(days=7)
    upcoming_tasks = Task.query.filter(
        Task.due_date > today,
        Task.due_date <= next_week,
        Task.status == TaskStatus.OPEN.value
    ).order_by(Task.due_date, Task.priority.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         today_tasks=today_tasks,
                         overdue_tasks=overdue_tasks,
                         upcoming_tasks=upcoming_tasks,
                         today=today)

