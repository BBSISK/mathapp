#!/usr/bin/env python3
"""
Check guest_quiz_attempts table structure
"""
import sqlite3
import os

DB_PATH = 'instance/mathquiz.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("GUEST_QUIZ_ATTEMPTS TABLE STRUCTURE")
    print("=" * 60)
    
    cursor.execute("PRAGMA table_info(guest_quiz_attempts)")
    columns = cursor.fetchall()
    
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA (last 10 entries)")
    print("=" * 60)
    
    # Get column names
    col_names = [c[1] for c in columns]
    print(f"\nColumns: {col_names}")
    
    cursor.execute("SELECT * FROM guest_quiz_attempts ORDER BY completed_at DESC LIMIT 10")
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"\n  {dict(zip(col_names, row))}")
    
    conn.close()

if __name__ == '__main__':
    main()
