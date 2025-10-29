#!/usr/bin/env python3
"""
Quick Admin Reset - Preset Credentials
Sets admin to barry.sisk@palmerstowncs.ie with a secure password
"""

from app import app, db, User

def quick_reset_admin():
    """Reset admin to Palmerstown CS credentials"""
    
    # Preset credentials for Palmerstown Community School
    ADMIN_EMAIL = 'barry.sisk@palmerstowncs.ie'
    ADMIN_NAME = 'Barry Sisk'
    ADMIN_PASSWORD = 'PCS2025!Admin'  # Change this to your desired password
    
    print("\n" + "="*60)
    print("QUICK ADMIN RESET - PALMERSTOWN CS")
    print("="*60 + "\n")
    
    with app.app_context():
        # Find any existing admin
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            print(f"📝 Found existing admin: {admin.email}")
            print(f"   Resetting to: {ADMIN_EMAIL}")
            
            # Update existing admin
            admin.email = ADMIN_EMAIL
            admin.full_name = ADMIN_NAME
            admin.set_password(ADMIN_PASSWORD)
            
            db.session.commit()
            print("\n✅ Admin account reset successfully!")
        else:
            print("📝 No admin found. Creating new admin account...")
            
            # Create new admin
            admin = User(
                email=ADMIN_EMAIL,
                full_name=ADMIN_NAME,
                role='admin',
                is_approved=True
            )
            admin.set_password(ADMIN_PASSWORD)
            
            db.session.add(admin)
            db.session.commit()
            print("\n✅ New admin account created successfully!")
        
        print("\n" + "="*60)
        print("ADMIN CREDENTIALS")
        print("="*60)
        print(f"Email:    {ADMIN_EMAIL}")
        print(f"Name:     {ADMIN_NAME}")
        print(f"Password: {ADMIN_PASSWORD}")
        print("="*60 + "\n")
        
        print("✅ You can now login with these credentials")
        print("🔗 Visit: http://127.0.0.1:5000")
        print("\n⚠️  Remember to change the password after first login!\n")

if __name__ == '__main__':
    quick_reset_admin()
