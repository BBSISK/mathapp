"""
DATABASE POPULATION SCRIPT FOR MULTIPLICATION & DIVISION QUESTIONS

Run this script ONCE to populate your database with multiplication_division questions.

IMPORTANT: This script should be run in your PythonAnywhere Bash console:
    cd ~/your-project-directory
    python populate_mult_div_questions.py

This will add 120 questions (40 per difficulty level) to your Question table.
"""

from app import app, db, Question
import random

def generate_mult_div_questions():
    """Generate all multiplication & division questions for the database"""
    
    questions = []
    
    # ========== BEGINNER LEVEL (40 questions) ==========
    print("Generating Beginner questions...")
    beginner_count = 0
    while beginner_count < 40:
        operation = random.choice(['multiply', 'divide'])
        
        if operation == 'multiply':
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            answer = a * b
            question_text = f"{a} × {b} = ?"
            
        else:  # divide
            divisor = random.randint(1, 10)
            quotient = random.randint(1, 10)
            dividend = divisor * quotient
            answer = quotient
            question_text = f"{dividend} ÷ {divisor} = ?"
        
        # Generate 4 options including the correct answer
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-3, -2, -1, 1, 2, 3, 5, -5])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}."
        })
        beginner_count += 1
    
    print(f"✓ Generated {beginner_count} Beginner questions")
    
    # ========== INTERMEDIATE LEVEL (40 questions) ==========
    print("Generating Intermediate questions...")
    intermediate_count = 0
    while intermediate_count < 40:
        operation = random.choice(['multiply', 'divide'])
        include_negative = random.choice([True, False])
        
        if operation == 'multiply':
            if include_negative:
                a = random.choice(list(range(-10, 0)) + list(range(1, 11)))
                b = random.choice(list(range(-10, 0)) + list(range(1, 11)))
                # Ensure only ONE is negative
                if (a < 0 and b < 0):
                    b = abs(b)
                elif (a > 0 and b > 0):
                    if random.choice([True, False]):
                        a = -a
                    else:
                        b = -b
            else:
                a = random.randint(10, 25)
                b = random.randint(2, 12)
            
            answer = a * b
            question_text = f"{a} × {b} = ?"
            
        else:  # divide
            if include_negative:
                divisor = random.choice(list(range(-10, 0)) + list(range(2, 11)))
                quotient = random.choice(list(range(-10, 0)) + list(range(1, 11)))
                # Ensure only ONE is negative
                if (divisor < 0 and quotient < 0):
                    quotient = abs(quotient)
                elif (divisor > 0 and quotient > 0):
                    if random.choice([True, False]):
                        divisor = -divisor
                    else:
                        quotient = -quotient
                
                dividend = divisor * quotient
                answer = quotient
            else:
                divisor = random.randint(2, 12)
                quotient = random.randint(10, 50)
                dividend = divisor * quotient
                answer = quotient
            
            question_text = f"{dividend} ÷ {divisor} = ?"
        
        # Generate 4 options
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-15, -10, -5, -3, -2, -1, 1, 2, 3, 5, 10, 15])
            if wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}. Remember: positive × negative = negative, negative × negative = positive."
        })
        intermediate_count += 1
    
    print(f"✓ Generated {intermediate_count} Intermediate questions")
    
    # ========== ADVANCED LEVEL (40 questions) ==========
    print("Generating Advanced questions...")
    advanced_count = 0
    
    # Generate 10 double negative multiplication
    for _ in range(10):
        a = random.randint(-50, -10)
        b = random.randint(-20, -2)
        answer = a * b
        question_text = f"({a}) × ({b}) = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-50, -30, -20, 20, 30, 50])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}. Negative × Negative = Positive."
        })
        advanced_count += 1
    
    # Generate 10 double negative division
    for _ in range(10):
        divisor = random.randint(-25, -2)
        quotient = random.randint(-50, -5)
        dividend = divisor * quotient
        answer = quotient
        question_text = f"({dividend}) ÷ ({divisor}) = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-20, -10, -5, 5, 10, 20])
            if wrong < 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}. Negative ÷ Negative = Positive."
        })
        advanced_count += 1
    
    # Generate 10 three-digit multiplication
    for _ in range(10):
        a = random.randint(100, 999)
        b = random.randint(10, 99)
        answer = a * b
        question_text = f"{a} × {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-500, -300, -100, 100, 300, 500])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}."
        })
        advanced_count += 1
    
    # Generate 10 three-digit division
    for _ in range(10):
        divisor = random.randint(10, 99)
        quotient = random.randint(10, 99)
        dividend = divisor * quotient
        answer = quotient
        question_text = f"{dividend} ÷ {divisor} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-20, -10, -5, 5, 10, 20])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        correct_index = options.index(answer)
        
        questions.append({
            'topic': 'multiplication_division',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': correct_index,
            'explanation': f"The correct answer is {answer}."
        })
        advanced_count += 1
    
    print(f"✓ Generated {advanced_count} Advanced questions")
    
    return questions


def populate_database():
    """Add all multiplication_division questions to the database"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("MULTIPLICATION & DIVISION QUESTION DATABASE POPULATION")
        print("="*70 + "\n")
        
        # Check if multiplication_division questions already exist
        existing = Question.query.filter_by(topic='multiplication_division').count()
        
        if existing > 0:
            print(f"⚠️  WARNING: {existing} multiplication_division questions already exist!")
            response = input("Do you want to DELETE them and repopulate? (yes/no): ")
            if response.lower() == 'yes':
                Question.query.filter_by(topic='multiplication_division').delete()
                db.session.commit()
                print("✓ Deleted existing multiplication_division questions")
            else:
                print("❌ Cancelled. No changes made.")
                return
        
        # Generate questions
        print("\nGenerating questions...")
        questions = generate_mult_div_questions()
        
        # Add to database
        print(f"\nAdding {len(questions)} questions to database...")
        for q_data in questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        
        # Verify
        total = Question.query.filter_by(topic='multiplication_division').count()
        beginner = Question.query.filter_by(topic='multiplication_division', difficulty='beginner').count()
        intermediate = Question.query.filter_by(topic='multiplication_division', difficulty='intermediate').count()
        advanced = Question.query.filter_by(topic='multiplication_division', difficulty='advanced').count()
        
        print("\n" + "="*70)
        print("✅ DATABASE POPULATION COMPLETE!")
        print("="*70)
        print(f"\nTotal multiplication_division questions: {total}")
        print(f"  - Beginner: {beginner}")
        print(f"  - Intermediate: {intermediate}")
        print(f"  - Advanced: {advanced}")
        print("\n✅ Students can now select 'Multiplication & Division' topic!")
        print("="*70 + "\n")


if __name__ == "__main__":
    populate_database()
