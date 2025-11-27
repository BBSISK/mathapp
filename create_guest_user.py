#!/usr/bin/env python3
"""
Quick Guest User Setup
Creates the guest user in your database
"""

import sqlite3
from datetime import datetime
import os

def create_guest_user():
    db_path = 'instance/mathquiz.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Are you in the right directory?")
        return False
    
    print("🔧 Creating guest user...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if guest user exists
        cursor.execute("SELECT id FROM users WHERE email = 'guest@agentmath.app'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ Guest user already exists (ID: {existing[0]})")
            return True
        
        # Create guest user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role, is_approved, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'guest@agentmath.app',
            'no_password_required',
            'Guest User',
            'student',
            1,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        guest_id = cursor.lastrowid
        
        print(f"✅ Guest user created successfully!")
        print(f"   Email: guest@agentmath.app")
        print(f"   ID: {guest_id}")
        print(f"   Role: student")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*50)
    print("Guest User Setup")
    print("="*50)
    print()
    
    if create_guest_user():
        print()
        print("="*50)
        print("✅ DONE!")
        print("="*50)
        print()
        print("Next step: Update guest routes in app.py")
        print("See SIMPLE_FIX_INSTRUCTIONS.txt")
    else:
        print()
        print("❌ Failed. Check the error above.")
