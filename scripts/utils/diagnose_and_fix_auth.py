"""
DIAGNOSE AND FIX AUTH ISSUES
Checks database, creates tables, creates test users
"""

from app import app, db, User

def diagnose_and_fix():
    with app.app_context():
        print("=" * 70)
        print("AUTHENTICATION DIAGNOSIS & FIX")
        print("=" * 70)
        
        # Step 1: Check database tables
        print("\n1. Checking database tables...")
        try:
            user_count = User.query.count()
            print(f"   ✅ Users table exists - {user_count} users found")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            print("\n   Creating all tables...")
            db.create_all()
            print("   ✅ Tables created!")
            user_count = 0
        
        # Step 2: Create test users if none exist
        print(f"\n2. Creating test users...")
        
        # Create admin
        admin = User.query.filter_by(email='admin@agentmath.app').first()
        if not admin:
            admin = User(
                email='admin@agentmath.app',
                full_name='Admin User',
                role='admin',
                is_approved=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("   ✅ Admin created: admin@agentmath.app / admin123")
        else:
            print("   ℹ️  Admin already exists")
        
        # Create test student
        student = User.query.filter_by(email='student@test.com').first()
        if not student:
            student = User(
                email='student@test.com',
                full_name='Test Student',
                role='student',
                is_approved=True
            )
            student.set_password('student123')
            db.session.add(student)
            print("   ✅ Student created: student@test.com / student123")
        else:
            print("   ℹ️  Test student already exists")
        
        # Create test teacher
        teacher = User.query.filter_by(email='teacher@test.com').first()
        if not teacher:
            teacher = User(
                email='teacher@test.com',
                full_name='Test Teacher',
                role='teacher',
                is_approved=True
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            print("   ✅ Teacher created: teacher@test.com / teacher123")
        else:
            print("   ℹ️  Test teacher already exists")
        
        db.session.commit()
        
        # Step 3: Verify routes
        print(f"\n3. Checking routes...")
        routes = []
        for rule in app.url_map.iter_rules():
            if any(x in str(rule) for x in ['login', 'register', 'logout']):
                routes.append(f"   {rule.methods} {rule}")
        
        if routes:
            print("   ✅ Auth routes found:")
            for route in routes:
                print(route)
        else:
            print("   ❌ No auth routes found!")
        
        # Step 4: Final summary
        print("\n" + "=" * 70)
        print("DIAGNOSIS COMPLETE")
        print("=" * 70)
        
        total_users = User.query.count()
        print(f"\n📊 Total users in database: {total_users}")
        
        if total_users > 0:
            print("\n🎉 SUCCESS! Database is ready.")
            print("\n📝 Test Accounts:")
            print("   Admin:    admin@agentmath.app / admin123")
            print("   Student:  student@test.com / student123")
            print("   Teacher:  teacher@test.com / teacher123")
            print("\n⚠️  If login still doesn't work:")
            print("   1. Check browser console for errors (F12)")
            print("   2. Clear browser cache (Ctrl+Shift+Delete)")
            print("   3. Make sure you're accessing the correct URL")
            print("   4. Check that Flask session is working (secret key set)")
        else:
            print("\n❌ No users created - there may be a database issue")
        
        print("\n" + "=" * 70)

if __name__ == '__main__':
    diagnose_and_fix()
