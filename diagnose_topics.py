#!/usr/bin/env python3
"""
TOPIC DIAGNOSTIC SCRIPT
========================
Run this on PythonAnywhere to diagnose topic issues:
    cd ~/mathapp
    source venv/bin/activate
    python diagnose_topics.py

This will show:
1. Topics in the `topics` database table
2. Topics in the `questions` table
3. Any mismatches or missing topics
"""

import sqlite3
import os

DB_PATH = 'instance/mathquiz.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("TOPIC DIAGNOSTIC REPORT")
    print("=" * 60)
    
    # 1. Check topics table
    print("\n📋 TOPICS TABLE (Admin-managed):")
    print("-" * 40)
    try:
        cursor.execute("""
            SELECT topic_id, display_name, is_visible 
            FROM topics 
            ORDER BY sort_order, display_name
        """)
        db_topics = cursor.fetchall()
        
        if db_topics:
            for topic_id, display_name, is_visible in db_topics:
                status = "✓" if is_visible else "🚫 HIDDEN"
                print(f"  {status} {topic_id} → {display_name}")
            print(f"\n  Total: {len(db_topics)} topics in database")
        else:
            print("  ⚠ No topics found in topics table!")
            print("  Run the topic migration script to populate it.")
    except sqlite3.OperationalError as e:
        print(f"  ❌ Error: {e}")
        print("  The topics table may not exist. Run migration first.")
    
    # 2. Check questions table
    print("\n📋 QUESTIONS TABLE (Topics with questions):")
    print("-" * 40)
    try:
        cursor.execute("""
            SELECT topic, COUNT(*) as count 
            FROM questions 
            GROUP BY topic 
            ORDER BY topic
        """)
        question_topics = cursor.fetchall()
        
        if question_topics:
            for topic, count in question_topics:
                print(f"  {topic}: {count} questions")
            print(f"\n  Total: {len(question_topics)} topics with questions")
        else:
            print("  ⚠ No questions found!")
    except sqlite3.OperationalError as e:
        print(f"  ❌ Error: {e}")
    
    # 3. Find mismatches
    print("\n🔍 MISMATCH ANALYSIS:")
    print("-" * 40)
    
    try:
        # Topics in questions but not in topics table
        cursor.execute("""
            SELECT DISTINCT q.topic
            FROM questions q
            LEFT JOIN topics t ON q.topic = t.topic_id
            WHERE t.topic_id IS NULL
        """)
        orphan_topics = cursor.fetchall()
        
        if orphan_topics:
            print("  ⚠ Topics with questions but NOT in topics table:")
            for (topic,) in orphan_topics:
                print(f"     - {topic}")
            print("\n  These topics need to be added via Admin Dashboard > Topic Management")
        else:
            print("  ✓ All topics with questions are in the topics table")
        
        # Topics in table but with no questions
        cursor.execute("""
            SELECT t.topic_id, t.display_name
            FROM topics t
            LEFT JOIN questions q ON t.topic_id = q.topic
            WHERE q.topic IS NULL AND t.is_visible = 1
        """)
        empty_topics = cursor.fetchall()
        
        if empty_topics:
            print("\n  ℹ Topics in database but with NO questions yet:")
            for topic_id, display_name in empty_topics:
                print(f"     - {topic_id} ({display_name})")
            print("\n  These topics need questions added via AI Generator or manual entry")
        
    except sqlite3.OperationalError as e:
        print(f"  ❌ Error during mismatch analysis: {e}")
    
    # 4. Check specific topics
    print("\n🎯 SPECIFIC TOPIC CHECK (coordinate_geometry):")
    print("-" * 40)
    
    # In topics table?
    cursor.execute("SELECT * FROM topics WHERE topic_id = 'coordinate_geometry'")
    in_topics = cursor.fetchone()
    print(f"  In topics table: {'✓ Yes' if in_topics else '❌ No'}")
    
    # Has questions?
    cursor.execute("SELECT COUNT(*) FROM questions WHERE topic = 'coordinate_geometry'")
    q_count = cursor.fetchone()[0]
    print(f"  Questions count: {q_count}")
    
    # Has quiz attempts?
    try:
        cursor.execute("SELECT COUNT(*) FROM quiz_attempts WHERE topic = 'coordinate_geometry'")
        a_count = cursor.fetchone()[0]
        print(f"  Quiz attempts: {a_count}")
    except:
        print(f"  Quiz attempts: (could not query)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if orphan_topics:
        print("""
1. Add missing topics to the topics table:
   - Go to Admin Dashboard > Topic Management
   - Click 'Add Topic' for each missing topic
   - Enter the topic_id exactly as shown above
""")
    
    if not in_topics:
        print("""
2. Add coordinate_geometry to topics table:
   - Go to Admin Dashboard > Topic Management  
   - Click 'Add Topic'
   - Topic ID: coordinate_geometry
   - Display Name: Coordinate Geometry
   - Strand: Geometry and Trigonometry
   - Icon: map-marker-alt
""")
    
    print("\nAfter making changes, the topics will be available immediately!")

if __name__ == '__main__':
    main()
