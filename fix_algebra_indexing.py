#!/usr/bin/env python3
"""
Fix algebra questions: Convert correct_answer from 1-4 indexing to 0-3 indexing
This matches the format used by working topics like Arithmetic
"""

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("FIXING ALGEBRA QUESTIONS - CONVERTING FROM 1-4 TO 0-3 INDEXING")
print("=" * 80)

algebra_topics = [
    'introductory_algebra',
    'solving_equations',
    'simplifying_expressions',
    'expanding_factorising',
    'patterns'
]

with app.app_context():
    with db.engine.connect() as conn:
        total_fixed = 0
        
        for topic in algebra_topics:
            print(f"\nProcessing: {topic}")
            
            # Count questions that need fixing (correct_answer >= 1)
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM questions 
                WHERE topic = :topic 
                AND correct_answer >= 1
            """), {'topic': topic})
            
            count = result.fetchone()[0]
            
            if count > 0:
                print(f"  Found {count} questions with 1-4 indexing")
                
                # Update: subtract 1 from correct_answer
                conn.execute(text("""
                    UPDATE questions 
                    SET correct_answer = correct_answer - 1
                    WHERE topic = :topic
                    AND correct_answer >= 1
                """), {'topic': topic})
                
                print(f"  ✓ Converted to 0-3 indexing")
                total_fixed += count
            else:
                print(f"  Already using 0-3 indexing (or no questions)")
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"✓ FIXED {total_fixed} QUESTIONS")
        print("=" * 80)
        
        # Verify the fix
        print("\nVERIFYING FIX...")
        print("-" * 80)
        
        for topic in algebra_topics:
            result = conn.execute(text("""
                SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
                FROM questions
                WHERE topic = :topic
                LIMIT 1
            """), {'topic': topic})
            
            q = result.fetchone()
            if q:
                q_id, q_text, opt_a, opt_b, opt_c, opt_d, correct_idx = q
                options = [opt_a, opt_b, opt_c, opt_d]
                
                print(f"\n{topic}:")
                print(f"  Question: {q_text[:50]}...")
                print(f"  Correct Answer Index: {correct_idx}")
                print(f"  This means: {['A', 'B', 'C', 'D'][correct_idx]} = '{options[correct_idx]}'")
                
                if correct_idx >= 0 and correct_idx <= 3:
                    print(f"  ✓ Using 0-3 indexing (CORRECT)")
                else:
                    print(f"  ✗ Still using wrong indexing!")
        
        print("\n" + "=" * 80)
        print("DONE! Now reload your web app and test the questions.")
        print("=" * 80)

if __name__ == '__main__':
    pass
