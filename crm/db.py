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
        _ensure_properties_address_nullable(db.engine)
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
        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}'))
        conn.commit()


def _ensure_properties_address_nullable(engine):
    """If properties.address is still NOT NULL (legacy schema), rebuild table to allow NULL."""
    with engine.connect() as conn:
        info = conn.execute(text("PRAGMA table_info(properties)")).fetchall()
        address_col = next((c for c in info if c[1] == 'address'), None)
        # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
        if not address_col or address_col[3] == 0:
            return  # already nullable or column missing (unexpected)

        conn.execute(text("PRAGMA foreign_keys=off;"))
        conn.execute(text("""
            CREATE TABLE properties_new (
              id INTEGER PRIMARY KEY,
              name VARCHAR(200),
              address VARCHAR(300),
              city VARCHAR(100),
              state VARCHAR(50),
              zip_code VARCHAR(20),
              units INTEGER,
              year_built INTEGER,
              property_class VARCHAR(10),
              notes TEXT,
              created_at DATETIME,
              updated_at DATETIME
            );
        """))
        conn.execute(text("""
            INSERT INTO properties_new
            (id, name, address, city, state, zip_code, units, year_built, property_class, notes, created_at, updated_at)
            SELECT id, name, address, city, state, zip_code, units, year_built, property_class, notes, created_at, updated_at
            FROM properties;
        """))
        conn.execute(text("DROP TABLE properties;"))
        conn.execute(text("ALTER TABLE properties_new RENAME TO properties;"))
        conn.execute(text("PRAGMA foreign_keys=on;"))
        conn.commit()

