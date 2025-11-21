#!/usr/bin/env python3
"""
Comprehensive Guest Leaderboard Diagnostic Tool
Standalone script to test all components of the leaderboard query
Run: python diagnose_leaderboard.py
"""

import sqlite3
import sys
import os
import traceback

# Database path
DATABASE_PATH = '/home/bbsisk/mathapp/instance/mathquiz.db'

def test_basic_connection():
    """Test 1: Basic database connection"""
    print("\n" + "="*60)
    print("TEST 1: DATABASE CONNECTION")
    print("="*60)
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        print(f"✅ Connected to: {DATABASE_PATH}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_table_exists(conn):
    """Test 2: Check if guest_quiz_attempts table exists"""
    print("\n" + "="*60)
    print("TEST 2: TABLE EXISTENCE")
    print("="*60)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='guest_quiz_attempts'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ Table 'guest_quiz_attempts' exists")
            return True
        else:
            print("❌ Table 'guest_quiz_attempts' NOT FOUND")
            # Show what tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\nAvailable tables:")
            for table in tables:
                print(f"   - {table[0]}")
            return False
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False

def test_table_structure(conn):
    """Test 3: Check table structure and columns"""
    print("\n" + "="*60)
    print("TEST 3: TABLE STRUCTURE")
    print("="*60)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(guest_quiz_attempts)")
        columns = cursor.fetchall()
        
        print("Columns in guest_quiz_attempts:")
        required = ['guest_code', 'score', 'total_questions', 'completed_at']
        found = {}
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"   - {col_name} ({col_type})")
            if col_name in required:
                found[col_name] = True
        
        print("\nRequired columns check:")
        all_found = True
        for req in required:
            if req in found:
                print(f"   ✅ {req}")
            else:
                print(f"   ❌ {req} - MISSING!")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking structure: {e}")
        traceback.print_exc()
        return False

def test_data_exists(conn):
    """Test 4: Check if data exists"""
    print("\n" + "="*60)
    print("TEST 4: DATA EXISTENCE")
    print("="*60)
    try:
        cursor = conn.cursor()
        
        # Count total rows
        cursor.execute("SELECT COUNT(*) FROM guest_quiz_attempts")
        total = cursor.fetchone()[0]
        print(f"Total quiz attempts: {total}")
        
        # Count with guest_code
        cursor.execute("SELECT COUNT(*) FROM guest_quiz_attempts WHERE guest_code IS NOT NULL")
        with_code = cursor.fetchone()[0]
        print(f"Attempts with guest_code: {with_code}")
        
        if with_code == 0:
            print("❌ No quiz attempts with guest_code found!")
            return False
        
        print(f"✅ {with_code} quiz attempts with guest codes")
        return True
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        traceback.print_exc()
        return False

def test_simple_query(conn):
    """Test 5: Simple SELECT query"""
    print("\n" + "="*60)
    print("TEST 5: SIMPLE QUERY")
    print("="*60)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT guest_code, score, total_questions, completed_at
            FROM guest_quiz_attempts
            LIMIT 3
        """)
        results = cursor.fetchall()
        
        print("Sample data (first 3 rows):")
        for row in results:
            print(f"   Code: {row[0][:10]}... | Score: {row[1]} | Questions: {row[2]} | Date: {row[3]}")
        
        print("✅ Simple query works")
        return True
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        traceback.print_exc()
        return False

def test_aggregation_query(conn):
    """Test 6: Basic aggregation query"""
    print("\n" + "="*60)
    print("TEST 6: AGGREGATION QUERY")
    print("="*60)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                guest_code,
                COUNT(*) as total_quizzes,
                SUM(score) as total_score
            FROM guest_quiz_attempts
            WHERE guest_code IS NOT NULL
            GROUP BY guest_code
            LIMIT 5
        """)
        results = cursor.fetchall()
        
        print("Aggregated data (first 5 guests):")
        for row in results:
            print(f"   Guest-{row[0][:6]}: {row[1]} quizzes, {row[2]} points")
        
        print("✅ Aggregation query works")
        return True
    except Exception as e:
        print(f"❌ Aggregation query failed: {e}")
        traceback.print_exc()
        return False

def test_full_leaderboard_query(conn):
    """Test 7: Full leaderboard query (exact copy from app.py)"""
    print("\n" + "="*60)
    print("TEST 7: FULL LEADERBOARD QUERY")
    print("="*60)
    try:
        cursor = conn.cursor()
        
        # This is the EXACT query from the app
        cursor.execute("""
            SELECT 
                guest_code,
                COUNT(*) as total_quizzes,
                SUM(score) as total_score,
                SUM(total_questions) as total_questions_attempted,
                ROUND(AVG(CAST(score AS FLOAT) / CAST(total_questions AS FLOAT) * 100), 1) as avg_percentage,
                MIN(completed_at) as first_quiz_date,
                MAX(completed_at) as last_quiz_date
            FROM guest_quiz_attempts
            WHERE guest_code IS NOT NULL
            GROUP BY guest_code
            HAVING COUNT(*) > 0
            ORDER BY total_score DESC
            LIMIT 20
        """)
        
        results = cursor.fetchall()
        
        print(f"Found {len(results)} guests for leaderboard")
        print("\n🏆 TOP 10 LEADERBOARD:")
        print("-" * 70)
        print(f"{'Rank':<6} {'Guest':<15} {'Quizzes':<10} {'Score':<10} {'Avg %':<10}")
        print("-" * 70)
        
        for rank, row in enumerate(results[:10], start=1):
            guest_code, quizzes, score, questions, avg, first, last = row
            display = f"Guest-{guest_code[:6]}"
            medal = ""
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            
            print(f"{medal:<2} {rank:<4} {display:<15} {quizzes:<10} {score:<10} {avg:.1f}%")
        
        print("\n✅ FULL LEADERBOARD QUERY WORKS PERFECTLY!")
        print("="*60)
        print("✅ ALL TESTS PASSED - DATABASE IS FINE!")
        print("="*60)
        print("\n🔍 CONCLUSION:")
        print("   The database and query work perfectly when tested directly.")
        print("   The issue must be with:")
        print("   1. Flask app not using the correct file")
        print("   2. Flask app not reloaded after upload")
        print("   3. Flask app using different database path")
        print("   4. Flask 'db' object not configured correctly")
        print("\n📋 NEXT STEPS:")
        print("   1. Check Web tab -> 'Source code' path")
        print("   2. Verify the correct file is named as shown in Source code")
        print("   3. Ensure web app was reloaded")
        print("   4. Check Flask error logs for actual error")
        
        return True
        
    except Exception as e:
        print(f"❌ Full leaderboard query failed: {e}")
        print("\nFull error:")
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("GUEST LEADERBOARD DIAGNOSTIC TOOL")
    print("="*60)
    print(f"Testing database: {DATABASE_PATH}")
    
    # Test 1: Connection
    if not test_basic_connection():
        print("\n❌ FATAL: Cannot connect to database")
        sys.exit(1)
    
    # Connect for remaining tests
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Test 2: Table exists
        if not test_table_exists(conn):
            print("\n❌ FATAL: Required table not found")
            conn.close()
            sys.exit(1)
        
        # Test 3: Table structure
        if not test_table_structure(conn):
            print("\n❌ FATAL: Table structure incorrect")
            conn.close()
            sys.exit(1)
        
        # Test 4: Data exists
        if not test_data_exists(conn):
            print("\n❌ FATAL: No data to display")
            conn.close()
            sys.exit(1)
        
        # Test 5: Simple query
        if not test_simple_query(conn):
            print("\n❌ FATAL: Basic queries failing")
            conn.close()
            sys.exit(1)
        
        # Test 6: Aggregation
        if not test_aggregation_query(conn):
            print("\n❌ FATAL: Aggregation queries failing")
            conn.close()
            sys.exit(1)
        
        # Test 7: Full query
        if not test_full_leaderboard_query(conn):
            print("\n❌ FATAL: Full leaderboard query failing")
            conn.close()
            sys.exit(1)
        
    finally:
        conn.close()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
