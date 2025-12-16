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

## Vercel Deployment

This app can be deployed to Vercel for web hosting:

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy to Vercel**:
```bash
vercel
```

3. **Set Environment Variables** (optional):
   - `SECRET_KEY`: Random secret key for Flask sessions
   - `DATABASE_URL`: Database connection string (SQLite works for basic use, but consider PostgreSQL for production)

4. **Database Note**: Since Vercel serverless functions are stateless, SQLite data won't persist between deployments. For production use, consider using a hosted database like:
   - Vercel Postgres
   - Supabase
   - Railway
   - PlanetScale

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

