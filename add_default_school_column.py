#!/usr/bin/env python3
"""
Database Migration: Add default_school_id column to users table
This allows school selection to persist across sessions
"""
import sys
import os

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("DATABASE MIGRATION: Add default_school_id Column")
print("=" * 80)
print()

with app.app_context():
    try:
        print("Adding default_school_id column to users table...")
        
        db.session.execute(text("""
            ALTER TABLE users ADD COLUMN default_school_id INTEGER
        """))
        db.session.commit()
        
        print("✓ Column added successfully!")
        print()
        print("=" * 80)
        print("✓ MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print("Users can now have a persistent default school selection.")
        print()
        
    except Exception as e:
        if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
            print("✓ Column already exists - nothing to do!")
        else:
            print()
            print("=" * 80)
            print("✗ ERROR")
            print("=" * 80)
            print(f"\n{e}\n")
            import traceback
            traceback.print_exc()
            sys.exit(1)
