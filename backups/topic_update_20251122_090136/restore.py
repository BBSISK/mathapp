#!/usr/bin/env python3
"""
RESTORE SCRIPT - Rollback Topic Configuration Update
=====================================================
Restores files from this backup to their original locations.
"""

import os
import shutil

BASE_DIR = '/home/bbsisk/mathapp'
BACKUP_DIR = '/home/bbsisk/mathapp/backups/topic_update_20251122_090136'

FILES_TO_RESTORE = ['app.py', 'templates/teacher_class_dashboard_v2.html', 'templates/teacher_class_dashboard_v3.html', 'templates/admin_dashboard.html', 'templates/student_app.html', 'templates/teacher_dashboard.html']

def restore():
    print("\n" + "=" * 70)
    print("RESTORE SCRIPT - Rolling back Topic Configuration Update")
    print("=" * 70)
    
    for file_path in FILES_TO_RESTORE:
        source = os.path.join(BACKUP_DIR, file_path)
        dest = os.path.join(BASE_DIR, file_path)
        
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"  ✓ Restored: {file_path}")
        else:
            print(f"  ✗ ERROR: Backup not found: {file_path}")
    
    print("\n" + "=" * 70)
    print("ROLLBACK COMPLETE")
    print("=" * 70)
    print("\n⚠ IMPORTANT: Reload your web app in PythonAnywhere!")
    print("   Go to: Web tab → Click 'Reload'")
    print("=" * 70)

if __name__ == '__main__':
    restore()
