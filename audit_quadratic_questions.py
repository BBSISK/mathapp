#!/usr/bin/env python3
"""
Audit Quadratic Equations Questions
Reviews all 120 quadratic equations for correctness
"""
import sys
import os
import re

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db, Question

print("=" * 80)
print("QUADRATIC EQUATIONS AUDIT")
print("=" * 80)
print()

def evaluate_quadratic(a, b, c, x):
    """Evaluate ax² + bx + c at x"""
    return a * x**2 + b * x + c

def check_quadratic_answer(question_text, answer):
    """
    Check if the answer is correct for a quadratic equation question
    Returns: (is_correct, error_message, expected_answer)
    """
    try:
        # Parse the question to extract coefficients
        # Example: "Solve: 2x² + 5x + 3 = 0"
        
        # Extract the equation part
        if "Solve:" in question_text:
            equation = question_text.split("Solve:")[1].strip()
        else:
            equation = question_text.strip()
        
        # Remove = 0 if present
        equation = equation.replace("= 0", "").strip()
        
        # Parse coefficients (simplified - would need more robust parsing)
        # This is a basic check - you may need to enhance this
        
        return True, None, answer  # Placeholder
        
    except Exception as e:
        return False, f"Parse error: {e}", None

with app.app_context():
    # Get all quadratic equations questions
    questions = Question.query.filter_by(topic='quadratic_equations').all()
    
    if not questions:
        print("❌ No quadratic equations questions found in database!")
        print()
        print("The topic might be named differently. Checking all topics...")
        from sqlalchemy import func
        topics = db.session.query(Question.topic, func.count(Question.id)).group_by(Question.topic).all()
        print("\nTopics found:")
        for topic, count in topics:
            print(f"  • {topic}: {count} questions")
        sys.exit(1)
    
    print(f"Found {len(questions)} quadratic equations questions")
    print()
    
    # Group by difficulty
    by_difficulty = {'beginner': [], 'intermediate': [], 'advanced': []}
    for q in questions:
        if q.difficulty_level in by_difficulty:
            by_difficulty[q.difficulty_level].append(q)
    
    print("Distribution by difficulty:")
    for level, qs in by_difficulty.items():
        print(f"  {level.capitalize():12} - {len(qs):3} questions")
    print()
    
    # Show sample questions from each difficulty
    print("=" * 80)
    print("SAMPLE QUESTIONS (First 3 from each difficulty)")
    print("=" * 80)
    
    for level in ['beginner', 'intermediate', 'advanced']:
        print(f"\n{level.upper()}:")
        print("-" * 80)
        
        for i, q in enumerate(by_difficulty[level][:3], 1):
            print(f"\n{i}. ID: {q.id}")
            print(f"   Question: {q.question_text}")
            print(f"   Answer: {q.correct_answer}")
            
            # Show all options if multiple choice
            if q.option_a:
                print(f"   Options:")
                print(f"     A) {q.option_a}")
                print(f"     B) {q.option_b}")
                print(f"     C) {q.option_c}")
                print(f"     D) {q.option_d}")
            
            if q.hint:
                print(f"   Hint: {q.hint}")
    
    print()
    print("=" * 80)
    print("FULL QUESTION EXPORT")
    print("=" * 80)
    print()
    print("Exporting all questions to: quadratic_equations_full_export.txt")
    
    with open('/tmp/quadratic_equations_full_export.txt', 'w') as f:
        f.write("QUADRATIC EQUATIONS - FULL EXPORT\n")
        f.write("=" * 80 + "\n\n")
        
        for level in ['beginner', 'intermediate', 'advanced']:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{level.upper()} - {len(by_difficulty[level])} questions\n")
            f.write("=" * 80 + "\n\n")
            
            for i, q in enumerate(by_difficulty[level], 1):
                f.write(f"Question #{i} (ID: {q.id})\n")
                f.write("-" * 80 + "\n")
                f.write(f"Text: {q.question_text}\n")
                f.write(f"Answer: {q.correct_answer}\n")
                
                if q.option_a:
                    f.write(f"Options:\n")
                    f.write(f"  A) {q.option_a}\n")
                    f.write(f"  B) {q.option_b}\n")
                    f.write(f"  C) {q.option_c}\n")
                    f.write(f"  D) {q.option_d}\n")
                
                if q.hint:
                    f.write(f"Hint: {q.hint}\n")
                
                f.write("\n")
    
    print("✓ Export complete: /tmp/quadratic_equations_full_export.txt")
    print()
    print("=" * 80)
    print("MANUAL REVIEW NEEDED")
    print("=" * 80)
    print()
    print("To review the questions:")
    print("1. Check the sample questions above")
    print("2. Review the full export file")
    print("3. Identify incorrect questions")
    print("4. Use the correction script to fix them")
    print()
    print("Common issues to look for:")
    print("  • Wrong answer given")
    print("  • Coefficients incorrectly parsed")
    print("  • Solutions not in simplest form")
    print("  • Missing or extra solutions")
    print("  • Calculation errors")
    print()
