#!/usr/bin/env python3
"""
Diagnostic script to check avatar data in the database.
Run this from your PythonAnywhere console:
    python check_avatar_data.py
"""

from app import app, db, UserAvatarInventory, UserAvatarEquipped, AvatarItem
from sqlalchemy import text

def check_avatar_data():
    with app.app_context():
        print("=" * 60)
        print("AVATAR SYSTEM DIAGNOSTIC")
        print("=" * 60)
        
        # Check all avatar items
        items = AvatarItem.query.all()
        print(f"\n📦 Total Avatar Items in shop: {len(items)}")
        for item in items[:5]:
            print(f"   - {item.item_key} ({item.item_type}): {item.point_cost} pts")
        if len(items) > 5:
            print(f"   ... and {len(items) - 5} more")
        
        # Check all inventory records
        inventory = UserAvatarInventory.query.all()
        print(f"\n🎒 Total Inventory Records: {len(inventory)}")
        for inv in inventory[:15]:
            item = AvatarItem.query.get(inv.item_id)
            item_name = item.item_key if item else "UNKNOWN"
            item_type = item.item_type if item else "?"
            owner = f"user_id={inv.user_id}" if inv.user_id else f"guest={inv.guest_code}"
            print(f"   - {owner}: owns '{item_name}' ({item_type})")
        
        # Check all equipped records
        equipped_all = UserAvatarEquipped.query.all()
        print(f"\n🎭 Total Equipped Records: {len(equipped_all)}")
        for eq in equipped_all:
            owner = f"user_id={eq.user_id}" if eq.user_id else f"guest_code={eq.guest_code}"
            print(f"   - {owner}:")
            print(f"       animal: {eq.animal_key}")
            print(f"       hat: {eq.hat_key}")
            print(f"       glasses: {eq.glasses_key}")
            print(f"       background: {eq.background_key}")
            print(f"       accessory: {eq.accessory_key}")
        
        # Check specific guest: fox
        print(f"\n🦊 Checking 'fox' guest codes specifically:")
        fox_guests = UserAvatarEquipped.query.filter(
            UserAvatarEquipped.guest_code.like('fox%')
        ).all()
        if fox_guests:
            for eq in fox_guests:
                print(f"   Found: guest_code={eq.guest_code}")
                print(f"       animal={eq.animal_key}, hat={eq.hat_key}, glasses={eq.glasses_key}")
        else:
            print("   No equipped records for fox guests!")
        
        # Check inventory for fox guests
        fox_inv = UserAvatarInventory.query.filter(
            UserAvatarInventory.guest_code.like('fox%')
        ).all()
        print(f"\n   Fox guest inventory: {len(fox_inv)} items")
        for inv in fox_inv:
            item = AvatarItem.query.get(inv.item_id)
            print(f"      - {inv.guest_code}: {item.item_key if item else 'UNKNOWN'} ({item.item_type if item else '?'})")
        
        print("\n" + "=" * 60)
        print("Check complete!")

if __name__ == "__main__":
    check_avatar_data()
