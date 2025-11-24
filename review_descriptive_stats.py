"""
DESCRIPTIVE STATISTICS QUESTION REVIEWER
=========================================
Displays all questions from Descriptive Statistics topic
so you can verify the correct answers are accurate.

Usage:
    cd ~/mathapp
    source venv/bin/activate
    python review_descriptive_stats.py
"""

import sqlite3

# Database path
DB_PATH = '/home/bbsisk/mathapp/instance/mathquiz.db'

def review_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all Descriptive Statistics questions
    cursor.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty
        FROM questions
        WHERE topic = 'Descriptive Statistics'
        ORDER BY 
            CASE difficulty 
                WHEN 'beginner' THEN 1 
                WHEN 'intermediate' THEN 2 
                WHEN 'advanced' THEN 3 
            END,
            id
    """)
    
    questions = cursor.fetchall()
    
    print("=" * 80)
    print("DESCRIPTIVE STATISTICS - QUESTION REVIEW")
    print(f"Total questions: {len(questions)}")
    print("=" * 80)
    
    labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
    current_difficulty = None
    question_num = 0
    issues = []
    
    for q in questions:
        q_id, question_text, opt_a, opt_b, opt_c, opt_d, correct_idx, difficulty = q
        
        # Print difficulty header when it changes
        if difficulty != current_difficulty:
            current_difficulty = difficulty
            question_num = 0
            print(f"\n{'='*80}")
            print(f"  {difficulty.upper()}")
            print(f"{'='*80}")
        
        question_num += 1
        options = [opt_a, opt_b, opt_c, opt_d]
        
        print(f"\n--- Question {question_num} (ID: {q_id}) ---")
        print(f"Q: {question_text}")
        print()
        
        for idx, opt in enumerate(options):
            marker = "  ✓ CORRECT →" if idx == correct_idx else "             "
            print(f"  {marker} {labels[idx]}: {opt}")
        
        # Check for potential issues
        if correct_idx is None or correct_idx < 0 or correct_idx > 3:
            issues.append((q_id, question_text, f"Invalid correct_answer: {correct_idx}"))
            print(f"\n  ⚠️  WARNING: Invalid correct_answer index!")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total questions reviewed: {len(questions)}")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for q_id, q_text, issue in issues:
            print(f"  - ID {q_id}: {issue}")
            print(f"    Question: {q_text[:50]}...")
    else:
        print("\n✓ No technical issues found with answer indices.")
    
    print("\nPlease review each question above to verify the marked CORRECT answer is accurate.")
    
    conn.close()


def review_interactive():
    """Interactive review - one question at a time"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty
        FROM questions
        WHERE topic = 'Descriptive Statistics'
        ORDER BY 
            CASE difficulty 
                WHEN 'beginner' THEN 1 
                WHEN 'intermediate' THEN 2 
                WHEN 'advanced' THEN 3 
            END,
            id
    """)
    
    questions = cursor.fetchall()
    labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
    
    print("=" * 80)
    print("INTERACTIVE QUESTION REVIEW")
    print("Press Enter to see next question, 'q' to quit, 'f' to flag an issue")
    print("=" * 80)
    
    flagged = []
    
    for i, q in enumerate(questions):
        q_id, question_text, opt_a, opt_b, opt_c, opt_d, correct_idx, difficulty = q
        options = [opt_a, opt_b, opt_c, opt_d]
        
        print(f"\n{'='*80}")
        print(f"Question {i+1}/{len(questions)} | {difficulty.upper()} | ID: {q_id}")
        print(f"{'='*80}")
        print(f"\nQ: {question_text}\n")
        
        for idx, opt in enumerate(options):
            marker = "✓" if idx == correct_idx else " "
            print(f"  [{marker}] {labels[idx]}: {opt}")
        
        print(f"\nMarked correct: {labels[correct_idx]} - {options[correct_idx]}")
        
        response = input("\nEnter=next, f=flag issue, q=quit: ").strip().lower()
        
        if response == 'q':
            break
        elif response == 'f':
            note = input("Describe the issue: ")
            flagged.append((q_id, question_text[:50], note))
            print("✓ Flagged!")
    
    if flagged:
        print("\n" + "=" * 80)
        print("FLAGGED QUESTIONS")
        print("=" * 80)
        for q_id, q_text, note in flagged:
            print(f"\nID {q_id}: {q_text}...")
            print(f"  Issue: {note}")
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        review_interactive()
    else:
        review_questions()
