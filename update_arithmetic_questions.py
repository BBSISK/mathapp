"""
Updated Arithmetic Question Generator
Specifications:
- Beginner: Stay as is (simple positive integers)
- Intermediate: Single negatives with low value integers
- Advanced: Double negatives and 3-digit computations
"""

from app import app, db, Question
import random

def generate_updated_arithmetic_questions():
    """Generate updated arithmetic questions with new difficulty specifications"""
    
    with app.app_context():
        # Delete existing arithmetic questions
        print("Removing old arithmetic questions...")
        Question.query.filter_by(topic='arithmetic').delete()
        db.session.commit()
        print("✓ Old questions removed")
        
        print("\nGenerating new arithmetic questions...")
        
        # ==================== BEGINNER (40 questions) ====================
        print("\n1. Generating Beginner questions (stay as is)...")
        beginner_questions = []
        
        # 20 Addition questions (1-20)
        for i in range(20):
            a = random.randint(1, 15)
            b = random.randint(1, 15)
            answer = a + b
            wrong1 = answer + random.randint(1, 3)
            wrong2 = answer - random.randint(1, 3)
            wrong3 = answer + random.randint(4, 6)
            
            # Randomize option positions
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            beginner_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'beginner',
                'question_text': f'What is {a} + {b}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} + {b} = {answer}. Start at {a} and count forward {b} spaces.'
            })
        
        # 20 Subtraction questions
        for i in range(20):
            a = random.randint(10, 20)
            b = random.randint(1, a-1)
            answer = a - b
            wrong1 = answer + random.randint(1, 3)
            wrong2 = answer - random.randint(1, 3) if answer > 3 else answer + 2
            wrong3 = a + b  # Common mistake
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            beginner_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'beginner',
                'question_text': f'What is {a} - {b}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} - {b} = {answer}. Start at {a} and count back {b} spaces.'
            })
        
        # Save beginner questions
        for q in beginner_questions:
            question = Question(**q)
            db.session.add(question)
        db.session.commit()
        print(f"✓ Added {len(beginner_questions)} Beginner questions")
        
        # ==================== INTERMEDIATE (40 questions) ====================
        print("\n2. Generating Intermediate questions (single negatives, low integers)...")
        intermediate_questions = []
        
        # 10 Addition with one negative (low values -10 to 10)
        for i in range(10):
            # Mix of formats: positive + negative, negative + positive
            if random.choice([True, False]):
                a = random.randint(5, 15)  # positive
                b = random.randint(-10, -1)  # negative
            else:
                a = random.randint(-10, -1)  # negative
                b = random.randint(5, 15)  # positive
            
            answer = a + b
            wrong1 = answer + random.randint(2, 5)
            wrong2 = answer - random.randint(2, 5)
            wrong3 = abs(a) + abs(b)  # Common mistake: ignoring negative
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            intermediate_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'intermediate',
                'question_text': f'What is {a} + ({b})?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} + ({b}) = {answer}. Adding a negative is the same as subtracting.'
            })
        
        # 10 Subtraction with one negative (low values)
        for i in range(10):
            a = random.randint(5, 15)
            b = random.randint(-10, -1)  # negative
            answer = a - b
            wrong1 = a + b  # Common mistake
            wrong2 = answer - random.randint(3, 7)
            wrong3 = answer + random.randint(3, 7)
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            intermediate_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'intermediate',
                'question_text': f'What is {a} - ({b})?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} - ({b}) = {answer}. Subtracting a negative is the same as adding: {a} - ({b}) = {a} + {abs(b)}.'
            })
        
        # 10 Simple multiplication (no negatives)
        for i in range(10):
            a = random.randint(3, 12)
            b = random.randint(2, 9)
            answer = a * b
            wrong1 = a + b  # Common mistake
            wrong2 = answer + random.randint(5, 15)
            wrong3 = answer - random.randint(5, 15)
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            intermediate_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'intermediate',
                'question_text': f'What is {a} × {b}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} × {b} = {answer}. This is {a} groups of {b}.'
            })
        
        # 10 Mixed operations with single negative
        for i in range(10):
            # Create expressions like: 8 + 5 - 3, 10 - (-2) + 4, etc.
            a = random.randint(5, 15)
            b = random.randint(-8, 8)
            if b == 0:
                b = 5
            c = random.randint(1, 8)
            
            # Random operation combinations
            if random.choice([True, False]):
                answer = a + b + c
                question_text = f'{a} + {b} + {c}' if b >= 0 else f'{a} + ({b}) + {c}'
                explanation = f'{a} + {b} + {c} = {answer}'
            else:
                answer = a + b - c
                question_text = f'{a} + {b} - {c}' if b >= 0 else f'{a} + ({b}) - {c}'
                explanation = f'{a} + {b} - {c} = {answer}'
            
            wrong1 = answer + random.randint(2, 6)
            wrong2 = answer - random.randint(2, 6)
            wrong3 = abs(a) + abs(b) + abs(c)  # Common mistake
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            intermediate_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'intermediate',
                'question_text': f'What is {question_text}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': explanation
            })
        
        # Save intermediate questions
        for q in intermediate_questions:
            question = Question(**q)
            db.session.add(question)
        db.session.commit()
        print(f"✓ Added {len(intermediate_questions)} Intermediate questions")
        
        # ==================== ADVANCED (40 questions) ====================
        print("\n3. Generating Advanced questions (double negatives, 3-digit)...")
        advanced_questions = []
        
        # 10 Double negative operations
        for i in range(10):
            a = random.randint(-15, -5)  # negative
            b = random.randint(-12, -3)  # negative
            
            if i < 5:  # Addition with two negatives
                answer = a + b
                wrong1 = abs(a) + abs(b)  # Common mistake: treating as positive
                wrong2 = a - b
                wrong3 = answer + random.randint(5, 10)
                
                question_text = f'({a}) + ({b})'
                explanation = f'({a}) + ({b}) = {answer}. Adding two negatives gives a more negative result.'
            else:  # Subtraction with two negatives
                answer = a - b
                wrong1 = a + b
                wrong2 = abs(a) - abs(b)
                wrong3 = answer - random.randint(5, 10)
                
                question_text = f'({a}) - ({b})'
                explanation = f'({a}) - ({b}) = {answer}. Subtracting a negative is the same as adding: ({a}) - ({b}) = ({a}) + {abs(b)}.'
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            advanced_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'advanced',
                'question_text': f'What is {question_text}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': explanation
            })
        
        # 15 Three-digit addition
        for i in range(15):
            a = random.randint(100, 500)
            b = random.randint(100, 400)
            answer = a + b
            wrong1 = answer + random.randint(10, 100)
            wrong2 = answer - random.randint(10, 100)
            wrong3 = (a // 10) + (b // 10)  # Common mistake: dropping digits
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            advanced_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'advanced',
                'question_text': f'What is {a} + {b}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} + {b} = {answer}'
            })
        
        # 15 Three-digit subtraction
        for i in range(15):
            a = random.randint(300, 900)
            b = random.randint(100, a - 50)
            answer = a - b
            wrong1 = answer + random.randint(10, 100)
            wrong2 = a + b  # Common mistake
            wrong3 = answer - random.randint(10, 100)
            
            options = [answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_index = options.index(answer)
            
            advanced_questions.append({
                'topic': 'arithmetic',
                'difficulty': 'advanced',
                'question_text': f'What is {a} - {b}?',
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': correct_index,
                'explanation': f'{a} - {b} = {answer}'
            })
        
        # Save advanced questions
        for q in advanced_questions:
            question = Question(**q)
            db.session.add(question)
        db.session.commit()
        print(f"✓ Added {len(advanced_questions)} Advanced questions")
        
        # Verification
        print("\n" + "="*60)
        print("VERIFICATION - Arithmetic Questions:")
        print("="*60)
        beginner_count = Question.query.filter_by(topic='arithmetic', difficulty='beginner').count()
        intermediate_count = Question.query.filter_by(topic='arithmetic', difficulty='intermediate').count()
        advanced_count = Question.query.filter_by(topic='arithmetic', difficulty='advanced').count()
        
        print(f"Beginner:     {beginner_count} questions")
        print(f"Intermediate: {intermediate_count} questions")
        print(f"Advanced:     {advanced_count} questions")
        print(f"Total:        {beginner_count + intermediate_count + advanced_count} questions")
        print("\n✓ Arithmetic questions updated successfully!")

if __name__ == '__main__':
    print("="*60)
    print("UPDATING ARITHMETIC QUESTIONS")
    print("="*60)
    print("\nNew Specifications:")
    print("- Beginner: Simple positive integers (stay as is)")
    print("- Intermediate: Single negatives with low value integers")
    print("- Advanced: Double negatives and 3-digit computations")
    print("\nStarting update...\n")
    
    generate_updated_arithmetic_questions()
    
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print("\nRestart your app to see the new questions.")
