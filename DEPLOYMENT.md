# Deployment Guide for Vercel + Supabase

## Step 1: Create Database Tables in Supabase

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/sbuambrtlkxxezszangx/sql
2. Open the SQL Editor
3. Copy and paste the contents of `supabase_migration.sql`
4. Click "Run" to execute the migration
5. Verify tables were created by checking the "Table Editor" section

## Step 2: Configure Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Navigate to: Settings → Environment Variables
3. Add the following variables:

### Required Variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://postgres.sbuambrtlkxxezszangx:c7OHGeA8O1v6HZ5u@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require` |
| `SECRET_KEY` | Generate a random secure string (e.g., use `openssl rand -hex 32`) |

**Important**: Make sure to add these for **Production**, **Preview**, and **Development** environments if you want them to work in all environments.

## Step 3: Deploy to Vercel

### Option A: Using Vercel CLI

```bash
# Install Vercel CLI if you haven't
npm install -g vercel

# Navigate to project directory
cd C:\Users\AnthonyParadiso\Desktop\Temp\CRM

# Deploy
vercel

# For production deployment
vercel --prod
```

### Option B: Using GitHub Integration

1. Push your code to a GitHub repository
2. Import the repository in Vercel dashboard
3. Vercel will automatically detect the Python project and deploy

## Step 4: Verify Deployment

1. Visit your Vercel deployment URL
2. Check that the app loads correctly
3. Try creating a contact or property to verify database connectivity

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly in Vercel environment variables
- Check that the Supabase database is accessible (not paused)
- Ensure the connection string uses `postgresql://` not `postgres://`

### Table Creation Issues

- If tables don't exist, run the migration SQL manually in Supabase SQL Editor
- The app will attempt to create tables on first request, but it's better to create them manually

### Static Files Not Loading

- Verify `vercel.json` routes static files correctly
- Check that CSS/JS files are in `crm/static/` directory

## Notes

- The database tables will be created automatically on first request if they don't exist (via `db.create_all()`)
- However, it's recommended to run the migration SQL manually for better control
- Local SQLite database won't work on Vercel - you must use the Supabase PostgreSQL database

