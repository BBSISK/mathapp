#!/usr/bin/env python3
"""
RACING CAR CHALLENGE - DATABASE MIGRATION
==========================================
Creates tables for the Racing Car Assembly feature.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python racing_car_migration.py
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/mathquiz.db'

# 50 car parts organized by assembly stage
CAR_PARTS = [
    # Stage 1: Chassis Foundation (Parts 1-10, 0-10K points)
    (1, "Floor Pan", "chassis", "The base carbon fiber floor of the car", 1000),
    (2, "Survival Cell", "chassis", "The reinforced driver safety cell", 2000),
    (3, "Front Bulkhead", "chassis", "Front structural mounting point", 3000),
    (4, "Rear Bulkhead", "chassis", "Rear structural mounting point", 4000),
    (5, "Side Impact Structures", "chassis", "Driver protection panels", 5000),
    (6, "Cockpit Opening", "chassis", "Driver entry area frame", 6000),
    (7, "Fuel Cell Housing", "chassis", "Protected fuel tank area", 7000),
    (8, "Roll Hoop Base", "chassis", "Primary roll protection mount", 8000),
    (9, "Engine Bay Frame", "chassis", "Rear engine mounting structure", 9000),
    (10, "Chassis Reinforcements", "chassis", "Additional structural bracing", 10000),
    
    # Stage 2: Aerodynamics Front (Parts 11-20, 10-20K points)
    (11, "Nose Cone", "aero_front", "Aerodynamic front nose section", 11000),
    (12, "Front Wing Main Plane", "aero_front", "Primary front downforce element", 12000),
    (13, "Front Wing Flaps", "aero_front", "Adjustable front wing elements", 13000),
    (14, "Front Wing Endplates", "aero_front", "Vortex-generating side plates", 14000),
    (15, "Front Suspension Fairings", "aero_front", "Aero covers for front suspension", 15000),
    (16, "Brake Duct Inlets", "aero_front", "Front brake cooling ducts", 16000),
    (17, "Bargeboard Assembly", "aero_front", "Complex airflow management", 17000),
    (18, "Side Deflectors", "aero_front", "Air directing vanes", 18000),
    (19, "Vortex Generators", "aero_front", "Small downforce elements", 19000),
    (20, "Front Wing Pylons", "aero_front", "Wing mounting structures", 20000),
    
    # Stage 3: Engine & Drivetrain (Parts 21-30, 20-30K points)
    (21, "Power Unit Block", "engine", "1.6L V6 turbo hybrid engine", 21000),
    (22, "Turbocharger", "engine", "Exhaust-driven compressor", 22000),
    (23, "MGU-H", "engine", "Heat energy recovery motor", 23000),
    (24, "MGU-K", "engine", "Kinetic energy recovery motor", 24000),
    (25, "Energy Store", "engine", "Hybrid battery pack", 25000),
    (26, "Gearbox Casing", "engine", "8-speed seamless shift housing", 26000),
    (27, "Exhaust System", "engine", "Wastegate and tailpipe", 27000),
    (28, "Cooling Radiators", "engine", "Engine and ERS cooling", 28000),
    (29, "Oil System", "engine", "Lubrication and cooling", 29000),
    (30, "Hydraulic System", "engine", "Gearshift and clutch actuation", 30000),
    
    # Stage 4: Rear Aero & Bodywork (Parts 31-40, 30-40K points)
    (31, "Engine Cover", "aero_rear", "Aerodynamic engine housing", 31000),
    (32, "Sidepod Left", "aero_rear", "Left side radiator housing", 32000),
    (33, "Sidepod Right", "aero_rear", "Right side radiator housing", 33000),
    (34, "Rear Wing Main Plane", "aero_rear", "Primary rear downforce", 34000),
    (35, "Rear Wing DRS Flap", "aero_rear", "Drag reduction system", 35000),
    (36, "Rear Wing Endplates", "aero_rear", "Rear vortex generators", 36000),
    (37, "Diffuser", "aero_rear", "Underbody aero extraction", 37000),
    (38, "Beam Wing", "aero_rear", "Lower rear wing element", 38000),
    (39, "Rear Crash Structure", "aero_rear", "Impact protection", 39000),
    (40, "Rain Light Housing", "aero_rear", "Rear visibility light", 40000),
    
    # Stage 5: Wheels, Suspension & Finishing (Parts 41-50, 40-50K points)
    (41, "Front Suspension Arms", "suspension", "Wishbone suspension components", 41000),
    (42, "Rear Suspension Arms", "suspension", "Rear wishbone assembly", 42000),
    (43, "Front Wheels", "wheels", "18-inch front wheel rims", 43000),
    (44, "Rear Wheels", "wheels", "18-inch rear wheel rims", 44000),
    (45, "Front Tyres", "wheels", "Pirelli front compounds", 45000),
    (46, "Rear Tyres", "wheels", "Pirelli rear compounds", 46000),
    (47, "Steering Wheel", "cockpit", "Multi-function racing wheel", 47000),
    (48, "Halo Device", "cockpit", "Titanium head protection", 48000),
    (49, "Driver Seat", "cockpit", "Custom-molded racing seat", 49000),
    (50, "Team Livery", "finishing", "Complete paint and sponsor decals", 50000),
]


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🏎️ RACING CAR CHALLENGE - DATABASE SETUP")
    print("=" * 60)
    
    # =========================================================
    # CREATE TABLES
    # =========================================================
    
    # 1. Car Parts Catalog
    print("\n📦 Creating car_parts table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_parts (
            id INTEGER PRIMARY KEY,
            part_number INTEGER UNIQUE NOT NULL,
            part_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            points_required INTEGER NOT NULL,
            model_component VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ car_parts table created")
    
    # 2. User Race Cars (tracks unlocked parts)
    print("\n🚗 Creating user_race_cars table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_race_cars (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            guest_code VARCHAR(20),
            parts_unlocked INTEGER DEFAULT 0,
            highest_points_seen INTEGER DEFAULT 0,
            car_name VARCHAR(100),
            primary_color VARCHAR(20) DEFAULT '#e10600',
            secondary_color VARCHAR(20) DEFAULT '#1e1e1e',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id),
            UNIQUE(guest_code)
        )
    """)
    print("  ✓ user_race_cars table created")
    
    # 3. Part Unlock History (for animations/celebrations)
    print("\n🎉 Creating car_part_unlocks table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_part_unlocks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            guest_code VARCHAR(20),
            part_id INTEGER NOT NULL,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            points_at_unlock INTEGER,
            celebrated BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (part_id) REFERENCES car_parts(id)
        )
    """)
    print("  ✓ car_part_unlocks table created")
    
    # Create indexes
    print("\n📇 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_race_cars_user ON user_race_cars(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_race_cars_guest ON user_race_cars(guest_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_parts_points ON car_parts(points_required)")
    print("  ✓ Indexes created")
    
    # =========================================================
    # SEED CAR PARTS DATA
    # =========================================================
    print("\n🔧 Seeding car parts data...")
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM car_parts")
    existing = cursor.fetchone()[0]
    
    if existing > 0:
        print(f"  ℹ️ car_parts already has {existing} entries, skipping seed")
    else:
        for part in CAR_PARTS:
            part_num, name, category, desc, points = part
            cursor.execute("""
                INSERT INTO car_parts (part_number, part_name, category, description, points_required, model_component)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (part_num, name, category, desc, points, f"part_{part_num:02d}"))
        print(f"  ✓ Seeded {len(CAR_PARTS)} car parts")
    
    conn.commit()
    
    # =========================================================
    # VERIFY
    # =========================================================
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE")
    print("=" * 60)
    
    # Show summary
    cursor.execute("SELECT COUNT(*) FROM car_parts")
    parts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT category, COUNT(*) FROM car_parts GROUP BY category ORDER BY MIN(points_required)")
    categories = cursor.fetchall()
    
    print(f"\n📊 Car Parts Summary:")
    print(f"   Total parts: {parts_count}")
    print(f"\n   By category:")
    for cat, count in categories:
        cursor.execute("SELECT MIN(points_required), MAX(points_required) FROM car_parts WHERE category = ?", (cat,))
        min_pts, max_pts = cursor.fetchone()
        print(f"   • {cat}: {count} parts ({min_pts:,} - {max_pts:,} pts)")
    
    cursor.execute("SELECT COUNT(*) FROM user_race_cars")
    cars_count = cursor.fetchone()[0]
    print(f"\n   User cars registered: {cars_count}")
    
    conn.close()
    
    print("""
🏁 Next Steps:
1. Upload the updated app.py with racing car routes
2. Upload the racing car viewer template
3. Upload the 3D model files to static/models/
4. Reload your web app
""")


if __name__ == '__main__':
    main()
