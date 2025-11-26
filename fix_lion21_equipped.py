#!/usr/bin/env python3
"""
Fix script to update lion21's equipped items based on their inventory.
Run this from your PythonAnywhere console:
    python fix_lion21_equipped.py
"""

from app import app, db, UserAvatarInventory, UserAvatarEquipped, AvatarItem

def fix_equipped():
    with app.app_context():
        guest_code = 'lion21'
        
        # Get the equipped record
        equipped = UserAvatarEquipped.query.filter_by(guest_code=guest_code).first()
        
        if not equipped:
            print(f"No equipped record for {guest_code}, creating one...")
            equipped = UserAvatarEquipped(guest_code=guest_code)
            db.session.add(equipped)
        
        print(f"Current equipped for {guest_code}:")
        print(f"  animal: {equipped.animal_key}")
        print(f"  hat: {equipped.hat_key}")
        print(f"  glasses: {equipped.glasses_key}")
        
        # Get their inventory and equip the first non-'none' item of each type
        inventory = UserAvatarInventory.query.filter_by(guest_code=guest_code).all()
        
        print(f"\nInventory has {len(inventory)} items")
        
        # Find best item for each slot
        for inv in inventory:
            item = db.session.get(AvatarItem, inv.item_id)
            if item and item.item_key != 'none':
                print(f"  Found: {item.item_key} ({item.item_type})")
                
                # Equip the first non-none item of each type
                if item.item_type == 'hat' and equipped.hat_key == 'none':
                    equipped.hat_key = item.item_key
                    print(f"    → Equipping hat: {item.item_key}")
                elif item.item_type == 'glasses' and equipped.glasses_key == 'none':
                    equipped.glasses_key = item.item_key
                    print(f"    → Equipping glasses: {item.item_key}")
                elif item.item_type == 'background' and equipped.background_key == 'none':
                    equipped.background_key = item.item_key
                    print(f"    → Equipping background: {item.item_key}")
                elif item.item_type == 'accessory' and equipped.accessory_key == 'none':
                    equipped.accessory_key = item.item_key
                    print(f"    → Equipping accessory: {item.item_key}")
        
        # Also set animal to lion (matches guest code)
        equipped.animal_key = 'lion'
        print(f"    → Setting animal to: lion (matches guest code)")
        
        db.session.commit()
        
        print(f"\n✅ Updated equipped for {guest_code}:")
        print(f"  animal: {equipped.animal_key}")
        print(f"  hat: {equipped.hat_key}")
        print(f"  glasses: {equipped.glasses_key}")
        print(f"  background: {equipped.background_key}")
        print(f"  accessory: {equipped.accessory_key}")

if __name__ == "__main__":
    fix_equipped()
