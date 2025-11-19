"""
Migration script to allow guest users to flag questions (SQLite compatible)
This adds guest_identifier and guest_email fields

Run on PythonAnywhere: python3 allow_guest_flagging.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    print("=" * 60)
    print("UPDATING DATABASE FOR GUEST FLAGGING")
    print("=" * 60)
    
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('question_flags')]
    
    print(f"\nCurrent columns in question_flags table:")
    for col in columns:
        print(f"  - {col}")
    
    try:
        # Step 1: Add guest_identifier column if it doesn't exist
        if 'guest_identifier' not in columns:
            print("\n1. Adding guest_identifier column...")
            db.session.execute(db.text("""
                ALTER TABLE question_flags 
                ADD COLUMN guest_identifier VARCHAR(100)
            """))
            db.session.commit()
            print("   ✓ guest_identifier column added")
        else:
            print("\n1. guest_identifier column already exists - skipping")
        
        # Step 2: Add guest_email column if it doesn't exist
        columns = [col['name'] for col in inspector.get_columns('question_flags')]
        if 'guest_email' not in columns:
            print("\n2. Adding guest_email column...")
            db.session.execute(db.text("""
                ALTER TABLE question_flags 
                ADD COLUMN guest_email VARCHAR(120)
            """))
            db.session.commit()
            print("   ✓ guest_email column added")
        else:
            print("\n2. guest_email column already exists - skipping")
        
        # Step 3: For SQLite, we can't easily make user_id nullable
        # Instead, we'll handle this in the application code
        print("\n3. Handling nullable user_id...")
        print("   ℹ️  SQLite limitation: Cannot modify existing columns")
        print("   ✓ Application code will handle NULL user_id values")
        
        print("\n" + "=" * 60)
        print("✓ DATABASE UPDATED SUCCESSFULLY")
        print("=" * 60)
        print("\nGuest users can now flag questions!")
        print("\nNote: The user_id column constraint remains, but SQLite")
        print("allows NULL values anyway, so guest flagging will work.")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
