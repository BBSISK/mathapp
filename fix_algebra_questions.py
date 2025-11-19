"""
Script to fix algebra questions:
1. Fix duplicate options (option_a, option_b, option_c, option_d)
Run this in PythonAnywhere bash console: python3 fix_algebra_questions.py
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, Question
import random

def generate_unique_option(correct_option, existing_options, question_text=''):
    """Generate a unique wrong answer that doesn't duplicate existing ones"""
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        try:
            # Try to parse as number
            correct_val = float(correct_option.strip())
            
            # Generate different types of wrong answers
            strategies = [
                lambda x: x + random.randint(1, 5),      # Add small number
                lambda x: x - random.randint(1, 5),      # Subtract small number
                lambda x: x * 2,                          # Double it
                lambda x: x / 2 if x != 0 else 1,        # Half it
                lambda x: -x,                             # Negate it
                lambda x: x + 10,                         # Add 10
                lambda x: x - 10,                         # Subtract 10
                lambda x: abs(x) + random.randint(1, 3), # Absolute value + small
                lambda x: x * random.choice([3, 4, 5]),  # Multiply by 3-5
            ]
            
            strategy = random.choice(strategies)
            wrong_val = strategy(correct_val)
            
            # Format the same way as correct answer
            if '.' in str(correct_option):
                new_option = str(round(wrong_val, 2))
            else:
                new_option = str(int(wrong_val))
            
            # Check if unique
            if new_option not in existing_options and new_option != correct_option:
                return new_option
                
        except (ValueError, TypeError):
            # If not numeric, try algebraic variations
            if 'x' in correct_option.lower():
                # It's an algebraic expression
                variations = [
                    correct_option + " + 1",
                    correct_option + " - 1", 
                    "2(" + correct_option + ")",
                    "-" + correct_option,
                ]
                for var in variations:
                    if var not in existing_options:
                        return var
            
            # Fallback for text answers
            new_option = str(random.randint(-20, 20))
            if new_option not in existing_options:
                return new_option
        
        attempts += 1
    
    # Final fallback
    return f"Option_{random.randint(1000, 9999)}"

with app.app_context():
    print("=" * 60)
    print("FIXING ALGEBRA QUESTIONS")
    print("=" * 60)
    
    # Find all algebra questions
    algebra_questions = Question.query.filter(Question.topic.ilike('%algebra%')).all()
    
    if not algebra_questions:
        print("\n⚠️  No algebra questions found. Looking for 'Introductory Algebra'...")
        algebra_questions = Question.query.filter(Question.topic.ilike('%introductory%')).all()
    
    if not algebra_questions:
        print("\n❌ No algebra questions found in database!")
        print("\nAvailable topics:")
        topics = db.session.query(Question.topic).distinct().all()
        for topic_tuple in topics:
            print(f"  - {topic_tuple[0]}")
    else:
        # Group by topic
        topics_dict = {}
        for q in algebra_questions:
            if q.topic not in topics_dict:
                topics_dict[q.topic] = []
            topics_dict[q.topic].append(q)
        
        total_fixed = 0
        
        for topic, questions in topics_dict.items():
            print(f"\n{'=' * 60}")
            print(f"Topic: {topic}")
            print(f"Questions: {len(questions)}")
            print(f"{'=' * 60}")
            
            fixed_count = 0
            for q in questions:
                options = [q.option_a, q.option_b, q.option_c, q.option_d]
                
                # Check for duplicates
                if len(options) != len(set(options)):
                    print(f"\n  Fixing Q{q.id}: {q.question_text[:50]}...")
                    print(f"    Old options: {options}")
                    
                    # Get the correct answer
                    correct_option = options[q.correct_answer - 1]
                    
                    # Create list to track new unique options
                    new_options = options.copy()
                    
                    # Fix each duplicate
                    for i in range(4):
                        # Count how many times this option appears
                        if new_options.count(new_options[i]) > 1:
                            # Don't change the correct answer
                            if i != (q.correct_answer - 1):
                                # Generate a new unique option
                                other_options = [new_options[j] for j in range(4) if j != i]
                                new_opt = generate_unique_option(correct_option, other_options, q.question_text)
                                new_options[i] = new_opt
                    
                    # Update the question
                    q.option_a = new_options[0]
                    q.option_b = new_options[1]
                    q.option_c = new_options[2]
                    q.option_d = new_options[3]
                    
                    print(f"    New options: {new_options}")
                    print(f"    Correct answer: Option {chr(64 + q.correct_answer)} = {new_options[q.correct_answer - 1]}")
                    fixed_count += 1
            
            if fixed_count > 0:
                db.session.commit()
                print(f"\n✓ Fixed {fixed_count} questions in '{topic}'")
                total_fixed += fixed_count
            else:
                print(f"\n✓ No duplicates found in '{topic}'")
        
        print(f"\n{'=' * 60}")
        print(f"SUMMARY: Fixed {total_fixed} questions total")
        print(f"{'=' * 60}")
