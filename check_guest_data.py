#!/usr/bin/env python3
"""
Guest Leaderboard Data Checker
Run this script to verify guest quiz data exists
Usage: python check_guest_data.py
"""

import sqlite3
import sys
import os

# Database path - adjust if your database is in a different location
DATABASE_PATH = '/home/bbsisk/mathapp/instance/mathquiz.db'

# Alternative paths to try if the above doesn't work
ALTERNATIVE_PATHS = [
    '/home/bbsisk/mathapp/mathquiz.db',
    '/home/bbsisk/instance/mathquiz.db',
    'instance/mathquiz.db',
    'mathquiz.db',
    '/home/bbsisk/mathapp/instance/math_master.db',
    '/home/bbsisk/mathapp/math_master.db'
]

def find_database():
    """Find the database file"""
    if os.path.exists(DATABASE_PATH):
        return DATABASE_PATH
    
    print(f"Database not found at: {DATABASE_PATH}")
    print("Trying alternative locations...")
    
    for path in ALTERNATIVE_PATHS:
        if os.path.exists(path):
            print(f"✅ Found database at: {path}")
            return path
    
    print("\n❌ Could not find database!")
    print("Please update DATABASE_PATH in this script to your database location.")
    sys.exit(1)

def check_tables(cursor):
    """Check what tables exist in the database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def find_guest_tables(cursor):
    """Find the correct table names for guest data"""
    tables = check_tables(cursor)
    
    # Possible table names
    guest_user_tables = ['guest_users', 'guest_user', 'guests']
    quiz_attempt_tables = ['guest_quiz_attempts', 'guest_quiz_attempt', 'guest_attempts', 'quiz_attempts']
    
    guest_table = None
    quiz_table = None
    
    for table in guest_user_tables:
        if table in tables:
            guest_table = table
            break
    
    for table in quiz_attempt_tables:
        if table in tables:
            quiz_table = table
            break
    
    return guest_table, quiz_table, tables

def main():
    print("=" * 60)
    print("GUEST LEADERBOARD DATA CHECKER")
    print("=" * 60)
    
    # Find database
    db_path = find_database()
    print(f"\nUsing database: {db_path}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check what tables exist
        guest_table, quiz_table, all_tables = find_guest_tables(cursor)
        
        if not guest_table or not quiz_table:
            print("⚠️  Could not find expected tables!")
            print(f"\nTables found in database:")
            for table in all_tables:
                print(f"   - {table}")
            print("\nLooking for tables like:")
            print("   - guest_users (or guest_user, guests)")
            print("   - guest_quiz_attempts (or guest_attempts, quiz_attempts)")
            print("\nPlease check your database schema.")
            conn.close()
            sys.exit(1)
        
        print(f"✅ Using tables: {guest_table}, {quiz_table}\n")
        
        # Check 1: Guest codes issued
        print("📊 CHECKING GUEST CODES...")
        cursor.execute(f"SELECT COUNT(*) FROM {guest_table}")
        total_codes = cursor.fetchone()[0]
        print(f"   Total guest codes issued: {total_codes}")
        
        # Check 2: Quiz attempts
        print("\n📝 CHECKING QUIZ ATTEMPTS...")
        cursor.execute(f"SELECT COUNT(*) FROM {quiz_table}")
        total_attempts = cursor.fetchone()[0]
        print(f"   Total quiz attempts by guests: {total_attempts}")
        
        # Check 3: Detailed leaderboard data
        if total_attempts > 0:
            print("\n🏆 LEADERBOARD DATA (Top 20):")
            print("-" * 60)
            cursor.execute(f"""
                SELECT 
                    guest_code,
                    COUNT(*) as total_quizzes,
                    SUM(score) as total_score,
                    SUM(total_questions) as total_questions,
                    ROUND(AVG(CAST(score AS FLOAT) / CAST(total_questions AS FLOAT) * 100), 1) as avg_percentage
                FROM {quiz_table}
                WHERE guest_code IS NOT NULL
                GROUP BY guest_code
                HAVING COUNT(*) > 0
                ORDER BY total_score DESC
                LIMIT 20
            """)
            
            results = cursor.fetchall()
            
            if results:
                print(f"{'Rank':<6} {'Guest Code':<15} {'Quizzes':<10} {'Score':<10} {'Avg %':<10}")
                print("-" * 60)
                for rank, row in enumerate(results, start=1):
                    guest_code, quizzes, score, questions, avg = row
                    display_name = f"Guest-{guest_code[:6]}"
                    medal = ""
                    if rank == 1:
                        medal = "🥇"
                    elif rank == 2:
                        medal = "🥈"
                    elif rank == 3:
                        medal = "🥉"
                    
                    print(f"{medal:<2} {rank:<4} {display_name:<15} {quizzes:<10} {score:<10} {avg:.1f}%")
                
                print("\n" + "=" * 60)
                print("✅ RESULT: Guest data exists! Leaderboard should work.")
                print("=" * 60)
                print("\n📋 NEXT STEPS:")
                print("   1. Deploy app_FIXED_LEADERBOARD.py to PythonAnywhere")
                print("   2. Rename it to app.py")
                print("   3. Reload your web app")
                print("   4. Visit: https://bbsisk.pythonanywhere.com/api/guest-leaderboard")
                print("   5. Check login page for leaderboard display")
            else:
                print("   ⚠️  No guest quiz data found (shouldn't happen if count > 0)")
        
        else:
            print("\n" + "=" * 60)
            print("❌ RESULT: No quiz attempts found!")
            print("=" * 60)
            print("\n📋 WHAT THIS MEANS:")
            print(f"   - {total_codes} guest codes were issued")
            print("   - But 0 guests have completed any quizzes")
            print("   - Leaderboard will be empty until guests take quizzes")
            print("\n📋 NEXT STEPS:")
            print("   1. Have a guest login with their code")
            print("   2. Complete at least 1 quiz")
            print("   3. Run this script again")
            print("   4. Then deploy the leaderboard")
        
        # Check 4: Sample guest codes
        if total_codes > 0:
            print("\n📋 SAMPLE GUEST CODES (First 5):")
            print("-" * 60)
            try:
                cursor.execute(f"""
                    SELECT guest_code, created_at, quizzes_completed
                    FROM {guest_table}
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    code, created, quizzes = row
                    print(f"   Code: {code[:20]}... | Created: {created} | Quizzes: {quizzes}")
            except Exception as e:
                print(f"   (Could not fetch sample codes: {e})")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("CHECK COMPLETE!")
        print("=" * 60 + "\n")
        
    except sqlite3.OperationalError as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        print("\nPossible issues:")
        print("   - Table doesn't exist")
        print("   - Database path is wrong")
        print("   - Database file is corrupted")
        print("\nPlease check your database setup.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
