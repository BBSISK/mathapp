#!/usr/bin/env python3
"""
AgentMath.app - Add New Animal Avatars to Shop
===============================================

This script adds the 16 new animal avatar items to the shop.
Run this AFTER deploying the updated app.py and avatar.js files.

Usage:
    python add_new_animal_avatars.py
"""

from app import app, db, AvatarItem

# New animals to add (the 16 not already in the shop)
NEW_ANIMALS = [
    # (item_key, display_name, point_cost, rarity, is_default)
    ('lion', 'Lion', 0, 'common', True),
    ('bear', 'Bear', 0, 'common', True),
    ('wolf', 'Wolf', 0, 'common', True),
    ('rabbit', 'Rabbit', 0, 'common', True),
    ('tiger', 'Tiger', 100, 'uncommon', False),
    ('penguin', 'Penguin', 100, 'uncommon', False),
    ('koala', 'Koala', 100, 'uncommon', False),
    ('elephant', 'Elephant', 150, 'uncommon', False),
    ('monkey', 'Monkey', 150, 'uncommon', False),
    ('dog', 'Dog', 0, 'common', True),
    ('dolphin', 'Dolphin', 200, 'rare', False),
    ('horse', 'Horse', 200, 'rare', False),
    ('deer', 'Deer', 200, 'rare', False),
    ('eagle', 'Eagle', 300, 'rare', False),
    ('parrot', 'Parrot', 300, 'rare', False),
    ('turtle', 'Turtle', 250, 'rare', False),
]

def add_new_animals():
    with app.app_context():
        print("=" * 60)
        print("AgentMath.app - Adding New Animal Avatars")
        print("=" * 60)
        
        added = 0
        skipped = 0
        
        for item_key, display_name, point_cost, rarity, is_default in NEW_ANIMALS:
            # Check if already exists
            existing = AvatarItem.query.filter_by(
                item_type='animal',
                item_key=item_key
            ).first()
            
            if existing:
                print(f"⏭️  Skipping {display_name} (already exists)")
                skipped += 1
                continue
            
            # Create new item
            new_item = AvatarItem(
                item_type='animal',
                item_key=item_key,
                display_name=display_name,
                description=f"{display_name} avatar",
                point_cost=point_cost,
                rarity=rarity,
                is_default=is_default,
                is_active=True
            )
            db.session.add(new_item)
            print(f"✅ Added {display_name} ({rarity}, {point_cost} pts)")
            added += 1
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Added: {added} new animals")
        print(f"⏭️  Skipped: {skipped} (already existed)")
        print("=" * 60)
        
        # Show all animal avatars
        print("\n📋 All Animal Avatars in Shop:")
        animals = AvatarItem.query.filter_by(item_type='animal', is_active=True).all()
        for animal in animals:
            default_tag = " (FREE)" if animal.is_default else ""
            print(f"   {animal.display_name}: {animal.point_cost} pts ({animal.rarity}){default_tag}")

if __name__ == "__main__":
    add_new_animals()
