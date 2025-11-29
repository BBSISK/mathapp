#!/usr/bin/env python3
"""
Puzzle of the Week - Database Migration Script
Run this on PythonAnywhere to create the puzzle tables.

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python puzzle_migration.py
"""

import sys
import os

# Add the app directory to path if not already there
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db
from sqlalchemy import text
from datetime import datetime

def create_puzzle_tables():
    """Create the puzzle-related database tables"""
    
    with app.app_context():
        print("=" * 60)
        print("PUZZLE OF THE WEEK - Database Migration")
        print("=" * 60)
        
        # Table 1: weekly_puzzles
        print("\n[1/3] Creating weekly_puzzles table...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS weekly_puzzles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    puzzle_type VARCHAR(20) DEFAULT 'image',
                    puzzle_image VARCHAR(500),
                    puzzle_text TEXT,
                    answer_image VARCHAR(500),
                    answer_text TEXT,
                    hint TEXT,
                    week_number INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    reveal_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    UNIQUE(week_number, year)
                )
            """))
            db.session.commit()
            print("   ✓ weekly_puzzles table created")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ✓ weekly_puzzles table already exists")
            else:
                print(f"   ✗ Error: {e}")
        
        # Table 2: puzzle_user_status
        print("\n[2/3] Creating puzzle_user_status table...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS puzzle_user_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    puzzle_id INTEGER NOT NULL,
                    user_id INTEGER,
                    guest_code VARCHAR(20),
                    session_id VARCHAR(100),
                    dismissed_popup BOOLEAN DEFAULT 0,
                    dismissed_answer BOOLEAN DEFAULT 0,
                    revealed_answer BOOLEAN DEFAULT 0,
                    hint_viewed BOOLEAN DEFAULT 0,
                    view_count INTEGER DEFAULT 1,
                    first_viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    answer_revealed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (puzzle_id) REFERENCES weekly_puzzles(id)
                )
            """))
            db.session.commit()
            print("   ✓ puzzle_user_status table created")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ✓ puzzle_user_status table already exists")
            else:
                print(f"   ✗ Error: {e}")
        
        # Create indexes for performance
        print("\n[3/3] Creating indexes...")
        indexes = [
            ("idx_puzzle_week_year", "weekly_puzzles", "week_number, year"),
            ("idx_puzzle_active", "weekly_puzzles", "is_active"),
            ("idx_puzzle_status_user", "puzzle_user_status", "user_id, puzzle_id"),
            ("idx_puzzle_status_guest", "puzzle_user_status", "guest_code, puzzle_id"),
        ]
        
        for idx_name, table, columns in indexes:
            try:
                db.session.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})"))
                db.session.commit()
                print(f"   ✓ Index {idx_name} created")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"   ✓ Index {idx_name} already exists")
                else:
                    print(f"   ✗ Index {idx_name} error: {e}")
        
        print("\n" + "=" * 60)
        print("Migration complete!")
        print("=" * 60)
        
        # Verify tables
        print("\nVerifying tables:")
        tables = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'puzzle%' OR name LIKE 'weekly%'"
        )).fetchall()
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        print("\n✅ Database is ready for Puzzle of the Week feature!")
        print("\nNext steps:")
        print("1. Add the models and routes to app.py")
        print("2. Create /static/puzzles/ directory for images")
        print("3. Add admin UI to manage puzzles")


def create_sample_puzzle():
    """Create a sample puzzle for testing"""
    
    with app.app_context():
        from datetime import datetime
        
        # Get current week
        now = datetime.utcnow()
        week_num = now.isocalendar()[1]
        year = now.year
        
        # Check if puzzle exists for this week
        existing = db.session.execute(text(
            "SELECT id FROM weekly_puzzles WHERE week_number = :week AND year = :year"
        ), {'week': week_num, 'year': year}).fetchone()
        
        if existing:
            print(f"Sample puzzle already exists for Week {week_num}, {year}")
            return
        
        # Create sample puzzle
        db.session.execute(text("""
            INSERT INTO weekly_puzzles 
            (title, description, puzzle_type, puzzle_text, answer_text, hint, week_number, year, is_active, created_by)
            VALUES 
            (:title, :desc, :ptype, :ptext, :atext, :hint, :week, :year, 1, 1)
        """), {
            'title': 'Number Sequence Challenge',
            'desc': 'Can you find the next number in this sequence?',
            'ptype': 'text',
            'ptext': 'What comes next?\n\n2, 6, 12, 20, 30, ?',
            'atext': 'The answer is 42!\n\nPattern: differences are 4, 6, 8, 10, 12...\n(Each difference increases by 2)',
            'hint': 'Look at the differences between consecutive numbers.',
            'week': week_num,
            'year': year
        })
        db.session.commit()
        
        print(f"✓ Created sample puzzle for Week {week_num}, {year}")


if __name__ == '__main__':
    create_puzzle_tables()
    
    # Ask if user wants sample data
    response = input("\nCreate a sample puzzle for testing? (y/n): ").strip().lower()
    if response == 'y':
        create_sample_puzzle()
    
    print("\nDone!")
