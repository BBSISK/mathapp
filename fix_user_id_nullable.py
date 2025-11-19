"""
SQLite migration to make user_id nullable in question_flags table
This recreates the table with the correct schema

Run on PythonAnywhere: python3 fix_user_id_nullable.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db
from sqlalchemy import text

with app.app_context():
    print("=" * 60)
    print("MAKING user_id NULLABLE IN question_flags")
    print("=" * 60)
    
    try:
        # Step 1: Create a new table with the correct schema
        print("\n1. Creating new table with nullable user_id...")
        db.session.execute(text("""
            CREATE TABLE question_flags_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_id INTEGER,  -- NOW NULLABLE!
                guest_identifier VARCHAR(100),
                guest_email VARCHAR(120),
                flag_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                admin_notes TEXT,
                created_at DATETIME,
                resolved_at DATETIME,
                resolved_by INTEGER,
                FOREIGN KEY (question_id) REFERENCES questions(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (resolved_by) REFERENCES users(id)
            )
        """))
        print("   ✓ New table created")
        
        # Step 2: Copy data from old table to new table
        print("\n2. Copying existing data...")
        db.session.execute(text("""
            INSERT INTO question_flags_new 
            (id, question_id, user_id, guest_identifier, guest_email, flag_type, 
             description, status, admin_notes, created_at, resolved_at, resolved_by)
            SELECT 
                id, question_id, user_id, guest_identifier, guest_email, flag_type,
                description, status, admin_notes, created_at, resolved_at, resolved_by
            FROM question_flags
        """))
        count = db.session.execute(text("SELECT COUNT(*) FROM question_flags_new")).scalar()
        print(f"   ✓ Copied {count} existing flags")
        
        # Step 3: Drop old table
        print("\n3. Removing old table...")
        db.session.execute(text("DROP TABLE question_flags"))
        print("   ✓ Old table removed")
        
        # Step 4: Rename new table to original name
        print("\n4. Renaming new table...")
        db.session.execute(text("ALTER TABLE question_flags_new RENAME TO question_flags"))
        print("   ✓ Table renamed")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✓ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\nuser_id is now nullable - guest flagging will work!")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING:")
        print("=" * 60)
        print("If you see an error about 'table already exists', run:")
        print("  DROP TABLE question_flags_new;")
        print("in your SQLite database and try again.")
