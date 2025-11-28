#!/usr/bin/env python3
"""
Migration: Ensure all users (including guests) have UserStats records
This fixes the "0 Points" display issue
"""
import sys
import os

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'

from app import app, db, User, UserStats
from sqlalchemy import text

print("=" * 80)
print("MIGRATION: Ensure UserStats for All Users")
print("=" * 80)
print()

with app.app_context():
    try:
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users")
        
        # Check each user for UserStats
        missing_stats = 0
        created_stats = 0
        
        for user in users:
            stats = UserStats.query.filter_by(user_id=user.id).first()
            if not stats:
                missing_stats += 1
                print(f"  Creating UserStats for user {user.id} ({user.email})...")
                
                # Create UserStats record
                new_stats = UserStats(
                    user_id=user.id,
                    total_points=0,
                    level=1,
                    total_quizzes=0,
                    total_questions_answered=0,
                    total_correct_answers=0
                )
                db.session.add(new_stats)
                created_stats += 1
        
        if created_stats > 0:
            db.session.commit()
            print(f"\n✓ Created {created_stats} UserStats records")
        else:
            print("\n✓ All users already have UserStats")
        
        # Also add default_school_id column if needed
        print("\nAdding default_school_id column...")
        try:
            db.session.execute(text("""
                ALTER TABLE users ADD COLUMN default_school_id INTEGER
            """))
            db.session.commit()
            print("✓ Column added")
        except Exception as e:
            if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                print("✓ Column already exists")
            else:
                print(f"Note: {e}")
        
        print()
        print("=" * 80)
        print("✓ MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Summary:")
        print(f"  - Total users: {len(users)}")
        print(f"  - UserStats created: {created_stats}")
        print(f"  - default_school_id column: Ready")
        print()
        print("Prize shop should now display points correctly!")
        print()
        
    except Exception as e:
        db.session.rollback()
        print()
        print("=" * 80)
        print("✗ ERROR")
        print("=" * 80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
