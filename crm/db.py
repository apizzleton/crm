"""
Database setup and initialization.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect

db = SQLAlchemy()


def init_db(app: Flask):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from crm.models import Contact, Property, Deal, DealContactRole, Touchpoint, Task, PropertyOwner
        
        # Create all tables
        db.create_all()

        # Database migration helpers - ensure new columns exist on existing databases
        _ensure_column(db.engine, 'tasks', 'property_id', 'INTEGER REFERENCES properties(id)')
        
        # Seed initial stage values if needed
        from crm.models import seed_initial_data
        seed_initial_data()


def _ensure_column(engine, table_name: str, column_name: str, column_def: str):
    """Add a column if it is missing (database-agnostic migration helper)."""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        if column_name in columns:
            return
        with engine.connect() as conn:
            # PostgreSQL uses IF NOT EXISTS, SQLite doesn't support it
            db_url = str(engine.url)
            if db_url.startswith('postgresql'):
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_def}'))
            else:
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}'))
            conn.commit()
    except Exception as e:
        # Column might already exist or table might not exist - ignore
        print(f"Note: Could not add column {column_name} to {table_name}: {e}")

