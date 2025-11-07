"""
Student Dashboard Loading Error - Diagnostic & Fix Script
Run this script to diagnose and fix common issues
"""

from app import app, db, User, UserStats, Badge
from datetime import datetime

def diagnose_user(email):
    """Diagnose issues for a specific student"""
    print(f"\n{'='*60}")
    print(f"DIAGNOSING USER: {email}")
    print('='*60)
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ ERROR: User '{email}' not found in database")
            print("\nSolutions:")
            print("1. Check email spelling")
            print("2. Register the user first")
            return False
        
        print(f"✅ User found: {user.full_name}")
        print(f"   ID: {user.id}")
        print(f"   Role: {user.role}")
        print(f"   Approved: {user.is_approved}")
        print(f"   Created: {user.created_at}")
        
        # Check if student is approved
        if user.role == 'student' and not user.is_approved:
            print("\n⚠️  WARNING: Student is not approved")
            print("   This should not happen - students are auto-approved")
            fix = input("\n   Fix this now? (y/n): ")
            if fix.lower() == 'y':
                user.is_approved = True
                db.session.commit()
                print("   ✅ Student approved!")
        
        # Check for UserStats
        print("\n" + "-"*60)
        print("Checking UserStats...")
        stats = UserStats.query.filter_by(user_id=user.id).first()
        
        if not stats:
            print("❌ ERROR: No UserStats record found")
            fix = input("\n   Create UserStats now? (y/n): ")
            if fix.lower() == 'y':
                stats = UserStats(
                    user_id=user.id,
                    total_quizzes=0,
                    total_questions_answered=0,
                    total_correct_answers=0,
                    current_streak_days=0,
                    longest_streak_days=0,
                    total_points=0,
                    level=1,
                    topics_mastered=0,
                    perfect_scores=0
                )
                db.session.add(stats)
                db.session.commit()
                print("   ✅ UserStats created!")
        else:
            print(f"✅ UserStats found")
            print(f"   Level: {stats.level}")
            print(f"   Total Quizzes: {stats.total_quizzes}")
            print(f"   Accuracy: {(stats.total_correct_answers / stats.total_questions_answered * 100) if stats.total_questions_answered > 0 else 0:.1f}%")
        
        # Check for badges
        print("\n" + "-"*60)
        print("Checking Badges...")
        badge_count = Badge.query.count()
        
        if badge_count == 0:
            print("⚠️  WARNING: No badges in database")
            print("   This is OK, but students won't earn badges")
            print("   Consider adding badges via admin panel")
        else:
            print(f"✅ {badge_count} badges found in system")
            user_badge_count = len(user.earned_badges)
            print(f"   User has earned: {user_badge_count} badges")
        
        # Check quiz attempts
        print("\n" + "-"*60)
        print("Checking Quiz History...")
        quiz_count = len(user.quiz_attempts)
        print(f"   Total quiz attempts: {quiz_count}")
        
        if quiz_count > 0:
            recent = sorted(user.quiz_attempts, key=lambda x: x.completed_at, reverse=True)[:5]
            print("\n   Recent attempts:")
            for qa in recent:
                print(f"   - {qa.topic} ({qa.difficulty}): {qa.percentage}% on {qa.completed_at.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "="*60)
        print("DIAGNOSIS COMPLETE")
        print("="*60)
        
        return True

def check_database():
    """Check overall database health"""
    print("\n{'='*60}")
    print("DATABASE HEALTH CHECK")
    print('='*60)
    
    with app.app_context():
        # Check if tables exist
        try:
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} users")
        except Exception as e:
            print(f"❌ Users table error: {e}")
            return False
        
        try:
            stats_count = UserStats.query.count()
            print(f"✅ UserStats table: {stats_count} records")
        except Exception as e:
            print(f"❌ UserStats table error: {e}")
            return False
        
        try:
            badge_count = Badge.query.count()
            print(f"✅ Badges table: {badge_count} badges")
        except Exception as e:
            print(f"❌ Badges table error: {e}")
            return False
        
        # Check for orphaned users (no stats)
        orphaned = User.query.filter(
            ~User.id.in_(db.session.query(UserStats.user_id))
        ).all()
        
        if orphaned:
            print(f"\n⚠️  Found {len(orphaned)} users without UserStats:")
            for user in orphaned:
                print(f"   - {user.email} (ID: {user.id})")
            
            fix = input("\n   Create UserStats for these users? (y/n): ")
            if fix.lower() == 'y':
                for user in orphaned:
                    stats = UserStats(
                        user_id=user.id,
                        total_quizzes=0,
                        total_questions_answered=0,
                        total_correct_answers=0,
                        current_streak_days=0,
                        longest_streak_days=0,
                        total_points=0,
                        level=1,
                        topics_mastered=0,
                        perfect_scores=0
                    )
                    db.session.add(stats)
                db.session.commit()
                print("   ✅ UserStats created for all orphaned users!")
        
        print("\n" + "="*60)
        return True

def fix_all_students():
    """Fix common issues for all students"""
    print("\n" + "="*60)
    print("FIXING ALL STUDENTS")
    print("="*60)
    
    with app.app_context():
        students = User.query.filter_by(role='student').all()
        print(f"\nFound {len(students)} students")
        
        fixed = 0
        for student in students:
            needs_fix = False
            
            # Ensure approved
            if not student.is_approved:
                student.is_approved = True
                needs_fix = True
            
            # Ensure has stats
            if not UserStats.query.filter_by(user_id=student.id).first():
                stats = UserStats(
                    user_id=student.id,
                    total_quizzes=0,
                    total_questions_answered=0,
                    total_correct_answers=0,
                    current_streak_days=0,
                    longest_streak_days=0,
                    total_points=0,
                    level=1,
                    topics_mastered=0,
                    perfect_scores=0
                )
                db.session.add(stats)
                needs_fix = True
            
            if needs_fix:
                fixed += 1
                print(f"  ✅ Fixed: {student.email}")
        
        db.session.commit()
        print(f"\n✅ Fixed {fixed} students")
        print("="*60)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("STUDENT DASHBOARD DIAGNOSTIC TOOL")
    print("="*60)
    
    print("\nOptions:")
    print("1. Check database health")
    print("2. Diagnose specific student")
    print("3. Fix all students")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == '1':
        check_database()
    elif choice == '2':
        email = input("\nEnter student email: ")
        diagnose_user(email)
    elif choice == '3':
        confirm = input("\nThis will fix all students. Continue? (y/n): ")
        if confirm.lower() == 'y':
            fix_all_students()
    elif choice == '4':
        print("\nExiting...")
    else:
        print("\nInvalid choice")
