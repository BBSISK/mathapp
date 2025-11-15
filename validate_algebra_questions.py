#!/usr/bin/env python3
"""
Validate ALL algebra questions for mathematical accuracy
Checks: solving_equations, simplifying_expressions, expanding_factorising, introductory_algebra
"""

from app import app, db
from sqlalchemy import text
import re

def validate_introductory_algebra(question_text, correct_answer, explanation, difficulty):
    """Validate introductory algebra questions"""
    errors = []
    
    try:
        if difficulty == 'beginner':
            # Collecting like terms: e.g., "3x + 5x" should be "8x"
            match = re.search(r'(\d+)([a-z])\s*\+\s*(\d+)\2', question_text)
            if match:
                a, var, b = int(match.group(1)), match.group(2), int(match.group(3))
                expected = f"{a + b}{var}"
                if correct_answer.strip() != expected:
                    errors.append(f"Expected {expected}, got {correct_answer}")
            
            # Subtraction: e.g., "8x - 3x" should be "5x"
            match = re.search(r'(\d+)([a-z])\s*-\s*(\d+)\2', question_text)
            if match:
                a, var, b = int(match.group(1)), match.group(2), int(match.group(3))
                expected = f"{a - b}{var}"
                if correct_answer.strip() != expected:
                    errors.append(f"Expected {expected}, got {correct_answer}")
        
        elif difficulty == 'intermediate':
            # Substitution questions: "If x = 5, find x + 3"
            match = re.search(r'x\s*=\s*(\d+)', question_text)
            if match:
                x_val = int(match.group(1))
                
                # Pattern: x + number
                if 'x +' in question_text or 'x+' in question_text:
                    num_match = re.search(r'x\s*\+\s*(\d+)', question_text)
                    if num_match:
                        b = int(num_match.group(1))
                        expected = str(x_val + b)
                        if correct_answer.strip() != expected:
                            errors.append(f"x={x_val}, x+{b} should be {expected}, got {correct_answer}")
                
                # Pattern: ax (multiplication)
                num_match = re.search(r'(\d+)x[^a-z\+\-]', question_text)
                if num_match:
                    a = int(num_match.group(1))
                    expected = str(a * x_val)
                    if correct_answer.strip() != expected:
                        errors.append(f"x={x_val}, {a}x should be {expected}, got {correct_answer}")
    
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors

def validate_solving_equations(question_text, correct_answer, explanation, difficulty):
    """Validate solving equations questions"""
    errors = []
    
    try:
        # Extract equation from question
        match = re.search(r'x\s*[\+\-]\s*\d+\s*=\s*\d+', question_text)
        if match:
            equation = match.group(0)
            
            # Parse: x + a = b
            if '+' in equation:
                parts = equation.split('=')
                left = parts[0].strip()
                right = int(parts[1].strip())
                
                num_match = re.search(r'x\s*\+\s*(\d+)', left)
                if num_match:
                    a = int(num_match.group(1))
                    expected_x = right - a
                    expected = f"x = {expected_x}"
                    
                    if expected not in correct_answer:
                        errors.append(f"For {equation}, expected {expected}, got {correct_answer}")
            
            # Parse: x - a = b
            elif '-' in equation:
                parts = equation.split('=')
                left = parts[0].strip()
                right = int(parts[1].strip())
                
                num_match = re.search(r'x\s*-\s*(\d+)', left)
                if num_match:
                    a = int(num_match.group(1))
                    expected_x = right + a
                    expected = f"x = {expected_x}"
                    
                    if expected not in correct_answer:
                        errors.append(f"For {equation}, expected {expected}, got {correct_answer}")
    
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors

def validate_all_algebra_questions():
    """Validate all algebra questions in database"""
    
    print("=" * 80)
    print("COMPREHENSIVE ALGEBRA QUESTION VALIDATION")
    print("=" * 80)
    
    topics_to_check = [
        'introductory_algebra',
        'solving_equations',
        'simplifying_expressions',
        'expanding_factorising'
    ]
    
    total_errors = 0
    total_checked = 0
    
    with app.app_context():
        with db.engine.connect() as conn:
            for topic in topics_to_check:
                print(f"\n{'='*80}")
                print(f"Checking: {topic.upper().replace('_', ' ')}")
                print('='*80)
                
                # Get all questions for this topic
                result = conn.execute(text("""
                    SELECT id, difficulty, question_text, correct_answer, explanation,
                           option_a, option_b, option_c, option_d
                    FROM questions
                    WHERE topic = :topic
                    ORDER BY difficulty, id
                """), {'topic': topic})
                
                questions = result.fetchall()
                print(f"\nTotal questions: {len(questions)}")
                
                topic_errors = []
                
                for q in questions:
                    total_checked += 1
                    q_id, difficulty, q_text, correct_ans, explanation, opt_a, opt_b, opt_c, opt_d = q
                    
                    # Get options as list
                    options = [opt_a, opt_b, opt_c, opt_d]
                    
                    # Validate based on topic
                    if topic == 'introductory_algebra':
                        errors = validate_introductory_algebra(q_text, correct_ans, explanation, difficulty)
                    elif topic == 'solving_equations':
                        errors = validate_solving_equations(q_text, correct_ans, explanation, difficulty)
                    else:
                        # For other topics, basic validation
                        errors = []
                        # Check if correct answer is in options
                        if correct_ans not in options:
                            errors.append(f"Correct answer '{correct_ans}' not in options: {options}")
                    
                    if errors:
                        topic_errors.append({
                            'id': q_id,
                            'difficulty': difficulty,
                            'question': q_text,
                            'correct_answer': correct_ans,
                            'options': options,
                            'errors': errors
                        })
                        total_errors += len(errors)
                
                # Report for this topic
                if topic_errors:
                    print(f"\n⚠️  FOUND {len(topic_errors)} PROBLEMATIC QUESTIONS:")
                    print("-" * 80)
                    
                    for i, err in enumerate(topic_errors[:10], 1):  # Show first 10
                        print(f"\n{i}. Question ID {err['id']} ({err['difficulty']})")
                        print(f"   Q: {err['question'][:70]}...")
                        print(f"   Correct Answer: {err['correct_answer']}")
                        print(f"   Options: {err['options']}")
                        for error in err['errors']:
                            print(f"   ❌ {error}")
                    
                    if len(topic_errors) > 10:
                        print(f"\n   ... and {len(topic_errors) - 10} more errors")
                else:
                    print(f"\n✅ All {len(questions)} questions appear correct!")
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total questions checked: {total_checked}")
    print(f"Questions with errors: {total_errors}")
    
    if total_errors > 0:
        print(f"\n⚠️  WARNING: Found {total_errors} errors!")
        print("\nRecommendation: Delete and regenerate questions:")
        print("  1. Delete current questions:")
        print("     python3 delete_algebra_questions.py")
        print("  2. Regenerate with corrected scripts:")
        print("     python3 add_introductory_algebra_FIXED.py")
        print("     python3 add_other_algebra_topics_FIXED.py")
    else:
        print("\n✅ All questions validated successfully!")
    
    print("=" * 80)

if __name__ == '__main__':
    validate_all_algebra_questions()
