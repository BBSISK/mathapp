"""
ANSWER DISTRIBUTION ANALYZER & FIXER (V2 - GUARANTEED EQUAL)
=============================================================
Analyzes the distribution of correct answers (A, B, C, D) across topics
and rebalances them to GUARANTEE uniform distribution.

This version forces exactly 25% to each answer (or as close as possible).

Usage:
    cd ~/mathapp
    source venv/bin/activate
    
    # Just analyze (no changes):
    python fix_answer_distribution_v2.py --analyze
    
    # Fix the distribution:
    python fix_answer_distribution_v2.py --fix
"""

import sqlite3
import random
import argparse

# Database path
DB_PATH = '/home/bbsisk/mathapp/instance/mathquiz.db'

def analyze_distribution(cursor):
    """Analyze answer distribution per topic and difficulty"""
    print("=" * 80)
    print("ANSWER DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    # Get all topics
    cursor.execute("""
        SELECT DISTINCT topic, difficulty 
        FROM questions 
        ORDER BY topic, 
            CASE difficulty 
                WHEN 'beginner' THEN 1 
                WHEN 'intermediate' THEN 2 
                WHEN 'advanced' THEN 3 
            END
    """)
    topic_difficulties = cursor.fetchall()
    
    problems = []
    
    for topic, difficulty in topic_difficulties:
        cursor.execute("""
            SELECT correct_answer, COUNT(*) as count
            FROM questions
            WHERE topic = ? AND difficulty = ?
            GROUP BY correct_answer
            ORDER BY correct_answer
        """, (topic, difficulty))
        
        distribution = {0: 0, 1: 0, 2: 0, 3: 0}  # A=0, B=1, C=2, D=3
        total = 0
        
        for row in cursor.fetchall():
            answer_idx = row[0]
            count = row[1]
            distribution[answer_idx] = count
            total += count
        
        if total == 0:
            continue
        
        # Calculate percentages
        percentages = {k: (v / total * 100) for k, v in distribution.items()}
        labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        
        # Check for imbalance (>30% or <20% for any answer)
        max_pct = max(percentages.values())
        min_pct = min(percentages.values())
        is_problem = max_pct > 30 or min_pct < 20
        
        if is_problem:
            problems.append((topic, difficulty, total, percentages))
        
        # Print distribution
        status = "⚠️  IMBALANCED" if is_problem else "✓"
        print(f"\n{topic} ({difficulty}) - {total} questions {status}")
        
        bar_width = 40
        for idx in range(4):
            pct = percentages[idx]
            bar_len = int(pct / 100 * bar_width)
            bar = "█" * bar_len + "░" * (bar_width - bar_len)
            highlight = " <<<" if pct > 30 else ""
            print(f"  {labels[idx]}: {bar} {pct:5.1f}% ({distribution[idx]:3d}){highlight}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(problems)} topic/difficulty combinations need rebalancing")
    print("=" * 80)
    
    if problems:
        print("\nProblems found in:")
        for topic, difficulty, total, pcts in problems:
            max_answer = max(pcts, key=pcts.get)
            labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
            print(f"  - {topic}/{difficulty}: Answer {labels[max_answer]} is {pcts[max_answer]:.1f}%")
    
    return problems


def fix_distribution_guaranteed(cursor, conn):
    """
    Fix answer distribution by GUARANTEEING equal distribution.
    
    For each topic/difficulty:
    1. Get all questions
    2. Calculate exact target: if 40 questions, each answer gets exactly 10
    3. Assign target correct answers and rearrange options accordingly
    """
    print("\n" + "=" * 80)
    print("FIXING ANSWER DISTRIBUTION (GUARANTEED EQUAL)")
    print("=" * 80)
    
    # Get all topics and difficulties
    cursor.execute("""
        SELECT DISTINCT topic, difficulty FROM questions
    """)
    topic_difficulties = cursor.fetchall()
    
    total_fixed = 0
    
    for topic, difficulty in topic_difficulties:
        # Get all questions for this topic/difficulty
        cursor.execute("""
            SELECT id, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE topic = ? AND difficulty = ?
        """, (topic, difficulty))
        
        questions = cursor.fetchall()
        total = len(questions)
        
        if total == 0:
            continue
        
        # Calculate EXACT target distribution
        # E.g., 40 questions = 10 each for A, B, C, D
        # E.g., 42 questions = 11, 11, 10, 10 (remainder distributed)
        base_count = total // 4
        remainder = total % 4
        
        # Create list of target answers: [0,0,0..., 1,1,1..., 2,2,2..., 3,3,3...]
        target_answers = []
        for answer_idx in range(4):
            # Give one extra to first 'remainder' answers
            count = base_count + (1 if answer_idx < remainder else 0)
            target_answers.extend([answer_idx] * count)
        
        # Shuffle to randomize which questions get which target
        random.shuffle(target_answers)
        
        # Process each question
        questions_fixed = 0
        for i, question in enumerate(questions):
            q_id = question[0]
            options = [question[1], question[2], question[3], question[4]]
            old_correct_idx = question[5]
            
            # Skip if correct_answer is invalid
            if old_correct_idx is None or old_correct_idx < 0 or old_correct_idx > 3:
                print(f"    ⚠️  Skipping question {q_id}: invalid correct_answer = {old_correct_idx}")
                continue
            
            # Get the actual correct answer TEXT
            correct_answer_text = options[old_correct_idx]
            
            # Get the TARGET position for correct answer (0=A, 1=B, 2=C, 3=D)
            target_position = target_answers[i]
            
            # Create new option order:
            # 1. Remove correct answer from options
            # 2. Shuffle the wrong answers
            # 3. Insert correct answer at target position
            
            wrong_options = [opt for idx, opt in enumerate(options) if idx != old_correct_idx]
            random.shuffle(wrong_options)
            
            # Build new options list with correct answer at target position
            new_options = []
            wrong_idx = 0
            for pos in range(4):
                if pos == target_position:
                    new_options.append(correct_answer_text)
                else:
                    new_options.append(wrong_options[wrong_idx])
                    wrong_idx += 1
            
            # Update the question
            cursor.execute("""
                UPDATE questions 
                SET option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?
                WHERE id = ?
            """, (new_options[0], new_options[1], new_options[2], new_options[3], target_position, q_id))
            
            questions_fixed += 1
        
        total_fixed += questions_fixed
        
        # Show what we did
        counts = [target_answers.count(i) for i in range(4)]
        print(f"  ✓ {topic}/{difficulty}: {questions_fixed} questions -> A:{counts[0]} B:{counts[1]} C:{counts[2]} D:{counts[3]}")
    
    conn.commit()
    print(f"\n✓ Total questions fixed: {total_fixed}")
    return total_fixed


def main():
    parser = argparse.ArgumentParser(description='Analyze and fix answer distribution (V2 - Guaranteed)')
    parser.add_argument('--analyze', action='store_true', help='Only analyze, do not fix')
    parser.add_argument('--fix', action='store_true', help='Fix the distribution (guaranteed equal)')
    args = parser.parse_args()
    
    if not args.analyze and not args.fix:
        print("Please specify --analyze or --fix")
        print("  --analyze: Show distribution without making changes")
        print("  --fix: Rearrange options to GUARANTEE equal distribution")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Always analyze first
    problems = analyze_distribution(cursor)
    
    if args.fix:
        print("\n" + "-" * 80)
        print("This version GUARANTEES equal distribution (not random shuffling)")
        print("-" * 80)
        
        confirm = input("\nThis will rearrange ALL question options. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            fix_distribution_guaranteed(cursor, conn)
            print("\n" + "=" * 80)
            print("VERIFICATION - New Distribution:")
            print("=" * 80)
            analyze_distribution(cursor)
        else:
            print("Cancelled.")
    
    conn.close()


if __name__ == "__main__":
    main()
