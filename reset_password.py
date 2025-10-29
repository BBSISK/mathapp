#!/usr/bin/env python3
"""
Reset User Password
This script allows you to reset any user's password
"""

from app import app, db, User

def list_users():
    """Display all users in the system"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in database")
            return
        
        print("\n" + "="*80)
        print("ALL USERS")
        print("="*80)
        print(f"{'ID':<5} {'Email':<35} {'Name':<25} {'Role':<10} {'Approved'}")
        print("-"*80)
        
        for user in users:
            approved = "✓" if user.is_approved else "✗"
            print(f"{user.id:<5} {user.email:<35} {user.full_name:<25} {user.role:<10} {approved}")
        
        print("="*80 + "\n")

def reset_user_password():
    """Reset password for a specific user"""
    
    print("\n" + "="*60)
    print("RESET USER PASSWORD")
    print("="*60 + "\n")
    
    # Show all users
    list_users()
    
    # Get user email
    email = input("Enter user email to reset: ").strip()
    if not email:
        print("❌ Error: Email cannot be empty")
        return
    
    with app.app_context():
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\n❌ Error: No user found with email: {email}")
            return
        
        print(f"\n📝 Found user: {user.full_name} ({user.role})")
        
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
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        print("\n✅ Password reset successfully!")
        print("\n" + "="*60)
        print("USER CREDENTIALS")
        print("="*60)
        print(f"Email:    {user.email}")
        print(f"Name:     {user.full_name}")
        print(f"Role:     {user.role}")
        print(f"Password: {new_password}")
        print("="*60 + "\n")

def reset_admin_only():
    """Quick reset for admin account only"""
    
    print("\n" + "="*60)
    print("RESET ADMIN PASSWORD")
    print("="*60 + "\n")
    
    with app.app_context():
        # Find admin
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            print("❌ Error: No admin account found")
            print("   Run: python quick_reset_admin.py to create one")
            return
        
        print(f"📝 Found admin: {admin.email}")
        
        # Get new password
        new_password = input("Enter new admin password: ").strip()
        if not new_password:
            print("❌ Error: Password cannot be empty")
            return
        
        # Confirm password
        confirm_password = input("Confirm password: ").strip()
        if new_password != confirm_password:
            print("❌ Error: Passwords do not match")
            return
        
        # Update password
        admin.set_password(new_password)
        db.session.commit()
        
        print("\n✅ Admin password reset successfully!")
        print("\n" + "="*60)
        print("ADMIN CREDENTIALS")
        print("="*60)
        print(f"Email:    {admin.email}")
        print(f"Name:     {admin.full_name}")
        print(f"Password: {new_password}")
        print("="*60 + "\n")

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("PASSWORD RESET TOOL")
    print("="*60)
    print("\n1. List all users")
    print("2. Reset any user password")
    print("3. Reset admin password only")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        list_users()
    elif choice == '2':
        reset_user_password()
    elif choice == '3':
        reset_admin_only()
    elif choice == '4':
        print("Goodbye!")
        return
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
