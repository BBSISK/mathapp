#!/usr/bin/env python3
"""
RACING CAR PHASE 2 - PERFORMANCE UPGRADES MIGRATION
=====================================================
Creates tables for the car upgrade/enhancement system.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python racing_car_phase2_migration.py
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/mathquiz.db'

# 25 upgrades across 5 categories (5 each)
# Total optimal cost: ~34,000 points
# Budget: 20,000 points
# This forces serious strategic choices!

CAR_UPGRADES = [
    # DRIVER EXPERIENCE (5 upgrades) - Affects consistency and reaction
    (1, "driver", "Reaction Training", 
     "Improves start performance and overtaking reactions", 
     1200, 8, "fa-bolt", "reaction"),
    (2, "driver", "Fitness Programme", 
     "Better stamina for consistent late-race performance", 
     1000, 6, "fa-heartbeat", "stamina"),
    (3, "driver", "Focus Enhancement", 
     "Reduces errors under pressure", 
     1400, 9, "fa-brain", "focus"),
    (4, "driver", "Strategy IQ", 
     "Better tyre management and pit timing decisions", 
     1100, 7, "fa-chess", "strategy"),
    (5, "driver", "Risk Management", 
     "Balanced aggression for safer overtakes", 
     900, 5, "fa-shield-alt", "risk"),
    
    # AERODYNAMICS (5 upgrades) - Affects cornering and top speed balance
    (6, "aero", "Front Wing Tune", 
     "Optimized front downforce for better turn-in", 
     1500, 10, "fa-wind", "front_downforce"),
    (7, "aero", "Rear Wing DRS+", 
     "Enhanced DRS effect for higher straight-line speed", 
     1800, 12, "fa-plane", "drs_boost"),
    (8, "aero", "Sidepod Vents", 
     "Improved cooling allows more aggressive engine modes", 
     1300, 8, "fa-fan", "cooling"),
    (9, "aero", "Floor Edge Sealing", 
     "Better ground effect for mid-corner grip", 
     1600, 11, "fa-layer-group", "ground_effect"),
    (10, "aero", "Diffuser Upgrade", 
     "Maximum rear downforce for traction zones", 
     1700, 11, "fa-arrow-down", "rear_downforce"),
    
    # ENGINE (5 upgrades) - Affects power and reliability
    (11, "engine", "Power Mode+", 
     "Extra 15bhp for qualifying and overtakes", 
     2000, 14, "fa-fire", "power"),
    (12, "engine", "Fuel Efficiency", 
     "Run lighter fuel loads for better pace", 
     1400, 9, "fa-gas-pump", "fuel"),
    (13, "engine", "Cooling System", 
     "Sustained high power in hot conditions", 
     1200, 7, "fa-snowflake", "heat_management"),
    (14, "engine", "Reliability Pack", 
     "Reduced chance of mechanical failures", 
     1100, 8, "fa-wrench", "reliability"),
    (15, "engine", "Hybrid Boost", 
     "Extended battery deployment zones", 
     1600, 10, "fa-battery-full", "ers"),
    
    # TYRES (5 upgrades) - Affects grip and degradation
    (16, "tyres", "Soft Compound Mastery", 
     "Extract maximum grip from soft tyres", 
     1300, 9, "fa-circle", "soft_grip"),
    (17, "tyres", "Medium Compound Balance", 
     "Optimal balance of pace and longevity", 
     1000, 6, "fa-adjust", "medium_balance"),
    (18, "tyres", "Hard Compound Endurance", 
     "Go longer stints on hard tyres", 
     900, 5, "fa-compact-disc", "hard_endurance"),
    (19, "tyres", "Tyre Management System", 
     "Reduced overall degradation across all compounds", 
     1500, 10, "fa-chart-line", "degradation"),
    (20, "tyres", "Pit Stop Optimization", 
     "Faster pit stops and better out-laps", 
     1100, 7, "fa-stopwatch", "pitstop"),
    
    # PIT CREW & TEAM (5 upgrades) - NEW! Affects race operations
    (21, "team", "Pit Crew Training", 
     "Faster wheel changes - save 0.3s per stop", 
     1400, 9, "fa-users-cog", "pit_speed"),
    (22, "team", "Race Engineer Upgrade", 
     "Better real-time strategy calls and adjustments", 
     1600, 11, "fa-headset", "engineer"),
    (23, "team", "Data Analytics Suite", 
     "Advanced telemetry for optimal setup tweaks", 
     1800, 12, "fa-chart-bar", "telemetry"),
    (24, "team", "Weather Prediction", 
     "Better rain timing calls for strategic advantage", 
     1200, 8, "fa-cloud-rain", "weather"),
    (25, "team", "Simulator Training", 
     "Pre-race practice improves qualifying pace", 
     1500, 10, "fa-desktop", "simulator"),
]

# Total cost if buying ALL: 34,100 points
# Budget: 20,000 points
# Must sacrifice: ~14,100 points worth of upgrades!


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🏎️ RACING CAR PHASE 2 - UPGRADES SETUP")
    print("=" * 60)
    
    # =========================================================
    # CREATE TABLES
    # =========================================================
    
    # 1. Upgrades Catalog
    print("\n🔧 Creating car_upgrades table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_upgrades (
            id INTEGER PRIMARY KEY,
            upgrade_number INTEGER UNIQUE NOT NULL,
            category VARCHAR(20) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            cost INTEGER NOT NULL,
            performance_boost INTEGER NOT NULL,
            icon VARCHAR(50),
            stat_key VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ car_upgrades table created")
    
    # 2. User Purchased Upgrades
    print("\n💰 Creating user_car_upgrades table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_car_upgrades (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            guest_code VARCHAR(20),
            upgrade_id INTEGER NOT NULL,
            purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            points_spent INTEGER,
            FOREIGN KEY (upgrade_id) REFERENCES car_upgrades(id),
            UNIQUE(user_id, upgrade_id),
            UNIQUE(guest_code, upgrade_id)
        )
    """)
    print("  ✓ user_car_upgrades table created")
    
    # 3. User Upgrade Budget Tracking
    print("\n📊 Adding upgrade budget columns to user_race_cars...")
    try:
        cursor.execute("ALTER TABLE user_race_cars ADD COLUMN upgrade_budget_used INTEGER DEFAULT 0")
        print("  ✓ Added upgrade_budget_used column")
    except:
        print("  ℹ️ upgrade_budget_used column already exists")
    
    try:
        cursor.execute("ALTER TABLE user_race_cars ADD COLUMN car_completed_at DATETIME")
        print("  ✓ Added car_completed_at column")
    except:
        print("  ℹ️ car_completed_at column already exists")
    
    # Create indexes
    print("\n📇 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_upgrades_category ON car_upgrades(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_car_upgrades_user ON user_car_upgrades(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_car_upgrades_guest ON user_car_upgrades(guest_code)")
    print("  ✓ Indexes created")
    
    # =========================================================
    # SEED UPGRADES DATA
    # =========================================================
    print("\n🔧 Seeding upgrades data...")
    
    cursor.execute("SELECT COUNT(*) FROM car_upgrades")
    existing = cursor.fetchone()[0]
    
    if existing > 0:
        print(f"  ℹ️ car_upgrades already has {existing} entries")
        print("  Clearing and re-seeding for consistency...")
        cursor.execute("DELETE FROM car_upgrades")
    
    for upgrade in CAR_UPGRADES:
        num, cat, name, desc, cost, boost, icon, stat = upgrade
        cursor.execute("""
            INSERT INTO car_upgrades (upgrade_number, category, name, description, cost, performance_boost, icon, stat_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (num, cat, name, desc, cost, boost, icon, stat))
    
    print(f"  ✓ Seeded {len(CAR_UPGRADES)} upgrades")
    
    conn.commit()
    
    # =========================================================
    # VERIFY & SUMMARY
    # =========================================================
    print("\n" + "=" * 60)
    print("✅ PHASE 2 SETUP COMPLETE")
    print("=" * 60)
    
    # Show summary by category
    cursor.execute("""
        SELECT category, COUNT(*), SUM(cost), SUM(performance_boost)
        FROM car_upgrades 
        GROUP BY category
        ORDER BY category
    """)
    categories = cursor.fetchall()
    
    print(f"\n📊 Upgrades Summary:")
    print(f"   {'Category':<12} {'Count':<8} {'Total Cost':<12} {'Total Boost'}")
    print(f"   {'-'*12} {'-'*8} {'-'*12} {'-'*12}")
    
    total_cost = 0
    total_boost = 0
    for cat, count, cost, boost in categories:
        print(f"   {cat.title():<12} {count:<8} {cost:,} pts     +{boost}")
        total_cost += cost
        total_boost += boost
    
    print(f"   {'-'*12} {'-'*8} {'-'*12} {'-'*12}")
    print(f"   {'TOTAL':<12} {len(CAR_UPGRADES):<8} {total_cost:,} pts     +{total_boost}")
    
    print(f"\n   💰 Budget allowed: 20,000 pts")
    print(f"   ⚠️  Must sacrifice: {total_cost - 20000:,} pts worth of upgrades!")
    print(f"   📊 That's {round((total_cost - 20000) / total_cost * 100)}% of available upgrades!")
    
    conn.close()
    
    print("""
🏁 Phase 2 Ready!

The upgrade shop will appear once a user has:
- All 50 car parts unlocked (50,000+ points)

Users get 20,000 points budget to spend on upgrades.
Total optimal upgrades cost ~34,100 points.
Strategic choices required - can only afford ~59% of upgrades!

5 Categories:
- Driver Experience (reaction, focus, strategy)
- Aerodynamics (downforce, DRS, cooling)
- Engine (power, efficiency, reliability)  
- Tyres (grip, degradation, pit stops)
- Pit Crew & Team (pit speed, engineer, data)
""")


if __name__ == '__main__':
    main()
