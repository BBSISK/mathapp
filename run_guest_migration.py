#!/usr/bin/env python3
"""
Guest Mode Database Migration Script
Run this to add guest user support to your AgentMath.app database.
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add guest user and session tracking to database"""
    
    # Path to your database - update if needed
    db_path = 'instance/mathquiz.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Database not found at {db_path}")
        print("Please update the db_path variable in this script.")
        return False
    
    print(f"🔧 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Check if guest user already exists
        print("\n📋 Step 1: Checking for existing guest user...")
        cursor.execute("SELECT id FROM users WHERE email = 'guest@agentmath.app'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ Guest user already exists (ID: {existing[0]})")
            guest_id = existing[0]
        else:
            # Create guest user
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
            guest_id = cursor.lastrowid
            print(f"✅ Guest user created (ID: {guest_id})")
        
        # Step 2: Check if guest_sessions table exists
        print("\n📋 Step 2: Checking guest_sessions table...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='guest_sessions'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ guest_sessions table already exists")
        else:
            # Create guest_sessions table
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
        
        # Step 3: Add is_guest column to quiz_attempts if needed
        print("\n📋 Step 3: Checking quiz_attempts table...")
        cursor.execute("PRAGMA table_info(quiz_attempts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_guest' not in columns:
            print("➕ Adding is_guest column to quiz_attempts...")
            cursor.execute("""
                ALTER TABLE quiz_attempts 
                ADD COLUMN is_guest BOOLEAN DEFAULT 0
            """)
            print("✅ is_guest column added")
        else:
            print("✅ is_guest column already exists")
        
        # Step 4: Commit all changes
        print("\n💾 Saving changes to database...")
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Summary
        print("\n" + "="*50)
        print("✨ MIGRATION COMPLETE ✨")
        print("="*50)
        print(f"Guest User ID: {guest_id}")
        print(f"Guest Email: guest@agentmath.app")
        print("\nYour database is now ready for guest mode!")
        print("You can now restart your Flask app.")
        print("="*50)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*50)
    print("AgentMath.app - Guest Mode Migration")
    print("="*50)
    print()
    
    success = run_migration()
    
    if not success:
        print("\n⚠️  Migration failed. Please check the errors above.")
        exit(1)
    else:
        print("\n✅ You can now run your Flask app with guest support!")
        exit(0)
