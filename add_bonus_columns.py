#!/usr/bin/env python3
"""
ADD BONUS COLUMNS TO GUEST_QUIZ_ATTEMPTS
=========================================
This script adds who_am_i_bonus and milestone_points columns
to the guest_quiz_attempts table so we can track max points per quiz.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python add_bonus_columns.py
"""

import sqlite3
import os

DB_PATH = 'instance/mathquiz.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ADDING BONUS COLUMNS TO GUEST_QUIZ_ATTEMPTS")
    print("=" * 60)
    
    # Check current columns
    cursor.execute("PRAGMA table_info(guest_quiz_attempts)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nCurrent columns: {columns}")
    
    # Add who_am_i_bonus if not exists
    if 'who_am_i_bonus' not in columns:
        try:
            cursor.execute("""
                ALTER TABLE guest_quiz_attempts 
                ADD COLUMN who_am_i_bonus INTEGER DEFAULT 0
            """)
            print("✓ Added who_am_i_bonus column")
        except Exception as e:
            print(f"⚠ Could not add who_am_i_bonus: {e}")
    else:
        print("✓ who_am_i_bonus column already exists")
    
    # Add milestone_points if not exists
    if 'milestone_points' not in columns:
        try:
            cursor.execute("""
                ALTER TABLE guest_quiz_attempts 
                ADD COLUMN milestone_points INTEGER DEFAULT 0
            """)
            print("✓ Added milestone_points column")
        except Exception as e:
            print(f"⚠ Could not add milestone_points: {e}")
    else:
        print("✓ milestone_points column already exists")
    
    # Add total_points computed column (for convenience)
    # Note: SQLite doesn't support computed columns, so we'll calculate in queries
    
    conn.commit()
    
    # Verify
    cursor.execute("PRAGMA table_info(guest_quiz_attempts)")
    columns = cursor.fetchall()
    print("\n" + "=" * 60)
    print("UPDATED TABLE STRUCTURE")
    print("=" * 60)
    for col in columns:
        print(f"  {col[1]}: {col[2]} (default: {col[4]})")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print("""
The guest_quiz_attempts table now has:
- who_am_i_bonus: Points earned from Who Am I game
- milestone_points: Points earned from in-quiz milestones

Future quiz completions will store these values.
Existing records will have 0 for these columns.

Reload your web app to start tracking bonus points!
""")

if __name__ == '__main__':
    main()
