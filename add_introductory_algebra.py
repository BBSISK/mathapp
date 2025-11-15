#!/usr/bin/env python3
"""
Generate and add 120 Introductory Algebra questions to the database
Perfect for students with NO prior algebra knowledge

Beginner (40): Collecting like terms - simple addition/subtraction
Intermediate (40): Basic substitution with single variables
Advanced (40): More complex substitution and mixed operations
"""

import random
from app import app, db
from sqlalchemy import text

def generate_multiple_choice(correct, similar_errors=None):
    """Generate 3 wrong answers for multiple choice"""
    try:
        # Try to parse as number
        correct_val = correct.replace(' ', '')
        
        # Generate wrong answers
        wrong_answers = []
        
        if similar_errors:
            # Use provided similar errors (common student mistakes)
            wrong_answers = similar_errors[:3]
        else:
            # Generate numeric wrong answers
            try:
                if 'x' in correct or 'y' in correct or 'a' in correct or 'b' in correct:
                    # It's an algebraic expression
                    # Create variations
                    wrong_answers = [
                        correct.replace('+', '-') if '+' in correct else correct + ' + 1',
                        correct.replace('x', '2x') if 'x' in correct else correct.replace('y', '2y'),
                        correct.replace(' ', '') + 'x' if 'x' not in correct else correct.replace('x', '')
                    ]
                else:
                    # Numeric answer
                    val = float(correct)
                    offsets = [-3, -2, -1, 1, 2, 3, 4, -4, 5, -5]
                    random.shuffle(offsets)
                    for offset in offsets:
                        wrong = val + offset
                        if wrong != val:
                            if wrong == int(wrong):
                                wrong_answers.append(str(int(wrong)))
                            else:
                                wrong_answers.append(str(wrong))
                        if len(wrong_answers) >= 3:
                            break
            except:
                # Fallback for complex expressions
                wrong_answers = [f"{correct} + 1", f"2{correct}", f"-{correct}"]
        
        # Ensure we have exactly 3 wrong answers
        while len(wrong_answers) < 3:
            wrong_answers.append("Cannot be solved")
        
        all_options = wrong_answers[:3] + [correct]
        random.shuffle(all_options)
        correct_position = all_options.index(correct) + 1
        
        return {
            'option_a': all_options[0],
            'option_b': all_options[1],
            'option_c': all_options[2],
            'option_d': all_options[3],
            'correct_answer': correct_position
        }
    except Exception as e:
        # Ultimate fallback
        return {
            'option_a': correct,
            'option_b': '0',
            'option_c': '1',
            'option_d': 'None',
            'correct_answer': 1
        }

def generate_introductory_algebra_questions():
    """Generate 120 introductory algebra questions"""
    questions = []
    
    # ==================== BEGINNER LEVEL (40 questions) ====================
    # Focus: Collecting like terms - very simple, gentle introduction
    
    # Type 1: Add two like terms (10 questions)
    for i in range(10):
        a = random.randint(2, 8)
        b = random.randint(1, 7)
        total = a + b
        
        var = random.choice(['x', 'y', 'a', 'b'])
        expression = f"{a}{var} + {b}{var}"
        answer = f"{total}{var}"
        
        # Common errors
        wrong_answers = [
            f"{a + b}",  # Forgot the variable
            f"{a}{var}",  # Only kept first term
            f"{b}{var}"   # Only kept second term
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'beginner',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Add the numbers: {a} + {b} = {total}, keep the variable {var}. Answer: {answer}'
        })
    
    # Type 2: Subtract like terms (10 questions)
    for i in range(10):
        a = random.randint(8, 15)
        b = random.randint(1, a - 2)
        diff = a - b
        
        var = random.choice(['x', 'y', 'a', 'b'])
        expression = f"{a}{var} - {b}{var}"
        answer = f"{diff}{var}"
        
        wrong_answers = [
            f"{a - b}",
            f"{a + b}{var}",
            f"{b}{var}"
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'beginner',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Subtract the numbers: {a} - {b} = {diff}, keep the variable {var}. Answer: {answer}'
        })
    
    # Type 3: Add three like terms (10 questions)
    for i in range(10):
        a = random.randint(2, 5)
        b = random.randint(1, 4)
        c = random.randint(1, 5)
        total = a + b + c
        
        var = random.choice(['x', 'y', 'a'])
        expression = f"{a}{var} + {b}{var} + {c}{var}"
        answer = f"{total}{var}"
        
        wrong_answers = [
            f"{a + b}{var}",
            f"{total}",
            f"{a}{var}"
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'beginner',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Add all numbers: {a} + {b} + {c} = {total}, keep {var}. Answer: {answer}'
        })
    
    # Type 4: Mix of addition and subtraction (10 questions)
    for i in range(10):
        a = random.randint(5, 10)
        b = random.randint(2, 6)
        c = random.randint(1, 4)
        result = a + b - c
        
        var = random.choice(['x', 'y', 'n', 'm'])
        expression = f"{a}{var} + {b}{var} - {c}{var}"
        answer = f"{result}{var}"
        
        wrong_answers = [
            f"{a + b + c}{var}",
            f"{result}",
            f"{a - b + c}{var}"
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'beginner',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Calculate: {a} + {b} - {c} = {result}, keep {var}. Answer: {answer}'
        })
    
    # ==================== INTERMEDIATE LEVEL (40 questions) ====================
    # Focus: Basic substitution with single variables
    
    # Type 1: Substitute into x + number (10 questions)
    for i in range(10):
        x = random.randint(3, 12)
        b = random.randint(2, 15)
        result = x + b
        
        expression = f"x + {b}"
        question = f"If x = {x}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(x - b) if x > b else str(b - x),
            str(x * b),
            str(x)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'intermediate',
            'question_text': question,
            **options,
            'explanation': f'Replace x with {x}: {x} + {b} = {result}'
        })
    
    # Type 2: Substitute into number × x (10 questions)
    for i in range(10):
        x = random.randint(2, 9)
        a = random.randint(2, 8)
        result = a * x
        
        expression = f"{a}x"
        question = f"If x = {x}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(a + x),
            str(a),
            str(x)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'intermediate',
            'question_text': question,
            **options,
            'explanation': f'Replace x with {x}: {a} × {x} = {result}'
        })
    
    # Type 3: Substitute into ax + b (10 questions)
    for i in range(10):
        x = random.randint(2, 8)
        a = random.randint(2, 6)
        b = random.randint(3, 12)
        result = a * x + b
        
        expression = f"{a}x + {b}"
        question = f"If x = {x}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(a * x),
            str(a + x + b),
            str(x + b)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'intermediate',
            'question_text': question,
            **options,
            'explanation': f'Replace x with {x}: {a} × {x} + {b} = {a * x} + {b} = {result}'
        })
    
    # Type 4: Substitute into x - number (10 questions)
    for i in range(10):
        x = random.randint(10, 20)
        b = random.randint(2, 9)
        result = x - b
        
        expression = f"x - {b}"
        question = f"If x = {x}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(x + b),
            str(b - x) if b > 5 else str(x),
            str(x)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'intermediate',
            'question_text': question,
            **options,
            'explanation': f'Replace x with {x}: {x} - {b} = {result}'
        })
    
    # ==================== ADVANCED LEVEL (40 questions) ====================
    # Focus: More complex substitution and expressions
    
    # Type 1: Two variables - simple (10 questions)
    for i in range(10):
        x = random.randint(3, 8)
        y = random.randint(2, 7)
        result = x + y
        
        expression = "x + y"
        question = f"If x = {x} and y = {y}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(x * y),
            str(x - y) if x > y else str(y - x),
            str(x)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'advanced',
            'question_text': question,
            **options,
            'explanation': f'Replace x with {x} and y with {y}: {x} + {y} = {result}'
        })
    
    # Type 2: ax + by (10 questions)
    for i in range(10):
        x = random.randint(2, 6)
        y = random.randint(2, 5)
        a = random.randint(2, 5)
        b = random.randint(2, 4)
        result = a * x + b * y
        
        expression = f"{a}x + {b}y"
        question = f"If x = {x} and y = {y}, find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(a * x),
            str(a + x + b + y),
            str(b * y)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'advanced',
            'question_text': question,
            **options,
            'explanation': f'Replace: {a} × {x} + {b} × {y} = {a*x} + {b*y} = {result}'
        })
    
    # Type 3: ax + bx (collecting and substituting) (10 questions)
    for i in range(10):
        x = random.randint(3, 8)
        a = random.randint(2, 5)
        b = random.randint(2, 6)
        total_coef = a + b
        result = total_coef * x
        
        expression = f"{a}x + {b}x"
        question = f"If x = {x}, simplify and find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(a * x),
            str(total_coef),
            str(a + b + x)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'advanced',
            'question_text': question,
            **options,
            'explanation': f'First simplify: {a}x + {b}x = {total_coef}x. Then: {total_coef} × {x} = {result}'
        })
    
    # Type 4: More complex - ax - bx + c (10 questions)
    for i in range(10):
        x = random.randint(4, 9)
        a = random.randint(5, 10)
        b = random.randint(2, 5)
        c = random.randint(3, 12)
        result = (a - b) * x + c
        
        expression = f"{a}x - {b}x + {c}"
        question = f"If x = {x}, simplify and find the value of: {expression}"
        answer = str(result)
        
        wrong_answers = [
            str(a * x - b * x),
            str((a - b) * x),
            str(a * x + c)
        ]
        
        options = generate_multiple_choice(answer, wrong_answers)
        
        questions.append({
            'topic': 'introductory_algebra',
            'strand': 'Algebra and Functions',
            'difficulty': 'advanced',
            'question_text': question,
            **options,
            'explanation': f'Simplify: {a}x - {b}x = {a-b}x. Then: {a-b} × {x} + {c} = {(a-b)*x} + {c} = {result}'
        })
    
    return questions

def add_introductory_algebra_to_db():
    """Add all questions to the database"""
    
    print("=" * 70)
    print("ADDING INTRODUCTORY ALGEBRA TOPIC")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Generate questions
            print("\nGenerating 120 Introductory Algebra questions...")
            questions = generate_introductory_algebra_questions()
            print(f"✓ Generated {len(questions)} questions")
            
            with db.engine.connect() as conn:
                # Check if topic exists
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM questions WHERE topic = 'introductory_algebra'"
                ))
                existing_count = result.fetchone()[0]
                
                if existing_count > 0:
                    print(f"\n⚠ Found {existing_count} existing introductory_algebra questions")
                    print("Deleting old questions...")
                    conn.execute(text(
                        "DELETE FROM questions WHERE topic = 'introductory_algebra'"
                    ))
                    conn.commit()
                    print(f"✓ Deleted {existing_count} old questions")
                
                # Insert new questions
                print(f"\nAdding {len(questions)} questions to database...")
                for q in questions:
                    conn.execute(text("""
                        INSERT INTO questions 
                        (topic, strand, difficulty, question_text, option_a, option_b, 
                         option_c, option_d, correct_answer, explanation)
                        VALUES 
                        (:topic, :strand, :difficulty, :question_text, :option_a, 
                         :option_b, :option_c, :option_d, :correct_answer, :explanation)
                    """), q)
                
                conn.commit()
                print(f"✓ Added {len(questions)} questions")
                
                # Verify
                result = conn.execute(text("""
                    SELECT difficulty, COUNT(*) as count
                    FROM questions 
                    WHERE topic = 'introductory_algebra'
                    GROUP BY difficulty
                    ORDER BY CASE difficulty 
                        WHEN 'beginner' THEN 1 
                        WHEN 'intermediate' THEN 2 
                        WHEN 'advanced' THEN 3 
                    END
                """))
                
                print("\nQuestions by difficulty:")
                for row in result:
                    print(f"  {row[0]}: {row[1]} questions")
                
                # Show total in Algebra and Functions strand
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM questions 
                    WHERE strand = 'Algebra and Functions'
                """))
                total = result.fetchone()[0]
                print(f"\nTotal Algebra and Functions questions: {total}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = add_introductory_algebra_to_db()
    if success:
        print("\n" + "=" * 70)
        print("✓ INTRODUCTORY ALGEBRA TOPIC ADDED SUCCESSFULLY!")
        print("  120 questions added (40 per difficulty level)")
        print("\n  Content:")
        print("  - Beginner: Collecting like terms (2x + 3x)")
        print("  - Intermediate: Basic substitution (if x=5, find 3x+2)")
        print("  - Advanced: Complex substitution & mixed operations")
        print("\n  NEXT STEP: Upload updated app.py and reload web app!")
        print("=" * 70)
    else:
        print("\n✗ Failed to add topic")
