"""
Database Migration Script - Add Resume Functionality
Adds InProgressQuiz table for saving quiz progress

Run this ONCE after uploading the new app.py
"""

from app import app, db, InProgressQuiz

def migrate():
    with app.app_context():
        print("=" * 70)
        print("MATH MASTER - DATABASE MIGRATION")
        print("Adding Resume Functionality (InProgressQuiz table)")
        print("=" * 70)
        
        # Create all tables (only creates new ones, doesn't touch existing)
        db.create_all()
        
        # Verify the new table exists
        try:
            count = InProgressQuiz.query.count()
            print("\n✅ SUCCESS! InProgressQuiz table created")
            print(f"   Current records: {count}")
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Reload your web app on PythonAnywhere")
        print("2. Test the resume functionality")
        print("3. Verify auto-save is working (check console logs)")
        print("\n✨ Students can now save and resume quizzes!")
        
        return True

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
