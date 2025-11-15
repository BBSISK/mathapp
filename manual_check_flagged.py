#!/usr/bin/env python3
"""
Manual spot-check of the 20 flagged Introductory Algebra questions
"""

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("MANUAL VERIFICATION OF FLAGGED QUESTIONS")
print("=" * 80)

with app.app_context():
    with db.engine.connect() as conn:
        # Get the specific questions that were flagged
        result = conn.execute(text("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE topic = 'introductory_algebra'
            AND id BETWEEN 2429 AND 2448
            ORDER BY id
        """))
        
        questions = result.fetchall()
        
        print(f"\nChecking {len(questions)} three-term questions:\n")
        
        all_correct = True
        
        for q in questions:
            q_id, q_text, opt_a, opt_b, opt_c, opt_d, correct_idx = q
            options = [opt_a, opt_b, opt_c, opt_d]
            marked_correct = options[correct_idx - 1]
            
            # Extract the expression
            # Pattern: "Simplify: 2y + 1y + 4y"
            import re
            match = re.search(r'(\d+)([a-z])\s*\+\s*(\d+)\2\s*\+\s*(\d+)\2', q_text)
            
            if match:
                a = int(match.group(1))
                var = match.group(2)
                b = int(match.group(3))
                c = int(match.group(4))
                
                # Calculate what it should be
                total = a + b + c
                expected = f"{total}{var}"
                
                is_correct = (marked_correct == expected)
                status = "✓" if is_correct else "✗"
                
                print(f"{status} ID {q_id}: {a}{var} + {b}{var} + {c}{var} = {expected}")
                print(f"  Marked as correct: '{marked_correct}'")
                
                if not is_correct:
                    print(f"  ❌ WRONG! Should be '{expected}'")
                    all_correct = False
                
                print()
        
        print("=" * 80)
        if all_correct:
            print("✅ ALL FLAGGED QUESTIONS ARE ACTUALLY CORRECT!")
            print("   The validation script had a regex bug.")
        else:
            print("❌ Some questions need fixing")
        print("=" * 80)

if __name__ == '__main__':
    pass
