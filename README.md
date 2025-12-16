# Multifamily CRM

A local-only CRM for tracking commercial multifamily deals, contacts, and follow-up tasks.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to: http://127.0.0.1:5000

## Backup

The database is stored as `crm.db` in the project root. To backup:
- Simply copy `crm.db` to a safe location
- Or use the backup/export feature in the app (coming in MVP)

## Features

- **Dashboard**: View today's tasks and overdue items
- **Pipeline**: Track deals through stages (Lead → Contacted → Underwriting → LOI → PSA → Closed)
- **Contacts**: Manage brokers, owners, and other contacts
- **Tasks**: Never miss a follow-up with task reminders
- **Touchpoints**: Log calls, emails, meetings, and notes

