"""
PROGRESS TRACKING & BADGES SYSTEM - DATABASE MIGRATION

This script adds progress tracking and achievement badges to the math app.

SAFE TO RUN:
- Creates new tables (doesn't modify existing ones)
- Idempotent (can run multiple times safely)
- Includes rollback function

Run this ONCE to add badges feature:
    python badges_migration.py migrate

To rollback (remove badges tables):
    python badges_migration.py rollback
"""

from app import app, db
from sqlalchemy import text
import sys

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with app.app_context():
        result = db.session.execute(text(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )).fetchone()
        return result is not None

def migrate_badges_tables():
    """Add badges and progress tracking tables to database"""
    
    with app.app_context():
        print("🚀 Starting Badges & Progress System Migration...")
        print("-" * 50)
        
        # Check if tables already exist
        if check_table_exists('badges'):
            print("⚠️  Badges tables already exist!")
            print("   Run 'python badges_migration.py rollback' first if you want to recreate them.")
            return False
        
        try:
            # Create badges definition table
            print("📝 Creating badges table...")
            db.session.execute(text("""
                CREATE TABLE badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    icon VARCHAR(50) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    requirement_type VARCHAR(50) NOT NULL,
                    requirement_value INTEGER NOT NULL,
                    points INTEGER DEFAULT 10,
                    color VARCHAR(50) DEFAULT 'blue',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create user_badges (earned badges) table
            print("📝 Creating user_badges table...")
            db.session.execute(text("""
                CREATE TABLE user_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    badge_id INTEGER NOT NULL,
                    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    progress INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
                    UNIQUE(user_id, badge_id)
                )
            """))
            
            # Create user_stats table for detailed progress tracking
            print("📝 Creating user_stats table...")
            db.session.execute(text("""
                CREATE TABLE user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    total_quizzes INTEGER DEFAULT 0,
                    total_questions_answered INTEGER DEFAULT 0,
                    total_correct_answers INTEGER DEFAULT 0,
                    current_streak_days INTEGER DEFAULT 0,
                    longest_streak_days INTEGER DEFAULT 0,
                    last_quiz_date DATE,
                    total_points INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    topics_mastered INTEGER DEFAULT 0,
                    perfect_scores INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            # Create topic_progress table for per-topic tracking
            print("📝 Creating topic_progress table...")
            db.session.execute(text("""
                CREATE TABLE topic_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(20) NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    best_percentage FLOAT DEFAULT 0,
                    total_questions_answered INTEGER DEFAULT 0,
                    total_correct INTEGER DEFAULT 0,
                    is_mastered BOOLEAN DEFAULT 0,
                    last_attempt_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, topic, difficulty)
                )
            """))
            
            # Create indexes for better performance
            print("📝 Creating indexes...")
            db.session.execute(text("""
                CREATE INDEX idx_user_badges_user ON user_badges(user_id)
            """))
            db.session.execute(text("""
                CREATE INDEX idx_user_badges_badge ON user_badges(badge_id)
            """))
            db.session.execute(text("""
                CREATE INDEX idx_user_stats_user ON user_stats(user_id)
            """))
            db.session.execute(text("""
                CREATE INDEX idx_topic_progress_user ON topic_progress(user_id)
            """))
            db.session.execute(text("""
                CREATE INDEX idx_topic_progress_topic ON topic_progress(topic, difficulty)
            """))
            
            db.session.commit()
            
            # Insert default badges
            print("📝 Creating default badges...")
            insert_default_badges()
            
            print("✅ Migration completed successfully!")
            print("-" * 50)
            print("\n📊 Database changes:")
            print("   ✓ Created table: badges (badge definitions)")
            print("   ✓ Created table: user_badges (earned badges)")
            print("   ✓ Created table: user_stats (progress tracking)")
            print("   ✓ Created table: topic_progress (per-topic progress)")
            print("   ✓ Created 5 indexes for performance")
            print("   ✓ Added 15 default badges")
            print("\n🎉 Badges & Progress System is now active!")
            print("\nNext steps:")
            print("   1. Upload the modified app.py")
            print("   2. Upload the modified student_app.html")
            print("   3. Reload your web app")
            print("   4. Students will start earning badges!")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            print("\n⚠️  Rolling back changes...")
            rollback_badges_tables()
            return False

def insert_default_badges():
    """Insert default badge definitions"""
    
    badges_data = [
        # Getting Started Badges
        {"name": "First Steps", "description": "Complete your first quiz", "icon": "fa-star", "category": "beginner", "requirement_type": "quizzes_completed", "requirement_value": 1, "points": 10, "color": "yellow"},
        {"name": "Curious Learner", "description": "Complete 5 quizzes", "icon": "fa-book", "category": "beginner", "requirement_type": "quizzes_completed", "requirement_value": 5, "points": 20, "color": "blue"},
        {"name": "Dedicated Student", "description": "Complete 10 quizzes", "icon": "fa-graduation-cap", "category": "progress", "requirement_type": "quizzes_completed", "requirement_value": 10, "points": 30, "color": "purple"},
        {"name": "Math Enthusiast", "description": "Complete 25 quizzes", "icon": "fa-heart", "category": "progress", "requirement_type": "quizzes_completed", "requirement_value": 25, "points": 50, "color": "red"},
        {"name": "Quiz Master", "description": "Complete 50 quizzes", "icon": "fa-trophy", "category": "progress", "requirement_type": "quizzes_completed", "requirement_value": 50, "points": 100, "color": "gold"},
        
        # Accuracy Badges
        {"name": "Sharp Shooter", "description": "Get 80%+ on any quiz", "icon": "fa-bullseye", "category": "accuracy", "requirement_type": "quiz_percentage", "requirement_value": 80, "points": 15, "color": "orange"},
        {"name": "Perfectionist", "description": "Get 100% on any quiz", "icon": "fa-crown", "category": "accuracy", "requirement_type": "perfect_scores", "requirement_value": 1, "points": 25, "color": "gold"},
        {"name": "Consistent Excellence", "description": "Get 90%+ on 5 quizzes", "icon": "fa-medal", "category": "accuracy", "requirement_type": "high_scores", "requirement_value": 5, "points": 50, "color": "silver"},
        {"name": "Flawless Five", "description": "Get 100% on 5 quizzes", "icon": "fa-gem", "category": "accuracy", "requirement_type": "perfect_scores", "requirement_value": 5, "points": 100, "color": "diamond"},
        
        # Streak Badges
        {"name": "Daily Habit", "description": "Practice 3 days in a row", "icon": "fa-fire", "category": "streak", "requirement_type": "streak_days", "requirement_value": 3, "points": 20, "color": "orange"},
        {"name": "Week Warrior", "description": "Practice 7 days in a row", "icon": "fa-bolt", "category": "streak", "requirement_type": "streak_days", "requirement_value": 7, "points": 40, "color": "yellow"},
        {"name": "Unstoppable", "description": "Practice 14 days in a row", "icon": "fa-rocket", "category": "streak", "requirement_type": "streak_days", "requirement_value": 14, "points": 75, "color": "red"},
        
        # Mastery Badges
        {"name": "Topic Master", "description": "Master any topic (3 levels)", "icon": "fa-certificate", "category": "mastery", "requirement_type": "topics_mastered", "requirement_value": 1, "points": 30, "color": "green"},
        {"name": "Subject Expert", "description": "Master 3 different topics", "icon": "fa-brain", "category": "mastery", "requirement_type": "topics_mastered", "requirement_value": 3, "points": 75, "color": "purple"},
        {"name": "Mathematics Genius", "description": "Master 5 different topics", "icon": "fa-infinity", "category": "mastery", "requirement_type": "topics_mastered", "requirement_value": 5, "points": 150, "color": "rainbow"},
    ]
    
    for badge in badges_data:
        db.session.execute(text("""
            INSERT INTO badges (name, description, icon, category, requirement_type, requirement_value, points, color)
            VALUES (:name, :description, :icon, :category, :requirement_type, :requirement_value, :points, :color)
        """), badge)
    
    db.session.commit()
    print(f"   ✓ Inserted {len(badges_data)} default badges")

def rollback_badges_tables():
    """Remove badges and progress tracking tables from database"""
    
    with app.app_context():
        print("🔄 Starting Badges System Rollback...")
        print("-" * 50)
        
        # Check if tables exist
        if not check_table_exists('badges'):
            print("✅ No badges tables found - nothing to rollback")
            return True
        
        try:
            # Drop indexes first
            print("📝 Dropping indexes...")
            indexes = [
                'idx_user_badges_user',
                'idx_user_badges_badge',
                'idx_user_stats_user',
                'idx_topic_progress_user',
                'idx_topic_progress_topic'
            ]
            for idx in indexes:
                try:
                    db.session.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                except:
                    pass
            
            # Drop tables (order matters due to foreign keys)
            print("📝 Dropping tables...")
            db.session.execute(text("DROP TABLE IF EXISTS topic_progress"))
            db.session.execute(text("DROP TABLE IF EXISTS user_stats"))
            db.session.execute(text("DROP TABLE IF EXISTS user_badges"))
            db.session.execute(text("DROP TABLE IF EXISTS badges"))
            
            db.session.commit()
            
            print("✅ Rollback completed successfully!")
            print("-" * 50)
            print("\n📊 Database changes:")
            print("   ✓ Removed table: badges")
            print("   ✓ Removed table: user_badges")
            print("   ✓ Removed table: user_stats")
            print("   ✓ Removed table: topic_progress")
            print("   ✓ Removed all badges indexes")
            print("\n✅ Badges & Progress System has been removed")
            print("   Your app is back to its previous state")
            print("\n⚠️  Note: Any badges data has been deleted")
            print("   BUT: Quiz attempts and scores are preserved!")
            
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            db.session.rollback()
            return False

def verify_migration():
    """Verify badges tables exist and are properly structured"""
    
    with app.app_context():
        print("🔍 Verifying Badges System Installation...")
        print("-" * 50)
        
        tables = ['badges', 'user_badges', 'user_stats', 'topic_progress']
        all_exist = True
        
        for table in tables:
            exists = check_table_exists(table)
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}': {'EXISTS' if exists else 'MISSING'}")
            if not exists:
                all_exist = False
        
        if all_exist:
            # Count badges and user data
            badge_count = db.session.execute(text(
                "SELECT COUNT(*) FROM badges"
            )).scalar()
            earned_count = db.session.execute(text(
                "SELECT COUNT(*) FROM user_badges"
            )).scalar()
            stats_count = db.session.execute(text(
                "SELECT COUNT(*) FROM user_stats"
            )).scalar()
            
            print("\n📊 Current badges data:")
            print(f"   • Total badge types: {badge_count}")
            print(f"   • Badges earned by users: {earned_count}")
            print(f"   • Users with stats: {stats_count}")
            print("\n✅ Badges System is properly installed!")
        else:
            print("\n❌ Badges System is NOT installed")
            print("   Run: python badges_migration.py migrate")
        
        return all_exist

def show_help():
    """Show usage instructions"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       PROGRESS TRACKING & BADGES SYSTEM - MIGRATION TOOL      ║
╚══════════════════════════════════════════════════════════════╝

USAGE:
    python badges_migration.py [command]

COMMANDS:
    migrate     Add badges system to database (safe to run)
    rollback    Remove badges system from database  
    verify      Check if badges system is installed
    help        Show this help message

EXAMPLES:
    # Install badges system
    python badges_migration.py migrate

    # Check installation status
    python badges_migration.py verify

    # Remove badges system (if needed)
    python badges_migration.py rollback

SAFETY:
    ✓ Migration is idempotent (safe to run multiple times)
    ✓ Creates NEW tables only (doesn't modify existing ones)
    ✓ Rollback completely removes badges feature
    ✓ Your existing data (quiz attempts, scores) is never touched

WHAT GETS ADDED:
    • badges table (15 default badges)
    • user_badges table (tracks earned badges)
    • user_stats table (overall progress tracking)
    • topic_progress table (per-topic mastery tracking)
    • 5 database indexes (improves performance)

DEFAULT BADGES INCLUDED:
    Beginner Badges:
    • First Steps (1 quiz)
    • Curious Learner (5 quizzes)
    • Dedicated Student (10 quizzes)
    
    Accuracy Badges:
    • Sharp Shooter (80%+)
    • Perfectionist (100%)
    • Flawless Five (5 perfect scores)
    
    Streak Badges:
    • Daily Habit (3 days)
    • Week Warrior (7 days)
    • Unstoppable (14 days)
    
    Mastery Badges:
    • Topic Master (master 1 topic)
    • Subject Expert (master 3 topics)
    • Mathematics Genius (master 5 topics)

ROLLBACK PLAN:
    If anything goes wrong or you want to remove the feature:
    1. Run: python badges_migration.py rollback
    2. All badges tables will be removed
    3. App returns to previous state
    4. Quiz attempts and scores are preserved
    5. Users won't see badges anymore

SUPPORT:
    Check BADGES_SYSTEM_GUIDE.md for complete documentation
    """)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ No command specified")
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'migrate':
        success = migrate_badges_tables()
        sys.exit(0 if success else 1)
    
    elif command == 'rollback':
        confirm = input("⚠️  This will DELETE all badges data. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            success = rollback_badges_tables()
            sys.exit(0 if success else 1)
        else:
            print("❌ Rollback cancelled")
            sys.exit(1)
    
    elif command == 'verify':
        success = verify_migration()
        sys.exit(0 if success else 1)
    
    elif command == 'help':
        show_help()
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)
