#!/usr/bin/env python3
"""
DIAGNOSE RACING CAR UPGRADES
=============================
Check if the upgrade tables exist and have data.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python diagnose_upgrades.py
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
    
    print("=" * 60)
    print("🔍 DIAGNOSING RACING CAR UPGRADES")
    print("=" * 60)
    
    # Check if car_upgrades table exists
    print("\n1. Checking car_upgrades table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_upgrades'")
    if cursor.fetchone():
        print("   ✓ car_upgrades table exists")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM car_upgrades")
        count = cursor.fetchone()[0]
        print(f"   ✓ Contains {count} upgrades")
        
        if count > 0:
            # Show sample
            cursor.execute("SELECT upgrade_number, category, name, cost FROM car_upgrades ORDER BY upgrade_number LIMIT 5")
            print("\n   Sample upgrades:")
            for row in cursor.fetchall():
                print(f"      #{row[0]} [{row[1]}] {row[2]} - {row[3]} pts")
        else:
            print("   ⚠️ Table is EMPTY! Need to run migration.")
    else:
        print("   ❌ car_upgrades table does NOT exist!")
        print("   → Run: python racing_car_phase2_migration.py")
    
    # Check if user_car_upgrades table exists
    print("\n2. Checking user_car_upgrades table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_car_upgrades'")
    if cursor.fetchone():
        print("   ✓ user_car_upgrades table exists")
    else:
        print("   ❌ user_car_upgrades table does NOT exist!")
    
    # Check user_race_cars for upgrade_budget_used column
    print("\n3. Checking user_race_cars columns...")
    cursor.execute("PRAGMA table_info(user_race_cars)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'upgrade_budget_used' in columns:
        print("   ✓ upgrade_budget_used column exists")
    else:
        print("   ❌ upgrade_budget_used column missing!")
        print("   → Run: python racing_car_phase2_migration.py")
    
    # Check for your guest record
    print("\n4. Checking your guest record (BBSISK)...")
    cursor.execute("SELECT guest_code, parts_unlocked, upgrade_budget_used FROM user_race_cars WHERE guest_code LIKE '%BBSISK%' OR guest_code LIKE '%bbsisk%'")
    row = cursor.fetchone()
    if row:
        print(f"   ✓ Found: {row[0]}")
        print(f"     Parts: {row[1]}/50")
        print(f"     Budget used: {row[2] or 0}/20,000")
    else:
        print("   ℹ️ No BBSISK guest record found (will be created on first visit)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION:")
    print("=" * 60)
    print("""
If car_upgrades is empty or missing, run:
    python racing_car_phase2_migration.py

Then reload your web app and try again.
""")


if __name__ == '__main__':
    main()
