"""
Check raw difficulty values for Introductory Algebra questions
Run on PythonAnywhere: python3 check_algebra_raw.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question

with app.app_context():
    algebra_questions = Question.query.filter(
        Question.topic == 'introductory_algebra'
    ).all()
    
    print("=" * 60)
    print(f"TOTAL QUESTIONS: {len(algebra_questions)}")
    print("=" * 60)
    
    # Check unique difficulty values
    difficulties = {}
    for q in algebra_questions:
        diff = q.difficulty
        if diff not in difficulties:
            difficulties[diff] = []
        difficulties[diff].append(q)
    
    print(f"\nUnique difficulty values found:")
    for diff, questions in difficulties.items():
        print(f"  '{diff}': {len(questions)} questions")
    
    # Show first 10 questions with their details
    print("\n" + "=" * 60)
    print("FIRST 10 QUESTIONS")
    print("=" * 60)
    
    for i, q in enumerate(algebra_questions[:10], 1):
        print(f"\n{i}. Difficulty: '{q.difficulty}'")
        print(f"   Question: {q.question_text}")
        options = [q.option_a, q.option_b, q.option_c, q.option_d]
        correct = options[q.correct_answer - 1]
        print(f"   Correct answer: {correct}")
    
    # Show sample from each difficulty
    print("\n" + "=" * 60)
    print("SAMPLES FROM EACH DIFFICULTY LEVEL")
    print("=" * 60)
    
    for diff in sorted(difficulties.keys()):
        print(f"\n--- DIFFICULTY: '{diff}' ({len(difficulties[diff])} total) ---")
        for i, q in enumerate(difficulties[diff][:3], 1):
            print(f"\n  Example {i}: {q.question_text}")
            options = [q.option_a, q.option_b, q.option_c, q.option_d]
            print(f"  Options: {', '.join(options)}")
            correct = options[q.correct_answer - 1]
            print(f"  Correct: {correct}")
