"""
Raffle System Database Migration Script
Run this on PythonAnywhere to create raffle tables if they don't exist.

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python migrate_raffle_tables.py
"""

from app import app, db
from sqlalchemy import text

def migrate_raffle_tables():
    with app.app_context():
        print("=" * 60)
        print("🎟️  RAFFLE SYSTEM DATABASE MIGRATION")
        print("=" * 60)
        
        # Check existing tables
        existing_tables = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )).fetchall()
        existing_table_names = [t[0] for t in existing_tables]
        print(f"\nExisting tables: {len(existing_table_names)}")
        
        # 1. Create raffles table
        if 'raffles' not in existing_table_names:
            print("\n📋 Creating 'raffles' table...")
            db.session.execute(text("""
                CREATE TABLE raffles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    prize_description TEXT NOT NULL,
                    emoji VARCHAR(10) DEFAULT '🎟️',
                    school_id INTEGER,
                    entry_cost INTEGER DEFAULT 100,
                    max_entries_per_student INTEGER DEFAULT 10,
                    draw_frequency VARCHAR(20) DEFAULT 'weekly',
                    draw_day_of_week INTEGER DEFAULT 5,
                    draw_time VARCHAR(10) DEFAULT '15:00:00',
                    prize_type VARCHAR(20) DEFAULT 'physical',
                    prize_value INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    auto_draw_enabled BOOLEAN DEFAULT 0,
                    total_entries INTEGER DEFAULT 0,
                    total_draws INTEGER DEFAULT 0,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES prize_schools(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """))
            print("   ✓ 'raffles' table created")
        else:
            print("\n✓ 'raffles' table already exists")
        
        # 2. Create raffle_entries table
        if 'raffle_entries' not in existing_table_names:
            print("\n📋 Creating 'raffle_entries' table...")
            db.session.execute(text("""
                CREATE TABLE raffle_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raffle_id INTEGER NOT NULL,
                    student_id INTEGER,
                    guest_code VARCHAR(20),
                    points_spent INTEGER NOT NULL,
                    entered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    draw_id INTEGER,
                    FOREIGN KEY (raffle_id) REFERENCES raffles(id),
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    FOREIGN KEY (draw_id) REFERENCES raffle_draws(id)
                )
            """))
            print("   ✓ 'raffle_entries' table created")
        else:
            print("\n✓ 'raffle_entries' table already exists")
        
        # 3. Create raffle_draws table
        if 'raffle_draws' not in existing_table_names:
            print("\n📋 Creating 'raffle_draws' table...")
            db.session.execute(text("""
                CREATE TABLE raffle_draws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raffle_id INTEGER NOT NULL,
                    school_id INTEGER,
                    draw_date DATE NOT NULL,
                    draw_time DATETIME,
                    winner_id INTEGER,
                    winner_guest_code VARCHAR(20),
                    winning_entry_id INTEGER,
                    total_entries INTEGER DEFAULT 0,
                    total_participants INTEGER DEFAULT 0,
                    token VARCHAR(50),
                    token_expires_at DATETIME,
                    status VARCHAR(20) DEFAULT 'scheduled',
                    drawn_at DATETIME,
                    drawn_by VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (raffle_id) REFERENCES raffles(id),
                    FOREIGN KEY (school_id) REFERENCES prize_schools(id),
                    FOREIGN KEY (winner_id) REFERENCES users(id),
                    FOREIGN KEY (winning_entry_id) REFERENCES raffle_entries(id)
                )
            """))
            print("   ✓ 'raffle_draws' table created")
        else:
            print("\n✓ 'raffle_draws' table already exists")
        
        # 4. Create winner_notifications table (if not exists)
        if 'winner_notifications' not in existing_table_names:
            print("\n📋 Creating 'winner_notifications' table...")
            db.session.execute(text("""
                CREATE TABLE winner_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draw_id INTEGER NOT NULL,
                    winner_id INTEGER,
                    winner_guest_code VARCHAR(20),
                    notification_type VARCHAR(20) DEFAULT 'on_login',
                    message TEXT,
                    acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draw_id) REFERENCES raffle_draws(id),
                    FOREIGN KEY (winner_id) REFERENCES users(id)
                )
            """))
            print("   ✓ 'winner_notifications' table created")
        else:
            print("\n✓ 'winner_notifications' table already exists")
        
        db.session.commit()
        
        # Verify tables
        print("\n" + "=" * 60)
        print("📊 VERIFICATION")
        print("=" * 60)
        
        for table in ['raffles', 'raffle_entries', 'raffle_draws', 'winner_notifications']:
            try:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                print(f"   ✓ {table}: {count} records")
            except Exception as e:
                print(f"   ✗ {table}: Error - {e}")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nYou can now use the Raffles tab in the Admin Dashboard.")
        print("Students will be able to enter raffles once you create them.")

if __name__ == '__main__':
    migrate_raffle_tables()
