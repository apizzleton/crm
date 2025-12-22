"""
Database models for the CRM.
"""
from datetime import datetime
from enum import Enum
from crm.db import db


class DealStage(Enum):
    """Deal pipeline stages."""
    LEAD = "Lead"
    CONTACTED = "Contacted"
    UNDERWRITING = "Underwriting"
    LOI_SENT = "LOI_Sent"
    LOI_ACCEPTED = "LOI_Accepted"
    PSA = "PSA"
    CLOSED_WON = "Closed_Won"
    CLOSED_LOST = "Closed_Lost"


class TaskStatus(Enum):
    """Task status options."""
    OPEN = "Open"
    DONE = "Done"
    SNOOZED = "Snoozed"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TouchpointType(Enum):
    """Types of touchpoints."""
    CALL = "Call"
    EMAIL = "Email"
    TEXT = "Text"
    MEETING = "Meeting"
    NOTE = "Note"


class ContactRole(Enum):
    """Roles a contact can have in relation to a deal."""
    LISTING_BROKER = "Listing_Broker"
    OWNER = "Owner"
    PROPERTY_MANAGER = "Property_Manager"
    LENDER = "Lender"
    VENDOR = "Vendor"
    OTHER = "Other"


class Contact(db.Model):
    """Contact model for brokers, owners, vendors, etc."""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    role_type = db.Column(db.String(50))  # General role (broker, owner, etc.)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deal_roles = db.relationship('DealContactRole', back_populates='contact', cascade='all, delete-orphan')
    property_ownerships = db.relationship('PropertyOwner', back_populates='contact', cascade='all, delete-orphan')
    touchpoints = db.relationship('Touchpoint', back_populates='contact', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='contact', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contact {self.name}>'


class Property(db.Model):
    """Property model for multifamily properties."""
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    units = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    property_class = db.Column(db.String(10))  # A, B, C, etc.
    estimated_value_min = db.Column(db.Numeric(15, 2))
    estimated_value_max = db.Column(db.Numeric(15, 2))
    buyer_interest = db.Column(db.Integer)  # 1-10 scale
    seller_motivation = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deals = db.relationship('Deal', back_populates='property', cascade='all, delete-orphan')
    owners = db.relationship('PropertyOwner', back_populates='property', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Property {self.address}>'


class PropertyOwner(db.Model):
    """Junction table linking properties to contacts with ownership details."""
    __tablename__ = 'property_owners'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    ownership_percentage = db.Column(db.Numeric(5, 2))  # e.g., 50.00
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    property = db.relationship('Property', back_populates='owners')
    contact = db.relationship('Contact', back_populates='property_ownerships')
    
    def __repr__(self):
        return f'<PropertyOwner property={self.property_id} contact={self.contact_id}>'


class Deal(db.Model):
    """Deal model for tracking multifamily deals."""
    __tablename__ = 'deals'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_name = db.Column(db.String(200), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    stage = db.Column(db.String(50), default=DealStage.LEAD.value, nullable=False)
    target_close_date = db.Column(db.Date)
    asking_price = db.Column(db.Numeric(15, 2))  # Optional
    links = db.Column(db.Text)  # JSON or comma-separated URLs
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = db.relationship('Property', back_populates='deals')
    contact_roles = db.relationship('DealContactRole', back_populates='deal', cascade='all, delete-orphan')
    touchpoints = db.relationship('Touchpoint', back_populates='deal', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='deal', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Deal {self.deal_name}>'


class DealContactRole(db.Model):
    """Junction table linking deals to contacts with specific roles."""
    __tablename__ = 'deal_contact_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # ContactRole enum value
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deal = db.relationship('Deal', back_populates='contact_roles')
    contact = db.relationship('Contact', back_populates='deal_roles')
    
    def __repr__(self):
        return f'<DealContactRole deal={self.deal_id} contact={self.contact_id} role={self.role}>'


class Touchpoint(db.Model):
    """Touchpoint model for logging calls, emails, meetings, etc."""
    __tablename__ = 'touchpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    touchpoint_type = db.Column(db.String(20), nullable=False)  # TouchpointType enum value
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    next_step = db.Column(db.Text)  # Optional next action noted during touchpoint
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deal = db.relationship('Deal', back_populates='touchpoints')
    contact = db.relationship('Contact', back_populates='touchpoints')
    
    def __repr__(self):
        return f'<Touchpoint {self.touchpoint_type} at {self.occurred_at}>'


class Task(db.Model):
    """Task model for follow-up reminders."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default=TaskStatus.OPEN.value, nullable=False)
    priority = db.Column(db.String(20), default=TaskPriority.MEDIUM.value)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deal = db.relationship('Deal', back_populates='tasks')
    contact = db.relationship('Contact', back_populates='tasks')
    related_property = db.relationship('Property')
    
    def __repr__(self):
        return f'<Task {self.description[:50]}>'
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.status == TaskStatus.DONE.value:
            return False
        return self.due_date < datetime.utcnow().date()
    
    @property
    def is_due_today(self):
        """Check if task is due today."""
        if self.status == TaskStatus.DONE.value:
            return False
        return self.due_date == datetime.utcnow().date()


def seed_initial_data():
    """Seed initial data if tables are empty."""
    # This function can be expanded to add default stages, etc.
    # For now, we'll rely on enum defaults
    pass

