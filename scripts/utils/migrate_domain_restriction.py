#!/usr/bin/env python3
"""
Database Migration: Add Domain Restriction Tables
Run this script to add the domain restriction feature to your database
"""

from app import app, db
from datetime import datetime
import sys

def run_migration():
    """Add domain restriction tables to the database"""
    
    with app.app_context():
        print("🔄 Starting database migration for domain restriction...")
        
        try:
            # Create the tables using raw SQL to avoid import issues
            with db.engine.connect() as conn:
                # Create teacher_domain_access table
                print("📝 Creating teacher_domain_access table...")
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS teacher_domain_access (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        teacher_id INTEGER NOT NULL,
                        email_domain VARCHAR(100) NOT NULL,
                        granted_by INTEGER NOT NULL,
                        granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (teacher_id) REFERENCES users(id),
                        FOREIGN KEY (granted_by) REFERENCES users(id),
                        UNIQUE (teacher_id, email_domain)
                    )
                """))
                conn.commit()
                print("✅ teacher_domain_access table created")
                
                # Create domain_access_requests table
                print("📝 Creating domain_access_requests table...")
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS domain_access_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        teacher_id INTEGER NOT NULL,
                        email_domain VARCHAR(100) NOT NULL,
                        reason TEXT NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        reviewed_by INTEGER,
                        reviewed_at DATETIME,
                        admin_notes TEXT,
                        FOREIGN KEY (teacher_id) REFERENCES users(id),
                        FOREIGN KEY (reviewed_by) REFERENCES users(id)
                    )
                """))
                conn.commit()
                print("✅ domain_access_requests table created")
                
                # Create indexes for better performance
                print("📝 Creating indexes...")
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_teacher_domain_teacher 
                    ON teacher_domain_access(teacher_id)
                """))
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_teacher_domain_domain 
                    ON teacher_domain_access(email_domain)
                """))
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_domain_requests_teacher 
                    ON domain_access_requests(teacher_id)
                """))
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_domain_requests_status 
                    ON domain_access_requests(status)
                """))
                conn.commit()
                print("✅ Indexes created")
            
            print("\n✨ Migration completed successfully!")
            print("\n📋 Next steps:")
            print("1. Add the domain models to your app.py (copy from domain_models.py)")
            print("2. Add the helper functions (copy from domain_helpers.py)")
            print("3. Add the admin API routes (copy from admin_domain_routes.py)")
            print("4. Add the teacher API routes (copy from teacher_domain_routes.py)")
            print("5. Update existing teacher routes with domain filtering")
            print("6. Add the admin UI template")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            print("\nThis might be because:")
            print("- The tables already exist")
            print("- There's a database lock")
            print("- The database file doesn't exist")
            print("\nTry stopping the app first, then run this migration.")
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
