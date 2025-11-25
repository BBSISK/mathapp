#!/usr/bin/env python3
"""
Diagnostic script to check guest_badges table and manually award badges
Run this on your server to see what's happening
"""

# Add at the top of your app.py or run separately:

def check_guest_badges_table():
    """Check if guest_badges table exists and has correct structure"""
    from sqlalchemy import text
    
    try:
        # Check if table exists
        result = db.session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='guest_badges'
        """)).fetchone()
        
        if not result:
            print("❌ guest_badges table does NOT exist!")
            print("Creating table...")
            
            db.session.execute(text("""
                CREATE TABLE guest_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guest_code TEXT NOT NULL,
                    badge_name TEXT NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guest_code, badge_name)
                )
            """))
            db.session.commit()
            print("✅ guest_badges table created!")
        else:
            print("✅ guest_badges table exists")
            
        # Check structure
        columns = db.session.execute(text("""
            PRAGMA table_info(guest_badges)
        """)).fetchall()
        
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Check existing data
        count = db.session.execute(text("""
            SELECT COUNT(*) FROM guest_badges
        """)).fetchone()[0]
        
        print(f"\nTotal badges awarded: {count}")
        
        if count > 0:
            badges = db.session.execute(text("""
                SELECT guest_code, badge_name, earned_at 
                FROM guest_badges 
                ORDER BY earned_at DESC 
                LIMIT 10
            """)).fetchall()
            
            print("\nRecent badges:")
            for badge in badges:
                print(f"  - {badge[0]}: {badge[1]} (earned {badge[2]})")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def manually_award_badges(guest_code):
    """Manually award badges at 100% for a specific guest"""
    from sqlalchemy import text
    
    print(f"\n🔍 Checking badges for guest: {guest_code}")
    
    # Get guest stats
    guest_stats = db.session.execute(text("""
        SELECT total_score, quizzes_completed
        FROM guest_users
        WHERE guest_code = :code
    """), {"code": guest_code}).fetchone()
    
    if not guest_stats:
        print(f"❌ No guest found with code: {guest_code}")
        return
        
    print(f"Guest stats: {guest_stats[1]} quizzes, {guest_stats[0]} points")
    
    # Check which badges should be awarded
    quizzes = guest_stats[1]
    
    badges_to_award = []
    
    if quizzes >= 1:
        badges_to_award.append("First Steps")
    if quizzes >= 5:
        badges_to_award.append("Curious Learner")
    if quizzes >= 10:
        badges_to_award.append("Dedicated Student")
    
    print(f"\nBadges at 100%: {badges_to_award}")
    
    # Award each badge
    for badge_name in badges_to_award:
        try:
            # Check if already awarded
            existing = db.session.execute(text("""
                SELECT COUNT(*) FROM guest_badges
                WHERE guest_code = :code AND badge_name = :name
            """), {"code": guest_code, "name": badge_name}).fetchone()[0]
            
            if existing == 0:
                # Award it!
                db.session.execute(text("""
                    INSERT INTO guest_badges (guest_code, badge_name, earned_at)
                    VALUES (:code, :name, datetime('now'))
                """), {"code": guest_code, "name": badge_name})
                db.session.commit()
                print(f"  ✅ Awarded: {badge_name}")
            else:
                print(f"  ⏭️  Already has: {badge_name}")
                
        except Exception as e:
            print(f"  ❌ Error awarding {badge_name}: {e}")


# Run diagnostics
print("=" * 60)
print("GUEST BADGES DIAGNOSTIC")
print("=" * 60)

check_guest_badges_table()

# Replace 'YOUR_GUEST_CODE' with your actual guest code
print("\n" + "=" * 60)
manually_award_badges('YOUR_GUEST_CODE')  # ← Change this to your guest code!
print("=" * 60)
