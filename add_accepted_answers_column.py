#!/usr/bin/env python3
"""
Add accepted_answers column to who_am_i_images table
Stores JSON array of acceptable answer variants
"""
import sys
import os

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("WHO AM I - ADD ACCEPTED_ANSWERS COLUMN")
print("=" * 80)
print()

with app.app_context():
    try:
        # Check if column already exists
        result = db.session.execute(text("PRAGMA table_info(who_am_i_images)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'accepted_answers' in columns:
            print("✓ Column 'accepted_answers' already exists")
        else:
            print("Adding 'accepted_answers' column...")
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE who_am_i_images 
                ADD COLUMN accepted_answers TEXT
            """))
            
            db.session.commit()
            print("✓ Column 'accepted_answers' added successfully")
        
        print()
        print("=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Run: python analyze_who_am_i_answers.py")
        print("2. Review the generated variants")
        print("3. Run the SQL update script to populate variants")
        print("4. Update the guess checking logic")
        print()
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)
