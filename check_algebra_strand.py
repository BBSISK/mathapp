"""
Check the strand value for introductory_algebra questions
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question

with app.app_context():
    # Get a sample algebra question
    algebra_q = Question.query.filter(
        Question.topic == 'introductory_algebra'
    ).first()
    
    if algebra_q:
        print("Sample Introductory Algebra Question:")
        print(f"  Topic: {algebra_q.topic}")
        print(f"  Strand: {algebra_q.strand if hasattr(algebra_q, 'strand') else 'NO STRAND FIELD'}")
        print(f"  Difficulty: {algebra_q.difficulty}")
        print(f"  Question: {algebra_q.question_text}")
        
        # Check if strand column exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('questions')]
        print(f"\nColumns in questions table:")
        for col in columns:
            print(f"  - {col}")
    else:
        print("No introductory_algebra questions found")
