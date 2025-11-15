#!/usr/bin/env python3
"""
Display first 10 questions from each algebra topic for manual inspection
"""

from app import app, db
from sqlalchemy import text

def show_questions():
    print("=" * 80)
    print("FIRST 10 QUESTIONS FROM EACH ALGEBRA TOPIC")
    print("=" * 80)
    
    topics = [
        'introductory_algebra',
        'solving_equations',
        'simplifying_expressions',
        'expanding_factorising'
    ]
    
    with app.app_context():
        with db.engine.connect() as conn:
            for topic in topics:
                print(f"\n{'='*80}")
                print(f"TOPIC: {topic.upper().replace('_', ' ')}")
                print('='*80)
                
                result = conn.execute(text("""
                    SELECT id, difficulty, question_text, 
                           option_a, option_b, option_c, option_d, correct_answer,
                           explanation
                    FROM questions
                    WHERE topic = :topic
                    ORDER BY difficulty, id
                    LIMIT 10
                """), {'topic': topic})
                
                questions = result.fetchall()
                
                for i, q in enumerate(questions, 1):
                    q_id, diff, q_text, opt_a, opt_b, opt_c, opt_d, correct, expl = q
                    
                    print(f"\n{i}. [{diff.upper()}] Question ID: {q_id}")
                    print(f"   Question: {q_text}")
                    print(f"   A) {opt_a}")
                    print(f"   B) {opt_b}")
                    print(f"   C) {opt_c}")
                    print(f"   D) {opt_d}")
                    print(f"   Correct Answer: {correct} ({['A','B','C','D'][correct-1]})")
                    print(f"   Explanation: {expl}")
                    
                    # Manual check
                    options = [opt_a, opt_b, opt_c, opt_d]
                    correct_option = options[correct - 1]
                    print(f"   → Selected answer: {correct_option}")

if __name__ == '__main__':
    show_questions()
