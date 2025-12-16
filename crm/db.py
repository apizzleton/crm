"""
Database setup and initialization.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()


def init_db(app: Flask):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from crm.models import Contact, Property, Deal, DealContactRole, Touchpoint, Task
        
        # Create all tables
        db.create_all()

        # Ensure new columns exist on existing databases without migrations.
        _ensure_column(db.engine, 'properties', 'name', 'VARCHAR(200)')
        with db.engine.connect() as conn:
            conn.execute(
                text("UPDATE properties SET name = address WHERE (name IS NULL OR name = '') AND address IS NOT NULL")
            )
            conn.commit()
        
        # Seed initial stage values if needed
        from crm.models import seed_initial_data
        seed_initial_data()


def _ensure_column(engine, table_name: str, column_name: str, column_def: str):
    """Add a column if it is missing (SQLite-safe, minimal migration helper)."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    if column_name in columns:
        return
    with engine.connect() as conn:
        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_def}'))
        conn.commit()

