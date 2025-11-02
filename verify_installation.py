#!/usr/bin/env python3
"""
Probability Topic Installation Verification Script
Run this after installing the probability files to verify everything is set up correctly.
"""

import sqlite3
import os
import sys

def check_database_questions():
    """Check if probability questions exist in the database"""
    print("=" * 70)
    print("CHECKING DATABASE FOR PROBABILITY QUESTIONS")
    print("=" * 70)
    
    db_paths = [
        'instance/mathquiz.db',
        'mathquiz.db',
        '../instance/mathquiz.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ ERROR: Could not find database file")
        print("   Looked in: " + ", ".join(db_paths))
        return False
    
    print(f"✅ Found database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if questions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if not cursor.fetchone():
            print("❌ ERROR: 'questions' table does not exist")
            conn.close()
            return False
        
        print("✅ Questions table exists")
        
        # Count probability questions by difficulty
        difficulties = ['Beginner', 'Intermediate', 'Advanced']
        total = 0
        
        print("\nProbability questions by difficulty:")
        for difficulty in difficulties:
            cursor.execute("""
                SELECT COUNT(*) FROM questions 
                WHERE topic = 'probability' AND difficulty = ?
            """, (difficulty,))
            count = cursor.fetchone()[0]
            print(f"  {difficulty:12} : {count:3} questions")
            total += count
        
        print(f"  {'Total':12} : {total:3} questions")
        
        if total == 0:
            print("\n❌ WARNING: No probability questions found!")
            print("   Run: python add_probability_questions.py")
            conn.close()
            return False
        elif total < 120:
            print(f"\n⚠️  WARNING: Only {total}/120 probability questions found")
            print("   Expected 120 (40 per difficulty)")
            conn.close()
            return False
        else:
            print("\n✅ All 120 probability questions found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Database error - {e}")
        return False

def check_app_py():
    """Check if app.py has been updated with probability"""
    print("\n" + "=" * 70)
    print("CHECKING APP.PY FOR PROBABILITY INTEGRATION")
    print("=" * 70)
    
    if not os.path.exists('app.py'):
        print("❌ ERROR: app.py not found in current directory")
        return False
    
    print("✅ Found app.py")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for probability in topics lists
        checks = [
            ("'probability' in topics list", "'probability'" in content),
            ("Topics list contains 'sets', 'probability', 'complex_numbers'", 
             "'sets', 'probability', 'complex_numbers_intro'" in content),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        if not all_passed:
            print("\n⚠️  WARNING: app.py may not be properly updated")
            print("   Make sure you uploaded the correct app.py file")
            return False
        else:
            print("\n✅ app.py is properly configured!")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Could not read app.py - {e}")
        return False

def check_templates():
    """Check if templates have been updated"""
    print("\n" + "=" * 70)
    print("CHECKING TEMPLATES FOR PROBABILITY INTEGRATION")
    print("=" * 70)
    
    templates_to_check = [
        'templates/admin_dashboard.html',
        'templates/student_app.html',
        'templates/student_app_with_mastery.html'
    ]
    
    found = 0
    updated = 0
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            found += 1
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'probability' in content.lower() or 'fa-dice' in content:
                    print(f"✅ {template_path} - Updated")
                    updated += 1
                else:
                    print(f"⚠️  {template_path} - May not be updated")
            except Exception as e:
                print(f"❌ {template_path} - Error reading file: {e}")
        else:
            print(f"⚠️  {template_path} - File not found")
    
    if found == 0:
        print("\n❌ ERROR: No template files found")
        print("   Make sure you're running this script from the app root directory")
        return False
    elif updated < found:
        print(f"\n⚠️  WARNING: Only {updated}/{found} templates appear to be updated")
        return False
    else:
        print(f"\n✅ All {updated} checked templates are updated!")
        return True

def main():
    """Run all verification checks"""
    print("\n" + "=" * 70)
    print("PROBABILITY TOPIC INSTALLATION VERIFICATION")
    print("=" * 70)
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
        print(f"Working directory: {os.getcwd()}\n")
    
    checks = [
        ("Database Questions", check_database_questions),
        ("app.py Configuration", check_app_py),
        ("Template Updates", check_templates),
    ]
    
    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()
    
    # Final summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 SUCCESS! Probability topic is fully installed and ready to use!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Log in as admin and verify probability appears in dropdowns")
        print("3. Test with students to ensure functionality")
        return 0
    else:
        print("\n⚠️  INCOMPLETE! Some checks failed.")
        print("\nRecommended actions:")
        print("1. Review the errors above")
        print("2. Check the INSTALLATION_GUIDE.md")
        print("3. Ensure all files were uploaded correctly")
        print("4. Run: python add_probability_questions.py (if needed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
