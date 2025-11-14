#!/usr/bin/env python3
"""
Change Admin Password
Quick script to update your admin password
"""

from app_with_auth import app, db, User
import getpass

def change_password():
    print("=" * 60)
    print("       CHANGE ADMIN PASSWORD")
    print("=" * 60)
    
    with app.app_context():
        # Get admin email
        email = input("\nEnter admin email: ").strip()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\n❌ User with email '{email}' not found!")
            print("\nAvailable admin accounts:")
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                print(f"  - {admin.email}")
            return
        
        if user.role != 'admin':
            print(f"\n❌ User '{email}' is not an admin!")
            print(f"   Role: {user.role}")
            return
        
        # Get new password
        print(f"\n✅ Found admin: {user.full_name}")
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("\n❌ Passwords don't match!")
            return
        
        if len(new_password) < 6:
            print("\n❌ Password must be at least 6 characters!")
            return
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ PASSWORD CHANGED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Email: {email}")
        print(f"New Password: {'*' * len(new_password)}")
        print("\nYou can now login with your new password!")
        print("=" * 60)

if __name__ == '__main__':
    try:
        change_password()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
