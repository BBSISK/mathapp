#!/usr/bin/env python3
"""
AgentMath.app - Prize System Database Setup
============================================

This script creates the prize system tables and seeds initial data.
Run this ONCE after deploying the updated app.py.

Usage:
    python setup_prize_system.py
"""

from app import app, db, Prize, PrizeSchool, SystemSetting

def create_tables():
    """Create all prize system tables"""
    with app.app_context():
        print("Creating prize system tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Tables created successfully!")

def seed_settings():
    """Set up default system settings"""
    with app.app_context():
        print("\nSeeding system settings...")
        
        defaults = [
            ('global_points_multiplier', '5.0', 'Global multiplier for prize point costs'),
            ('prize_expiry_days', '30', 'Days before unclaimed prizes expire'),
            ('raffle_enabled', 'true', 'Whether raffle system is enabled'),
        ]
        
        for key, value, description in defaults:
            existing = SystemSetting.query.get(key)
            if not existing:
                setting = SystemSetting(key=key, value=value, description=description)
                db.session.add(setting)
                print(f"  ✅ {key} = {value}")
            else:
                print(f"  ⏭️  {key} already exists")
        
        db.session.commit()
        print("✅ Settings seeded!")

def seed_sample_prizes():
    """Create sample prize catalogue"""
    with app.app_context():
        print("\nSeeding sample prizes...")
        
        # Check if prizes already exist
        if Prize.query.count() > 0:
            print("  ⏭️  Prizes already exist, skipping seed")
            return
        
        prizes = [
            # Bronze tier (base cost 100-300)
            {'name': 'Pencil', 'emoji': '✏️', 'base_point_cost': 200, 'tier': 'bronze', 'description': 'Quality wooden pencil'},
            {'name': 'Eraser', 'emoji': '🧽', 'base_point_cost': 150, 'tier': 'bronze', 'description': 'Soft eraser'},
            {'name': 'Ruler', 'emoji': '📏', 'base_point_cost': 200, 'tier': 'bronze', 'description': '15cm ruler'},
            {'name': 'Sticker Pack', 'emoji': '⭐', 'base_point_cost': 250, 'tier': 'bronze', 'description': 'Fun maths stickers'},
            
            # Silver tier (base cost 400-700)
            {'name': 'Pen Set', 'emoji': '🖊️', 'base_point_cost': 500, 'tier': 'silver', 'description': 'Set of 4 coloured pens'},
            {'name': 'Notebook', 'emoji': '📓', 'base_point_cost': 600, 'tier': 'silver', 'description': 'A5 lined notebook'},
            {'name': 'Highlighters', 'emoji': '🖍️', 'base_point_cost': 500, 'tier': 'silver', 'description': 'Pack of highlighters'},
            
            # Gold tier (base cost 800-1500)
            {'name': 'Geometry Set', 'emoji': '📐', 'base_point_cost': 1000, 'tier': 'gold', 'description': 'Compass, protractor & set squares'},
            {'name': 'Calculator', 'emoji': '🔢', 'base_point_cost': 1200, 'tier': 'gold', 'description': 'Scientific calculator'},
            {'name': 'Maths Poster', 'emoji': '🖼️', 'base_point_cost': 800, 'tier': 'gold', 'description': 'Inspirational maths poster'},
            
            # Platinum tier (base cost 1500+)
            {'name': 'Book Voucher €10', 'emoji': '📚', 'base_point_cost': 2000, 'tier': 'platinum', 'description': '€10 book shop voucher'},
            {'name': 'Maths Game', 'emoji': '🎮', 'base_point_cost': 2500, 'tier': 'platinum', 'description': 'Educational maths game'},
            
            # Raffle entries
            {'name': 'Raffle Entry (1x)', 'emoji': '🎟️', 'base_point_cost': 1000, 'tier': 'gold', 'prize_type': 'raffle_entry', 'description': '1 entry into weekly draw'},
            {'name': 'Raffle Entry (3x)', 'emoji': '🎫', 'base_point_cost': 2000, 'tier': 'platinum', 'prize_type': 'raffle_entry', 'description': '3 entries into weekly draw'},
        ]
        
        for i, p in enumerate(prizes):
            prize = Prize(
                name=p['name'],
                emoji=p['emoji'],
                base_point_cost=p['base_point_cost'],
                tier=p['tier'],
                description=p.get('description', ''),
                prize_type=p.get('prize_type', 'physical'),
                sort_order=i,
                is_active=True
            )
            db.session.add(prize)
            print(f"  ✅ {p['emoji']} {p['name']} ({p['tier']}, {p['base_point_cost']} base pts)")
        
        db.session.commit()
        print(f"✅ {len(prizes)} prizes created!")

def seed_sample_school():
    """Create a sample school for testing"""
    with app.app_context():
        print("\nSeeding sample school...")
        
        # Check if schools already exist
        if PrizeSchool.query.count() > 0:
            print("  ⏭️  Schools already exist, skipping seed")
            return
        
        school = PrizeSchool(
            name='Palmerstown Community School',
            county='Dublin',
            status='approved',
            points_multiplier=1.0,
            rep_name='Sample Rep',
            rep_email='rep@school.ie'
        )
        
        db.session.add(school)
        db.session.commit()
        
        print(f"  ✅ {school.name} created!")

def show_summary():
    """Show summary of prize system"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("PRIZE SYSTEM SUMMARY")
        print("=" * 60)
        
        multiplier = float(SystemSetting.get('global_points_multiplier', 5.0))
        print(f"\nGlobal Multiplier: {multiplier}x")
        
        prizes = Prize.query.filter_by(is_active=True).order_by(Prize.tier, Prize.sort_order).all()
        print(f"\nPrizes ({len(prizes)} active):")
        
        current_tier = None
        for p in prizes:
            if p.tier != current_tier:
                current_tier = p.tier
                print(f"\n  {current_tier.upper()}:")
            
            effective = int(p.base_point_cost * multiplier)
            print(f"    {p.emoji} {p.name}: {p.base_point_cost} base → {effective} pts")
        
        schools = PrizeSchool.query.filter_by(status='approved').all()
        print(f"\nApproved Schools ({len(schools)}):")
        for s in schools:
            print(f"    🏫 {s.name} ({s.county})")
        
        print("\n" + "=" * 60)
        print("Access prize admin at: /admin/prizes")
        print("=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("AgentMath.app Prize System Setup")
    print("=" * 60)
    
    create_tables()
    seed_settings()
    seed_sample_prizes()
    seed_sample_school()
    show_summary()
    
    print("\n✅ Prize system setup complete!")
