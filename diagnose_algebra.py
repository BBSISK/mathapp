"""
Diagnostic script to check algebra questions
Run this in PythonAnywhere bash console: python3 diagnose_algebra.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question

with app.app_context():
    # Check all topics
    print("=" * 60)
    print("ALL TOPICS IN DATABASE:")
    print("=" * 60)
    
    topics = db.session.query(Question.topic).distinct().all()
    for topic_tuple in topics:
        topic = topic_tuple[0]
        q_count = Question.query.filter_by(topic=topic).count()
        print(f"{topic:40s} ({q_count} questions)")
    
    # Check for algebra-related topics
    print("\n" + "=" * 60)
    print("ALGEBRA-RELATED TOPICS:")
    print("=" * 60)
    algebra_questions = Question.query.filter(Question.topic.ilike('%algebra%')).all()
    
    if not algebra_questions:
        print("No questions found with 'algebra' in topic name")
        print("\nTrying 'Introductory Algebra'...")
        algebra_questions = Question.query.filter(Question.topic.ilike('%introductory%')).all()
    
    if not algebra_questions:
        print("\n❌ No algebra questions found in database!")
    else:
        # Group by topic
        topics_dict = {}
        for q in algebra_questions:
            if q.topic not in topics_dict:
                topics_dict[q.topic] = []
            topics_dict[q.topic].append(q)
        
        for topic, questions in topics_dict.items():
            print(f"\n{'=' * 60}")
            print(f"Topic: {topic}")
            print(f"Questions: {len(questions)}")
            print(f"{'=' * 60}")
            
            # Check for duplicate answers
            duplicate_count = 0
            for i, q in enumerate(questions[:10], 1):  # Check first 10
                options = [q.option_a, q.option_b, q.option_c, q.option_d]
                print(f"\nQ{i} (ID: {q.id}): {q.question_text[:60]}...")
                print(f"  Options: {options}")
                print(f"  Correct: Option {chr(64 + q.correct_answer)} ({options[q.correct_answer - 1]})")
                
                # Check for duplicates
                if len(options) != len(set(options)):
                    print(f"  ⚠️  DUPLICATE OPTIONS FOUND!")
                    from collections import Counter
                    duplicates = [item for item, count in Counter(options).items() if count > 1]
                    print(f"  Duplicates: {duplicates}")
                    duplicate_count += 1
            
            if duplicate_count > 0:
                print(f"\n⚠️  Found {duplicate_count} questions with duplicate options (in first 10 checked)")
            else:
                print(f"\n✓ No duplicates found (in first 10 checked)")
