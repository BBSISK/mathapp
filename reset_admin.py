#!/usr/bin/env python3
"""
Reset Admin Email and Password
This script resets the admin account credentials
"""

from app import app, db, User

def reset_admin():
    """Reset admin account with new credentials"""
    
    print("\n" + "="*60)
    print("ADMIN ACCOUNT RESET")
    print("="*60 + "\n")
    
    # Get new email
    new_email = input("Enter new admin email: ").strip()
    if not new_email:
        print("❌ Error: Email cannot be empty")
        return
    
    # Get new name
    new_name = input("Enter admin full name: ").strip()
    if not new_name:
        print("❌ Error: Name cannot be empty")
        return
    
    # Get new password
    new_password = input("Enter new password: ").strip()
    if not new_password:
        print("❌ Error: Password cannot be empty")
        return
    
    # Confirm password
    confirm_password = input("Confirm password: ").strip()
    if new_password != confirm_password:
        print("❌ Error: Passwords do not match")
        return
    
    with app.app_context():
        # Find existing admin account
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            print(f"\n📝 Found existing admin: {admin.email}")
            print(f"   Updating to: {new_email}")
            
            # Update existing admin
            admin.email = new_email
            admin.full_name = new_name
            admin.set_password(new_password)
            
            db.session.commit()
            print("\n✅ Admin account updated successfully!")
        else:
            print("\n📝 No admin found. Creating new admin account...")
            
            # Create new admin
            admin = User(
                email=new_email,
                full_name=new_name,
                role='admin',
                is_approved=True
            )
            admin.set_password(new_password)
            
            db.session.add(admin)
            db.session.commit()
            print("\n✅ New admin account created successfully!")
        
        print("\n" + "="*60)
        print("NEW ADMIN CREDENTIALS")
        print("="*60)
        print(f"Email:    {new_email}")
        print(f"Name:     {new_name}")
        print(f"Password: {new_password}")
        print("="*60 + "\n")
        
        print("⚠️  IMPORTANT:")
        print("   - Keep these credentials safe")
        print("   - Consider changing password after first login")
        print("   - Use a strong password for production")
        print()

if __name__ == '__main__':
    reset_admin()
