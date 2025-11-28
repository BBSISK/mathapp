#!/usr/bin/env python3
"""
Check all topics in database and their question counts
"""
import sys
import os

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text

print("=" * 70)
print("DATABASE TOPICS AUDIT")
print("=" * 70)
print()

with app.app_context():
    # Get all distinct topics from questions table
    result = db.session.execute(text("SELECT DISTINCT topic, COUNT(*) as count FROM questions GROUP BY topic ORDER BY topic"))
    topics = result.fetchall()
    
    print(f"Found {len(topics)} unique topics in questions table:")
    print()
    
    for topic, count in topics:
        print(f"  • {topic:40} - {count:4} questions")
    
    print()
    print("=" * 70)
    print()
    
    # Check which topics are missing from the hardcoded dropdown
    hardcoded_topics = [
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems', 'bodmas', 'introductory_algebra', 'patterns',
        'functions', 'solving_equations', 'simplifying_expressions',
        'expanding_factorising', 'surds', 'sets', 'probability',
        'descriptive_statistics', 'complex_numbers_intro', 'complex_numbers_expanded'
    ]
    
    db_topics = [topic for topic, _ in topics]
    
    missing_from_dropdown = [t for t in db_topics if t not in hardcoded_topics]
    missing_from_db = [t for t in hardcoded_topics if t not in db_topics]
    
    if missing_from_dropdown:
        print("⚠️  TOPICS IN DATABASE BUT NOT IN DROPDOWN:")
        for topic in missing_from_dropdown:
            count = next(c for t, c in topics if t == topic)
            print(f"  • {topic} ({count} questions)")
        print()
    
    if missing_from_db:
        print("⚠️  TOPICS IN DROPDOWN BUT NOT IN DATABASE:")
        for topic in missing_from_db:
            print(f"  • {topic}")
        print()
    
    if not missing_from_dropdown and not missing_from_db:
        print("✓ All topics are synchronized!")
        print()
