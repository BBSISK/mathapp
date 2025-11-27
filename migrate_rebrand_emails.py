#!/usr/bin/env python3
"""
AgentMath.app - Database Migration Script for Rebranding
=========================================================

This script updates user email addresses in the database from the old
MathMaster branding to the new AgentMath.app branding.

Run this AFTER deploying the updated code files.

Usage:
    python migrate_rebrand_emails.py

Changes:
    - guest@mathmaster.app -> guest@agentmath.app
    - admin@mathmaster.com -> admin@agentmath.app
"""

from app import app, db, User
from sqlalchemy import text

def migrate_emails():
    with app.app_context():
        print("=" * 60)
        print("AgentMath.app - Email Migration Script")
        print("=" * 60)
        
        # Check current state
        print("\n📊 Current state:")
        
        old_guest = User.query.filter_by(email='guest@mathmaster.app').first()
        old_admin = User.query.filter_by(email='admin@mathmaster.com').first()
        new_guest = User.query.filter_by(email='guest@agentmath.app').first()
        new_admin = User.query.filter_by(email='admin@agentmath.app').first()
        
        print(f"   guest@mathmaster.app exists: {old_guest is not None}")
        print(f"   admin@mathmaster.com exists: {old_admin is not None}")
        print(f"   guest@agentmath.app exists: {new_guest is not None}")
        print(f"   admin@agentmath.app exists: {new_admin is not None}")
        
        changes_made = False
        
        # Migrate guest user
        if old_guest and not new_guest:
            print(f"\n🔄 Migrating guest user...")
            old_guest.email = 'guest@agentmath.app'
            db.session.commit()
            print(f"   ✅ guest@mathmaster.app -> guest@agentmath.app")
            changes_made = True
        elif old_guest and new_guest:
            print(f"\n⚠️  Both old and new guest accounts exist!")
            print(f"   You may need to manually resolve this.")
        elif new_guest:
            print(f"\n✅ Guest user already migrated (guest@agentmath.app)")
        else:
            print(f"\n⚠️  No guest user found - will be created on first guest login")
        
        # Migrate admin user
        if old_admin and not new_admin:
            print(f"\n🔄 Migrating admin user...")
            old_admin.email = 'admin@agentmath.app'
            db.session.commit()
            print(f"   ✅ admin@mathmaster.com -> admin@agentmath.app")
            changes_made = True
        elif old_admin and new_admin:
            print(f"\n⚠️  Both old and new admin accounts exist!")
            print(f"   You may need to manually resolve this.")
        elif new_admin:
            print(f"\n✅ Admin user already migrated (admin@agentmath.app)")
        else:
            print(f"\n⚠️  No admin user found - will be created on app start")
        
        # Final verification
        print("\n" + "=" * 60)
        print("📊 Final state:")
        
        new_guest = User.query.filter_by(email='guest@agentmath.app').first()
        new_admin = User.query.filter_by(email='admin@agentmath.app').first()
        
        print(f"   guest@agentmath.app exists: {new_guest is not None}")
        print(f"   admin@agentmath.app exists: {new_admin is not None}")
        
        if changes_made:
            print("\n✅ Migration complete!")
        else:
            print("\n✅ No changes needed - already migrated or clean state.")
        
        print("=" * 60)

if __name__ == "__main__":
    migrate_emails()
