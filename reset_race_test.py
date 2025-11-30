#!/usr/bin/env python3
"""
RESET RACE RESULTS FOR TESTING
===============================
Clears race results so you can test the race again.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python reset_race_test.py
"""

import sqlite3

DB_PATH = 'instance/mathquiz.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 50)
    print("🔄 RESETTING RACE DATA FOR TESTING")
    print("=" * 50)
    
    # Show current race results
    print("\n📊 Current race results:")
    cursor.execute("""
        SELECT rr.id, g.guest_code, rc.name, rr.finish_position, rr.points_earned
        FROM race_results rr
        LEFT JOIN guest_users g ON rr.guest_code = g.guest_code
        LEFT JOIN race_calendar rc ON rr.race_id = rc.id
        ORDER BY rr.created_at DESC
        LIMIT 10
    """)
    results = cursor.fetchall()
    if results:
        for r in results:
            print(f"   ID {r[0]}: {r[1]} - {r[2]} - P{r[3]} ({r[4]} pts)")
    else:
        print("   No race results found")
    
    # Delete all race results
    print("\n🗑️ Deleting race results...")
    cursor.execute("DELETE FROM race_results")
    deleted_results = cursor.rowcount
    print(f"   ✓ Deleted {deleted_results} race result(s)")
    
    # Reset championship standings
    print("\n🗑️ Resetting championship standings...")
    cursor.execute("DELETE FROM championship_standings")
    deleted_champ = cursor.rowcount
    print(f"   ✓ Deleted {deleted_champ} championship record(s)")
    
    # Reset season to race 1
    print("\n🔄 Resetting season to Round 1...")
    cursor.execute("UPDATE race_season_status SET current_race_number = 1")
    print("   ✓ Season reset to Round 1")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ RESET COMPLETE!")
    print("=" * 50)
    print("""
You can now test the race again!
Go to: /racing-car?test=race
""")


if __name__ == '__main__':
    main()
