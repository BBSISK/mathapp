#!/usr/bin/env python3
"""
Change Admin Email and Password
This script updates the default admin account to use your email
"""

from app_with_auth import app, db, User

def change_admin():
    with app.app_context():
        # Find the default admin
        admin = User.query.filter_by(email='admin@agentmath.app').first()
        
        if admin:
            # Update email and password
            admin.email = 'barry.sisk@palmerstowncs.ie'
            admin.full_name = 'Barry Sisk'
            admin.set_password('admin123')  # Change this to your secure password
            
            db.session.commit()
            print("✅ Admin account updated successfully!")
            print(f"Email: barry.sisk@palmerstowncs.ie")
            print(f"Password: admin123")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
        else:
            # Create new admin if default doesn't exist
            new_admin = User(
                email='barry.sisk@palmerstowncs.ie',
                full_name='Barry Sisk',
                role='admin',
                is_approved=True
            )
            new_admin.set_password('admin123')  # Change this to your secure password
            
            db.session.add(new_admin)
            db.session.commit()
            print("✅ New admin account created!")
            print(f"Email: barry.sisk@palmerstowncs.ie")
            print(f"Password: admin123")
            print("\n⚠️  IMPORTANT: Change the password after first login!")

if __name__ == '__main__':
    change_admin()
