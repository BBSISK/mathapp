#!/usr/bin/env python3
"""
Avatar System Rollback Script
=============================

Emergency rollback script for the avatar feature.
Use this to disable or completely remove the avatar system.

USAGE:
    python rollback_avatar_feature.py status   - Show current status
    python rollback_avatar_feature.py disable  - Show how to disable UI
    python rollback_avatar_feature.py backup   - Backup all avatar data
    python rollback_avatar_feature.py remove   - Remove tables (backs up first)

The 'disable' option is the safest and fastest way to hide the avatar system.
The 'remove' option will permanently delete all avatar data after backing up.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/mathquiz.db'


def show_status():
    """Show current avatar system status"""
    
    print("\n" + "=" * 60)
    print("AVATAR SYSTEM STATUS")
    print("=" * 60 + "\n")
    
    # Check feature flag
    avatar_enabled = os.environ.get('AVATAR_SYSTEM_ENABLED', 'false').lower() == 'true'
    print(f"Feature Flag (AVATAR_SYSTEM_ENABLED): {'✅ ENABLED' if avatar_enabled else '🛑 DISABLED'}")
    print()
    
    # Check database tables
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['avatar_items', 'user_avatar_inventory', 'user_avatar_equipped', 'avatar_purchase_log']
    
    print("Database Tables:")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} rows")
        except sqlite3.OperationalError:
            print(f"   ❌ {table}: NOT FOUND")
    
    # Check for any purchases
    try:
        cursor.execute("SELECT COUNT(*) FROM avatar_purchase_log")
        purchases = cursor.fetchone()[0]
        if purchases > 0:
            print(f"\n⚠️  Warning: {purchases} purchases have been made")
            print("   Consider backing up before any destructive operations")
    except:
        pass
    
    # Check for equipped avatars
    try:
        cursor.execute("SELECT COUNT(*) FROM user_avatar_equipped")
        equipped = cursor.fetchone()[0]
        if equipped > 0:
            print(f"   {equipped} users have customized avatars")
    except:
        pass
    
    conn.close()
    print()


def disable_feature():
    """
    Show how to disable avatar UI instantly.
    This doesn't delete any data - just hides the feature.
    """
    
    print("\n" + "=" * 60)
    print("HOW TO DISABLE AVATAR SYSTEM")
    print("=" * 60 + "\n")
    
    print("To disable the avatar system, set this environment variable:\n")
    print("   AVATAR_SYSTEM_ENABLED=false")
    print()
    print("Methods to set this:")
    print()
    print("1. In your .env file:")
    print("   AVATAR_SYSTEM_ENABLED=false")
    print()
    print("2. In PythonAnywhere web app environment:")
    print("   Go to Web tab → Environment variables")
    print("   Set AVATAR_SYSTEM_ENABLED = false")
    print()
    print("3. In app.py, change the default:")
    print("   'AVATAR_SYSTEM_ENABLED': os.environ.get('AVATAR_SYSTEM_ENABLED', 'false').lower() == 'true',")
    print("   (The 'false' default means it's disabled unless explicitly enabled)")
    print()
    print("After setting the flag, restart your web app.")
    print()
    print("✅ This is the SAFEST and FASTEST way to disable avatars.")
    print("   All data is preserved and can be re-enabled anytime.")
    print()


def backup_data():
    """Backup all avatar data to SQL file"""
    
    print("\n" + "=" * 60)
    print("BACKING UP AVATAR DATA")
    print("=" * 60 + "\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'avatar_backup_{timestamp}.sql'
    
    conn = sqlite3.connect(DB_PATH)
    
    tables = ['avatar_items', 'user_avatar_inventory', 'user_avatar_equipped', 'avatar_purchase_log']
    
    with open(backup_file, 'w') as f:
        f.write(f"-- Avatar System Backup\n")
        f.write(f"-- Created: {datetime.now().isoformat()}\n")
        f.write(f"-- Database: {DB_PATH}\n\n")
        
        for table in tables:
            try:
                # Get table schema
                cursor = conn.cursor()
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                schema = cursor.fetchone()
                
                if schema:
                    f.write(f"-- Table: {table}\n")
                    f.write(f"{schema[0]};\n\n")
                    
                    # Get all data
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, str):
                                values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                            else:
                                values.append(str(val))
                        
                        f.write(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                    
                    f.write(f"\n-- {len(rows)} rows exported from {table}\n\n")
                    print(f"   ✅ {table}: {len(rows)} rows backed up")
                    
            except sqlite3.OperationalError as e:
                f.write(f"-- Table {table} not found or error: {e}\n\n")
                print(f"   ⏭️  {table}: skipped (not found)")
    
    conn.close()
    
    print(f"\n✅ Backup saved to: {backup_file}")
    print(f"   File size: {os.path.getsize(backup_file)} bytes")
    print()
    
    return backup_file


def remove_tables(confirm=False):
    """
    Completely remove avatar tables.
    THIS IS DESTRUCTIVE - backs up first!
    """
    
    print("\n" + "=" * 60)
    print("⚠️  REMOVING AVATAR TABLES")
    print("=" * 60 + "\n")
    
    if not confirm:
        print("This will PERMANENTLY DELETE all avatar data!")
        print()
        print("To proceed, run:")
        print("   python rollback_avatar_feature.py remove --confirm")
        print()
        return
    
    # Backup first
    print("Step 1: Creating backup...")
    backup_file = backup_data()
    
    if not backup_file:
        print("❌ Backup failed - aborting removal")
        return
    
    print(f"\nStep 2: Removing tables...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop indexes first
    indexes = [
        'idx_inventory_user', 'idx_inventory_guest',
        'idx_equipped_user', 'idx_equipped_guest',
        'idx_purchase_user', 'idx_purchase_guest'
    ]
    
    for index in indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index}")
        except:
            pass
    
    # Drop tables in reverse dependency order
    tables = [
        'avatar_purchase_log',
        'user_avatar_inventory',
        'user_avatar_equipped',
        'avatar_items'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"   ✅ Dropped {table}")
        except Exception as e:
            print(f"   ❌ Error dropping {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 60)
    print("✅ AVATAR TABLES REMOVED")
    print("=" * 60)
    print()
    print(f"Backup saved to: {backup_file}")
    print("To restore, run the SQL in that file.")
    print()


def restore_from_backup(backup_file):
    """Restore avatar data from a backup file"""
    
    print(f"\nRestoring from {backup_file}...")
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(backup_file, 'r') as f:
        sql = f.read()
    
    try:
        cursor.executescript(sql)
        conn.commit()
        print("✅ Restore complete")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        show_status()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        show_status()
    
    elif command == 'disable':
        disable_feature()
    
    elif command == 'backup':
        backup_data()
    
    elif command == 'remove':
        confirm = '--confirm' in sys.argv
        remove_tables(confirm=confirm)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Usage: python rollback_avatar_feature.py restore <backup_file.sql>")
        else:
            restore_from_backup(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
