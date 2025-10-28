"""
Setup Supabase tables for multi-dataset system
Runs SQL setup automatically via Supabase client
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY not found in .env")
    sys.exit(1)

from supabase import create_client

def setup_tables():
    """Create all necessary tables for the multi-dataset system"""
    
    print("\n" + "="*70)
    print("SETTING UP SUPABASE TABLES FOR MULTI-DATASET SYSTEM")
    print("="*70 + "\n")
    
    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Check if tables exist
    tables_to_check = ['documents_new', 'documents_old', 'documents_combined']
    
    print("📊 Checking existing tables...")
    for table_name in tables_to_check:
        try:
            result = supabase.table(table_name).select("id").limit(1).execute()
            print(f"   ✅ Table '{table_name}' exists")
        except Exception as e:
            if "Could not find the table" in str(e):
                print(f"   ❌ Table '{table_name}' does not exist (will create on first insert)")
            else:
                print(f"   ⚠️  Error checking '{table_name}': {e}")
    
    print("\n📝 NOTE: You need to manually run the SQL setup in Supabase dashboard:")
    print("   1. Go to: https://app.supabase.com → Your Project → SQL Editor")
    print("   2. Click 'New Query'")
    print("   3. Open file: setup_supabase_datasets_sql.sql")
    print("   4. Copy and paste the SQL into the editor")
    print("   5. Click 'Run'")
    print("\n   OR run via psql:")
    print("   psql -h db.fgrltciphyzxzjqmdsdc.supabase.co -U postgres < setup_supabase_datasets_sql.sql\n")
    
    # Try to read and display the SQL file
    sql_file = Path("setup_supabase_datasets_sql.sql")
    if sql_file.exists():
        print("📄 SQL Setup File Contents:")
        print("="*70)
        with open(sql_file, 'r') as f:
            print(f.read())
        print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    setup_tables()
    print("✅ Setup complete! Run the SQL in Supabase dashboard to create tables.\n")
