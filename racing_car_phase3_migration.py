#!/usr/bin/env python3
"""
RACING CAR PHASE 3 - WEEKLY RACES MIGRATION
=============================================
Creates tables for the racing/competition system.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python racing_car_phase3_migration.py
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = 'instance/mathquiz.db'

# =====================================================
# AI OPPONENTS - 9 rivals with different personalities
# =====================================================
AI_DRIVERS = [
    # (name, team, nationality, flag, driving_style, 
    #  base_skill, consistency, aggression, wet_skill, tyre_management,
    #  personality_desc, avatar_color)
    
    ("Max Velocity", "Red Storm Racing", "Dutch", "🇳🇱", "aggressive",
     92, 75, 95, 80, 70,
     "Lightning fast but sometimes too aggressive", "#1e41ff"),
    
    ("Lewis Hammer", "Silver Arrows", "British", "🇬🇧", "consistent",
     90, 95, 70, 90, 90,
     "The experienced champion - always in contention", "#00d2be"),
    
    ("Charles Leclerc", "Scarlet Speed", "Monégasque", "🇲🇨", "balanced",
     88, 80, 80, 75, 80,
     "Smooth and fast, great on street circuits", "#dc0000"),
    
    ("Carlos Sainz", "Scarlet Speed", "Spanish", "🇪🇸", "strategic",
     85, 88, 65, 85, 92,
     "The tyre whisperer - makes strategies work", "#dc0000"),
    
    ("Lando Norris", "Papaya Racing", "British", "🇬🇧", "aggressive",
     86, 78, 85, 82, 75,
     "Young and hungry, loves a battle", "#ff8700"),
    
    ("Oscar Piastri", "Papaya Racing", "Australian", "🇦🇺", "calculated",
     84, 85, 60, 78, 85,
     "Rookie sensation with ice-cold nerves", "#ff8700"),
    
    ("George Russell", "Silver Arrows", "British", "🇬🇧", "consistent",
     86, 90, 70, 88, 85,
     "Mr. Saturday - qualifying specialist", "#00d2be"),
    
    ("Fernando Alonso", "Green Machine", "Spanish", "🇪🇸", "strategic",
     87, 88, 80, 92, 88,
     "The veteran master - never gives up", "#006f62"),
    
    ("Sergio Perez", "Red Storm Racing", "Mexican", "🇲🇽", "defensive",
     83, 82, 60, 75, 90,
     "Tyre management king, great defender", "#1e41ff"),
]

# =====================================================
# RACE CALENDAR - Mix of real-inspired and practice tracks
# =====================================================
RACE_CALENDAR = [
    # (race_number, name, country, flag, track_type, 
    #  aero_factor, engine_factor, driver_factor, tyre_factor, team_factor,
    #  rain_chance, description)
    
    (1, "Bahrain Grand Prix", "Bahrain", "🇧🇭", "balanced",
     0.20, 0.25, 0.20, 0.20, 0.15, 10,
     "Season opener under the desert lights"),
    
    (2, "Saudi Arabian Grand Prix", "Saudi Arabia", "🇸🇦", "high_speed",
     0.15, 0.30, 0.25, 0.15, 0.15, 5,
     "Street circuit with incredible speeds"),
    
    (3, "Australian Grand Prix", "Australia", "🇦🇺", "balanced",
     0.22, 0.22, 0.22, 0.17, 0.17, 25,
     "Classic Albert Park - anything can happen"),
    
    (4, "Japanese Grand Prix", "Japan", "🇯🇵", "technical",
     0.28, 0.20, 0.22, 0.15, 0.15, 30,
     "The legendary Suzuka - figure-8 challenge"),
    
    (5, "Chinese Grand Prix", "China", "🇨🇳", "balanced",
     0.20, 0.25, 0.20, 0.20, 0.15, 20,
     "Long straights and tight hairpins"),
    
    (6, "Miami Grand Prix", "USA", "🇺🇸", "high_speed",
     0.18, 0.28, 0.20, 0.17, 0.17, 35,
     "Glitz, glamour and Florida weather"),
    
    (7, "Emilia Romagna Grand Prix", "Italy", "🇮🇹", "technical",
     0.25, 0.20, 0.25, 0.15, 0.15, 30,
     "Historic Imola - old school challenge"),
    
    (8, "Monaco Grand Prix", "Monaco", "🇲🇨", "street",
     0.30, 0.10, 0.30, 0.15, 0.15, 15,
     "The crown jewel - no room for error"),
    
    (9, "Canadian Grand Prix", "Canada", "🇨🇦", "high_speed",
     0.15, 0.30, 0.20, 0.20, 0.15, 25,
     "Wall of Champions awaits the brave"),
    
    (10, "Spanish Grand Prix", "Spain", "🇪🇸", "balanced",
     0.22, 0.22, 0.22, 0.17, 0.17, 15,
     "The ultimate test track"),
    
    (11, "Austrian Grand Prix", "Austria", "🇦🇹", "high_speed",
     0.18, 0.28, 0.20, 0.17, 0.17, 35,
     "Short lap, big drama in the mountains"),
    
    (12, "British Grand Prix", "UK", "🇬🇧", "high_speed",
     0.25, 0.25, 0.20, 0.15, 0.15, 45,
     "Silverstone - home of racing, unpredictable weather"),
    
    (13, "Hungarian Grand Prix", "Hungary", "🇭🇺", "technical",
     0.28, 0.15, 0.27, 0.15, 0.15, 30,
     "Monaco without walls - overtaking nightmare"),
    
    (14, "Belgian Grand Prix", "Belgium", "🇧🇪", "high_speed",
     0.22, 0.28, 0.20, 0.15, 0.15, 50,
     "Spa - legendary Eau Rouge and crazy weather"),
    
    (15, "Dutch Grand Prix", "Netherlands", "🇳🇱", "technical",
     0.25, 0.18, 0.25, 0.17, 0.15, 35,
     "Zandvoort's banked turns and orange army"),
    
    (16, "Italian Grand Prix", "Italy", "🇮🇹", "high_speed",
     0.12, 0.35, 0.18, 0.20, 0.15, 20,
     "Monza - Temple of Speed, slipstream heaven"),
    
    (17, "Azerbaijan Grand Prix", "Azerbaijan", "🇦🇿", "street",
     0.18, 0.30, 0.22, 0.15, 0.15, 10,
     "Baku - the chaos circuit with 2km straight"),
    
    (18, "Singapore Grand Prix", "Singapore", "🇸🇬", "street",
     0.25, 0.15, 0.28, 0.17, 0.15, 40,
     "Night race in the humidity - survival test"),
    
    (19, "United States Grand Prix", "USA", "🇺🇸", "balanced",
     0.22, 0.22, 0.22, 0.17, 0.17, 20,
     "COTA - a bit of everything"),
    
    (20, "Mexico City Grand Prix", "Mexico", "🇲🇽", "high_altitude",
     0.15, 0.30, 0.20, 0.20, 0.15, 25,
     "Thin air means less downforce, more power"),
    
    (21, "São Paulo Grand Prix", "Brazil", "🇧🇷", "balanced",
     0.22, 0.25, 0.20, 0.18, 0.15, 55,
     "Interlagos - drama guaranteed, rain likely"),
    
    (22, "Las Vegas Grand Prix", "USA", "🇺🇸", "street",
     0.18, 0.28, 0.22, 0.17, 0.15, 5,
     "Night race on the Strip"),
    
    (23, "Qatar Grand Prix", "Qatar", "🇶🇦", "high_speed",
     0.20, 0.28, 0.20, 0.17, 0.15, 5,
     "Flowing high-speed desert circuit"),
    
    (24, "Abu Dhabi Grand Prix", "UAE", "🇦🇪", "balanced",
     0.22, 0.25, 0.20, 0.18, 0.15, 5,
     "Season finale under the Yas Marina lights"),
]

# Points for finishing positions (F1 style)
POINTS_SYSTEM = {
    1: 500,   # Winner gets big points to motivate!
    2: 350,
    3: 250,
    4: 180,
    5: 140,
    6: 110,
    7: 85,
    8: 65,
    9: 50,
    10: 25,
    # 11+ get 10 participation points
}


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🏁 RACING CAR PHASE 3 - WEEKLY RACES SETUP")
    print("=" * 60)
    
    # =========================================================
    # CREATE TABLES
    # =========================================================
    
    # 1. AI Drivers table
    print("\n🤖 Creating ai_race_drivers table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_race_drivers (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            team VARCHAR(100),
            nationality VARCHAR(50),
            flag VARCHAR(10),
            driving_style VARCHAR(30),
            base_skill INTEGER DEFAULT 80,
            consistency INTEGER DEFAULT 80,
            aggression INTEGER DEFAULT 50,
            wet_skill INTEGER DEFAULT 80,
            tyre_management INTEGER DEFAULT 80,
            personality_desc TEXT,
            avatar_color VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ ai_race_drivers table created")
    
    # 2. Race Calendar table
    print("\n📅 Creating race_calendar table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS race_calendar (
            id INTEGER PRIMARY KEY,
            race_number INTEGER NOT NULL,
            season_year INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            country VARCHAR(50),
            flag VARCHAR(10),
            track_type VARCHAR(30),
            aero_factor REAL DEFAULT 0.2,
            engine_factor REAL DEFAULT 0.2,
            driver_factor REAL DEFAULT 0.2,
            tyre_factor REAL DEFAULT 0.2,
            team_factor REAL DEFAULT 0.2,
            rain_chance INTEGER DEFAULT 20,
            description TEXT,
            race_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(race_number, season_year)
        )
    """)
    print("  ✓ race_calendar table created")
    
    # 3. Race Results table
    print("\n🏆 Creating race_results table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY,
            race_id INTEGER NOT NULL,
            user_id INTEGER,
            guest_code VARCHAR(20),
            finish_position INTEGER NOT NULL,
            points_earned INTEGER DEFAULT 0,
            tyre_choice VARCHAR(20),
            is_wet_race BOOLEAN DEFAULT 0,
            race_performance_score REAL,
            highlight_text TEXT,
            dnf_reason VARCHAR(100),
            race_time_ms INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (race_id) REFERENCES race_calendar(id)
        )
    """)
    print("  ✓ race_results table created")
    
    # 4. AI Results (for each race, store AI finishing positions)
    print("\n🤖 Creating race_ai_results table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS race_ai_results (
            id INTEGER PRIMARY KEY,
            race_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            finish_position INTEGER NOT NULL,
            performance_score REAL,
            highlight_text TEXT,
            dnf_reason VARCHAR(100),
            FOREIGN KEY (race_id) REFERENCES race_calendar(id),
            FOREIGN KEY (driver_id) REFERENCES ai_race_drivers(id),
            UNIQUE(race_id, driver_id)
        )
    """)
    print("  ✓ race_ai_results table created")
    
    # 5. Championship Standings table
    print("\n🏅 Creating championship_standings table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS championship_standings (
            id INTEGER PRIMARY KEY,
            season_year INTEGER NOT NULL,
            user_id INTEGER,
            guest_code VARCHAR(20),
            total_points INTEGER DEFAULT 0,
            races_entered INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            podiums INTEGER DEFAULT 0,
            best_finish INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(season_year, user_id),
            UNIQUE(season_year, guest_code)
        )
    """)
    print("  ✓ championship_standings table created")
    
    # 6. Weekly Race Status (tracks which race is current)
    print("\n📊 Creating race_season_status table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS race_season_status (
            id INTEGER PRIMARY KEY,
            season_year INTEGER UNIQUE NOT NULL,
            current_race_number INTEGER DEFAULT 1,
            season_started_at DATETIME,
            last_race_completed_at DATETIME,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    print("  ✓ race_season_status table created")
    
    # Create indexes
    print("\n📇 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_results_user ON race_results(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_results_guest ON race_results(guest_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_results_race ON race_results(race_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_championship_season ON championship_standings(season_year)")
    print("  ✓ Indexes created")
    
    # =========================================================
    # SEED DATA
    # =========================================================
    
    # Seed AI Drivers
    print("\n🏎️ Seeding AI drivers...")
    cursor.execute("SELECT COUNT(*) FROM ai_race_drivers")
    if cursor.fetchone()[0] == 0:
        for driver in AI_DRIVERS:
            cursor.execute("""
                INSERT INTO ai_race_drivers 
                (name, team, nationality, flag, driving_style, base_skill, consistency, 
                 aggression, wet_skill, tyre_management, personality_desc, avatar_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, driver)
        print(f"  ✓ Seeded {len(AI_DRIVERS)} AI drivers")
    else:
        print("  ℹ️ AI drivers already exist")
    
    # Seed Race Calendar for current season
    print("\n📅 Seeding race calendar...")
    current_year = datetime.now().year
    cursor.execute("SELECT COUNT(*) FROM race_calendar WHERE season_year = ?", (current_year,))
    if cursor.fetchone()[0] == 0:
        # Start races from next Monday
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        first_race_date = today + timedelta(days=days_until_monday)
        
        for i, race in enumerate(RACE_CALENDAR):
            race_date = first_race_date + timedelta(weeks=i)
            cursor.execute("""
                INSERT INTO race_calendar 
                (race_number, season_year, name, country, flag, track_type,
                 aero_factor, engine_factor, driver_factor, tyre_factor, team_factor,
                 rain_chance, description, race_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (race[0], current_year, race[1], race[2], race[3], race[4],
                  race[5], race[6], race[7], race[8], race[9], race[10], race[11],
                  race_date.strftime('%Y-%m-%d')))
        print(f"  ✓ Seeded {len(RACE_CALENDAR)} races for {current_year} season")
        print(f"  ℹ️ First race: {first_race_date.strftime('%A %d %B %Y')}")
    else:
        print(f"  ℹ️ {current_year} calendar already exists")
    
    # Create season status
    cursor.execute("""
        INSERT OR IGNORE INTO race_season_status (season_year, current_race_number, season_started_at, is_active)
        VALUES (?, 1, ?, 1)
    """, (current_year, datetime.now()))
    
    conn.commit()
    
    # =========================================================
    # SUMMARY
    # =========================================================
    print("\n" + "=" * 60)
    print("✅ PHASE 3 SETUP COMPLETE!")
    print("=" * 60)
    
    print(f"\n🏎️ AI Drivers: {len(AI_DRIVERS)}")
    print(f"📅 Race Calendar: {len(RACE_CALENDAR)} races")
    print(f"🏆 Points System: 1st={POINTS_SYSTEM[1]}, 2nd={POINTS_SYSTEM[2]}, 3rd={POINTS_SYSTEM[3]}")
    
    # Show AI drivers
    print("\n👥 AI Competitors:")
    cursor.execute("SELECT name, team, flag, driving_style, base_skill FROM ai_race_drivers ORDER BY base_skill DESC")
    for d in cursor.fetchall():
        print(f"   {d[2]} {d[0]} ({d[1]}) - {d[3]} - Skill: {d[4]}")
    
    # Show next few races
    print(f"\n📅 Upcoming Races ({current_year}):")
    cursor.execute("""
        SELECT race_number, name, flag, race_date, track_type, rain_chance 
        FROM race_calendar 
        WHERE season_year = ? 
        ORDER BY race_number 
        LIMIT 5
    """, (current_year,))
    for r in cursor.fetchall():
        print(f"   R{r[0]:02d}: {r[2]} {r[1]} - {r[3]} ({r[4]}, {r[5]}% rain)")
    
    conn.close()
    
    print("""
🏁 Phase 3 Ready!

Features:
- 9 AI drivers with unique personalities
- 24-race season calendar
- Weather variability
- Track-specific performance factors
- Championship standings

Next: Add routes and race UI!
""")


if __name__ == '__main__':
    main()
