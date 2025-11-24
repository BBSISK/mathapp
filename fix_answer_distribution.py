"""
ANSWER DISTRIBUTION ANALYZER & FIXER
=====================================
Analyzes the distribution of correct answers (A, B, C, D) across topics
and rebalances them to ensure uniform distribution.

Usage:
    cd ~/mathapp
    source venv/bin/activate
    
    # Just analyze (no changes):
    python fix_answer_distribution.py --analyze
    
    # Fix the distribution:
    python fix_answer_distribution.py --fix
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
        
        # Check for imbalance (>35% or <15% for any answer)
        max_pct = max(percentages.values())
        min_pct = min(percentages.values())
        is_problem = max_pct > 35 or min_pct < 15
        
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
            highlight = " <<<" if pct > 35 else ""
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


def fix_distribution(cursor, conn):
    """Fix answer distribution by shuffling options for each question"""
    print("\n" + "=" * 80)
    print("FIXING ANSWER DISTRIBUTION")
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
        
        # Calculate target distribution (roughly equal)
        target_per_answer = total // 4
        remainder = total % 4
        
        # Shuffle questions and assign new correct answers
        question_ids = [q[0] for q in questions]
        random.shuffle(question_ids)
        
        # Create target answer assignments
        answer_assignments = []
        for answer_idx in range(4):
            count = target_per_answer + (1 if answer_idx < remainder else 0)
            answer_assignments.extend([answer_idx] * count)
        
        random.shuffle(answer_assignments)
        
        # Update each question
        for q_id, new_correct in zip(question_ids, answer_assignments):
            # Get current question
            cursor.execute("""
                SELECT option_a, option_b, option_c, option_d, correct_answer
                FROM questions WHERE id = ?
            """, (q_id,))
            row = cursor.fetchone()
            
            options = [row[0], row[1], row[2], row[3]]
            old_correct = row[4]
            
            # Skip if correct_answer is invalid
            if old_correct is None or old_correct < 0 or old_correct > 3:
                print(f"    ⚠️  Skipping question {q_id}: invalid correct_answer = {old_correct}")
                continue
            
            # Get the actual correct answer text
            correct_text = options[old_correct]
            
            # Shuffle the options
            random.shuffle(options)
            
            # Find where the correct answer ended up
            new_correct_idx = options.index(correct_text)
            
            # Update the question with shuffled options
            cursor.execute("""
                UPDATE questions 
                SET option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?
                WHERE id = ?
            """, (options[0], options[1], options[2], options[3], new_correct_idx, q_id))
            
            total_fixed += 1
        
        print(f"  ✓ {topic}/{difficulty}: Shuffled {total} questions")
    
    conn.commit()
    print(f"\n✓ Total questions shuffled: {total_fixed}")
    return total_fixed


def main():
    parser = argparse.ArgumentParser(description='Analyze and fix answer distribution')
    parser.add_argument('--analyze', action='store_true', help='Only analyze, do not fix')
    parser.add_argument('--fix', action='store_true', help='Fix the distribution')
    args = parser.parse_args()
    
    if not args.analyze and not args.fix:
        print("Please specify --analyze or --fix")
        print("  --analyze: Show distribution without making changes")
        print("  --fix: Shuffle options to balance distribution")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Always analyze first
    problems = analyze_distribution(cursor)
    
    if args.fix:
        if not problems:
            print("\nNo problems found, but will still shuffle to ensure randomness...")
        
        confirm = input("\nThis will shuffle ALL question options. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            fix_distribution(cursor, conn)
            print("\n" + "=" * 80)
            print("VERIFICATION - New Distribution:")
            print("=" * 80)
            analyze_distribution(cursor)
        else:
            print("Cancelled.")
    
    conn.close()


if __name__ == "__main__":
    main()
