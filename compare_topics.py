"""
Compare working topics vs algebra topics to find the difference
Run on PythonAnywhere: python3 compare_topics.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db
from sqlalchemy import text

with app.app_context():
    print("=" * 70)
    print("COMPARING WORKING TOPICS VS ALGEBRA TOPICS")
    print("=" * 70)
    
    # Get all topics with their strand values
    result = db.session.execute(text("""
        SELECT topic, strand, COUNT(*) as count
        FROM questions
        GROUP BY topic, strand
        ORDER BY topic
    """))
    
    print("\nALL TOPICS IN DATABASE:")
    print("-" * 70)
    print(f"{'Topic':<40} {'Strand':<20} {'Count':<10}")
    print("-" * 70)
    
    has_strand = []
    no_strand = []
    
    for row in result:
        topic, strand, count = row
        strand_display = strand if strand else "NULL"
        print(f"{topic:<40} {strand_display:<20} {count:<10}")
        
        if strand:
            has_strand.append((topic, strand, count))
        else:
            no_strand.append((topic, count))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nTopics WITH strand (showing in admin): {len(has_strand)}")
    for topic, strand, count in has_strand[:5]:
        print(f"  - {topic} ({strand})")
    if len(has_strand) > 5:
        print(f"  ... and {len(has_strand) - 5} more")
    
    print(f"\nTopics WITHOUT strand (NOT showing in admin): {len(no_strand)}")
    for topic, count in no_strand:
        print(f"  - {topic} ({count} questions)")
    
    # Check if there's a pattern in strand values
    print("\n" + "=" * 70)
    print("STRAND VALUES USED:")
    print("=" * 70)
    strands = db.session.execute(text("""
        SELECT DISTINCT strand, COUNT(DISTINCT topic) as topic_count
        FROM questions
        WHERE strand IS NOT NULL
        GROUP BY strand
        ORDER BY strand
    """))
    
    for row in strands:
        strand, topic_count = row
        print(f"  {strand}: {topic_count} topics")
