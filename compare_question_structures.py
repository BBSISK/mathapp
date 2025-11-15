#!/usr/bin/env python3
"""
Compare structure of working topics (Arithmetic) vs broken topics (Algebra)
"""

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("COMPARING WORKING vs BROKEN QUESTION STRUCTURES")
print("=" * 80)

with app.app_context():
    with db.engine.connect() as conn:
        # Get a sample Arithmetic question (WORKING)
        print("\n" + "="*80)
        print("WORKING TOPIC: Arithmetic")
        print("="*80)
        
        result = conn.execute(text("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE topic = 'arithmetic'
            LIMIT 1
        """))
        
        arith = result.fetchone()
        if arith:
            print(f"\nQuestion ID: {arith[0]}")
            print(f"Question: {arith[1][:60]}...")
            print(f"Option A: '{arith[2]}'")
            print(f"Option B: '{arith[3]}'")
            print(f"Option C: '{arith[4]}'")
            print(f"Option D: '{arith[5]}'")
            print(f"Correct Answer: {arith[6]}")
            print(f"  Type: {type(arith[6])}")
            print(f"  Value: {arith[6]}")
        
        # Get a sample Algebra question (BROKEN)
        print("\n" + "="*80)
        print("BROKEN TOPIC: Introductory Algebra")
        print("="*80)
        
        result = conn.execute(text("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE topic = 'introductory_algebra'
            LIMIT 1
        """))
        
        algebra = result.fetchone()
        if algebra:
            print(f"\nQuestion ID: {algebra[0]}")
            print(f"Question: {algebra[1][:60]}...")
            print(f"Option A: '{algebra[2]}'")
            print(f"Option B: '{algebra[3]}'")
            print(f"Option C: '{algebra[4]}'")
            print(f"Option D: '{algebra[5]}'")
            print(f"Correct Answer: {algebra[6]}")
            print(f"  Type: {type(algebra[6])}")
            print(f"  Value: {algebra[6]}")
        
        # Compare the structures
        print("\n" + "="*80)
        print("COMPARISON")
        print("="*80)
        
        if arith and algebra:
            print(f"\nArithmetic correct_answer type: {type(arith[6])}")
            print(f"Algebra correct_answer type: {type(algebra[6])}")
            
            if type(arith[6]) != type(algebra[6]):
                print("\n⚠️  TYPES ARE DIFFERENT!")
                print("This is the problem - frontend expects one type but got another")
            else:
                print("\n✓ Types are the same")
                print("\nBoth store as:", type(arith[6]))
        
        # Check the database schema
        print("\n" + "="*80)
        print("DATABASE SCHEMA")
        print("="*80)
        
        result = conn.execute(text("PRAGMA table_info(questions)"))
        for row in result:
            if 'correct' in row[1].lower():
                print(f"\nColumn: {row[1]}")
                print(f"  Type: {row[2]}")
                print(f"  Not Null: {row[3]}")
                print(f"  Default: {row[4]}")

if __name__ == '__main__':
    pass
