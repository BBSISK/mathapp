#!/usr/bin/env python3
"""
DIAGNOSE BADGE DISPLAY ISSUE
=============================
This script checks why badges are showing "undefined"

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python diagnose_badges.py
"""

import sqlite3
import os

DB_PATH = 'instance/mathquiz.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("BADGE DISPLAY DIAGNOSTIC")
    print("=" * 70)
    
    # 1. Check badges table structure
    print("\n📋 BADGES TABLE STRUCTURE:")
    print("-" * 50)
    cursor.execute("PRAGMA table_info(badges)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]}: {col[2]} {'(NULL allowed)' if col[3] == 0 else '(NOT NULL)'}")
    
    # 2. Check all badges with ALL fields
    print("\n📛 ALL BADGES (with all fields):")
    print("-" * 50)
    cursor.execute("""
        SELECT id, name, description, icon, category, 
               requirement_type, requirement_value, points, color
        FROM badges
    """)
    badges = cursor.fetchall()
    
    for b in badges:
        badge_id, name, desc, icon, cat, req_type, req_val, points, color = b
        print(f"\n  ID {badge_id}: {name}")
        print(f"    description: {repr(desc)}")
        print(f"    points: {repr(points)}")
        print(f"    icon: {icon}, category: {cat}")
        print(f"    requirement: {req_type} = {req_val}")
        
        # Flag issues
        if desc is None or desc == '':
            print(f"    ⚠️ ISSUE: description is empty/null!")
        if points is None:
            print(f"    ⚠️ ISSUE: points is NULL!")
    
    # 3. Check user_badges table
    print("\n\n👤 USER BADGES (earned badges):")
    print("-" * 50)
    cursor.execute("""
        SELECT ub.id, ub.user_id, u.full_name, u.email, ub.badge_id, 
               b.name as badge_name, b.description, b.points, ub.earned_at
        FROM user_badges ub
        JOIN users u ON ub.user_id = u.id
        LEFT JOIN badges b ON ub.badge_id = b.id
        ORDER BY ub.user_id, ub.earned_at
    """)
    user_badges = cursor.fetchall()
    
    if not user_badges:
        print("  No user_badges entries found!")
    else:
        current_user = None
        for ub in user_badges:
            ub_id, user_id, name, email, badge_id, badge_name, desc, points, earned_at = ub
            
            if user_id != current_user:
                print(f"\n  User: {name} ({email}) - ID: {user_id}")
                current_user = user_id
            
            if badge_name is None:
                print(f"    ⚠️ Badge ID {badge_id}: NO MATCHING BADGE IN badges TABLE!")
            else:
                print(f"    ✓ {badge_name} (ID:{badge_id}, pts:{points}) - earned {earned_at}")
                if desc is None or points is None:
                    print(f"      ⚠️ Missing data: desc={repr(desc)}, points={repr(points)}")
    
    # 4. Check for orphaned user_badges
    print("\n\n🔍 CHECKING FOR ORPHANED USER_BADGES:")
    print("-" * 50)
    cursor.execute("""
        SELECT ub.id, ub.user_id, ub.badge_id
        FROM user_badges ub
        LEFT JOIN badges b ON ub.badge_id = b.id
        WHERE b.id IS NULL
    """)
    orphans = cursor.fetchall()
    
    if orphans:
        print(f"  ⚠️ Found {len(orphans)} orphaned user_badge entries!")
        print("  These reference badge IDs that don't exist:")
        for ub_id, user_id, badge_id in orphans:
            print(f"    - user_badges.id={ub_id}, user_id={user_id}, badge_id={badge_id}")
        print("\n  This could cause 'undefined' display issues!")
    else:
        print("  ✓ No orphaned user_badges found")
    
    # 5. Check specific user (likely the test user based on screenshot)
    print("\n\n🎯 CHECKING SPECIFIC USERS WITH 8 BADGES:")
    print("-" * 50)
    cursor.execute("""
        SELECT user_id, COUNT(*) as badge_count
        FROM user_badges
        GROUP BY user_id
        HAVING badge_count = 8
    """)
    users_with_8 = cursor.fetchall()
    
    for user_id, count in users_with_8:
        cursor.execute("SELECT full_name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        print(f"\n  User ID {user_id}: {user[0]} ({user[1]}) has {count} badges")
        
        # Get their badges
        cursor.execute("""
            SELECT b.name, b.description, b.points, ub.earned_at
            FROM user_badges ub
            LEFT JOIN badges b ON ub.badge_id = b.id
            WHERE ub.user_id = ?
        """, (user_id,))
        
        for name, desc, points, earned_at in cursor.fetchall():
            if name is None:
                print(f"    ⚠️ ORPHAN BADGE - no matching badge record!")
            else:
                status = "⚠️" if (desc is None or points is None) else "✓"
                print(f"    {status} {name}: desc={repr(desc)[:30]}..., points={points}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
