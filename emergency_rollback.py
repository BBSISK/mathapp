"""
BADGES SYSTEM - EMERGENCY ROLLBACK SCRIPT

Use this if badges_migration.py rollback doesn't work.

This script will:
1. Remove all badges tables
2. Restore original app.py (if backup exists)
3. Clean up completely

Run: python3 emergency_rollback.py
"""

from app import app, db
from sqlalchemy import text
import os
import shutil

def emergency_rollback():
    """Complete rollback of badges system"""
    
    print("=" * 60)
    print("🚨 EMERGENCY ROLLBACK - BADGES SYSTEM")
    print("=" * 60)
    print()
    
    confirm = input("This will remove ALL badges data. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Rollback cancelled")
        return False
    
    print("\n🔄 Starting emergency rollback...")
    print("-" * 60)
    
    success_count = 0
    total_steps = 6
    
    # Step 1: Remove topic_progress table
    try:
        print("1/6 Removing topic_progress table...")
        with app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS topic_progress"))
            db.session.commit()
        print("    ✅ Removed topic_progress")
        success_count += 1
    except Exception as e:
        print(f"    ⚠️  Error (might not exist): {e}")
    
    # Step 2: Remove user_stats table
    try:
        print("2/6 Removing user_stats table...")
        with app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS user_stats"))
            db.session.commit()
        print("    ✅ Removed user_stats")
        success_count += 1
    except Exception as e:
        print(f"    ⚠️  Error (might not exist): {e}")
    
    # Step 3: Remove user_badges table
    try:
        print("3/6 Removing user_badges table...")
        with app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS user_badges"))
            db.session.commit()
        print("    ✅ Removed user_badges")
        success_count += 1
    except Exception as e:
        print(f"    ⚠️  Error (might not exist): {e}")
    
    # Step 4: Remove badges table
    try:
        print("4/6 Removing badges table...")
        with app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS badges"))
            db.session.commit()
        print("    ✅ Removed badges")
        success_count += 1
    except Exception as e:
        print(f"    ⚠️  Error (might not exist): {e}")
    
    # Step 5: Restore app.py backup if exists
    try:
        print("5/6 Restoring app.py from backup...")
        if os.path.exists('app.py.backup'):
            shutil.copy2('app.py.backup', 'app.py')
            print("    ✅ Restored app.py from backup")
            success_count += 1
        else:
            print("    ⚠️  No app.py.backup found - skipping")
    except Exception as e:
        print(f"    ❌ Error restoring app.py: {e}")
    
    # Step 6: Restore student_app.html backup if exists
    try:
        print("6/6 Restoring student_app.html from backup...")
        if os.path.exists('templates/student_app.html.backup'):
            shutil.copy2('templates/student_app.html.backup', 'templates/student_app.html')
            print("    ✅ Restored student_app.html from backup")
            success_count += 1
        else:
            print("    ⚠️  No student_app.html.backup found - skipping")
    except Exception as e:
        print(f"    ❌ Error restoring student_app.html: {e}")
    
    print()
    print("-" * 60)
    print(f"✅ Rollback complete: {success_count}/{total_steps} steps successful")
    print()
    
    if success_count >= 4:
        print("🎉 Emergency rollback successful!")
        print()
        print("Next steps:")
        print("  1. Reload your web app (PythonAnywhere Web tab)")
        print("  2. Test that app works normally")
        print("  3. Badges system is now completely removed")
        print()
        print("⚠️  Note: All badges data has been deleted")
        print("   BUT: Quiz attempts and scores are preserved!")
    else:
        print("⚠️  Rollback partially complete")
        print()
        print("Manual cleanup needed:")
        print("  1. Check which tables still exist:")
        print("     python3 -c \"from app import app, db; from sqlalchemy import text; \\")
        print("               with app.app_context(): \\")
        print("               result = db.session.execute(text(\\")
        print("               'SELECT name FROM sqlite_master WHERE type=\\\"table\\\"')); \\")
        print("               print([r[0] for r in result])\"")
        print()
        print("  2. Manually drop any remaining badges tables")
        print("  3. Contact support if needed")
    
    return success_count >= 4

def verify_rollback():
    """Verify that badges tables are gone"""
    print()
    print("🔍 Verifying rollback...")
    print("-" * 60)
    
    tables_to_check = ['badges', 'user_badges', 'user_stats', 'topic_progress']
    all_gone = True
    
    with app.app_context():
        for table in tables_to_check:
            result = db.session.execute(text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )).fetchone()
            
            if result:
                print(f"❌ Table '{table}' still exists!")
                all_gone = False
            else:
                print(f"✅ Table '{table}' removed")
    
    print()
    if all_gone:
        print("✅ All badges tables successfully removed!")
    else:
        print("⚠️  Some tables still exist - may need manual cleanup")
    
    return all_gone

if __name__ == '__main__':
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  BADGES SYSTEM - EMERGENCY ROLLBACK SCRIPT".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    print("This script will completely remove the badges system.")
    print()
    print("⚠️  WARNING: This will delete:")
    print("   • All badges tables (badges, user_badges, user_stats, topic_progress)")
    print("   • All earned badges data")
    print("   • All progress tracking data")
    print()
    print("✅ This will NOT delete:")
    print("   • Quiz attempts")
    print("   • User scores")
    print("   • Questions")
    print("   • Classes")
    print("   • User accounts")
    print()
    
    if emergency_rollback():
        verify_rollback()
        print()
        print("=" * 60)
        print("🎉 EMERGENCY ROLLBACK COMPLETE!")
        print("=" * 60)
        print()
        print("Remember to:")
        print("  1. Reload your web app")
        print("  2. Test that everything works")
        print("  3. Clear browser cache if needed")
        print()
    else:
        print()
        print("=" * 60)
        print("⚠️  ROLLBACK INCOMPLETE")
        print("=" * 60)
        print()
        print("Please check error messages above and try manual cleanup.")
        print()
