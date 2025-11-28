#!/usr/bin/env python3
"""
Fix Quadratic Equations Questions
Allows batch correction of incorrect questions
"""
import sys
import os

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db, Question

print("=" * 80)
print("QUADRATIC EQUATIONS CORRECTION TOOL")
print("=" * 80)
print()

def fix_question(question_id, new_answer=None, new_text=None, new_hint=None, **kwargs):
    """Fix a specific question"""
    with app.app_context():
        q = Question.query.get(question_id)
        
        if not q:
            print(f"❌ Question ID {question_id} not found")
            return False
        
        print(f"Updating Question ID {question_id}:")
        print(f"  Old Question: {q.question_text}")
        print(f"  Old Answer: {q.correct_answer}")
        
        if new_text:
            q.question_text = new_text
            print(f"  New Question: {new_text}")
        
        if new_answer:
            q.correct_answer = new_answer
            print(f"  New Answer: {new_answer}")
        
        if new_hint:
            q.hint = new_hint
            print(f"  New Hint: {new_hint}")
        
        # Update any other fields
        for key, value in kwargs.items():
            if hasattr(q, key):
                setattr(q, key, value)
                print(f"  Updated {key}: {value}")
        
        try:
            db.session.commit()
            print("✓ Question updated successfully")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating question: {e}")
            return False

def bulk_fix_questions(corrections):
    """
    Apply multiple corrections
    
    corrections = [
        {
            'id': 123,
            'new_answer': 'x = 2 or x = -3',
            'new_text': 'Solve: x² + x - 6 = 0' (optional)
        },
        ...
    ]
    """
    success_count = 0
    fail_count = 0
    
    for correction in corrections:
        question_id = correction.pop('id')
        
        # Map 'new_answer' to correct parameter name
        if 'new_answer' in correction:
            correction['correct_answer'] = correction.pop('new_answer')
        if 'new_text' in correction:
            correction['question_text'] = correction.pop('new_text')
        if 'new_hint' in correction:
            correction['hint'] = correction.pop('new_hint')
        
        with app.app_context():
            q = Question.query.get(question_id)
            
            if not q:
                print(f"❌ Question ID {question_id} not found")
                fail_count += 1
                continue
            
            print(f"\nUpdating Question ID {question_id}:")
            print(f"  Current: {q.question_text}")
            print(f"  Answer: {q.correct_answer}")
            
            for key, value in correction.items():
                if hasattr(q, key):
                    old_value = getattr(q, key)
                    setattr(q, key, value)
                    print(f"  {key}: {old_value} → {value}")
            
            try:
                db.session.commit()
                print("✓ Updated successfully")
                success_count += 1
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error: {e}")
                fail_count += 1
    
    print()
    print("=" * 80)
    print(f"Batch Update Complete: {success_count} succeeded, {fail_count} failed")
    print("=" * 80)

def delete_incorrect_questions(question_ids):
    """Delete multiple questions by ID"""
    with app.app_context():
        for qid in question_ids:
            q = Question.query.get(qid)
            if q:
                print(f"Deleting Question ID {qid}: {q.question_text[:50]}...")
                db.session.delete(q)
        
        try:
            db.session.commit()
            print(f"✓ Deleted {len(question_ids)} questions")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")

# Example usage
if __name__ == '__main__':
    print("This is a correction tool. Use it in interactive Python or import it.")
    print()
    print("Example usage:")
    print()
    print("  from fix_quadratic_questions import fix_question, bulk_fix_questions")
    print()
    print("  # Fix a single question")
    print("  fix_question(123, new_answer='x = 2 or x = -3')")
    print()
    print("  # Fix multiple questions")
    print("  corrections = [")
    print("      {'id': 123, 'new_answer': 'x = 2 or x = -3'},")
    print("      {'id': 124, 'new_answer': 'x = 1 or x = -5'},")
    print("  ]")
    print("  bulk_fix_questions(corrections)")
    print()
    print("To use interactively:")
    print("  python")
    print("  >>> from fix_quadratic_questions import *")
    print("  >>> fix_question(123, new_answer='x = 2 or x = -3')")
    print()
