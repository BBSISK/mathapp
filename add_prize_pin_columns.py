#!/usr/bin/env python3
"""
Add Prize PIN Protection Columns

This script adds prize_pin and prize_pin_hint columns to:
- user_stats table (for registered users)
- guest_users table (for guest code users)

Also initializes the threshold setting if not set.

Run on PythonAnywhere:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python add_prize_pin_columns.py
"""

import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db, SystemSetting
from sqlalchemy import text

def add_columns():
    print("\n" + "="*60)
    print("  ADD PRIZE PIN COLUMNS")
    print("="*60)
    
    with app.app_context():
        # Check and add columns to user_stats
        print("\n📊 Checking user_stats table...")
        
        result = db.session.execute(text("PRAGMA table_info(user_stats)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'prize_pin' not in columns:
            print("  Adding prize_pin column...")
            db.session.execute(text("ALTER TABLE user_stats ADD COLUMN prize_pin VARCHAR(50)"))
            print("  ✓ prize_pin added")
        else:
            print("  ✓ prize_pin already exists")
        
        if 'prize_pin_hint' not in columns:
            print("  Adding prize_pin_hint column...")
            db.session.execute(text("ALTER TABLE user_stats ADD COLUMN prize_pin_hint VARCHAR(100)"))
            print("  ✓ prize_pin_hint added")
        else:
            print("  ✓ prize_pin_hint already exists")
        
        # Check and add columns to guest_users
        print("\n👤 Checking guest_users table...")
        
        result = db.session.execute(text("PRAGMA table_info(guest_users)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'prize_pin' not in columns:
            print("  Adding prize_pin column...")
            db.session.execute(text("ALTER TABLE guest_users ADD COLUMN prize_pin VARCHAR(50)"))
            print("  ✓ prize_pin added")
        else:
            print("  ✓ prize_pin already exists")
        
        if 'prize_pin_hint' not in columns:
            print("  Adding prize_pin_hint column...")
            db.session.execute(text("ALTER TABLE guest_users ADD COLUMN prize_pin_hint VARCHAR(100)"))
            print("  ✓ prize_pin_hint added")
        else:
            print("  ✓ prize_pin_hint already exists")
        
        db.session.commit()
        
        # Initialize threshold setting
        print("\n⚙️  Checking prize_pin_threshold setting...")
        current = SystemSetting.get('prize_pin_threshold', None)
        if current is None:
            SystemSetting.set(
                'prize_pin_threshold',
                '2000',
                'Points threshold for Prize Shop PIN protection',
                None
            )
            print("  ✓ Threshold set to 2000 points (default)")
        else:
            print(f"  ✓ Threshold already set: {current} points")
        
        # Verify final structure
        print("\n📋 Final table structures:")
        
        print("\n  user_stats columns:")
        result = db.session.execute(text("PRAGMA table_info(user_stats)")).fetchall()
        for row in result:
            print(f"    - {row[1]} ({row[2]})")
        
        print("\n  guest_users columns:")
        result = db.session.execute(text("PRAGMA table_info(guest_users)")).fetchall()
        for row in result:
            print(f"    - {row[1]} ({row[2]})")
        
        # Show users who would need PIN
        print("\n📊 Users above threshold:")
        threshold = int(SystemSetting.get('prize_pin_threshold', '2000'))
        
        # Registered users
        result = db.session.execute(text(f"""
            SELECT COUNT(*) FROM user_stats WHERE total_points >= {threshold}
        """)).fetchone()
        print(f"  - Registered users: {result[0]}")
        
        # Guest users
        result = db.session.execute(text(f"""
            SELECT COUNT(*) FROM guest_users WHERE total_score >= {threshold}
        """)).fetchone()
        print(f"  - Guest code users: {result[0]}")
        
        print("\n" + "="*60)
        print("✅ Prize PIN setup complete!")
        print("="*60)
        print("\nUsers above the threshold will be asked to set a PIN")
        print("when they next try to access the Prize Shop.")


if __name__ == '__main__':
    add_columns()
