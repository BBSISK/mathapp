#!/usr/bin/env python3
"""
Prize System Diagnostic Script
Checks the status of the prize system and identifies issues
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db, Prize, PrizeSchool, SystemSetting

def check_feature_flag():
    """Check if prize system feature flag is enabled"""
    print("\n=== FEATURE FLAG STATUS ===")
    env_value = os.environ.get('PRIZE_SYSTEM_ENABLED', 'false')
    print(f"Environment Variable PRIZE_SYSTEM_ENABLED: {env_value}")
    
    with app.app_context():
        from app import FEATURE_FLAGS
        flag_value = FEATURE_FLAGS.get('PRIZE_SYSTEM_ENABLED', False)
        print(f"Runtime Feature Flag: {flag_value}")
        
        if not flag_value:
            print("\n⚠️  WARNING: Prize system is DISABLED")
            print("To enable it, set environment variable: PRIZE_SYSTEM_ENABLED=true")
            return False
        else:
            print("✓ Prize system is ENABLED")
            return True

def check_database_tables():
    """Check if prize system tables exist"""
    print("\n=== DATABASE TABLES ===")
    
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['prizes', 'prize_schools', 'school_prizes', 'prize_redemptions', 'prize_school_requests']
        
        for table in required_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' MISSING")
        
        # Check if all tables exist
        return all(table in tables for table in required_tables)

def check_prizes():
    """Check if any prizes exist in the database"""
    print("\n=== PRIZE CATALOGUE ===")
    
    with app.app_context():
        prizes = Prize.query.all()
        
        if not prizes:
            print("✗ NO PRIZES in the database")
            print("You need to add prizes through the admin dashboard")
            return False
        else:
            print(f"✓ Found {len(prizes)} prizes in the catalogue")
            
            active_prizes = Prize.query.filter_by(is_active=True).all()
            print(f"  - {len(active_prizes)} active prizes")
            print(f"  - {len(prizes) - len(active_prizes)} inactive prizes")
            
            print("\nPrizes by tier:")
            for tier in ['bronze', 'silver', 'gold', 'platinum']:
                tier_prizes = [p for p in prizes if p.tier == tier]
                print(f"  - {tier.capitalize()}: {len(tier_prizes)} prizes")
            
            return True

def check_schools():
    """Check if any schools exist"""
    print("\n=== PRIZE SCHOOLS ===")
    
    with app.app_context():
        schools = PrizeSchool.query.all()
        
        if not schools:
            print("✗ NO SCHOOLS registered")
            print("Students won't be able to redeem prizes without selecting a school")
            return False
        else:
            print(f"✓ Found {len(schools)} registered schools")
            
            active_schools = PrizeSchool.query.filter_by(is_active=True).all()
            print(f"  - {len(active_schools)} active schools")
            print(f"  - {len(schools) - len(active_schools)} inactive schools")
            
            return True

def check_system_settings():
    """Check prize system settings"""
    print("\n=== SYSTEM SETTINGS ===")
    
    with app.app_context():
        multiplier = SystemSetting.get('global_points_multiplier', '5.0')
        level_lock = SystemSetting.get('prize_level_lock_enabled', 'false')
        
        print(f"Global Points Multiplier: {multiplier}x")
        print(f"Level Lock Enabled: {level_lock}")

def main():
    print("=" * 60)
    print("PRIZE SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    # Run all checks
    flag_ok = check_feature_flag()
    tables_ok = check_database_tables()
    prizes_ok = check_prizes()
    schools_ok = check_schools()
    check_system_settings()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_ok = flag_ok and tables_ok and prizes_ok
    
    if all_ok:
        print("✓ Prize system appears to be configured correctly!")
        if not schools_ok:
            print("⚠️  No schools registered - students should add schools")
    else:
        print("\n⚠️  Issues detected:")
        if not flag_ok:
            print("  1. Enable the prize system feature flag")
        if not tables_ok:
            print("  2. Run database migrations to create tables")
        if not prizes_ok:
            print("  3. Add prizes through the admin dashboard")
        
        print("\nNext steps:")
        print("  1. Run: python setup_prize_system.py")
        print("  2. Access admin dashboard to add prizes")
        print("  3. Set PRIZE_SYSTEM_ENABLED=true in environment")

if __name__ == '__main__':
    main()
