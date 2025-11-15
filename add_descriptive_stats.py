#!/usr/bin/env python3
"""
Generate and add 120 descriptive statistics questions to the database
Covers: mean, median, mode, range, quartiles, IQR
"""

import json
import random
from app import app, db
from sqlalchemy import text

def generate_descriptive_stats_questions():
    """Generate 120 descriptive statistics questions"""
    questions = []
    
    # FOUNDATION LEVEL (40 questions)
    # Mean - 10 questions
    for i in range(10):
        values = sorted([random.randint(1, 20) for _ in range(random.choice([4, 5, 6]))])
        mean = sum(values) / len(values)
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the mean of: {", ".join(map(str, values))}',
            'correct_answer': str(mean) if mean == int(mean) else f'{mean:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'mean'})
        })
    
    # Median - 10 questions (odd and even counts)
    for i in range(10):
        count = random.choice([5, 7, 9]) if i < 5 else random.choice([4, 6, 8])
        values = sorted([random.randint(1, 30) for _ in range(count)])
        if len(values) % 2 == 1:
            median = values[len(values) // 2]
        else:
            mid = len(values) // 2
            median = (values[mid - 1] + values[mid]) / 2
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the median of: {", ".join(map(str, values))}',
            'correct_answer': str(median) if median == int(median) else f'{median:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'median'})
        })
    
    # Mode - 10 questions
    for i in range(10):
        mode_value = random.randint(5, 20)
        other_values = [random.randint(1, 25) for _ in range(random.randint(4, 6))]
        # Insert mode value 2-3 times
        values = other_values + [mode_value] * random.choice([2, 3])
        random.shuffle(values)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the mode of: {", ".join(map(str, values))}',
            'correct_answer': str(mode_value),
            'topic_data': json.dumps({'values': values, 'type': 'mode'})
        })
    
    # Range - 10 questions
    for i in range(10):
        values = sorted([random.randint(1, 50) for _ in range(random.randint(5, 8))])
        range_val = values[-1] - values[0]
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'foundation',
            'question_text': f'Find the range of: {", ".join(map(str, values))}',
            'correct_answer': str(range_val),
            'topic_data': json.dumps({'values': values, 'type': 'range'})
        })
    
    # ORDINARY LEVEL (40 questions)
    # Mean with larger numbers - 10 questions
    for i in range(10):
        values = sorted([random.randint(20, 100) for _ in range(random.choice([5, 6, 7]))])
        mean = sum(values) / len(values)
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Calculate the mean of: {", ".join(map(str, values))}',
            'correct_answer': str(mean) if mean == int(mean) else f'{mean:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'mean'})
        })
    
    # Median with larger datasets - 10 questions
    for i in range(10):
        count = random.choice([7, 9, 11]) if i < 5 else random.choice([6, 8, 10])
        values = sorted([random.randint(10, 80) for _ in range(count)])
        if len(values) % 2 == 1:
            median = values[len(values) // 2]
        else:
            mid = len(values) // 2
            median = (values[mid - 1] + values[mid]) / 2
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Find the median of: {", ".join(map(str, values))}',
            'correct_answer': str(median) if median == int(median) else f'{median:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'median'})
        })
    
    # Quartiles Q1 - 10 questions
    for i in range(10):
        values = sorted([random.randint(5, 60) for _ in range(random.choice([8, 9, 12]))])
        n = len(values)
        q1_pos = (n + 1) / 4
        if q1_pos == int(q1_pos):
            q1 = values[int(q1_pos) - 1]
        else:
            lower = int(q1_pos) - 1
            upper = lower + 1
            q1 = (values[lower] + values[upper]) / 2
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Find Q1 (lower quartile) of: {", ".join(map(str, values))}',
            'correct_answer': str(q1) if q1 == int(q1) else f'{q1:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'q1'})
        })
    
    # Quartiles Q3 - 10 questions
    for i in range(10):
        values = sorted([random.randint(5, 60) for _ in range(random.choice([8, 9, 12]))])
        n = len(values)
        q3_pos = 3 * (n + 1) / 4
        if q3_pos == int(q3_pos):
            q3 = values[int(q3_pos) - 1]
        else:
            lower = int(q3_pos) - 1
            upper = lower + 1
            q3 = (values[lower] + values[upper]) / 2
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'ordinary',
            'question_text': f'Find Q3 (upper quartile) of: {", ".join(map(str, values))}',
            'correct_answer': str(q3) if q3 == int(q3) else f'{q3:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'q3'})
        })
    
    # HIGHER LEVEL (40 questions)
    # Interquartile Range (IQR) - 15 questions
    for i in range(15):
        values = sorted([random.randint(10, 80) for _ in range(random.choice([9, 11, 13]))])
        n = len(values)
        
        # Calculate Q1
        q1_pos = (n + 1) / 4
        if q1_pos == int(q1_pos):
            q1 = values[int(q1_pos) - 1]
        else:
            lower = int(q1_pos) - 1
            upper = lower + 1
            q1 = (values[lower] + values[upper]) / 2
        
        # Calculate Q3
        q3_pos = 3 * (n + 1) / 4
        if q3_pos == int(q3_pos):
            q3 = values[int(q3_pos) - 1]
        else:
            lower = int(q3_pos) - 1
            upper = lower + 1
            q3 = (values[lower] + values[upper]) / 2
        
        iqr = q3 - q1
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'Find the interquartile range (IQR) of: {", ".join(map(str, values))}',
            'correct_answer': str(iqr) if iqr == int(iqr) else f'{iqr:.1f}',
            'topic_data': json.dumps({'values': values, 'type': 'iqr', 'q1': q1, 'q3': q3})
        })
    
    # Mean with decimals - 10 questions
    for i in range(10):
        values = sorted([round(random.uniform(10, 50), 1) for _ in range(random.choice([5, 6, 7]))])
        mean = sum(values) / len(values)
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'Calculate the mean of: {", ".join(map(str, values))}',
            'correct_answer': f'{mean:.2f}',
            'topic_data': json.dumps({'values': values, 'type': 'mean'})
        })
    
    # Combined statistics - 10 questions (find mean AND median)
    for i in range(10):
        values = sorted([random.randint(15, 75) for _ in range(random.choice([7, 9]))])
        mean = sum(values) / len(values)
        
        if len(values) % 2 == 1:
            median = values[len(values) // 2]
        else:
            mid = len(values) // 2
            median = (values[mid - 1] + values[mid]) / 2
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'For the data: {", ".join(map(str, values))}, find the difference between the mean and median (mean - median)',
            'correct_answer': str(round(mean - median, 1)) if mean - median != int(mean - median) else str(int(mean - median)),
            'topic_data': json.dumps({'values': values, 'type': 'mean_median_diff', 'mean': mean, 'median': median})
        })
    
    # Standard deviation concept - 5 questions (which set has larger spread)
    for i in range(5):
        # Create two sets with different spreads
        set_a = sorted([random.randint(40, 60) for _ in range(6)])
        set_b_min = random.randint(10, 30)
        set_b_max = random.randint(70, 90)
        set_b = sorted([set_b_min] + [random.randint(set_b_min + 5, set_b_max - 5) for _ in range(4)] + [set_b_max])
        
        range_a = set_a[-1] - set_a[0]
        range_b = set_b[-1] - set_b[0]
        
        answer = 'A' if range_a > range_b else 'B'
        
        questions.append({
            'topic': 'descriptive_statistics',
            'strand': 'Statistics and Probability',
            'difficulty': 'higher',
            'question_text': f'Which dataset has the larger range?\nSet A: {", ".join(map(str, set_a))}\nSet B: {", ".join(map(str, set_b))}\nAnswer A or B',
            'correct_answer': answer,
            'topic_data': json.dumps({'set_a': set_a, 'set_b': set_b, 'type': 'compare_range', 'range_a': range_a, 'range_b': range_b})
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
                        (topic, strand, difficulty, question_text, correct_answer, topic_data)
                        VALUES 
                        (:topic, :strand, :difficulty, :question_text, :correct_answer, :topic_data)
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
        print("=" * 60)
    else:
        print("\n✗ Failed to add questions")
