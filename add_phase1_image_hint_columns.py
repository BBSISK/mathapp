#!/usr/bin/env python3
"""
Phase 1 Migration: Add Image and Hint Support to Questions

This script adds the following columns to the questions table:
- image_url: Path to question image (optional)
- image_caption: Caption for the image (optional)
- hint_text: Hint text to help students (optional)
- hint_penalty: Percentage of points lost if hint is used (default 50)

Also creates the static/question_images directory for storing uploaded images.

Run on PythonAnywhere:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python add_phase1_image_hint_columns.py
"""

import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db
from sqlalchemy import text

def add_columns():
    print("\n" + "="*60)
    print("  PHASE 1: ADD IMAGE AND HINT COLUMNS TO QUESTIONS")
    print("="*60)
    
    with app.app_context():
        # Check current columns in questions table
        print("\n📊 Checking questions table...")
        
        result = db.session.execute(text("PRAGMA table_info(questions)")).fetchall()
        columns = [row[1] for row in result]
        
        print(f"  Current columns: {', '.join(columns)}")
        
        # Add image_url column
        if 'image_url' not in columns:
            print("\n  Adding image_url column...")
            db.session.execute(text("ALTER TABLE questions ADD COLUMN image_url VARCHAR(500)"))
            print("  ✓ image_url added")
        else:
            print("\n  ✓ image_url already exists")
        
        # Add image_caption column
        if 'image_caption' not in columns:
            print("  Adding image_caption column...")
            db.session.execute(text("ALTER TABLE questions ADD COLUMN image_caption VARCHAR(200)"))
            print("  ✓ image_caption added")
        else:
            print("  ✓ image_caption already exists")
        
        # Add hint_text column
        if 'hint_text' not in columns:
            print("  Adding hint_text column...")
            db.session.execute(text("ALTER TABLE questions ADD COLUMN hint_text VARCHAR(500)"))
            print("  ✓ hint_text added")
        else:
            print("  ✓ hint_text already exists")
        
        # Add hint_penalty column
        if 'hint_penalty' not in columns:
            print("  Adding hint_penalty column...")
            db.session.execute(text("ALTER TABLE questions ADD COLUMN hint_penalty INTEGER DEFAULT 50"))
            print("  ✓ hint_penalty added")
        else:
            print("  ✓ hint_penalty already exists")
        
        db.session.commit()
        
        # Create question_images directory
        print("\n📁 Creating question_images directory...")
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'question_images')
        os.makedirs(static_dir, exist_ok=True)
        print(f"  ✓ Directory ready: {static_dir}")
        
        # Verify final structure
        print("\n📋 Final questions table structure:")
        result = db.session.execute(text("PRAGMA table_info(questions)")).fetchall()
        for row in result:
            default_val = f" (default: {row[4]})" if row[4] else ""
            nullable = "nullable" if row[3] == 0 else "NOT NULL"
            print(f"    - {row[1]} ({row[2]}) {nullable}{default_val}")
        
        # Count questions
        count = db.session.execute(text("SELECT COUNT(*) FROM questions")).fetchone()[0]
        print(f"\n📊 Total questions in database: {count}")
        
        print("\n" + "="*60)
        print("✅ Phase 1 migration complete!")
        print("="*60)
        print("""
Next steps:
1. Questions can now have images and hints
2. Edit questions in Admin Dashboard to add images/hints
3. Students will see images and can use hints during quizzes
4. Streaks will multiply points for consecutive correct answers

Streak Multipliers:
  - 3 in a row: 1.5x points
  - 5 in a row: 1.75x points  
  - 7 in a row: 2.0x points
  - 10+ in a row: 2.5x points

Hint Penalties:
  - Easy hint: 25% point reduction
  - Standard: 50% point reduction
  - Big hint: 75% point reduction
""")


if __name__ == '__main__':
    add_columns()
