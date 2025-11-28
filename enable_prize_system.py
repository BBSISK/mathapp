#!/usr/bin/env python3
"""
Enable Prize System Script
This script enables the prize system feature flag and verifies the setup
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def enable_feature_flag():
    """Enable the PRIZE_SYSTEM_ENABLED feature flag"""
    print("=" * 60)
    print("ENABLING PRIZE SYSTEM")
    print("=" * 60)
    
    print("\nTo enable the prize system, you need to set the environment variable:")
    print("\n  PRIZE_SYSTEM_ENABLED=true")
    print("\nDepending on your deployment:")
    print("\n1. For local development (.env file):")
    print("   Add this line to your .env file:")
    print("   PRIZE_SYSTEM_ENABLED=true")
    
    print("\n2. For Render.com:")
    print("   - Go to your service dashboard")
    print("   - Navigate to 'Environment' tab")
    print("   - Add environment variable:")
    print("     Key: PRIZE_SYSTEM_ENABLED")
    print("     Value: true")
    print("   - Click 'Save Changes' and redeploy")
    
    print("\n3. For Heroku:")
    print("   heroku config:set PRIZE_SYSTEM_ENABLED=true -a your-app-name")
    
    print("\n4. For direct Python execution:")
    print("   export PRIZE_SYSTEM_ENABLED=true  # Linux/Mac")
    print("   set PRIZE_SYSTEM_ENABLED=true     # Windows")
    
    print("\n" + "=" * 60)

def check_current_status():
    """Check if the feature flag is currently enabled"""
    from app import app, FEATURE_FLAGS
    
    print("\nCurrent Status:")
    print("-" * 60)
    
    with app.app_context():
        is_enabled = FEATURE_FLAGS.get('PRIZE_SYSTEM_ENABLED', False)
        env_value = os.environ.get('PRIZE_SYSTEM_ENABLED', 'not set')
        
        print(f"Environment Variable: {env_value}")
        print(f"Feature Flag Value: {is_enabled}")
        
        if is_enabled:
            print("\n✓ Prize system is ENABLED")
            return True
        else:
            print("\n✗ Prize system is DISABLED")
            return False

def verify_database():
    """Verify database tables exist"""
    from app import app, db
    from sqlalchemy import inspect
    
    print("\nDatabase Tables:")
    print("-" * 60)
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'prizes',
            'prize_schools', 
            'school_prizes',
            'prize_redemptions',
            'prize_school_requests'
        ]
        
        all_exist = True
        for table in required_tables:
            exists = table in tables
            symbol = "✓" if exists else "✗"
            print(f"{symbol} {table}")
            if not exists:
                all_exist = False
        
        return all_exist

def create_sample_prizes():
    """Optionally create some sample prizes for testing"""
    from app import app, db, Prize
    
    print("\nSample Prizes Setup:")
    print("-" * 60)
    
    with app.app_context():
        existing = Prize.query.count()
        
        if existing > 0:
            print(f"✓ {existing} prizes already exist in the database")
            return
        
        response = input("\nNo prizes found. Would you like to create sample prizes? (y/n): ")
        
        if response.lower() != 'y':
            print("Skipped sample prize creation")
            return
        
        sample_prizes = [
            # Bronze Tier
            {
                'name': 'Pencil Set',
                'description': 'Pack of 3 quality pencils',
                'emoji': '✏️',
                'tier': 'bronze',
                'base_point_cost': 20,
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Eraser',
                'description': 'Quality rubber eraser',
                'emoji': '🧹',
                'tier': 'bronze',
                'base_point_cost': 15,
                'is_active': True,
                'sort_order': 2
            },
            # Silver Tier
            {
                'name': 'Notebook',
                'description': 'A5 ruled notebook',
                'emoji': '📓',
                'tier': 'silver',
                'base_point_cost': 50,
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Calculator',
                'description': 'Basic scientific calculator',
                'emoji': '🔢',
                'tier': 'silver',
                'base_point_cost': 75,
                'is_active': True,
                'sort_order': 2
            },
            # Gold Tier
            {
                'name': 'Headphones',
                'description': 'Quality over-ear headphones',
                'emoji': '🎧',
                'tier': 'gold',
                'base_point_cost': 150,
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Book Voucher',
                'description': '€20 book voucher',
                'emoji': '📚',
                'tier': 'gold',
                'base_point_cost': 120,
                'is_active': True,
                'sort_order': 2
            },
            # Platinum Tier
            {
                'name': 'Wireless Earbuds',
                'description': 'Premium wireless earbuds',
                'emoji': '🎵',
                'tier': 'platinum',
                'base_point_cost': 300,
                'is_active': True,
                'sort_order': 1,
                'minimum_level': 10
            }
        ]
        
        for prize_data in sample_prizes:
            prize = Prize(**prize_data)
            db.session.add(prize)
        
        db.session.commit()
        print(f"✓ Created {len(sample_prizes)} sample prizes")

def main():
    print("\n" + "=" * 60)
    print("PRIZE SYSTEM SETUP")
    print("=" * 60)
    
    # Check current status
    is_enabled = check_current_status()
    
    # Verify database
    tables_ok = verify_database()
    
    if not tables_ok:
        print("\n⚠️  WARNING: Some database tables are missing")
        print("Run the setup_prize_system.py script first to create tables")
        return
    
    # Optionally create sample prizes
    if is_enabled:
        create_sample_prizes()
    
    # Show how to enable if not enabled
    if not is_enabled:
        print("\n" + "=" * 60)
        enable_feature_flag()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    if is_enabled:
        print("\n✓ Prize system is enabled and ready!")
        print("\n1. Access the admin dashboard at /admin/prizes")
        print("2. Add your school(s) to the system")
        print("3. Configure prizes and point costs")
        print("4. Students can then access the prize shop at /prizes")
    else:
        print("\n1. Set PRIZE_SYSTEM_ENABLED=true (see instructions above)")
        print("2. Restart your application")
        print("3. Run this script again to verify")
        print("4. Access admin dashboard to configure prizes")
    
    print()

if __name__ == '__main__':
    main()
