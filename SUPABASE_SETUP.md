# Supabase Setup Guide

## Step 1: Create/Access Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create an account
3. Create a new project or select an existing one
4. Wait for the project to be fully initialized

## Step 2: Get Your Credentials

### Method A: From Dashboard
1. Go to **Settings** → **Database**
2. Scroll down to **Connection parameters**
3. Copy the following:
   - **Host**: `db.[your-project-ref].supabase.co`
   - **Database**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: [your database password]

### Method B: From API Settings (Recommended)
1. Go to **Settings** → **API**
2. Copy the following:
   - **Project URL**: `https://[your-project-ref].supabase.co`
   - **anon public key**: `eyJ...` (starts with eyJ)
   - **service_role secret**: `eyJ...` (starts with eyJ, keep this secure!)

## Step 3: Update Your .env File

Replace the placeholder values in your `.env` file:

```env
# For REST API method (recommended)
SUPABASE_URL = https://your-project-ref.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# For direct PostgreSQL connection (alternative)
PG_HOST = db.your-project-ref.supabase.co
PG_PASSWORD = your-actual-database-password
```

## Step 4: Set Up Database Schema

1. Go to **SQL Editor** in your Supabase dashboard
2. Create a **New Query**
3. Copy and paste the contents of `setup_supabase_sql.sql`
4. Click **Run** to execute the SQL

## Step 5: Test Connection

Run the test script:
```bash
python src/vector_store_supabase_rest.py
```

## Step 6: Migrate Your Data

Once the connection is working:
```bash
python migrate_to_supabase.py
```

## Troubleshooting

### Connection Timeouts
- Check if your Supabase project is active (not paused)
- Verify your internet connection
- Try the REST API method instead of direct PostgreSQL

### Authentication Errors
- Double-check your credentials
- Make sure you're using the service_role key (not anon key) for write operations
- Verify your project URL format

### Vector Extension Issues
- Ensure the `vector` extension is enabled in your Supabase project
- Go to **Database** → **Extensions** and enable `vector` if not already enabled

## Current Status
- ✅ Local RAG system working
- 🔄 Setting up Supabase credentials
- ⏳ Pending: Database connection and data migration
