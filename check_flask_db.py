#!/usr/bin/env python3
"""
Flask Database Configuration Checker
This script checks what database Flask is actually using
Run: python check_flask_db.py
"""

import sys
import os

# Add your app directory to path
sys.path.insert(0, '/home/bbsisk/mathapp')

print("="*60)
print("FLASK DATABASE CONFIGURATION CHECKER")
print("="*60)

try:
    # Import your Flask app
    print("\n1. Importing Flask app...")
    from app import app, db
    print("   ✅ Successfully imported app and db")
    
    # Check database URI
    print("\n2. Checking database configuration...")
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
        print(f"   Database URI: {db_uri}")
        
        # Try to extract actual database path
        if 'sqlite:///' in db_uri:
            db_path = db_uri.replace('sqlite:///', '')
            print(f"   Actual DB path: {db_path}")
            
            # Check if file exists
            if os.path.exists(db_path):
                print(f"   ✅ Database file exists")
                print(f"   File size: {os.path.getsize(db_path)} bytes")
            else:
                print(f"   ❌ Database file does NOT exist!")
        
        # Test the actual Flask db connection
        print("\n3. Testing Flask db.session.execute()...")
        from sqlalchemy import text
        
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM guest_quiz_attempts"))
            count = result.scalar()
            print(f"   ✅ Query successful!")
            print(f"   Quiz attempts in Flask db: {count}")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test the leaderboard query through Flask
        print("\n4. Testing leaderboard query through Flask db...")
        try:
            query = text("""
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
            
            results = db.session.execute(query).fetchall()
            print(f"   ✅ Leaderboard query successful!")
            print(f"   Found {len(results)} guests")
            
            if len(results) > 0:
                print("\n   Top 3:")
                for i, row in enumerate(results[:3], 1):
                    print(f"   {i}. Guest-{row.guest_code[:6]}: {row.total_score} points")
            
        except Exception as e:
            print(f"   ❌ Leaderboard query failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Check if the endpoint exists
        print("\n5. Checking if /api/guest-leaderboard endpoint exists...")
        rules = list(app.url_map.iter_rules())
        leaderboard_exists = any('guest-leaderboard' in str(rule) for rule in rules)
        
        if leaderboard_exists:
            print("   ✅ /api/guest-leaderboard endpoint is registered!")
        else:
            print("   ❌ /api/guest-leaderboard endpoint NOT found!")
            print("\n   Available /api/ endpoints:")
            for rule in rules:
                if '/api/' in str(rule):
                    print(f"      - {rule}")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    
    print("\n📋 SUMMARY:")
    print("   If all tests passed, the Flask app should work.")
    print("   If tests failed, the error above shows what's wrong.")
    print("\n   Next: Try the API again after ensuring web app is reloaded:")
    print("   https://bbsisk.pythonanywhere.com/api/guest-leaderboard")
    
except ImportError as e:
    print(f"\n❌ FATAL: Could not import Flask app")
    print(f"   Error: {e}")
    print("\n   This means:")
    print("   1. The app file might not be named 'app.py'")
    print("   2. There's a syntax error in your Flask file")
    print("   3. The path is wrong")
    print("\n   Check:")
    print("   - Go to Web tab")
    print("   - Look at 'Source code' section")
    print("   - See what file it says is being used")
    
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
