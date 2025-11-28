#!/usr/bin/env python3
"""
Phase 4 Database Migration: School Rep Dashboard + Raffle System
FIXED VERSION - Properly handles existing tables
"""
import sys
import os

# Setup paths
project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text
from datetime import datetime

print("=" * 80)
print("PHASE 4 DATABASE MIGRATION (FIXED)")
print("School Representative Dashboard + Raffle System")
print("=" * 80)
print()

with app.app_context():
    try:
        # ====================================================================
        # CLEANUP: Drop tables if they exist (in reverse order due to FK)
        # ====================================================================
        print("Checking for existing tables...")
        
        # Check what tables exist
        existing_tables = db.session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('winner_notifications', 'raffle_draws', 'raffle_entries', 'raffles', 'school_representatives')
        """)).fetchall()
        
        if existing_tables:
            print(f"Found {len(existing_tables)} existing Phase 4 tables")
            print("Dropping them to recreate cleanly...")
            
            # Drop in reverse order due to foreign keys
            drop_order = [
                'winner_notifications',
                'raffle_draws', 
                'raffle_entries',
                'raffles',
                'school_representatives'
            ]
            
            for table in drop_order:
                try:
                    db.session.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    print(f"  ✓ Dropped {table}")
                except:
                    pass
            
            db.session.commit()
            print()
        else:
            print("No existing Phase 4 tables found")
            print()
        
        # ====================================================================
        # TABLE 1: school_representatives
        # ====================================================================
        print("Creating table: school_representatives...")
        db.session.execute(text("""
            CREATE TABLE school_representatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                school_id INTEGER NOT NULL,
                role VARCHAR(50) DEFAULT 'representative',
                is_active BOOLEAN DEFAULT 1,
                can_fulfill_redemptions BOOLEAN DEFAULT 1,
                can_add_prizes BOOLEAN DEFAULT 1,
                can_view_analytics BOOLEAN DEFAULT 1,
                added_by INTEGER,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (school_id) REFERENCES prize_schools(id),
                FOREIGN KEY (added_by) REFERENCES users(id),
                UNIQUE(user_id, school_id)
            )
        """))
        print("✓ school_representatives table created")
        
        # ====================================================================
        # TABLE 2: raffles
        # ====================================================================
        print("\nCreating table: raffles...")
        db.session.execute(text("""
            CREATE TABLE raffles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                prize_description TEXT NOT NULL,
                emoji VARCHAR(10) DEFAULT '🎟️',
                
                school_id INTEGER,
                
                entry_cost INTEGER NOT NULL,
                min_level INTEGER DEFAULT 0,
                max_entries_per_student INTEGER DEFAULT 10,
                
                draw_frequency VARCHAR(20) DEFAULT 'weekly',
                draw_day_of_week INTEGER DEFAULT 5,
                draw_time TIME DEFAULT '15:00:00',
                
                prize_type VARCHAR(20) DEFAULT 'physical',
                prize_value VARCHAR(100),
                
                is_active BOOLEAN DEFAULT 1,
                auto_draw_enabled BOOLEAN DEFAULT 1,
                
                total_entries INTEGER DEFAULT 0,
                total_draws INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                
                FOREIGN KEY (school_id) REFERENCES prize_schools(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """))
        print("✓ raffles table created")
        
        # ====================================================================
        # TABLE 3: raffle_entries
        # ====================================================================
        print("\nCreating table: raffle_entries...")
        db.session.execute(text("""
            CREATE TABLE raffle_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raffle_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                school_id INTEGER NOT NULL,
                
                entry_count INTEGER DEFAULT 1,
                points_spent INTEGER NOT NULL,
                
                draw_id INTEGER,
                
                is_active BOOLEAN DEFAULT 1,
                entered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (raffle_id) REFERENCES raffles(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (school_id) REFERENCES prize_schools(id)
            )
        """))
        print("✓ raffle_entries table created")
        
        # ====================================================================
        # TABLE 4: raffle_draws
        # ====================================================================
        print("\nCreating table: raffle_draws...")
        db.session.execute(text("""
            CREATE TABLE raffle_draws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raffle_id INTEGER NOT NULL,
                school_id INTEGER,
                
                draw_date DATE NOT NULL,
                draw_time DATETIME NOT NULL,
                
                winner_id INTEGER,
                winning_entry_id INTEGER,
                
                total_entries INTEGER DEFAULT 0,
                total_participants INTEGER DEFAULT 0,
                
                token VARCHAR(100) UNIQUE,
                token_expires_at DATETIME,
                
                status VARCHAR(20) DEFAULT 'pending',
                winner_notified BOOLEAN DEFAULT 0,
                winner_notified_at DATETIME,
                
                fulfilled_by INTEGER,
                fulfilled_at DATETIME,
                fulfillment_notes TEXT,
                
                drawn_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                drawn_by VARCHAR(20) DEFAULT 'system',
                
                FOREIGN KEY (raffle_id) REFERENCES raffles(id),
                FOREIGN KEY (school_id) REFERENCES prize_schools(id),
                FOREIGN KEY (winner_id) REFERENCES users(id),
                FOREIGN KEY (winning_entry_id) REFERENCES raffle_entries(id),
                FOREIGN KEY (fulfilled_by) REFERENCES users(id)
            )
        """))
        print("✓ raffle_draws table created")
        
        # ====================================================================
        # TABLE 5: winner_notifications
        # ====================================================================
        print("\nCreating table: winner_notifications...")
        db.session.execute(text("""
            CREATE TABLE winner_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_id INTEGER NOT NULL,
                winner_id INTEGER NOT NULL,
                
                notification_type VARCHAR(20) DEFAULT 'on_login',
                shown_at DATETIME,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at DATETIME,
                
                message TEXT,
                
                FOREIGN KEY (draw_id) REFERENCES raffle_draws(id),
                FOREIGN KEY (winner_id) REFERENCES users(id)
            )
        """))
        print("✓ winner_notifications table created")
        
        # Commit tables first before creating indexes
        db.session.commit()
        
        # ====================================================================
        # CREATE INDEXES
        # ====================================================================
        print("\nCreating indexes...")
        
        # School representatives indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_school_reps_user 
            ON school_representatives(user_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_school_reps_school 
            ON school_representatives(school_id)
        """))
        
        # Raffle indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffles_active 
            ON raffles(is_active)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffles_school 
            ON raffles(school_id)
        """))
        
        # Raffle entries indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_entries_raffle 
            ON raffle_entries(raffle_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_entries_student 
            ON raffle_entries(student_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_entries_active 
            ON raffle_entries(is_active)
        """))
        
        # Raffle draws indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_draws_raffle 
            ON raffle_draws(raffle_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_draws_winner 
            ON raffle_draws(winner_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_draws_token 
            ON raffle_draws(token)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_raffle_draws_status 
            ON raffle_draws(status)
        """))
        
        # Winner notifications indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_winner_notifs_winner 
            ON winner_notifications(winner_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_winner_notifs_ack 
            ON winner_notifications(acknowledged)
        """))
        
        print("✓ All indexes created")
        
        # ====================================================================
        # COMMIT
        # ====================================================================
        db.session.commit()
        
        print()
        print("=" * 80)
        print("✓ MIGRATION COMPLETE!")
        print("=" * 80)
        print()
        print("Created 5 tables:")
        print("  1. school_representatives")
        print("  2. raffles")
        print("  3. raffle_entries")
        print("  4. raffle_draws")
        print("  5. winner_notifications")
        print()
        print("Created 14 indexes for performance")
        print()
        print("Next steps:")
        print("  1. Deploy updated app.py with new routes")
        print("  2. Deploy school rep dashboard template")
        print("  3. Deploy raffle interface templates")
        print("  4. Set up scheduler for automated draws")
        print()
        
    except Exception as e:
        db.session.rollback()
        print()
        print("=" * 80)
        print("✗ ERROR!")
        print("=" * 80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
