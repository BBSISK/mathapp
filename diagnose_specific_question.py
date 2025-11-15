#!/usr/bin/env python3
"""
Diagnose why "7m + 3m - 1m" question is marked wrong
"""

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("DIAGNOSING SPECIFIC QUESTION: 7m + 3m - 1m")
print("=" * 80)

with app.app_context():
    with db.engine.connect() as conn:
        # Find this specific question
        result = conn.execute(text("""
            SELECT id, question_text, 
                   option_a, option_b, option_c, option_d, 
                   correct_answer, explanation
            FROM questions
            WHERE topic = 'introductory_algebra'
            AND question_text LIKE '%7m + 3m - 1m%'
        """))
        
        question = result.fetchone()
        
        if question:
            q_id, q_text, opt_a, opt_b, opt_c, opt_d, correct_ans, expl = question
            
            print(f"\nQuestion ID: {q_id}")
            print(f"Question: {q_text}")
            print(f"\nOptions:")
            print(f"  A (option_a): '{opt_a}'")
            print(f"  B (option_b): '{opt_b}'")
            print(f"  C (option_c): '{opt_c}'")
            print(f"  D (option_d): '{opt_d}'")
            print(f"\nCorrect Answer (stored as integer): {correct_ans}")
            print(f"  This means option: {['A', 'B', 'C', 'D'][correct_ans - 1]}")
            
            options = [opt_a, opt_b, opt_c, opt_d]
            correct_text = options[correct_ans - 1]
            print(f"  Which is: '{correct_text}'")
            
            print(f"\nExplanation: {expl}")
            
            # Check what the answer SHOULD be
            print("\n" + "=" * 80)
            print("MANUAL CALCULATION:")
            print("  7m + 3m - 1m")
            print("  = (7 + 3 - 1)m")
            print("  = 9m")
            print("\n" + "=" * 80)
            
            if correct_text == '9m':
                print("✓ DATABASE IS CORRECT: Answer is '9m'")
                print("\n⚠️  PROBLEM: Frontend answer checking logic is wrong!")
                print("\nThe issue is likely:")
                print("  1. Frontend is comparing wrong option")
                print("  2. Frontend has incorrect answer checking code")
                print("  3. Option order is shuffled in frontend but not tracked correctly")
            else:
                print(f"✗ DATABASE IS WRONG: Answer is '{correct_text}', should be '9m'")
                print(f"\nThe correct_answer field ({correct_ans}) points to the wrong option!")
        else:
            print("\n✗ Question not found in database")
            print("\nSearching for similar questions...")
            
            result = conn.execute(text("""
                SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
                FROM questions
                WHERE topic = 'introductory_algebra'
                AND difficulty = 'beginner'
                AND question_text LIKE '%7%m%3%m%1%m%'
                LIMIT 5
            """))
            
            for q in result:
                print(f"\nID {q[0]}: {q[1]}")
                print(f"  Options: {q[2]}, {q[3]}, {q[4]}, {q[5]}")
                print(f"  Correct: {q[6]} = {[q[2], q[3], q[4], q[5]][q[6]-1]}")

if __name__ == '__main__':
    pass
