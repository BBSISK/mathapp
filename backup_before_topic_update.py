#!/usr/bin/env python3
"""
BACKUP SCRIPT - Run BEFORE Deploying Topic Configuration Update
================================================================
Creates timestamped backups of all files that will be modified.
Run this on PythonAnywhere BEFORE uploading any new files.
"""

import os
import shutil
from datetime import datetime

# Configuration
BASE_DIR = '/home/bbsisk/mathapp'
BACKUP_DIR = os.path.join(BASE_DIR, 'backups', f'topic_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

# Files to backup
FILES_TO_BACKUP = [
    'app.py',
    'templates/teacher_class_dashboard_v2.html',
    'templates/teacher_class_dashboard_v3.html',
    'templates/admin_dashboard.html',
    'templates/student_app.html',
    'templates/teacher_dashboard.html',
]

def create_backup():
    print("\n" + "=" * 70)
    print("BACKUP SCRIPT - Topic Configuration Update")
    print("=" * 70)
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"\n✓ Created backup directory: {BACKUP_DIR}")
    
    backed_up = []
    skipped = []
    
    for file_path in FILES_TO_BACKUP:
        source = os.path.join(BASE_DIR, file_path)
        if os.path.exists(source):
            # Create subdirectories in backup if needed
            dest_dir = os.path.dirname(os.path.join(BACKUP_DIR, file_path))
            os.makedirs(dest_dir, exist_ok=True)
            
            dest = os.path.join(BACKUP_DIR, file_path)
            shutil.copy2(source, dest)
            backed_up.append(file_path)
            print(f"  ✓ Backed up: {file_path}")
        else:
            skipped.append(file_path)
            print(f"  ⚠ Skipped (not found): {file_path}")
    
    # Create restore script
    restore_script = os.path.join(BACKUP_DIR, 'restore.py')
    with open(restore_script, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
"""
RESTORE SCRIPT - Rollback Topic Configuration Update
=====================================================
Restores files from this backup to their original locations.
"""

import os
import shutil

BASE_DIR = '/home/bbsisk/mathapp'
BACKUP_DIR = '{BACKUP_DIR}'

FILES_TO_RESTORE = {backed_up!r}

def restore():
    print("\\n" + "=" * 70)
    print("RESTORE SCRIPT - Rolling back Topic Configuration Update")
    print("=" * 70)
    
    for file_path in FILES_TO_RESTORE:
        source = os.path.join(BACKUP_DIR, file_path)
        dest = os.path.join(BASE_DIR, file_path)
        
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"  ✓ Restored: {{file_path}}")
        else:
            print(f"  ✗ ERROR: Backup not found: {{file_path}}")
    
    print("\\n" + "=" * 70)
    print("ROLLBACK COMPLETE")
    print("=" * 70)
    print("\\n⚠ IMPORTANT: Reload your web app in PythonAnywhere!")
    print("   Go to: Web tab → Click 'Reload'")
    print("=" * 70)

if __name__ == '__main__':
    restore()
''')
    
    print(f"\n  ✓ Created restore script: {restore_script}")
    
    # Summary
    print("\n" + "=" * 70)
    print("BACKUP COMPLETE")
    print("=" * 70)
    print(f"\n📁 Backup location: {BACKUP_DIR}")
    print(f"✓ Files backed up: {len(backed_up)}")
    if skipped:
        print(f"⚠ Files skipped: {len(skipped)}")
    
    print("\n📋 TO ROLLBACK (if needed):")
    print(f"   cd {BACKUP_DIR}")
    print("   python3 restore.py")
    print("=" * 70)
    
    return BACKUP_DIR

if __name__ == '__main__':
    create_backup()
