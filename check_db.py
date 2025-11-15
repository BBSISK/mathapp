#!/usr/bin/env python3
"""Check what topics are in the database"""

from app import app, db, Question
from sqlalchemy import text

with app.app_context():
    # Check if strand column exists and has data
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT topic, strand, COUNT(*) as count 
            FROM questions 
            GROUP BY topic, strand 
            ORDER BY strand, topic
        """))
        
        print("Current database contents:")
        print("-" * 50)
        for row in result:
            print(f"{row[1] or 'NULL':<30} | {row[0]:<25} | {row[2]} questions")
        
        # Specifically check for patterns
        print("\n" + "=" * 50)
        result2 = conn.execute(text("SELECT COUNT(*) FROM questions WHERE topic='patterns'"))
        patterns_count = result2.fetchone()[0]
        print(f"Patterns questions in database: {patterns_count}")
