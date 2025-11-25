#!/usr/bin/env python3
"""
Avatar System Database Migration
================================

This script creates the necessary database tables for the avatar system.
It is safe to run multiple times - it will not overwrite existing data.

BACKOUT: Run rollback_avatar_feature.py to remove these tables.

Usage:
    python migrate_avatar_tables.py

Tables created:
    - avatar_items: Shop catalogue of all available items
    - user_avatar_inventory: Items owned by users/guests
    - user_avatar_equipped: Currently equipped avatar configuration
    - avatar_purchase_log: Audit trail of all purchases
"""

import sqlite3
import os
from datetime import datetime

# Database path - adjust if your database is elsewhere
DB_PATH = 'instance/mathquiz.db'

# SQL statements for creating tables
CREATE_TABLES_SQL = """
-- Avatar Items: The shop catalogue
CREATE TABLE IF NOT EXISTS avatar_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type VARCHAR(50) NOT NULL,
    item_key VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    point_cost INTEGER NOT NULL DEFAULT 0,
    rarity VARCHAR(20) DEFAULT 'common',
    is_default BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_type, item_key)
);

-- User Avatar Inventory: Items owned by users
CREATE TABLE IF NOT EXISTS user_avatar_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    guest_code VARCHAR(50),
    item_id INTEGER NOT NULL,
    purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES avatar_items(id)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_inventory_user ON user_avatar_inventory(user_id);
CREATE INDEX IF NOT EXISTS idx_inventory_guest ON user_avatar_inventory(guest_code);

-- User Avatar Equipped: Currently worn items
CREATE TABLE IF NOT EXISTS user_avatar_equipped (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    guest_code VARCHAR(50),
    animal_key VARCHAR(50) DEFAULT 'panda',
    hat_key VARCHAR(50) DEFAULT 'none',
    glasses_key VARCHAR(50) DEFAULT 'none',
    background_key VARCHAR(50) DEFAULT 'none',
    accessory_key VARCHAR(50) DEFAULT 'none',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for equipped lookups
CREATE INDEX IF NOT EXISTS idx_equipped_user ON user_avatar_equipped(user_id);
CREATE INDEX IF NOT EXISTS idx_equipped_guest ON user_avatar_equipped(guest_code);

-- Avatar Purchase Log: Audit trail
CREATE TABLE IF NOT EXISTS avatar_purchase_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    guest_code VARCHAR(50),
    item_id INTEGER NOT NULL,
    points_spent INTEGER NOT NULL,
    points_before INTEGER NOT NULL,
    points_after INTEGER NOT NULL,
    purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES avatar_items(id)
);

-- Create index for purchase history lookups
CREATE INDEX IF NOT EXISTS idx_purchase_user ON avatar_purchase_log(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_guest ON avatar_purchase_log(guest_code);
"""

# Default items to seed
DEFAULT_ITEMS = [
    # Animals (all free)
    ('animal', 'panda', 'Panda', 'A friendly black and white panda', 0, 'common', 1, 1, 1),
    ('animal', 'fox', 'Fox', 'A clever orange fox', 0, 'common', 1, 1, 2),
    ('animal', 'cat', 'Cat', 'A curious ginger cat', 0, 'common', 1, 1, 3),
    ('animal', 'owl', 'Owl', 'A wise brown owl', 0, 'common', 1, 1, 4),
    
    # Hats
    ('hat', 'none', 'None', 'No hat', 0, 'common', 1, 1, 0),
    ('hat', 'party', 'Party Hat', 'A colorful party hat - let\'s celebrate!', 50, 'common', 0, 1, 1),
    ('hat', 'cap', 'Baseball Cap', 'A cool sporty cap', 75, 'common', 0, 1, 2),
    ('hat', 'beanie', 'Cozy Beanie', 'A warm knitted beanie', 100, 'common', 0, 1, 3),
    ('hat', 'tophat', 'Top Hat', 'A distinguished top hat', 250, 'rare', 0, 1, 4),
    ('hat', 'wizard', 'Wizard Hat', 'A magical wizard hat with stars', 300, 'rare', 0, 1, 5),
    ('hat', 'crown', 'Royal Crown', 'A crown fit for maths royalty!', 500, 'epic', 0, 1, 6),
    ('hat', 'graduation', 'Graduation Cap', 'The ultimate achievement - you did it!', 1000, 'legendary', 0, 1, 7),
    
    # Glasses
    ('glasses', 'none', 'None', 'No glasses', 0, 'common', 1, 1, 0),
    ('glasses', 'round', 'Round Specs', 'Classic round spectacles', 75, 'common', 0, 1, 1),
    ('glasses', 'cool', 'Cool Shades', 'Super cool sunglasses', 150, 'common', 0, 1, 2),
    ('glasses', 'heart', 'Heart Glasses', 'Show some love with heart-shaped frames', 200, 'rare', 0, 1, 3),
    ('glasses', 'star', 'Star Glasses', 'You\'re a star!', 300, 'rare', 0, 1, 4),
    
    # Backgrounds
    ('background', 'none', 'Plain', 'Simple grey background', 0, 'common', 1, 1, 0),
    ('background', 'forest', 'Forest', 'A peaceful green forest', 75, 'common', 0, 1, 1),
    ('background', 'ocean', 'Ocean', 'Calm blue ocean vibes', 75, 'common', 0, 1, 2),
    ('background', 'sunset', 'Sunset', 'Beautiful orange sunset', 150, 'rare', 0, 1, 3),
    ('background', 'space', 'Space', 'Deep space with stars', 300, 'rare', 0, 1, 4),
    ('background', 'rainbow', 'Rainbow', 'A magical rainbow gradient', 500, 'epic', 0, 1, 5),
    
    # Accessories
    ('accessory', 'none', 'None', 'No accessory', 0, 'common', 1, 1, 0),
    ('accessory', 'pencil', 'Pencil', 'Ready to work out problems!', 50, 'common', 0, 1, 1),
    ('accessory', 'calculator', 'Calculator', 'A trusty calculator', 100, 'common', 0, 1, 2),
    ('accessory', 'protractor', 'Protractor', 'Measure those angles!', 150, 'rare', 0, 1, 3),
    ('accessory', 'medal', 'Gold Medal', 'A shiny gold medal for excellence', 750, 'epic', 0, 1, 4),
    ('accessory', 'trophy', 'Trophy', 'The ultimate prize!', 1000, 'legendary', 0, 1, 5),
]


def run_migration():
    """Run the database migration"""
    
    print("=" * 60)
    print("AVATAR SYSTEM DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    # Check database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("   Make sure you're running this from the mathapp-main directory")
        return False
    
    print(f"📂 Database: {DB_PATH}")
    print()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        print("Creating tables...")
        cursor.executescript(CREATE_TABLES_SQL)
        print("   ✅ avatar_items")
        print("   ✅ user_avatar_inventory")
        print("   ✅ user_avatar_equipped")
        print("   ✅ avatar_purchase_log")
        print()
        
        # Seed default items
        print("Seeding default items...")
        items_added = 0
        items_skipped = 0
        
        for item in DEFAULT_ITEMS:
            # Check if item already exists
            cursor.execute(
                "SELECT id FROM avatar_items WHERE item_type = ? AND item_key = ?",
                (item[0], item[1])
            )
            
            if cursor.fetchone():
                items_skipped += 1
            else:
                cursor.execute("""
                    INSERT INTO avatar_items 
                    (item_type, item_key, display_name, description, point_cost, rarity, is_default, is_active, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, item)
                items_added += 1
        
        conn.commit()
        
        print(f"   ✅ Added {items_added} new items")
        if items_skipped > 0:
            print(f"   ⏭️  Skipped {items_skipped} existing items")
        print()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM avatar_items")
        total_items = cursor.fetchone()[0]
        print(f"📊 Total items in shop: {total_items}")
        
        # Show breakdown by type
        cursor.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM avatar_items 
            GROUP BY item_type 
            ORDER BY item_type
        """)
        print("\n   Breakdown by type:")
        for row in cursor.fetchall():
            print(f"      {row[0]}: {row[1]} items")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ MIGRATION COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Set AVATAR_SYSTEM_ENABLED=true in environment")
        print("  2. Restart the Flask app")
        print("  3. Test with a single user before full rollout")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tables():
    """Verify avatar tables exist and have data"""
    
    print("Verifying avatar tables...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['avatar_items', 'user_avatar_inventory', 'user_avatar_equipped', 'avatar_purchase_log']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} rows")
        except sqlite3.OperationalError:
            print(f"   ❌ {table}: NOT FOUND")
    
    conn.close()
    return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_tables()
    else:
        run_migration()
