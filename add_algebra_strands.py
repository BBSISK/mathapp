"""
Add strand values to algebra questions so they appear in admin dropdown
Run on PythonAnywhere: python3 add_algebra_strands.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question

# Map topics to their appropriate strands
TOPIC_TO_STRAND = {
    'introductory_algebra': 'Algebra',
    'patterns': 'Algebra',
    'functions': 'Algebra',
    'solving_equations': 'Algebra',
    'simplifying_expressions': 'Algebra',
    'expanding_factorising': 'Algebra',
    # Add any other algebra topics you have
}

with app.app_context():
    print("=" * 60)
    print("ADDING STRAND VALUES TO ALGEBRA QUESTIONS")
    print("=" * 60)
    
    total_updated = 0
    
    for topic, strand in TOPIC_TO_STRAND.items():
        # Get all questions for this topic
        questions = Question.query.filter_by(topic=topic).all()
        
        if questions:
            # Count how many need updating
            need_update = [q for q in questions if q.strand is None]
            
            if need_update:
                print(f"\n{topic}:")
                print(f"  Total questions: {len(questions)}")
                print(f"  Missing strand: {len(need_update)}")
                
                # Update all questions for this topic
                for q in need_update:
                    q.strand = strand
                    total_updated += 1
                
                print(f"  ✓ Updated to strand: '{strand}'")
            else:
                print(f"\n{topic}: All {len(questions)} questions already have strand")
        else:
            print(f"\n{topic}: No questions found")
    
    # Commit all changes
    if total_updated > 0:
        db.session.commit()
        print("\n" + "=" * 60)
        print(f"✓ SUCCESSFULLY UPDATED {total_updated} QUESTIONS")
        print("=" * 60)
        print("\nAlgebra topics should now appear in admin dropdown!")
    else:
        print("\n" + "=" * 60)
        print("✓ All algebra questions already have strand values")
        print("=" * 60)
    
    # Show summary of all topics and their strands
    print("\n" + "=" * 60)
    print("SUMMARY: ALL TOPICS BY STRAND")
    print("=" * 60)
    
    from sqlalchemy import text
    result = db.session.execute(text("""
        SELECT DISTINCT topic, strand, COUNT(*) as count
        FROM questions
        GROUP BY topic, strand
        ORDER BY strand, topic
    """))
    
    current_strand = None
    for row in result:
        topic, strand, count = row
        if strand != current_strand:
            current_strand = strand
            print(f"\n{strand or 'NO STRAND'}:")
        print(f"  - {topic}: {count} questions")
