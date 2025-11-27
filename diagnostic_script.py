#!/usr/bin/env python3
"""
AgentMath.app Diagnostic Script
Run this on PythonAnywhere to identify missing components and functionality
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_file(filepath, description):
    """Check if a file exists and report its status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: Found ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: MISSING")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists and list its contents"""
    if os.path.exists(dirpath):
        files = os.listdir(dirpath)
        print(f"✅ {description}: Found ({len(files)} items)")
        if files:
            for f in files[:10]:  # Show first 10 files
                print(f"   - {f}")
            if len(files) > 10:
                print(f"   ... and {len(files)-10} more")
        return True
    else:
        print(f"❌ {description}: MISSING")
        return False

def check_database():
    """Check database structure and contents"""
    print_header("DATABASE CHECK")
    
    try:
        from app import app, db, User, Class, Question, Badge
        
        with app.app_context():
            # Check if database file exists
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            check_file(db_path, "Database file (mathquiz.db)")
            
            # Try to query database
            try:
                user_count = User.query.count()
                print(f"✅ Users in database: {user_count}")
                
                admin_count = User.query.filter_by(role='admin').count()
                teacher_count = User.query.filter_by(role='teacher').count()
                student_count = User.query.filter_by(role='student').count()
                print(f"   - Admins: {admin_count}")
                print(f"   - Teachers: {teacher_count}")
                print(f"   - Students: {student_count}")
                
            except Exception as e:
                print(f"❌ Could not query Users table: {e}")
            
            try:
                class_count = Class.query.count()
                print(f"✅ Classes in database: {class_count}")
            except Exception as e:
                print(f"❌ Could not query Classes table: {e}")
            
            try:
                question_count = Question.query.count()
                print(f"✅ Questions in database: {question_count}")
                
                if question_count > 0:
                    # Count by topic
                    topics = db.session.query(Question.topic, db.func.count(Question.id))\
                        .group_by(Question.topic).all()
                    print("   Questions by topic:")
                    for topic, count in topics:
                        print(f"   - {topic}: {count}")
            except Exception as e:
                print(f"❌ Could not query Questions table: {e}")
            
            try:
                badge_count = Badge.query.count()
                print(f"✅ Badges in database: {badge_count}")
            except Exception as e:
                print(f"❌ Could not query Badges table: {e}")
                
    except ImportError as e:
        print(f"❌ Could not import app modules: {e}")
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def check_routes():
    """Check if key routes are accessible"""
    print_header("ROUTE CHECK")
    
    try:
        from app import app
        
        with app.app_context():
            rules = list(app.url_map.iter_rules())
            print(f"✅ Total routes defined: {len(rules)}")
            
            # Check key routes
            key_routes = [
                '/',
                '/register',
                '/student',
                '/teacher',
                '/admin',
                '/api/login',
                '/api/register',
                '/api/quiz/start',
                '/api/teacher/classes',
                '/api/admin/stats'
            ]
            
            existing_routes = [str(rule) for rule in rules]
            
            print("\nKey routes:")
            for route in key_routes:
                if route in existing_routes:
                    print(f"✅ {route}")
                else:
                    print(f"❌ {route} - MISSING")
                    
    except Exception as e:
        print(f"❌ Route check failed: {e}")

def check_environment():
    """Check environment variables and configuration"""
    print_header("ENVIRONMENT CHECK")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check for SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        print(f"✅ SECRET_KEY is set (length: {len(secret_key)})")
    else:
        print("⚠️  SECRET_KEY not set in environment (using default)")
    
    # Check required packages
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug'
    ]
    
    print("\nRequired packages:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")

def main():
    """Run all diagnostic checks"""
    print("="*60)
    print("  MATH MASTER DIAGNOSTIC REPORT")
    print("="*60)
    
    # Check file structure
    print_header("FILE STRUCTURE CHECK")
    
    base_dir = os.getcwd()
    print(f"Current directory: {base_dir}")
    
    # Check key files
    check_file("app.py", "Main application file")
    check_file("requirements.txt", "Requirements file")
    check_file("mathquiz.db", "Database file")
    
    # Check directories
    check_directory("templates", "Templates directory")
    check_directory("static", "Static files directory")
    
    # Check template files
    if os.path.exists("templates"):
        print("\nTemplate files:")
        templates = [
            "index.html",
            "register.html",
            "student_app.html",
            "teacher_class_dashboard_v2.html",
            "admin_dashboard.html"
        ]
        for template in templates:
            check_file(f"templates/{template}", f"  {template}")
    
    # Check environment
    check_environment()
    
    # Check routes
    check_routes()
    
    # Check database
    check_database()
    
    # Summary
    print_header("SUMMARY")
    print("""
Next steps:
1. Review the report above for any ❌ MISSING items
2. Check error logs in PythonAnywhere
3. Verify WSGI configuration points to app.py
4. Ensure virtual environment has all required packages
5. Test key functionality (login, quiz, class creation)

For detailed restoration plan, see:
functionality_analysis_and_restoration_plan.md
    """)

if __name__ == "__main__":
    main()
