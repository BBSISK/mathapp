#!/usr/bin/env python3
"""
Prize System Database Migration for PythonAnywhere
Adds missing columns and tables to support Phase 3 prize system
"""
import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (same as your WSGI file)
os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SHOP_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text, inspect

print("=" * 70)
print("PRIZE SYSTEM DATABASE MIGRATION - PythonAnywhere")
print("=" * 70)
print()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

print("Step 1: Checking current database state...")
print("-" * 70)

with app.app_context():
    # Check what's missing
    missing_column = not check_column_exists('prizes', 'minimum_level')
    missing_table = not check_table_exists('prize_school_requests')
    
    if missing_column:
        print("❌ Column 'prizes.minimum_level' is MISSING")
    else:
        print("✓ Column 'prizes.minimum_level' already exists")
    
    if missing_table:
        print("❌ Table 'prize_school_requests' is MISSING")
    else:
        print("✓ Table 'prize_school_requests' already exists")
    
    if not missing_column and not missing_table:
        print()
        print("✓ Database schema is already up to date!")
        print()
        sys.exit(0)

print()
print("Step 2: Applying database migrations...")
print("-" * 70)

with app.app_context():
    try:
        # Add missing column
        if missing_column:
            print("Adding 'minimum_level' column to 'prizes' table...")
            db.session.execute(text('ALTER TABLE prizes ADD COLUMN minimum_level INTEGER DEFAULT 0'))
            db.session.commit()
            print("✓ Added column 'minimum_level' to 'prizes' table")
        
        # Add missing table
        if missing_table:
            print("Creating 'prize_school_requests' table...")
            
            create_table_sql = """
            CREATE TABLE prize_school_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_name VARCHAR(200) NOT NULL,
                county VARCHAR(100),
                suggested_rep_email VARCHAR(200),
                student_user_id INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                admin_notes TEXT,
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_at DATETIME,
                reviewed_by INTEGER,
                FOREIGN KEY (student_user_id) REFERENCES users(id),
                FOREIGN KEY (reviewed_by) REFERENCES users(id)
            )
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✓ Created 'prize_school_requests' table")
        
        print()
        print("=" * 70)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        db.session.rollback()
        print()
        print("=" * 70)
        print("❌ MIGRATION FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("This might happen if:")
        print("1. The database is locked (close any SQLite browser)")
        print("2. You don't have write permissions")
        print("3. The changes have already been applied")
        sys.exit(1)

print()
print("Step 3: Verifying changes...")
print("-" * 70)

with app.app_context():
    # Verify the changes
    all_ok = True
    
    if check_column_exists('prizes', 'minimum_level'):
        print("✓ Column 'prizes.minimum_level' verified")
    else:
        print("❌ Column 'prizes.minimum_level' still missing!")
        all_ok = False
    
    if check_table_exists('prize_school_requests'):
        print("✓ Table 'prize_school_requests' verified")
    else:
        print("❌ Table 'prize_school_requests' still missing!")
        all_ok = False
    
    print()
    
    if all_ok:
        print("=" * 70)
        print("✓✓✓ ALL CHECKS PASSED! ✓✓✓")
        print("=" * 70)
        print()
        print("Next steps:")
        print()
        print("1. Reload your web app in PythonAnywhere:")
        print("   Web → Reload button")
        print()
        print("2. Test the prize shop:")
        print("   Visit /prizes as a student")
        print()
        print("3. If you see 'No prizes available', add prizes:")
        print("   Go to /admin/prizes")
        print()
        print("4. Add schools if needed:")
        print("   Go to /admin/prizes → Schools tab")
        print()
    else:
        print("=" * 70)
        print("⚠️ VERIFICATION FAILED")
        print("=" * 70)
        print("Some changes were not applied. Check the errors above.")
        sys.exit(1)
