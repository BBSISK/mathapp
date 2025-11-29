#!/usr/bin/env python3
"""
Fix missing hint_view_count column in weekly_puzzles table.

Run this on PythonAnywhere:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python fix_puzzle_table.py
"""

import sys
import os

# Add the app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db
from sqlalchemy import text

def fix_puzzle_table():
    with app.app_context():
        print("Checking weekly_puzzles table...")
        
        # Check current columns
        columns = db.session.execute(text("PRAGMA table_info(weekly_puzzles)")).fetchall()
        column_names = [col[1] for col in columns]
        print(f"Current columns: {column_names}")
        
        # Add hint_view_count if missing
        if 'hint_view_count' not in column_names:
            print("Adding hint_view_count column...")
            db.session.execute(text("""
                ALTER TABLE weekly_puzzles 
                ADD COLUMN hint_view_count INTEGER DEFAULT 0
            """))
            db.session.commit()
            print("✓ hint_view_count column added!")
        else:
            print("✓ hint_view_count column already exists")
        
        # Verify
        columns = db.session.execute(text("PRAGMA table_info(weekly_puzzles)")).fetchall()
        column_names = [col[1] for col in columns]
        print(f"\nFinal columns: {column_names}")
        print("\n✅ Table fix complete!")

if __name__ == '__main__':
    fix_puzzle_table()
