"""
Diagnostic Script for Number Systems Topic Display Issues

This script will help identify why Number Systems isn't showing in your app.
Run this to get a detailed report of what's working and what needs fixing.
"""

from app import app, db, Question
from flask import url_for

def diagnose_number_systems():
    with app.app_context():
        print("\n" + "="*70)
        print("NUMBER SYSTEMS DIAGNOSTIC REPORT")
        print("="*70 + "\n")
        
        # Check 1: Database Questions
        print("CHECK 1: Database Questions")
        print("-" * 70)
        total = Question.query.filter_by(topic='number_systems').count()
        print(f"✓ Total Number Systems questions: {total}")
        
        if total == 0:
            print("❌ ERROR: No questions found in database!")
            print("   Solution: Run add_number_systems_questions.py")
            return False
        
        beginner = Question.query.filter_by(topic='number_systems', difficulty='beginner').count()
        intermediate = Question.query.filter_by(topic='number_systems', difficulty='intermediate').count()
        advanced = Question.query.filter_by(topic='number_systems', difficulty='advanced').count()
        
        print(f"   • Beginner: {beginner}")
        print(f"   • Intermediate: {intermediate}")
        print(f"   • Advanced: {advanced}")
        
        if total < 90:
            print(f"⚠️  WARNING: Expected 90 questions, found {total}")
        
        # Check 2: API Endpoint Configuration
        print("\n" + "CHECK 2: Backend API Configuration")
        print("-" * 70)
        
        # Simulate API call
        from app import get_topics
        with app.test_request_context():
            try:
                # Mock the login and approval requirements
                from unittest.mock import patch
                with patch('app.login_required', lambda f: f), \
                     patch('app.approved_required', lambda f: f):
                    result = get_topics()
                    topics_data = result.get_json()
                    
                    if 'number_systems' in topics_data:
                        print("✓ Number Systems found in /api/topics endpoint")
                        topic_info = topics_data['number_systems']
                        print(f"   • Title: {topic_info['title']}")
                        print(f"   • Icon: {topic_info['icon']}")
                        print(f"   • Color: {topic_info['color']}")
                    else:
                        print("❌ ERROR: Number Systems NOT in /api/topics endpoint!")
                        print("   Solution: Check app.py line 1189")
                        return False
            except Exception as e:
                print(f"⚠️  Could not test API endpoint: {e}")
        
        # Check 3: Template Files
        print("\n" + "CHECK 3: Template Files")
        print("-" * 70)
        
        import os
        template_dir = 'templates'
        
        # Check student_app.html
        student_app = os.path.join(template_dir, 'student_app.html')
        if os.path.exists(student_app):
            with open(student_app, 'r') as f:
                content = f.read()
                if "'number_systems'" in content or '"number_systems"' in content:
                    print("✓ Number Systems found in student_app.html")
                else:
                    print("❌ ERROR: Number Systems NOT in student_app.html")
                    print("   Solution: Add 'number_systems' to path1Topics array")
        
        # Check admin_dashboard.html
        admin_dash = os.path.join(template_dir, 'admin_dashboard.html')
        if os.path.exists(admin_dash):
            with open(admin_dash, 'r') as f:
                content = f.read()
                if 'number_systems' in content.lower():
                    print("✓ Number Systems found in admin_dashboard.html")
                else:
                    print("⚠️  Number Systems NOT in admin_dashboard.html")
        
        # Check 4: Questions API Endpoint
        print("\n" + "CHECK 4: Questions API Endpoints")
        print("-" * 70)
        
        # Test if we can query questions for each difficulty
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            questions = Question.query.filter_by(
                topic='number_systems', 
                difficulty=difficulty
            ).all()
            if len(questions) > 0:
                print(f"✓ Can retrieve {difficulty} questions (found {len(questions)})")
                sample = questions[0]
                print(f"   Sample: {sample.question_text[:50]}...")
            else:
                print(f"❌ ERROR: No {difficulty} questions found!")
        
        # Check 5: Quiz Submission Validation
        print("\n" + "CHECK 5: Quiz Submission Validation")
        print("-" * 70)
        
        # Check if number_systems is in valid topics list in app.py
        import inspect
        source = inspect.getsource(app.view_functions['submit_quiz'])
        if 'number_systems' in source:
            print("✓ Number Systems in quiz submission validation")
        else:
            print("❌ ERROR: Number Systems NOT in valid_topics list")
            print("   Solution: Check app.py submit_quiz function")
        
        # Summary
        print("\n" + "="*70)
        print("DIAGNOSTIC SUMMARY")
        print("="*70)
        
        if total >= 90:
            print("✅ All checks passed! Number Systems should be working.")
            print("\nIf topic still not showing, try:")
            print("1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
            print("2. Check browser console for JavaScript errors (F12)")
            print("3. Verify you're logged in as an approved user")
            print("4. Restart your Flask application")
            print("5. Check the browser network tab to see if /api/topics is being called")
        else:
            print("⚠️  Issues found. Review errors above and apply solutions.")
        
        print("\n" + "="*70 + "\n")
        
        return True

if __name__ == '__main__':
    try:
        diagnose_number_systems()
    except Exception as e:
        print(f"\n❌ Diagnostic script error: {e}")
        print("Make sure you're in the project directory with access to the database\n")
