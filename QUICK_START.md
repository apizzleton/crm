# Quick Start: Deploy to Vercel

## ✅ Step 1: Create Database Tables (5 minutes)

1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/sbuambrtlkxxezszangx/sql
2. Copy entire contents of `supabase_migration.sql`
3. Paste into SQL Editor
4. Click "Run"
5. Verify tables created in "Table Editor"

## ✅ Step 2: Set Vercel Environment Variables (2 minutes)

1. Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables
2. Add these two variables:

**DATABASE_URL:**
```
postgresql://postgres.sbuambrtlkxxezszangx:c7OHGeA8O1v6HZ5u@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

**SECRET_KEY:**
Generate one: Run `openssl rand -hex 32` in terminal, copy output

3. Select all environments (Production, Preview, Development)
4. Save

## ✅ Step 3: Deploy (1 minute)

```bash
cd C:\Users\AnthonyParadiso\Desktop\Temp\CRM
vercel --prod
```

Or connect GitHub repo in Vercel dashboard for automatic deployments.

## 🎉 Done!

Your CRM will be live at: `https://your-project.vercel.app`

---

**Troubleshooting:**
- If tables don't exist: Run the SQL migration manually
- If connection fails: Double-check DATABASE_URL in Vercel
- If static files don't load: Check vercel.json routes

