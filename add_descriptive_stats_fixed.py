#!/usr/bin/env python3
"""
Generate and add 120 descriptive statistics questions to the database
Matches actual database schema with multiple choice format
"""

import random
from app import app, db
from sqlalchemy import text

def generate_multiple_choice_options(correct_answer, is_decimal=False):
    """Generate 3 wrong answers around the correct answer"""
    try:
        correct = float(correct_answer)
    except:
        # For non-numeric answers (like 'A' or 'B'), handle differently
        return None
    
    wrong_answers = []
    
    if is_decimal:
        # For decimals, create options within ±2 of correct
        offsets = [-1.5, -0.5, 0.5, 1.5]
        random.shuffle(offsets)
        for offset in offsets[:3]:
            wrong = round(correct + offset, 1)
            if wrong != correct and wrong > 0:
                wrong_answers.append(str(wrong))
    else:
        # For integers, create options within ±3 of correct
        offsets = [-3, -2, -1, 1, 2, 3]
        random.shuffle(offsets)
        for offset in offsets:
            wrong = correct + offset
            if wrong != correct and wrong > 0:
                if wrong == int(wrong):
                    wrong_answers.append(str(int(wrong)))
                else:
                    wrong_answers.append(str(wrong))
                if len(wrong_answers) >= 3:
                    break
    
    # Ensure we have exactly 3 wrong answers
    while len(wrong_answers) < 3:
        offset = random.choice([-2, -1, 1, 2])
        wrong = correct + offset
        if wrong > 0 and str(wrong) not in wrong_answers and wrong != correct:
            if wrong == int(wrong):
                wrong_answers.append(str(int(wrong)))
            else:
                wrong_answers.append(str(wrong))
    
    # Shuffle and insert correct answer
    all_options = wrong_answers[:3] + [correct_answer]
    random.shuffle(all_options)
    
    # Find position of correct answer (1-4)
    correct_position = all_options.index(correct_answer) + 1
    
    return {
        'option_a': all_options[0],
        'option_b': all_options[1],
        'option_c': all_options[2],
        'option_d': all_options[3],
        'correct_answer': correct_position
    }

def generate_descriptive_stats_questions():
    """Generate 120 descriptive statistics questions"""
    questions = []
    
    # FOUNDATION LEVEL (40 questions)
    # Mean - 10 questions
    for i in range(10):
        values = sorted([random.randint(1, 20) for _ in range(random.choice([4, 5, 6]))])
        mean = sum(values) / len(values)
        mean_str = str(int(mean)) if mean == int(mean) else f'{mean:.1f}'
        
        options = generate_multiple_choice_options(mean_str, '.' in mean_str)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the mean of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Add all values and divide by {len(values)}: ({" + ".join(map(str, values))}) ÷ {len(values)} = {mean_str}'
        })
    
    # Median - 10 questions
    for i in range(10):
        count = random.choice([5, 7, 9]) if i < 5 else random.choice([4, 6, 8])
        values = sorted([random.randint(1, 30) for _ in range(count)])
        
        if len(values) % 2 == 1:
            median = values[len(values) // 2]
            median_str = str(median)
        else:
            mid = len(values) // 2
            median = (values[mid - 1] + values[mid]) / 2
            median_str = str(int(median)) if median == int(median) else f'{median:.1f}'
        
        options = generate_multiple_choice_options(median_str, '.' in median_str)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the median of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Arrange in order (already done). Middle value = {median_str}'
        })
    
    # Mode - 10 questions
    for i in range(10):
        mode_value = random.randint(5, 20)
        other_values = [random.randint(1, 25) for _ in range(random.randint(4, 5))]
        # Make sure other values don't include mode_value
        other_values = [v for v in other_values if v != mode_value]
        values = other_values + [mode_value] * random.choice([2, 3])
        random.shuffle(values)
        
        options = generate_multiple_choice_options(str(mode_value), False)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the mode of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'The mode is the most frequent value: {mode_value} appears most often'
        })
    
    # Range - 10 questions
    for i in range(10):
        values = sorted([random.randint(1, 50) for _ in range(random.randint(5, 8))])
        range_val = values[-1] - values[0]
        
        options = generate_multiple_choice_options(str(range_val), False)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the range of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Range = Maximum - Minimum = {values[-1]} - {values[0]} = {range_val}'
        })
    
    # ORDINARY LEVEL (40 questions)
    # Mean with larger numbers - 10 questions
    for i in range(10):
        values = sorted([random.randint(20, 100) for _ in range(random.choice([5, 6, 7]))])
        mean = sum(values) / len(values)
        mean_str = str(int(mean)) if mean == int(mean) else f'{mean:.1f}'
        
        options = generate_multiple_choice_options(mean_str, '.' in mean_str)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Calculate the mean of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Sum = {sum(values)}, Count = {len(values)}, Mean = {mean_str}'
        })
    
    # Median with larger datasets - 10 questions
    for i in range(10):
        count = random.choice([7, 9, 11]) if i < 5 else random.choice([6, 8, 10])
        values = sorted([random.randint(10, 80) for _ in range(count)])
        
        if len(values) % 2 == 1:
            median = values[len(values) // 2]
            median_str = str(median)
        else:
            mid = len(values) // 2
            median = (values[mid - 1] + values[mid]) / 2
            median_str = str(int(median)) if median == int(median) else f'{median:.1f}'
        
        options = generate_multiple_choice_options(median_str, '.' in median_str)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Find the median of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Middle value(s) = {median_str}'
        })
    
    # Range with larger numbers - 20 questions
    for i in range(20):
        values = sorted([random.randint(10, 100) for _ in range(random.randint(6, 10))])
        range_val = values[-1] - values[0]
        
        options = generate_multiple_choice_options(str(range_val), False)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Find the range of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Range = {values[-1]} - {values[0]} = {range_val}'
        })
    
    # HIGHER LEVEL (40 questions)
    # Mean with decimals - 20 questions
    for i in range(20):
        values = sorted([round(random.uniform(10, 50), 1) for _ in range(random.choice([5, 6, 7]))])
        mean = sum(values) / len(values)
        mean_str = f'{mean:.1f}'
        
        options = generate_multiple_choice_options(mean_str, True)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'Calculate the mean of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Sum = {sum(values):.1f}, Mean = {mean_str}'
        })
    
    # Median with decimals - 20 questions
    for i in range(20):
        count = random.choice([6, 8, 10])
        values = sorted([round(random.uniform(5, 60), 1) for _ in range(count)])
        
        mid = len(values) // 2
        median = (values[mid - 1] + values[mid]) / 2
        median_str = str(int(median)) if median == int(median) else f'{median:.1f}'
        
        options = generate_multiple_choice_options(median_str, True)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'Find the median of: {", ".join(map(str, values))}',
            **options,
            'explanation': f'Median = ({values[mid-1]} + {values[mid]}) ÷ 2 = {median_str}'
        })
    
    return questions

def add_questions_to_db():
    """Add all questions to the database"""
    print("Generating 120 descriptive statistics questions...")
    questions = generate_descriptive_stats_questions()
    print(f"✓ Generated {len(questions)} questions")
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Check if any exist
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM questions WHERE topic = 'descriptive_statistics'"
                ))
                existing_count = result.fetchone()[0]
                
                if existing_count > 0:
                    print(f"\n⚠ Found {existing_count} existing descriptive_statistics questions")
                    print("Deleting old questions...")
                    conn.execute(text(
                        "DELETE FROM questions WHERE topic = 'descriptive_statistics'"
                    ))
                    conn.commit()
                    print(f"✓ Deleted {existing_count} old questions")
                
                # Insert new questions
                print("\nAdding new questions...")
                for q in questions:
                    conn.execute(text("""
                        INSERT INTO questions 
                        (topic, strand, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                        VALUES 
                        (:topic, :strand, :difficulty, :question_text, :option_a, :option_b, :option_c, :option_d, :correct_answer, :explanation)
                    """), q)
                
                conn.commit()
                print(f"✓ Added {len(questions)} questions")
                
                # Verify
                result = conn.execute(text("""
                    SELECT difficulty, COUNT(*) as count
                    FROM questions 
                    WHERE topic = 'descriptive_statistics'
                    GROUP BY difficulty
                    ORDER BY CASE difficulty 
                        WHEN 'foundation' THEN 1 
                        WHEN 'ordinary' THEN 2 
                        WHEN 'higher' THEN 3 
                    END
                """))
                
                print("\nQuestions by difficulty:")
                for row in result:
                    print(f"  {row[0]}: {row[1]} questions")
                
                # Show total in Statistics and Probability strand
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM questions 
                    WHERE strand = 'Statistics and Probability'
                """))
                total = result.fetchone()[0]
                print(f"\nTotal Statistics and Probability questions: {total}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = add_questions_to_db()
    if success:
        print("\n" + "=" * 60)
        print("✓ Descriptive statistics questions added successfully!")
        print("  Now reload your web app on PythonAnywhere!")
        print("=" * 60)
    else:
        print("\n✗ Failed to add questions")
