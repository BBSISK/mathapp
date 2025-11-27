"""
Script to expand AgentMath.app questions from 20 to 40 per topic/difficulty level
Run this to add 20 more questions to each existing topic/difficulty combination
"""

from app import app, db, Question
import random

def generate_arithmetic_questions(difficulty, start_id):
    """Generate arithmetic questions based on difficulty"""
    questions = []
    
    if difficulty == 'beginner':
        # Simple addition and subtraction (1-20)
        for i in range(20):
            q_id = start_id + i
            if i < 10:  # Addition
                a = random.randint(1, 15)
                b = random.randint(1, 15)
                answer = a + b
                wrong1 = answer + random.randint(1, 3)
                wrong2 = answer - random.randint(1, 3)
                wrong3 = answer + random.randint(4, 6)
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'beginner',
                    'question_text': f'What is {a} + {b}?',
                    'option_a': str(answer),
                    'option_b': str(wrong1),
                    'option_c': str(wrong2),
                    'option_d': str(wrong3),
                    'correct_answer': 0,
                    'explanation': f'{a} + {b} = {answer}. Start at {a} and count forward {b} spaces.'
                })
            else:  # Subtraction
                a = random.randint(10, 20)
                b = random.randint(1, a-1)
                answer = a - b
                wrong1 = answer + random.randint(1, 3)
                wrong2 = answer - random.randint(1, 3) if answer > 3 else answer + 2
                wrong3 = a + b  # Common mistake
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'beginner',
                    'question_text': f'What is {a} - {b}?',
                    'option_a': str(wrong1),
                    'option_b': str(answer),
                    'option_c': str(wrong2),
                    'option_d': str(wrong3),
                    'correct_answer': 1,
                    'explanation': f'{a} - {b} = {answer}. Start at {a} and count back {b} spaces.'
                })
    
    elif difficulty == 'intermediate':
        # Larger numbers and mixed operations
        for i in range(20):
            q_id = start_id + i
            if i < 7:  # Addition with larger numbers
                a = random.randint(20, 100)
                b = random.randint(10, 50)
                answer = a + b
                wrong1 = answer + random.randint(5, 15)
                wrong2 = answer - random.randint(5, 15)
                wrong3 = abs(a - b)
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'intermediate',
                    'question_text': f'What is {a} + {b}?',
                    'option_a': str(wrong1),
                    'option_b': str(wrong2),
                    'option_c': str(answer),
                    'option_d': str(wrong3),
                    'correct_answer': 2,
                    'explanation': f'{a} + {b} = {answer}.'
                })
            elif i < 14:  # Subtraction with larger numbers
                a = random.randint(50, 150)
                b = random.randint(10, a-10)
                answer = a - b
                wrong1 = answer + random.randint(5, 15)
                wrong2 = a + b
                wrong3 = answer - random.randint(5, 15)
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'intermediate',
                    'question_text': f'What is {a} - {b}?',
                    'option_a': str(answer),
                    'option_b': str(wrong1),
                    'option_c': str(wrong2),
                    'option_d': str(wrong3),
                    'correct_answer': 0,
                    'explanation': f'{a} - {b} = {answer}.'
                })
            else:  # Simple multiplication
                a = random.randint(2, 12)
                b = random.randint(2, 12)
                answer = a * b
                wrong1 = a + b
                wrong2 = answer + a
                wrong3 = answer - b
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'intermediate',
                    'question_text': f'What is {a} × {b}?',
                    'option_a': str(wrong1),
                    'option_b': str(answer),
                    'option_c': str(wrong2),
                    'option_d': str(wrong3),
                    'correct_answer': 1,
                    'explanation': f'{a} × {b} = {answer}. This is {a} groups of {b}.'
                })
    
    elif difficulty == 'advanced':
        # Complex operations
        for i in range(20):
            q_id = start_id + i
            if i < 10:  # Multi-digit multiplication
                a = random.randint(10, 50)
                b = random.randint(10, 25)
                answer = a * b
                wrong1 = a + b
                wrong2 = answer + random.randint(50, 100)
                wrong3 = answer - random.randint(50, 100)
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'advanced',
                    'question_text': f'What is {a} × {b}?',
                    'option_a': str(wrong2),
                    'option_b': str(wrong1),
                    'option_c': str(answer),
                    'option_d': str(wrong3),
                    'correct_answer': 2,
                    'explanation': f'{a} × {b} = {answer}.'
                })
            else:  # Division
                b = random.randint(5, 15)
                answer = random.randint(10, 50)
                a = b * answer
                wrong1 = answer + random.randint(1, 5)
                wrong2 = answer - random.randint(1, 5)
                wrong3 = a - b
                
                questions.append({
                    'topic': 'arithmetic',
                    'difficulty': 'advanced',
                    'question_text': f'What is {a} ÷ {b}?',
                    'option_a': str(wrong1),
                    'option_b': str(answer),
                    'option_c': str(wrong2),
                    'option_d': str(wrong3),
                    'correct_answer': 1,
                    'explanation': f'{a} ÷ {b} = {answer}.'
                })
    
    return questions

def generate_fractions_questions(difficulty, start_id):
    """Generate fractions questions"""
    questions = []
    
    if difficulty == 'beginner':
        for i in range(20):
            # Simple fraction recognition and equivalence
            num = random.randint(1, 4)
            denom = random.randint(num+1, 8)
            
            questions.append({
                'topic': 'fractions',
                'difficulty': 'beginner',
                'question_text': f'Which fraction represents {num} out of {denom} parts?',
                'option_a': f'{num}/{denom}',
                'option_b': f'{denom}/{num}',
                'option_c': f'{num+1}/{denom}',
                'option_d': f'{num}/{denom+1}',
                'correct_answer': 0,
                'explanation': f'{num} out of {denom} parts is written as {num}/{denom}.'
            })
    
    elif difficulty == 'intermediate':
        for i in range(20):
            # Fraction addition/subtraction with same denominator
            denom = random.choice([4, 5, 6, 8, 10])
            a = random.randint(1, denom-1)
            b = random.randint(1, denom-a)
            
            if i < 10:  # Addition
                answer_num = a + b
                wrong1 = a + b + 1
                wrong2 = abs(a - b)
                wrong3 = a * b
                
                questions.append({
                    'topic': 'fractions',
                    'difficulty': 'intermediate',
                    'question_text': f'What is {a}/{denom} + {b}/{denom}?',
                    'option_a': f'{answer_num}/{denom}',
                    'option_b': f'{wrong1}/{denom}',
                    'option_c': f'{wrong2}/{denom}',
                    'option_d': f'{wrong3}/{denom*2}',
                    'correct_answer': 0,
                    'explanation': f'When denominators are the same, add numerators: {a} + {b} = {answer_num}, so {a}/{denom} + {b}/{denom} = {answer_num}/{denom}.'
                })
            else:  # Subtraction
                a = random.randint(3, denom-1)
                b = random.randint(1, a-1)
                answer_num = a - b
                wrong1 = a + b
                wrong2 = answer_num + 1
                wrong3 = b - a
                
                questions.append({
                    'topic': 'fractions',
                    'difficulty': 'intermediate',
                    'question_text': f'What is {a}/{denom} - {b}/{denom}?',
                    'option_a': f'{wrong1}/{denom}',
                    'option_b': f'{answer_num}/{denom}',
                    'option_c': f'{wrong2}/{denom}',
                    'option_d': f'{abs(wrong3)}/{denom}',
                    'correct_answer': 1,
                    'explanation': f'When denominators are the same, subtract numerators: {a} - {b} = {answer_num}, so {a}/{denom} - {b}/{denom} = {answer_num}/{denom}.'
                })
    
    elif difficulty == 'advanced':
        for i in range(20):
            # Fraction multiplication and division
            if i < 10:  # Multiplication
                a_num = random.randint(1, 5)
                a_den = random.randint(a_num+1, 8)
                b_num = random.randint(1, 5)
                b_den = random.randint(b_num+1, 8)
                
                ans_num = a_num * b_num
                ans_den = a_den * b_den
                
                questions.append({
                    'topic': 'fractions',
                    'difficulty': 'advanced',
                    'question_text': f'What is {a_num}/{a_den} × {b_num}/{b_den}?',
                    'option_a': f'{ans_num}/{ans_den}',
                    'option_b': f'{a_num + b_num}/{a_den + b_den}',
                    'option_c': f'{ans_num}/{a_den}',
                    'option_d': f'{a_num}/{ans_den}',
                    'correct_answer': 0,
                    'explanation': f'Multiply numerators and denominators: ({a_num} × {b_num})/({a_den} × {b_den}) = {ans_num}/{ans_den}.'
                })
            else:  # Equivalent fractions
                num = random.randint(1, 4)
                denom = random.randint(num+1, 6)
                mult = random.randint(2, 4)
                
                questions.append({
                    'topic': 'fractions',
                    'difficulty': 'advanced',
                    'question_text': f'Which fraction is equivalent to {num}/{denom}?',
                    'option_a': f'{num*mult}/{denom*mult}',
                    'option_b': f'{num+mult}/{denom+mult}',
                    'option_c': f'{num*mult}/{denom}',
                    'option_d': f'{num}/{denom*mult}',
                    'correct_answer': 0,
                    'explanation': f'{num}/{denom} = {num*mult}/{denom*mult} (multiply both numerator and denominator by {mult}).'
                })
    
    return questions

def add_additional_questions():
    """Add 20 more questions to each topic/difficulty combination"""
    
    with app.app_context():
        # Get current max ID
        max_id = db.session.query(db.func.max(Question.id)).scalar() or 0
        next_id = max_id + 1
        
        topics_difficulties = [
            ('arithmetic', 'beginner'),
            ('arithmetic', 'intermediate'),
            ('arithmetic', 'advanced'),
            ('fractions', 'beginner'),
            ('fractions', 'intermediate'),
            ('fractions', 'advanced'),
        ]
        
        for topic, difficulty in topics_difficulties:
            print(f"\nGenerating additional questions for {topic} - {difficulty}...")
            
            if topic == 'arithmetic':
                new_questions = generate_arithmetic_questions(difficulty, next_id)
            elif topic == 'fractions':
                new_questions = generate_fractions_questions(difficulty, next_id)
            
            # Add questions to database
            for q_data in new_questions:
                question = Question(
                    topic=q_data['topic'],
                    difficulty=q_data['difficulty'],
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation']
                )
                db.session.add(question)
                next_id += 1
            
            db.session.commit()
            print(f"✓ Added 20 questions for {topic} - {difficulty}")
        
        # Verify totals
        print("\n" + "="*50)
        print("VERIFICATION - Questions per topic/difficulty:")
        print("="*50)
        for topic, difficulty in topics_difficulties:
            count = Question.query.filter_by(topic=topic, difficulty=difficulty).count()
            print(f"{topic:15} {difficulty:15} {count:3} questions")
        
        print("\n✓ Question expansion complete!")
        print(f"Total questions in database: {Question.query.count()}")

if __name__ == '__main__':
    print("="*50)
    print("EXPANDING MATH MASTER QUESTIONS")
    print("="*50)
    print("\nThis will add 20 more questions to each topic/difficulty")
    print("Current: 20 questions per combination")
    print("After: 40 questions per combination")
    print("\nStarting...\n")
    
    add_additional_questions()
