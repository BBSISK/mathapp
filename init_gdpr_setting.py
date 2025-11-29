#!/usr/bin/env python3
"""
Initialize GDPR Login Setting

This script sets FULL_ACCOUNT_LOGIN_ENABLED to 'false' in the database.
Run once after deploying the new code.

Run on PythonAnywhere:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python init_gdpr_setting.py
"""

import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db, SystemSetting

def init_setting():
    with app.app_context():
        # Check current value
        current = SystemSetting.get('FULL_ACCOUNT_LOGIN_ENABLED', None)
        print(f"Current value: {current}")
        
        if current is None:
            # Set initial value
            SystemSetting.set(
                'FULL_ACCOUNT_LOGIN_ENABLED',
                'false',
                'Enable full account login on the login page (GDPR compliance)',
                None
            )
            print("✓ Setting initialized to: false")
        else:
            print(f"✓ Setting already exists: {current}")
        
        # Verify
        final = SystemSetting.get('FULL_ACCOUNT_LOGIN_ENABLED', 'not found')
        print(f"\nFinal value in database: {final}")
        print("\nFull account login is now HIDDEN on the login page.")
        print("Admin can enable it via Admin Dashboard > Site Settings.")

if __name__ == '__main__':
    init_setting()
