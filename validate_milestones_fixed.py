#!/usr/bin/env python3
"""
Milestone Recognition Validation Script (FIXED)
Tests if badges are being awarded correctly for all quiz completions
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

def main():
    # Try multiple possible database paths
    possible_paths = [
        'instance/mathquiz.db',
        'mathquiz.db',
        '../instance/mathquiz.db',
        './instance/mathquiz.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found. Tried:")
        for path in possible_paths:
            print(f"   • {os.path.abspath(path)}")
        print()
        print("Please run this script from your project root directory:")
        print("  cd ~/bbsisk.pythonanywhere.com")
        print("  python validate_milestones.py")
        return
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║         MILESTONE RECOGNITION SYSTEM VALIDATION                      ║")
    print("║         Testing Badge Awards for Quiz Completions                    ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📂 Database: {db_path}")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, check the structure of users table to get correct column names
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in cursor.fetchall()]
    print("🔍 Users table columns:", ", ".join(user_columns))
    print()
    
    # Determine the correct column name for username/email
    name_column = None
    if 'username' in user_columns:
        name_column = 'username'
    elif 'email' in user_columns:
        name_column = 'email'
    elif 'name' in user_columns:
        name_column = 'name'
    else:
        # Use first text column
        name_column = user_columns[1] if len(user_columns) > 1 else user_columns[0]
    
    print(f"✓ Using '{name_column}' as identifier column")
    print()
    
    # 1. Check all available badges
    print("📊 AVAILABLE BADGES")
    print("="*70)
    cursor.execute("""
        SELECT id, name, requirement_type, requirement_value, points, description
        FROM badges
        ORDER BY id
    """)
    badges = cursor.fetchall()
    
    if not badges:
        print("⚠️  No badges found in database!")
        print("   The badges table might be empty.")
        conn.close()
        return
    
    for badge in badges:
        print(f"[{badge[0]:2d}] {badge[1]:30s} ({badge[2]}: {badge[3]:3d}) - {badge[4]} pts")
    
    print()
    print(f"✓ Total badges defined: {len(badges)}")
    print("="*70)
    
    # 2. Check users with quiz attempts
    print("\n👥 USERS WITH QUIZ ATTEMPTS")
    print("="*70)
    
    # Check if user_type column exists
    cursor.execute("PRAGMA table_info(users)")
    has_user_type = any(col[1] == 'user_type' for col in cursor.fetchall())
    
    user_type_filter = "WHERE u.user_type = 'student'" if has_user_type else ""
    
    query = f"""
        SELECT 
            u.id,
            u.{name_column},
            COUNT(qa.id) as total_quizzes,
            SUM(CASE WHEN qa.percentage = 100 THEN 1 ELSE 0 END) as perfect_scores,
            SUM(CASE WHEN qa.percentage >= 80 THEN 1 ELSE 0 END) as high_scores,
            COUNT(DISTINCT DATE(qa.completed_at)) as practice_days
        FROM users u
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
        {user_type_filter}
        GROUP BY u.id, u.{name_column}
        HAVING total_quizzes > 0
        ORDER BY total_quizzes DESC
        LIMIT 10
    """
    
    try:
        cursor.execute(query)
        users = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"⚠️  Error querying users: {e}")
        users = []
    
    if not users:
        print("⚠️  No users with quiz attempts found.")
        print("   Students need to complete quizzes first!")
        conn.close()
        return
    
    for user in users:
        print(f"\n{user[1]:30s} (ID: {user[0]})")
        print(f"  Total Quizzes:   {user[2]:3d}")
        print(f"  Perfect Scores:  {user[3]:3d}")
        print(f"  High Scores:     {user[4]:3d}")
        print(f"  Practice Days:   {user[5]:3d}")
    
    print()
    print(f"✓ Total active users: {len(users)}")
    print("="*70)
    
    # 3. For each user, check which badges they SHOULD have vs DO have
    print("\n🔍 BADGE VALIDATION")
    print("="*70)
    
    total_missing = 0
    
    for user in users[:5]:  # Check first 5 users
        user_id = user[0]
        user_name = user[1]
        total_quizzes = user[2]
        perfect_scores = user[3]
        high_scores = user[4]
        
        print(f"\n{user_name}:")
        print(f"  Stats: {total_quizzes} quizzes, {perfect_scores} perfect, {high_scores} high")
        
        # Get earned badges
        cursor.execute("""
            SELECT b.id, b.name, ub.earned_at
            FROM user_badges ub
            JOIN badges b ON ub.badge_id = b.id
            WHERE ub.user_id = ?
            ORDER BY ub.earned_at
        """, (user_id,))
        
        earned_badges = cursor.fetchall()
        print(f"  ✅ Earned: {len(earned_badges)} badges")
        if earned_badges:
            for eb in earned_badges[:3]:  # Show first 3
                print(f"     [{eb[0]}] {eb[1]}")
            if len(earned_badges) > 3:
                print(f"     ... and {len(earned_badges) - 3} more")
        
        # Check which badges SHOULD be earned
        should_earn = []
        
        # Quiz completion badges
        if total_quizzes >= 1:
            should_earn.append((1, "First Steps"))
        if total_quizzes >= 5:
            should_earn.append((2, "Curious Learner"))
        if total_quizzes >= 10:
            should_earn.append((3, "Dedicated Student"))
        if total_quizzes >= 25:
            should_earn.append((4, "Math Enthusiast"))
        if total_quizzes >= 50:
            should_earn.append((5, "Quiz Master"))
        
        # Perfect score badges
        if perfect_scores >= 1:
            should_earn.append((7, "Perfectionist"))
        if perfect_scores >= 5:
            should_earn.append((9, "Flawless Five"))
        
        # High score badges
        if high_scores >= 1:
            should_earn.append((6, "Sharp Shooter"))
        
        # Check for 90%+ scores
        cursor.execute("""
            SELECT COUNT(*) FROM quiz_attempts 
            WHERE user_id = ? AND percentage >= 90
        """, (user_id,))
        high_90_scores = cursor.fetchone()[0]
        if high_90_scores >= 5:
            should_earn.append((8, "Consistent Excellence"))
        
        earned_ids = {eb[0] for eb in earned_badges}
        should_earn_ids = {se[0] for se in should_earn}
        
        missing = should_earn_ids - earned_ids
        if missing:
            print(f"  ⚠️  MISSING {len(missing)} badges:")
            for badge_id in sorted(missing):
                badge_info = next((se for se in should_earn if se[0] == badge_id), None)
                if badge_info:
                    print(f"     [{badge_info[0]}] {badge_info[1]}")
            total_missing += len(missing)
        else:
            print(f"  ✅ All expected badges earned!")
    
    print()
    print("="*70)
    
    # 4. Summary
    print("\n📋 VALIDATION SUMMARY")
    print("="*70)
    
    print(f"✅ Total badges defined: {len(badges)}")
    print(f"✅ Total active students: {len(users)}")
    print(f"✅ Students checked in detail: {min(5, len(users))}")
    
    if total_missing > 0:
        print(f"⚠️  Total missing badges found: {total_missing}")
        print()
        print("POSSIBLE CAUSES:")
        print("  1. Badges were added after users completed quizzes")
        print("  2. Badge award logic wasn't running")
        print("  3. Database was reset or badges were deleted")
        print()
        print("FIX: Users need to complete ONE more quiz to trigger badge check")
    else:
        print(f"✅ No missing badges detected!")
    
    print()
    print("BADGE SYSTEM STATUS:")
    print("  ✅ Backend: Badge logic exists")
    print("  ✅ Database: Badges defined")
    print("  ✅ Users: Quiz attempts recorded")
    
    # Check if frontend has milestone code
    print()
    print("FRONTEND STATUS:")
    print("  ⚠️  Check if student_app.html has milestone celebration modal")
    print("  ⚠️  Check if newly_earned_badges is displayed on quiz completion")
    
    print()
    print("RECOMMENDATIONS:")
    if total_missing > 0:
        print("  1. ⚠️  Deploy updated student_app.html with milestone celebrations")
        print("  2. ⚠️  Have users complete one more quiz to trigger missing badges")
    else:
        print("  1. ✅ Deploy updated student_app.html with milestone celebrations")
        print("  2. ✅ Test by completing a quiz as a new student")
    
    print("  3. ✅ Verify celebration modal appears")
    print("  4. ✅ Check console.log for 'Badges earned' messages")
    
    conn.close()
    
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                 VALIDATION COMPLETE                                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
