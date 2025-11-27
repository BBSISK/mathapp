#!/usr/bin/env python3
"""
Fix Database Integrity Errors
Removes duplicate entries and ensures guest user exists
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix database integrity issues"""
    
    db_path = 'instance/mathquiz.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔧 Fixing database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Remove duplicate question_flags if they exist
        print("\n📋 Fixing question_flags duplicates...")
        try:
            cursor.execute("""
                DELETE FROM question_flags 
                WHERE rowid NOT IN (
                    SELECT MIN(rowid) 
                    FROM question_flags 
                    GROUP BY question_id, user_id, guest_identifier, guest_email
                )
            """)
            deleted = cursor.rowcount
            print(f"✅ Removed {deleted} duplicate question_flags")
        except Exception as e:
            print(f"Note: {e}")
        
        # Fix 2: Ensure guest user exists
        print("\n📋 Checking guest user...")
        cursor.execute("SELECT id FROM users WHERE email = 'guest@agentmath.app'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ Guest user exists (ID: {existing[0]})")
        else:
            print("➕ Creating guest user...")
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
            print(f"✅ Guest user created (ID: {cursor.lastrowid})")
        
        # Fix 3: Ensure guest_sessions table exists
        print("\n📋 Checking guest_sessions table...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='guest_sessions'
        """)
        
        if cursor.fetchone():
            print("✅ guest_sessions table exists")
        else:
            print("➕ Creating guest_sessions table...")
            cursor.execute("""
                CREATE TABLE guest_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    quiz_attempts INTEGER DEFAULT 0
                )
            """)
            print("✅ guest_sessions table created")
        
        # Fix 4: Add is_guest column if needed
        print("\n📋 Checking quiz_attempts table...")
        cursor.execute("PRAGMA table_info(quiz_attempts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_guest' not in columns:
            print("➕ Adding is_guest column...")
            cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN is_guest BOOLEAN DEFAULT 0")
            print("✅ is_guest column added")
        else:
            print("✅ is_guest column exists")
        
        # Commit all changes
        print("\n💾 Saving changes...")
        conn.commit()
        
        print("\n" + "="*50)
        print("✅ DATABASE FIXED SUCCESSFULLY!")
        print("="*50)
        print("\nYou can now reload your Flask app.")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*50)
    print("AgentMath.app - Database Fix Script")
    print("="*50)
    print()
    
    success = fix_database()
    
    if success:
        print("\n✅ Database fixed! Reload your app now.")
        exit(0)
    else:
        print("\n❌ Fix failed. Check errors above.")
        exit(1)
