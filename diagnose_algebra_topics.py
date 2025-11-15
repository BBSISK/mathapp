#!/usr/bin/env python3
"""
Diagnostic script to check why new algebra topics aren't loading questions
"""

from app import app, db
from sqlalchemy import text

print("=" * 70)
print("DIAGNOSTIC: Checking New Algebra Topics")
print("=" * 70)

with app.app_context():
    with db.engine.connect() as conn:
        # Check 1: Do the questions exist?
        print("\n1. Checking if questions exist in database...")
        result = conn.execute(text("""
            SELECT topic, difficulty, COUNT(*) as count
            FROM questions 
            WHERE topic IN ('solving_equations', 'simplifying_expressions', 'expanding_factorising')
            GROUP BY topic, difficulty
            ORDER BY topic, 
                CASE difficulty 
                    WHEN 'foundation' THEN 1 
                    WHEN 'ordinary' THEN 2 
                    WHEN 'higher' THEN 3 
                END
        """))
        
        rows = result.fetchall()
        if len(rows) == 0:
            print("   ✗ NO QUESTIONS FOUND!")
            print("   → You need to run: python3 add_algebra_topics.py")
        else:
            print(f"   ✓ Found questions:")
            for row in rows:
                print(f"     {row[0]} - {row[1]}: {row[2]} questions")
        
        # Check 2: Are strands set correctly?
        print("\n2. Checking strand values...")
        result = conn.execute(text("""
            SELECT topic, strand, COUNT(*) as count
            FROM questions 
            WHERE topic IN ('solving_equations', 'simplifying_expressions', 'expanding_factorising')
            GROUP BY topic, strand
        """))
        
        for row in result:
            if row[1] == 'Algebra and Functions':
                print(f"   ✓ {row[0]}: strand = '{row[1]}' ({row[2]} questions)")
            else:
                print(f"   ✗ {row[0]}: strand = '{row[1]}' (WRONG! Should be 'Algebra and Functions')")
        
        # Check 3: Sample a question to see its structure
        print("\n3. Checking question structure (sample question)...")
        result = conn.execute(text("""
            SELECT question_text, option_a, option_b, option_c, option_d, correct_answer, explanation
            FROM questions 
            WHERE topic = 'solving_equations'
            LIMIT 1
        """))
        
        row = result.fetchone()
        if row:
            print(f"   Question: {row[0][:60]}...")
            print(f"   Option A: {row[1]}")
            print(f"   Option B: {row[2]}")
            print(f"   Option C: {row[3]}")
            print(f"   Option D: {row[4]}")
            print(f"   Correct: {row[5]}")
            print(f"   Explanation: {row[6][:50]}...")
        else:
            print("   ✗ No sample question found")
        
        # Check 4: Test the API endpoint query
        print("\n4. Testing the actual query app.py uses...")
        try:
            result = conn.execute(text("""
                SELECT id, question_text, option_a, option_b, option_c, option_d, 
                       correct_answer, explanation, difficulty
                FROM questions
                WHERE topic = :topic
                AND difficulty = :difficulty
                ORDER BY RANDOM()
                LIMIT 10
            """), {'topic': 'solving_equations', 'difficulty': 'foundation'})
            
            questions = result.fetchall()
            print(f"   ✓ Query returned {len(questions)} questions")
            
            if len(questions) == 0:
                print("   ✗ WARNING: No questions returned even though they exist!")
                print("   → This suggests a query mismatch issue")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
        
        # Check 5: Verify topics are in TOPICS configuration
        print("\n5. Checking if topics exist in app configuration...")
        from app import TOPICS
        
        new_topics = ['solving_equations', 'simplifying_expressions', 'expanding_factorising']
        for topic in new_topics:
            if topic in TOPICS:
                print(f"   ✓ {topic}: {TOPICS[topic]['title']}")
            else:
                print(f"   ✗ {topic}: NOT FOUND in TOPICS dictionary!")
                print(f"   → app.py needs to be updated!")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
