"""
User Question History Migration Script
======================================

This script creates the user_question_history table which tracks
which questions each user has seen. This prevents duplicate questions
in quizzes.

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python migrate_question_history.py
"""

from app import app, db
from sqlalchemy import text

def migrate_question_history():
    with app.app_context():
        print("=" * 60)
        print("🔄 USER QUESTION HISTORY MIGRATION")
        print("=" * 60)
        
        # Check if table exists
        existing = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_question_history'"
        )).fetchone()
        
        if existing:
            print("\n✓ 'user_question_history' table already exists")
            
            # Show current stats
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM user_question_history"
            )).fetchone()[0]
            print(f"   Current records: {count}")
        else:
            print("\n📋 Creating 'user_question_history' table...")
            
            db.session.execute(text("""
                CREATE TABLE user_question_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guest_code VARCHAR(20),
                    question_id INTEGER NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(20) NOT NULL,
                    seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """))
            
            print("   ✓ Table created")
            
            # Create indexes for fast lookups
            print("\n📋 Creating indexes...")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX idx_user_question 
                    ON user_question_history(user_id, question_id)
                """))
                print("   ✓ Index idx_user_question created")
            except Exception as e:
                print(f"   Note: idx_user_question may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX idx_guest_question 
                    ON user_question_history(guest_code, question_id)
                """))
                print("   ✓ Index idx_guest_question created")
            except Exception as e:
                print(f"   Note: idx_guest_question may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX idx_user_topic_diff 
                    ON user_question_history(user_id, topic, difficulty)
                """))
                print("   ✓ Index idx_user_topic_diff created")
            except Exception as e:
                print(f"   Note: idx_user_topic_diff may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX idx_guest_topic_diff 
                    ON user_question_history(guest_code, topic, difficulty)
                """))
                print("   ✓ Index idx_guest_topic_diff created")
            except Exception as e:
                print(f"   Note: idx_guest_topic_diff may already exist: {e}")
            
            # Create unique constraint to prevent duplicate entries
            try:
                db.session.execute(text("""
                    CREATE UNIQUE INDEX idx_unique_user_question 
                    ON user_question_history(user_id, question_id) 
                    WHERE user_id IS NOT NULL
                """))
                print("   ✓ Unique index for user questions created")
            except Exception as e:
                print(f"   Note: Unique index may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE UNIQUE INDEX idx_unique_guest_question 
                    ON user_question_history(guest_code, question_id)
                    WHERE guest_code IS NOT NULL
                """))
                print("   ✓ Unique index for guest questions created")
            except Exception as e:
                print(f"   Note: Unique index may already exist: {e}")
            
            db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nHow it works:")
        print("  • When a user starts a quiz, questions they've already seen")
        print("    for that topic/difficulty are excluded")
        print("  • If all questions have been seen, history is reset")
        print("  • Quiz may have fewer than 25 questions if not enough unseen")
        print("  • Works for both registered users and guest users")

if __name__ == '__main__':
    migrate_question_history()
