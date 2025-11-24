#!/usr/bin/env python3
"""
TOPIC MANAGEMENT SYSTEM - Database Migration
=============================================
Creates the strands, topics, and tutorials tables.
Migrates existing hardcoded data to the database.

Run this ONCE after uploading the new app.py
"""

import os
import sys
import json

# Add the app directory to path
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db
from sqlalchemy import text

def run_migration():
    print("\n" + "=" * 70)
    print("TOPIC MANAGEMENT SYSTEM - Database Migration")
    print("=" * 70)
    
    with app.app_context():
        # Check if tables already exist
        result = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='strands'"
        )).fetchone()
        
        if result:
            print("\n⚠️  Tables already exist. Skipping table creation.")
            print("   If you need to re-run migration, drop tables first.")
            return
        
        print("\n📋 Step 1: Creating tables...")
        
        # Create strands table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS strands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                color VARCHAR(20) DEFAULT '#667eea',
                icon VARCHAR(10) DEFAULT '📚',
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("   ✓ Created 'strands' table")
        
        # Create topics table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id VARCHAR(50) NOT NULL UNIQUE,
                display_name VARCHAR(100) NOT NULL,
                icon VARCHAR(50) DEFAULT 'book',
                strand_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                is_visible BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (strand_id) REFERENCES strands(id)
            )
        """))
        print("   ✓ Created 'topics' table")
        
        # Create tutorials table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS tutorials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                difficulty VARCHAR(20) NOT NULL,
                title VARCHAR(200) NOT NULL,
                introduction TEXT,
                principles TEXT,
                examples TEXT,
                tips TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                UNIQUE(topic_id, difficulty)
            )
        """))
        print("   ✓ Created 'tutorials' table")
        
        db.session.commit()
        
        print("\n📋 Step 2: Populating strands...")
        
        # Insert strands
        strands_data = [
            ('Number', '#667eea', '📊', 'Master the fundamentals of numbers and operations', 1),
            ('Algebra and Functions', '#f093fb', '🔢', 'Discover patterns, equations, and functions', 2),
            ('Statistics and Probability', '#4facfe', '📈', 'Analyze data and understand probability', 3),
            ('Senior Cycle - Algebra', '#fa709a', '🎓', 'Advanced algebraic concepts for senior students', 4),
            ('Geometry and Trigonometry', '#764ba2', '📐', 'Explore shapes, measurements, and spatial reasoning', 5),
        ]
        
        for name, color, icon, description, sort_order in strands_data:
            db.session.execute(text("""
                INSERT OR IGNORE INTO strands (name, color, icon, description, sort_order)
                VALUES (:name, :color, :icon, :description, :sort_order)
            """), {'name': name, 'color': color, 'icon': icon, 'description': description, 'sort_order': sort_order})
        
        db.session.commit()
        print("   ✓ Inserted 5 strands")
        
        print("\n📋 Step 3: Populating topics...")
        
        # Get strand IDs
        strand_ids = {}
        strands = db.session.execute(text("SELECT id, name FROM strands")).fetchall()
        for s in strands:
            strand_ids[s[1]] = s[0]
        
        # Topics data: (topic_id, display_name, icon, strand_name, sort_order)
        topics_data = [
            # Number strand
            ('arithmetic', 'Arithmetic', 'calculator', 'Number', 1),
            ('multiplication_division', 'Multiplication & Division', 'times', 'Number', 2),
            ('number_systems', 'Number Systems', 'hashtag', 'Number', 3),
            ('bodmas', 'BODMAS', 'list-ol', 'Number', 4),
            ('fractions', 'Fractions', 'divide', 'Number', 5),
            ('decimals', 'Decimals', 'percent', 'Number', 6),
            ('percentages', 'Percentages', 'percent', 'Number', 7),
            ('sets', 'Sets', 'circle-notch', 'Number', 8),
            
            # Algebra and Functions strand
            ('introductory_algebra', 'Introductory Algebra', 'superscript', 'Algebra and Functions', 1),
            ('patterns', 'Patterns', 'th', 'Algebra and Functions', 2),
            ('functions', 'Functions', 'chart-line', 'Algebra and Functions', 3),
            ('solving_equations', 'Solving Equations', 'equals', 'Algebra and Functions', 4),
            ('simplifying_expressions', 'Simplifying Expressions', 'calculator', 'Algebra and Functions', 5),
            ('expanding_factorising', 'Expanding & Factorising', 'brackets', 'Algebra and Functions', 6),
            
            # Statistics and Probability strand
            ('descriptive_statistics', 'Descriptive Statistics', 'chart-bar', 'Statistics and Probability', 1),
            ('probability', 'Probability', 'dice', 'Statistics and Probability', 2),
            
            # Senior Cycle - Algebra strand
            ('surds', 'Surds', 'square-root-alt', 'Senior Cycle - Algebra', 1),
            ('complex_numbers_intro', 'Complex Numbers Intro', 'infinity', 'Senior Cycle - Algebra', 2),
            ('complex_numbers_expanded', 'Complex Numbers - Expanded', 'infinity', 'Senior Cycle - Algebra', 3),
            
            # Geometry and Trigonometry strand (for future)
            ('geometry', 'Geometry', 'shapes', 'Geometry and Trigonometry', 1),
            ('trigonometry', 'Trigonometry', 'drafting-compass', 'Geometry and Trigonometry', 2),
        ]
        
        for topic_id, display_name, icon, strand_name, sort_order in topics_data:
            strand_id = strand_ids.get(strand_name)
            db.session.execute(text("""
                INSERT OR IGNORE INTO topics (topic_id, display_name, icon, strand_id, sort_order, is_visible)
                VALUES (:topic_id, :display_name, :icon, :strand_id, :sort_order, 1)
            """), {
                'topic_id': topic_id,
                'display_name': display_name,
                'icon': icon,
                'strand_id': strand_id,
                'sort_order': sort_order
            })
        
        db.session.commit()
        print(f"   ✓ Inserted {len(topics_data)} topics")
        
        print("\n📋 Step 4: Verifying migration...")
        
        # Verify
        strand_count = db.session.execute(text("SELECT COUNT(*) FROM strands")).fetchone()[0]
        topic_count = db.session.execute(text("SELECT COUNT(*) FROM topics")).fetchone()[0]
        
        print(f"   ✓ Strands in database: {strand_count}")
        print(f"   ✓ Topics in database: {topic_count}")
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE!")
        print("=" * 70)
        print("\n✅ Next steps:")
        print("   1. Reload your web app")
        print("   2. Go to Admin Dashboard → Topic Management")
        print("   3. Add tutorials for each topic (optional)")
        print("=" * 70)

if __name__ == '__main__':
    run_migration()
