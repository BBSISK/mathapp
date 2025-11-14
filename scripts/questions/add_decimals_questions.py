"""
ADD DECIMALS QUESTIONS - Junior Cycle Mathematics (Ireland)

This script adds comprehensive decimals questions across 3 difficulty levels:
- BEGINNER: Basic decimal operations (addition, subtraction, place value, ordering)
- INTERMEDIATE: Multiplication, division, converting fractions to decimals
- ADVANCED: Recurring decimals, significant figures, rounding, complex conversions

Based on Corbett Maths curriculum materials.

Run this ONCE in the terminal:
    python add_decimals_questions.py

This will add 40 questions per difficulty level (120 total decimal questions).
"""

from app import app, db, Question
import random
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

def generate_decimals_questions():
    """Generate comprehensive decimals questions (40 per difficulty)"""
    questions = []
    
    # ========== BEGINNER (40 questions) ==========
    print("Generating Decimals Beginner questions...")
    
    # 10 questions: Adding decimals (1 decimal place)
    for _ in range(10):
        a = round(random.uniform(1.0, 9.9), 1)
        b = round(random.uniform(0.5, 8.5), 1)
        
        answer = round(a + b, 1)
        question_text = f"{a} + {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-1.1, -0.9, -0.5, 0.5, 0.9, 1.1]), 1)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Line up the decimal points: {a} + {b} = {answer}"
        })
    
    # 10 questions: Subtracting decimals (1 decimal place)
    for _ in range(10):
        a = round(random.uniform(5.0, 15.0), 1)
        b = round(random.uniform(1.0, a-0.5), 1)
        
        answer = round(a - b, 1)
        question_text = f"{a} − {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-1.2, -0.8, 0.8, 1.2]), 1)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Line up the decimal points: {a} − {b} = {answer}"
        })
    
    # 10 questions: Ordering decimals
    for _ in range(10):
        nums = [round(random.uniform(0.1, 9.9), 1) for _ in range(4)]
        sorted_nums = sorted(nums)
        smallest = sorted_nums[0]
        
        question_text = f"Which is the smallest number? {nums[0]}, {nums[1]}, {nums[2]}, {nums[3]}"
        
        options = nums.copy()
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(smallest),
            'explanation': f"Compare the digits from left to right. The smallest is {smallest}"
        })
    
    # 10 questions: Place value with decimals
    for _ in range(10):
        whole = random.randint(1, 9)
        tenths = random.randint(0, 9)
        hundredths = random.randint(1, 9)
        
        decimal_num = float(f"{whole}.{tenths}{hundredths}")
        
        questions_types = [
            ("What is the digit in the tenths place?", tenths, "The tenths place is the first digit after the decimal point"),
            ("What is the digit in the hundredths place?", hundredths, "The hundredths place is the second digit after the decimal point"),
            ("What is the digit in the ones place?", whole, "The ones place is the digit before the decimal point")
        ]
        
        q_type = random.choice(questions_types)
        question_text = f"In the number {decimal_num}, {q_type[0]}"
        answer = q_type[1]
        
        options = [answer]
        while len(options) < 4:
            wrong = random.randint(0, 9)
            if wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"{q_type[2]}. The answer is {answer}"
        })
    
    print("✓ Generated 40 Decimals Beginner questions")
    
    # ========== INTERMEDIATE (40 questions) ==========
    print("Generating Decimals Intermediate questions...")
    
    # 10 questions: Multiplying decimals by whole numbers
    for _ in range(10):
        a = round(random.uniform(1.2, 9.8), 1)
        b = random.randint(2, 9)
        
        answer = round(a * b, 1)
        question_text = f"{a} × {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-2.1, -1.5, 1.5, 2.1]), 1)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Multiply {a} by {b}: {answer}"
        })
    
    # 10 questions: Dividing decimals by whole numbers
    for _ in range(10):
        b = random.randint(2, 8)
        answer = round(random.uniform(1.5, 9.5), 1)
        a = round(answer * b, 1)
        
        question_text = f"{a} ÷ {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-1.2, -0.8, 0.8, 1.2]), 1)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Divide {a} by {b}: {answer}"
        })
    
    # 10 questions: Converting simple fractions to decimals
    fractions_data = [
        (1, 2, 0.5), (1, 4, 0.25), (3, 4, 0.75),
        (1, 5, 0.2), (2, 5, 0.4), (3, 5, 0.6), (4, 5, 0.8),
        (1, 10, 0.1), (3, 10, 0.3), (7, 10, 0.7), (9, 10, 0.9)
    ]
    
    for _ in range(10):
        num, den, answer = random.choice(fractions_data)
        
        question_text = f"Convert {num}/{den} to a decimal"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-0.25, -0.2, -0.1, 0.1, 0.2, 0.25]), 2)
            if 0 < wrong < 1 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"{num}/{den} = {num} ÷ {den} = {answer}"
        })
    
    # 10 questions: Rounding decimals to 1 decimal place
    for _ in range(10):
        a = round(random.uniform(1.01, 99.99), 2)
        answer = round(a, 1)
        
        question_text = f"Round {a} to 1 decimal place"
        
        options = [answer]
        # Add options that might be confused
        if answer < a:
            options.append(round(answer + 0.1, 1))
        else:
            options.append(round(answer - 0.1, 1))
        
        while len(options) < 4:
            wrong = round(answer + random.choice([-0.2, -0.1, 0.1, 0.2]), 1)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        hundredths = int((a * 100) % 10)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Look at the hundredths digit ({hundredths}). {'Round up' if hundredths >= 5 else 'Round down'} to get {answer}"
        })
    
    print("✓ Generated 40 Decimals Intermediate questions")
    
    # ========== ADVANCED (40 questions) ==========
    print("Generating Decimals Advanced questions...")
    
    # 10 questions: Multiplying decimals by decimals
    for _ in range(10):
        a = round(random.uniform(1.1, 9.9), 1)
        b = round(random.uniform(0.2, 0.9), 1)
        
        answer = round(a * b, 2)
        question_text = f"{a} × {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = round(answer + random.choice([-0.5, -0.3, 0.3, 0.5]), 2)
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Count total decimal places: {a} × {b} = {answer}"
        })
    
    # 10 questions: Dividing by decimals
    for _ in range(10):
        b = round(random.uniform(0.2, 0.9), 1)
        answer_whole = random.randint(4, 20)
        a = round(b * answer_whole, 1)
        answer = float(answer_whole)
        
        question_text = f"{a} ÷ {b} = ?"
        
        options = [answer]
        while len(options) < 4:
            wrong = float(answer + random.choice([-3, -2, -1, 1, 2, 3]))
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(int(options[0]) if options[0] == int(options[0]) else options[0]),
            'option_b': str(int(options[1]) if options[1] == int(options[1]) else options[1]),
            'option_c': str(int(options[2]) if options[2] == int(options[2]) else options[2]),
            'option_d': str(int(options[3]) if options[3] == int(options[3]) else options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"To divide by {b}, multiply both numbers by 10: {a*10} ÷ {int(b*10)} = {int(answer)}"
        })
    
    # 10 questions: Recurring decimals (recognizing patterns)
    recurring_fractions = [
        (1, 3, "0.333...", "0.3̇"),
        (2, 3, "0.666...", "0.6̇"),
        (1, 6, "0.1666...", "0.16̇"),
        (5, 6, "0.8333...", "0.83̇"),
        (1, 9, "0.111...", "0.1̇"),
        (2, 9, "0.222...", "0.2̇"),
        (4, 9, "0.444...", "0.4̇"),
        (5, 9, "0.555...", "0.5̇"),
        (7, 9, "0.777...", "0.7̇"),
        (8, 9, "0.888...", "0.8̇")
    ]
    
    for _ in range(10):
        num, den, long_form, answer = random.choice(recurring_fractions)
        
        question_text = f"Convert {num}/{den} to a recurring decimal (use dot notation)"
        
        # Create plausible wrong answers
        options = [answer]
        
        # Add similar looking options
        digit = answer[2]  # Get the recurring digit
        for offset in [-1, 1, 2]:
            new_digit = str((int(digit) + offset) % 10)
            if len(answer) == 4:  # Single recurring digit like 0.3̇
                wrong = f"0.{new_digit}̇"
            else:  # Two digits like 0.16̇
                wrong = f"0.{answer[2]}{new_digit}̇"
            if wrong not in options:
                options.append(wrong)
                if len(options) >= 4:
                    break
        
        # Fill remaining options if needed
        while len(options) < 4:
            random_digit = random.randint(1, 9)
            wrong = f"0.{random_digit}̇"
            if wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"{num}/{den} = {num} ÷ {den} = {long_form} = {answer}"
        })
    
    # 10 questions: Significant figures
    for _ in range(10):
        # Generate a number with 4-5 significant figures
        a = round(random.uniform(123.4, 9876.5), 1)
        sig_figs = random.choice([2, 3])
        
        # Round to significant figures
        if sig_figs == 2:
            if a >= 1000:
                answer = round(a, -2)
            elif a >= 100:
                answer = round(a, -1)
            else:
                answer = round(a, 0)
        else:  # 3 sig figs
            if a >= 1000:
                answer = round(a, -1)
            elif a >= 100:
                answer = round(a, 0)
            else:
                answer = round(a, 1)
        
        question_text = f"Round {a} to {sig_figs} significant figures"
        
        options = [answer]
        while len(options) < 4:
            if sig_figs == 2:
                wrong = answer + random.choice([-100, -50, -10, 10, 50, 100])
            else:
                wrong = answer + random.choice([-10, -5, 5, 10])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'decimals',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(int(options[0]) if options[0] == int(options[0]) else options[0]),
            'option_b': str(int(options[1]) if options[1] == int(options[1]) else options[1]),
            'option_c': str(int(options[2]) if options[2] == int(options[2]) else options[2]),
            'option_d': str(int(options[3]) if options[3] == int(options[3]) else options[3]),
            'correct_answer': options.index(answer),
            'explanation': f"Count {sig_figs} significant figures from the left: {answer}"
        })
    
    print("✓ Generated 40 Decimals Advanced questions")
    
    return questions

def add_questions_to_db():
    """Add all decimals questions to the database"""
    with app.app_context():
        print("\n" + "="*50)
        print("ADDING DECIMALS QUESTIONS TO DATABASE")
        print("="*50 + "\n")
        
        # Generate questions
        questions = generate_decimals_questions()
        
        # Check if decimals questions already exist
        existing_count = Question.query.filter_by(topic='decimals').count()
        if existing_count > 0:
            print(f"\n⚠️  WARNING: {existing_count} decimals questions already exist!")
            response = input("Do you want to ADD MORE questions? (yes/no): ")
            if response.lower() != 'yes':
                print("Operation cancelled.")
                return
        
        # Add to database
        print(f"\nAdding {len(questions)} decimals questions to database...")
        added_count = 0
        
        for q_data in questions:
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
            added_count += 1
        
        db.session.commit()
        
        print(f"\n✅ Successfully added {added_count} decimals questions!")
        
        # Show breakdown
        print("\nBreakdown by difficulty:")
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = Question.query.filter_by(topic='decimals', difficulty=difficulty).count()
            print(f"  {difficulty.capitalize()}: {count} questions")
        
        total = Question.query.filter_by(topic='decimals').count()
        print(f"\nTotal decimals questions in database: {total}")
        print("\n" + "="*50)
        print("DECIMALS QUESTIONS ADDED SUCCESSFULLY!")
        print("="*50)

if __name__ == '__main__':
    add_questions_to_db()
