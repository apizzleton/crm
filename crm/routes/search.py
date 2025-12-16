"""
Search routes for global search functionality.
"""
from flask import Blueprint, render_template, request
from crm.db import db
from crm.models import Deal, Contact, Property

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
def search():
    """Global search across deals, contacts, and properties."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search/results.html', 
                             deals=[], 
                             contacts=[], 
                             properties=[], 
                             query='')
    
    # Search deals
    deals = Deal.query.filter(
        Deal.deal_name.ilike(f'%{query}%')
    ).limit(20).all()
    
    # Search contacts
    contacts = Contact.query.filter(
        db.or_(
            Contact.name.ilike(f'%{query}%'),
            Contact.company.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    # Search properties
    properties = Property.query.filter(
        db.or_(
            Property.address.ilike(f'%{query}%'),
            Property.city.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    return render_template('search/results.html',
                         deals=deals,
                         contacts=contacts,
                         properties=properties,
                         query=query)

