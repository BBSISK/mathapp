#!/usr/bin/env python3
"""
Add 3 new Algebra topics to Math Master:
1. Solving Linear Equations (solving_equations)
2. Simplifying Algebraic Expressions (simplifying_expressions)
3. Expanding and Factorising (expanding_factorising)

Each topic has 120 questions across 3 difficulty levels
"""

import random
from app import app, db
from sqlalchemy import text

def generate_multiple_choice(correct, is_equation=False):
    """Generate 3 wrong answers for multiple choice"""
    try:
        # Handle equation answers like "x = 5"
        if is_equation and '=' in correct:
            var, value = correct.split('=')
            var = var.strip()
            value = float(value.strip())
            
            wrong_values = []
            offsets = [-3, -2, -1, 1, 2, 3, 4, -4]
            random.shuffle(offsets)
            
            for offset in offsets:
                wrong_val = value + offset
                if wrong_val != value:
                    if wrong_val == int(wrong_val):
                        wrong_values.append(f"{var} = {int(wrong_val)}")
                    else:
                        wrong_values.append(f"{var} = {wrong_val:.1f}")
                if len(wrong_values) >= 3:
                    break
            
            all_options = wrong_values[:3] + [correct]
        else:
            # For numeric or expression answers
            correct_clean = correct.replace(' ', '')
            
            # Generate similar-looking wrong answers
            wrong_answers = []
            
            # Common wrong answer patterns for expressions
            if any(op in correct for op in ['+', '-', '*', '/']):
                # It's an expression
                # Generate variations
                wrong_answers = [
                    correct.replace('+', '-') if '+' in correct else correct + ' + 1',
                    correct.replace('-', '+') if '-' in correct else correct + ' - 1',
                    correct.replace('2', '3') if '2' in correct else correct.replace('x', '2x')
                ]
            else:
                # Numeric answer
                try:
                    val = float(correct)
                    for offset in [-2, -1, 1, 2]:
                        wrong = val + offset
                        if wrong != val and wrong > 0:
                            if wrong == int(wrong):
                                wrong_answers.append(str(int(wrong)))
                            else:
                                wrong_answers.append(f"{wrong:.1f}")
                        if len(wrong_answers) >= 3:
                            break
                except:
                    # Fallback for complex expressions
                    wrong_answers = [f"{correct}x", f"2{correct}", f"-{correct}"]
            
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
        # Fallback
        return {
            'option_a': correct,
            'option_b': 'None of these',
            'option_c': 'Cannot solve',
            'option_d': 'Undefined',
            'correct_answer': 1
        }

def generate_solving_equations_questions():
    """Generate 120 solving linear equations questions"""
    questions = []
    
    # FOUNDATION (40 questions) - Simple one-step and two-step equations
    # One-step: x + a = b (20 questions)
    for i in range(20):
        a = random.randint(1, 15)
        b = random.randint(a + 1, 30)
        x = b - a
        
        equation = f"x + {a} = {b}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Subtract {a} from both sides: x = {b} - {a} = {x}'
        })
    
    # One-step: x - a = b (20 questions)
    for i in range(20):
        a = random.randint(1, 15)
        x = random.randint(a + 5, 30)
        b = x - a
        
        equation = f"x - {a} = {b}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Add {a} to both sides: x = {b} + {a} = {x}'
        })
    
    # ORDINARY (40 questions) - Two-step and equations with x on both sides
    # Two-step: ax + b = c (20 questions)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(1, 15)
        x = random.randint(2, 12)
        c = a * x + b
        
        equation = f"{a}x + {b} = {c}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Subtract {b}: {a}x = {c - b}. Divide by {a}: x = {x}'
        })
    
    # x on both sides: ax + b = cx + d (20 questions)
    for i in range(20):
        a = random.randint(3, 8)
        c = random.randint(2, a - 1)
        x = random.randint(2, 10)
        b = random.randint(1, 12)
        d = a * x + b - c * x
        
        equation = f"{a}x + {b} = {c}x + {d}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Collect x terms on one side, then solve'
        })
    
    # HIGHER (40 questions) - Equations with brackets and fractions
    # With brackets: a(x + b) = c (20 questions)
    for i in range(20):
        a = random.randint(2, 6)
        b = random.randint(1, 10)
        x = random.randint(2, 15)
        c = a * (x + b)
        
        equation = f"{a}(x + {b}) = {c}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Expand brackets: {a}x + {a*b} = {c}, then solve'
        })
    
    # Simple fractions: x/a = b (20 questions)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(3, 12)
        x = a * b
        
        equation = f"x/{a} = {b}"
        answer = f"x = {x}"
        
        options = generate_multiple_choice(answer, is_equation=True)
        
        questions.append({
            'topic': 'solving_equations',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Solve: {equation}',
            **options,
            'explanation': f'Multiply both sides by {a}: x = {x}'
        })
    
    return questions

def generate_simplifying_expressions_questions():
    """Generate 120 simplifying algebraic expressions questions"""
    questions = []
    
    # FOUNDATION (40 questions) - Collecting like terms
    # Add like terms: ax + bx (20 questions)
    for i in range(20):
        a = random.randint(2, 12)
        b = random.randint(1, 10)
        total = a + b
        
        expression = f"{a}x + {b}x"
        answer = f"{total}x"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Collect like terms: ({a} + {b})x = {total}x'
        })
    
    # Subtract like terms: ax - bx (20 questions)
    for i in range(20):
        a = random.randint(8, 20)
        b = random.randint(1, a - 1)
        diff = a - b
        
        expression = f"{a}x - {b}x"
        answer = f"{diff}x"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Collect like terms: ({a} - {b})x = {diff}x'
        })
    
    # ORDINARY (40 questions) - Multiple terms and constants
    # ax + b + cx + d (20 questions)
    for i in range(20):
        a = random.randint(2, 10)
        b = random.randint(1, 15)
        c = random.randint(1, 8)
        d = random.randint(1, 12)
        
        total_x = a + c
        total_const = b + d
        
        expression = f"{a}x + {b} + {c}x + {d}"
        answer = f"{total_x}x + {total_const}"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Collect x terms and constants: {total_x}x + {total_const}'
        })
    
    # ax + by + cx - dy (20 questions - two variables)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        c = random.randint(1, 6)
        d = random.randint(1, b)
        
        total_x = a + c
        total_y = b - d
        
        expression = f"{a}x + {b}y + {c}x - {d}y"
        answer = f"{total_x}x + {total_y}y"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Collect like terms: {total_x}x + {total_y}y'
        })
    
    # HIGHER (40 questions) - Complex expressions with powers
    # ax² + bx + cx² + dx (20 questions)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(2, 10)
        c = random.randint(1, 5)
        d = random.randint(1, 8)
        
        total_x2 = a + c
        total_x = b + d
        
        expression = f"{a}x² + {b}x + {c}x² + {d}x"
        answer = f"{total_x2}x² + {total_x}x"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Collect like terms: {total_x2}x² + {total_x}x'
        })
    
    # Multiply: a × bx (20 questions)
    for i in range(20):
        a = random.randint(2, 9)
        b = random.randint(2, 12)
        product = a * b
        
        expression = f"{a} × {b}x"
        answer = f"{product}x"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'simplifying_expressions',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Simplify: {expression}',
            **options,
            'explanation': f'Multiply: {a} × {b} = {product}, so answer is {product}x'
        })
    
    return questions

def generate_expanding_factorising_questions():
    """Generate 120 expanding and factorising questions"""
    questions = []
    
    # FOUNDATION (40 questions) - Basic expanding single brackets
    # a(x + b) (20 questions)
    for i in range(20):
        a = random.randint(2, 9)
        b = random.randint(1, 12)
        
        expression = f"{a}(x + {b})"
        answer = f"{a}x + {a * b}"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Expand: {expression}',
            **options,
            'explanation': f'Multiply {a} by each term: {a}x + {a * b}'
        })
    
    # a(bx + c) (20 questions)
    for i in range(20):
        a = random.randint(2, 6)
        b = random.randint(2, 5)
        c = random.randint(1, 10)
        
        expression = f"{a}({b}x + {c})"
        answer = f"{a * b}x + {a * c}"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'foundation',
            'question_text': f'Expand: {expression}',
            **options,
            'explanation': f'{a} × {b}x = {a*b}x and {a} × {c} = {a*c}'
        })
    
    # ORDINARY (40 questions) - Factorising and expanding with subtraction
    # Factorise: ax + ab (20 questions)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(2, 12)
        
        expression = f"{a}x + {a * b}"
        answer = f"{a}(x + {b})"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Factorise: {expression}',
            **options,
            'explanation': f'Common factor is {a}: {a}(x + {b})'
        })
    
    # Expand: a(x - b) (20 questions)
    for i in range(20):
        a = random.randint(2, 8)
        b = random.randint(1, 12)
        
        expression = f"{a}(x - {b})"
        answer = f"{a}x - {a * b}"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'ordinary',
            'question_text': f'Expand: {expression}',
            **options,
            'explanation': f'Multiply: {a}x - {a * b}'
        })
    
    # HIGHER (40 questions) - Double brackets and complex factorising
    # Expand: (x + a)(x + b) (20 questions)
    for i in range(20):
        a = random.randint(1, 8)
        b = random.randint(1, 9)
        
        # (x + a)(x + b) = x² + (a+b)x + ab
        coef_x = a + b
        const = a * b
        
        expression = f"(x + {a})(x + {b})"
        answer = f"x² + {coef_x}x + {const}"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Expand: {expression}',
            **options,
            'explanation': f'Use FOIL: x² + {coef_x}x + {const}'
        })
    
    # Factorise: ax + ay (20 questions with two terms)
    for i in range(20):
        a = random.randint(2, 9)
        
        # Choose two different variables/terms
        expression = f"{a}x + {a}y"
        answer = f"{a}(x + y)"
        
        options = generate_multiple_choice(answer)
        
        questions.append({
            'topic': 'expanding_factorising',
            'strand': 'Algebra and Functions',
            'difficulty': 'higher',
            'question_text': f'Factorise: {expression}',
            **options,
            'explanation': f'Common factor {a}: answer is {a}(x + y)'
        })
    
    return questions

def add_all_algebra_topics():
    """Add all three algebra topics to the database"""
    
    print("=" * 70)
    print("ADDING 3 NEW ALGEBRA TOPICS TO MATH MASTER")
    print("=" * 70)
    
    topics = [
        ('solving_equations', generate_solving_equations_questions, 'Solving Linear Equations'),
        ('simplifying_expressions', generate_simplifying_expressions_questions, 'Simplifying Expressions'),
        ('expanding_factorising', generate_expanding_factorising_questions, 'Expanding & Factorising')
    ]
    
    with app.app_context():
        for topic_id, generator_func, topic_name in topics:
            print(f"\n{'='*70}")
            print(f"Processing: {topic_name} ({topic_id})")
            print('='*70)
            
            try:
                # Generate questions
                print(f"Generating 120 questions for {topic_name}...")
                questions = generator_func()
                print(f"✓ Generated {len(questions)} questions")
                
                with db.engine.connect() as conn:
                    # Check if topic exists
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM questions WHERE topic = :topic"
                    ), {'topic': topic_id})
                    existing_count = result.fetchone()[0]
                    
                    if existing_count > 0:
                        print(f"⚠ Found {existing_count} existing questions for {topic_id}")
                        print(f"Deleting old questions...")
                        conn.execute(text(
                            "DELETE FROM questions WHERE topic = :topic"
                        ), {'topic': topic_id})
                        conn.commit()
                        print(f"✓ Deleted {existing_count} old questions")
                    
                    # Insert new questions
                    print(f"Adding {len(questions)} questions...")
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
                        WHERE topic = :topic
                        GROUP BY difficulty
                        ORDER BY CASE difficulty 
                            WHEN 'foundation' THEN 1 
                            WHEN 'ordinary' THEN 2 
                            WHEN 'higher' THEN 3 
                        END
                    """), {'topic': topic_id})
                    
                    print(f"\nQuestions by difficulty:")
                    for row in result:
                        print(f"  {row[0]}: {row[1]} questions")
                    
            except Exception as e:
                print(f"✗ Error processing {topic_name}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Final summary
        print(f"\n{'='*70}")
        print("FINAL SUMMARY - Algebra and Functions Strand")
        print('='*70)
        
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT topic, COUNT(*) as count
                    FROM questions 
                    WHERE strand = 'Algebra and Functions'
                    GROUP BY topic
                    ORDER BY topic
                """))
                
                total = 0
                for row in result:
                    print(f"  {row[0]}: {row[1]} questions")
                    total += row[1]
                
                print(f"\n  TOTAL: {total} questions in Algebra and Functions")
        except Exception as e:
            print(f"Error in summary: {e}")
    
    return True

if __name__ == '__main__':
    success = add_all_algebra_topics()
    if success:
        print("\n" + "=" * 70)
        print("✓ ALL 3 ALGEBRA TOPICS ADDED SUCCESSFULLY!")
        print("  Topics: Solving Equations, Simplifying Expressions, Expanding & Factorising")
        print("  Total: 360 new questions (120 per topic)")
        print("\n  NEXT STEP: Reload your web app on PythonAnywhere!")
        print("=" * 70)
    else:
        print("\n✗ Failed to add topics")
