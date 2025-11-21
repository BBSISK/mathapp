#!/usr/bin/env python3
"""
Auto-fix script for guest_leaderboard function
This will find and replace the problematic code in app.py
Run: python fix_leaderboard.py
"""

import os
import sys

APP_PATH = '/home/bbsisk/mathapp/app.py'

# The old problematic code
OLD_CODE = '''        leaderboard = []
        for rank, row in enumerate(results, start=1):
            # Generate guest display name from code
            # Uses first 6 characters of code for anonymity
            guest_display = f"Guest-{row.guest_code[:6]}" if len(row.guest_code) > 6 else f"Guest-{row.guest_code}"

            leaderboard.append({
                'rank': rank,
                'guest_code': row.guest_code,  # Full code (not displayed to others)
                'display_name': guest_display,  # Public display name
                'total_quizzes': row.total_quizzes,
                'total_score': row.total_score,
                'total_questions': row.total_questions_attempted,
                'avg_percentage': float(row.avg_percentage) if row.avg_percentage else 0.0,
                'first_quiz': row.first_quiz_date.strftime('%Y-%m-%d') if row.first_quiz_date else None,
                'last_quiz': row.last_quiz_date.strftime('%Y-%m-%d') if row.last_quiz_date else None
            })'''

# The new working code
NEW_CODE = '''        leaderboard = []
        for rank, row in enumerate(results, start=1):
            # Use array indexing [0], [1], etc. instead of row.attribute
            guest_code = row[0]
            total_quizzes = row[1]
            total_score = row[2]
            total_questions = row[3]
            avg_percentage = row[4]
            first_quiz_date = row[5]
            last_quiz_date = row[6]
            
            # Generate guest display name from code
            guest_display = f"Guest-{guest_code[:6]}"
            
            # Handle dates safely (they might be strings already)
            first_quiz = str(first_quiz_date)[:10] if first_quiz_date else None
            last_quiz = str(last_quiz_date)[:10] if last_quiz_date else None

            leaderboard.append({
                'rank': rank,
                'guest_code': guest_code,
                'display_name': guest_display,
                'total_quizzes': int(total_quizzes),
                'total_score': int(total_score),
                'total_questions': int(total_questions),
                'avg_percentage': float(avg_percentage) if avg_percentage else 0.0,
                'first_quiz': first_quiz,
                'last_quiz': last_quiz
            })'''

def main():
    print("="*60)
    print("AUTO-FIX SCRIPT FOR GUEST LEADERBOARD")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(APP_PATH):
        print(f"❌ ERROR: {APP_PATH} not found!")
        print("\nPlease update APP_PATH in this script to your actual app.py location")
        sys.exit(1)
    
    print(f"\n✅ Found: {APP_PATH}")
    
    # Read the file
    print("📖 Reading app.py...")
    with open(APP_PATH, 'r') as f:
        content = f.read()
    
    # Check if old code exists
    if OLD_CODE not in content:
        if 'row[0]' in content and 'guest_code = row[0]' in content:
            print("✅ ALREADY FIXED! The new code is already in place.")
            print("   No changes needed.")
            sys.exit(0)
        else:
            print("⚠️  WARNING: Could not find the expected old code.")
            print("   The function might have different formatting.")
            print("   Please manually replace the guest_leaderboard function.")
            sys.exit(1)
    
    print("🔍 Found old problematic code!")
    
    # Make backup
    backup_path = APP_PATH + '.backup'
    print(f"💾 Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Replace the code
    print("🔧 Replacing with fixed code...")
    new_content = content.replace(OLD_CODE, NEW_CODE)
    
    # Write back
    print("💾 Writing fixed code to app.py...")
    with open(APP_PATH, 'w') as f:
        f.write(new_content)
    
    print("\n" + "="*60)
    print("✅ SUCCESS! app.py has been fixed!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("   1. Go to Web tab on PythonAnywhere")
    print("   2. Click green 'Reload' button")
    print("   3. Wait 10 seconds")
    print("   4. Test: https://bbsisk.pythonanywhere.com/api/guest-leaderboard")
    print("\n💾 BACKUP:")
    print(f"   Your original file is saved as: {backup_path}")
    print("   If something goes wrong, you can restore it.")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
