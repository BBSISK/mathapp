"""
Check Introductory Algebra questions by difficulty level
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question

with app.app_context():
    # Get all Introductory Algebra questions
    algebra_questions = Question.query.filter(
        Question.topic.ilike('%introductory%algebra%')
    ).all()
    
    if not algebra_questions:
        # Try alternative search
        algebra_questions = Question.query.filter(
            Question.topic.ilike('%algebra%')
        ).all()
    
    if not algebra_questions:
        print("No algebra questions found!")
        print("\nAvailable topics:")
        topics = db.session.query(Question.topic).distinct().all()
        for t in topics:
            print(f"  - {t[0]}")
    else:
        # Group by difficulty
        easy = []
        medium = []
        hard = []
        
        for q in algebra_questions:
            if q.difficulty.lower() == 'easy':
                easy.append(q)
            elif q.difficulty.lower() == 'medium':
                medium.append(q)
            elif q.difficulty.lower() == 'hard':
                hard.append(q)
        
        print("=" * 60)
        print(f"INTRODUCTORY ALGEBRA QUESTIONS ANALYSIS")
        print("=" * 60)
        print(f"\nTopic: {algebra_questions[0].topic}")
        print(f"Total Questions: {len(algebra_questions)}")
        print(f"\nBy Difficulty:")
        print(f"  Easy:   {len(easy)} questions")
        print(f"  Medium: {len(medium)} questions")
        print(f"  Hard:   {len(hard)} questions")
        
        # Show sample questions from each difficulty
        print("\n" + "=" * 60)
        print("SAMPLE QUESTIONS BY DIFFICULTY")
        print("=" * 60)
        
        if easy:
            print("\n--- EASY (First 5) ---")
            for i, q in enumerate(easy[:5], 1):
                print(f"\n{i}. {q.question_text}")
                print(f"   Options: {q.option_a}, {q.option_b}, {q.option_c}, {q.option_d}")
                correct_option = [q.option_a, q.option_b, q.option_c, q.option_d][q.correct_answer - 1]
                print(f"   Correct: {correct_option}")
        
        if medium:
            print("\n--- MEDIUM (First 5) ---")
            for i, q in enumerate(medium[:5], 1):
                print(f"\n{i}. {q.question_text}")
                print(f"   Options: {q.option_a}, {q.option_b}, {q.option_c}, {q.option_d}")
                correct_option = [q.option_a, q.option_b, q.option_c, q.option_d][q.correct_answer - 1]
                print(f"   Correct: {correct_option}")
        
        if hard:
            print("\n--- HARD (First 5) ---")
            for i, q in enumerate(hard[:5], 1):
                print(f"\n{i}. {q.question_text}")
                print(f"   Options: {q.option_a}, {q.option_b}, {q.option_c}, {q.option_d}")
                correct_option = [q.option_a, q.option_b, q.option_c, q.option_d][q.correct_answer - 1]
                print(f"   Correct: {correct_option}")

