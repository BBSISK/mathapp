#!/usr/bin/env python3
"""
FIX BADGES AND TOPIC PROGRESS
==============================
This script:
1. Ensures all badges in the database have proper descriptions and points
2. Diagnoses topic_progress table issues
3. Creates test entries if needed

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python fix_badges_and_progress.py
"""

import sqlite3
import os

DB_PATH = 'instance/mathquiz.db'

# Badge definitions with full data
BADGE_DEFINITIONS = {
    'First Steps': {
        'description': 'Complete your first quiz',
        'icon': 'fa-star',
        'category': 'beginner',
        'requirement_type': 'quizzes_completed',
        'requirement_value': 1,
        'points': 10,
        'color': 'blue'
    },
    'Curious Learner': {
        'description': 'Complete 5 quizzes',
        'icon': 'fa-lightbulb',
        'category': 'progress',
        'requirement_type': 'quizzes_completed',
        'requirement_value': 5,
        'points': 25,
        'color': 'green'
    },
    'Dedicated Student': {
        'description': 'Complete 10 quizzes',
        'icon': 'fa-book',
        'category': 'progress',
        'requirement_type': 'quizzes_completed',
        'requirement_value': 10,
        'points': 50,
        'color': 'purple'
    },
    'Perfectionist': {
        'description': 'Get a perfect score on any quiz',
        'icon': 'fa-trophy',
        'category': 'accuracy',
        'requirement_type': 'perfect_scores',
        'requirement_value': 1,
        'points': 30,
        'color': 'gold'
    },
    'Flawless Five': {
        'description': 'Get 5 perfect scores',
        'icon': 'fa-medal',
        'category': 'accuracy',
        'requirement_type': 'perfect_scores',
        'requirement_value': 5,
        'points': 75,
        'color': 'gold'
    },
    'Subject Expert': {
        'description': 'Master a topic with 90%+ accuracy',
        'icon': 'fa-graduation-cap',
        'category': 'mastery',
        'requirement_type': 'topics_mastered',
        'requirement_value': 1,
        'points': 50,
        'color': 'purple'
    },
    'Topic Master': {
        'description': 'Master 3 different topics',
        'icon': 'fa-crown',
        'category': 'mastery',
        'requirement_type': 'topics_mastered',
        'requirement_value': 3,
        'points': 100,
        'color': 'gold'
    },
    'Consistent Excellence': {
        'description': 'Achieve 80%+ on 10 quizzes',
        'icon': 'fa-chart-line',
        'category': 'accuracy',
        'requirement_type': 'high_scores',
        'requirement_value': 10,
        'points': 60,
        'color': 'blue'
    },
    'Quiz Champion': {
        'description': 'Complete 25 quizzes',
        'icon': 'fa-award',
        'category': 'progress',
        'requirement_type': 'quizzes_completed',
        'requirement_value': 25,
        'points': 100,
        'color': 'gold'
    },
    'Math Enthusiast': {
        'description': 'Complete 50 quizzes',
        'icon': 'fa-fire',
        'category': 'progress',
        'requirement_type': 'quizzes_completed',
        'requirement_value': 50,
        'points': 200,
        'color': 'red'
    },
    'Streak Starter': {
        'description': 'Maintain a 3-day streak',
        'icon': 'fa-bolt',
        'category': 'streak',
        'requirement_type': 'streak_days',
        'requirement_value': 3,
        'points': 20,
        'color': 'orange'
    },
    'Week Warrior': {
        'description': 'Maintain a 7-day streak',
        'icon': 'fa-calendar-check',
        'category': 'streak',
        'requirement_type': 'streak_days',
        'requirement_value': 7,
        'points': 50,
        'color': 'orange'
    },
    'Fortnight Fighter': {
        'description': 'Maintain a 14-day streak',
        'icon': 'fa-calendar-alt',
        'category': 'streak',
        'requirement_type': 'streak_days',
        'requirement_value': 14,
        'points': 100,
        'color': 'red'
    },
    'Point Collector': {
        'description': 'Earn 500 total points',
        'icon': 'fa-coins',
        'category': 'progress',
        'requirement_type': 'total_points',
        'requirement_value': 500,
        'points': 25,
        'color': 'gold'
    },
    'Point Hoarder': {
        'description': 'Earn 1000 total points',
        'icon': 'fa-gem',
        'category': 'progress',
        'requirement_type': 'total_points',
        'requirement_value': 1000,
        'points': 50,
        'color': 'purple'
    }
}


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("BADGE AND PROGRESS FIX")
    print("=" * 60)
    
    # =====================================================
    # PART 1: FIX BADGES
    # =====================================================
    print("\n📛 CHECKING BADGES:")
    print("-" * 40)
    
    # Check existing badges
    cursor.execute("SELECT id, name, description, points FROM badges")
    badges = cursor.fetchall()
    
    print(f"Found {len(badges)} badges in database")
    
    badges_fixed = 0
    for badge_id, name, description, points in badges:
        # Check if this badge has undefined values
        needs_update = False
        
        if description is None or description == '' or description == 'undefined':
            needs_update = True
        if points is None or points == 0:
            needs_update = True
            
        if needs_update and name in BADGE_DEFINITIONS:
            badge_def = BADGE_DEFINITIONS[name]
            cursor.execute("""
                UPDATE badges 
                SET description = ?,
                    icon = ?,
                    category = ?,
                    requirement_type = ?,
                    requirement_value = ?,
                    points = ?,
                    color = ?
                WHERE id = ?
            """, (
                badge_def['description'],
                badge_def['icon'],
                badge_def['category'],
                badge_def['requirement_type'],
                badge_def['requirement_value'],
                badge_def['points'],
                badge_def['color'],
                badge_id
            ))
            badges_fixed += 1
            print(f"  ✓ Fixed: {name}")
        elif needs_update:
            print(f"  ⚠ Unknown badge needs fix: {name}")
        else:
            print(f"  ✓ OK: {name} (points: {points})")
    
    if badges_fixed > 0:
        conn.commit()
        print(f"\n✓ Fixed {badges_fixed} badges")
    else:
        print("\n✓ All badges already have correct data")
    
    # =====================================================
    # PART 2: CHECK TOPIC PROGRESS
    # =====================================================
    print("\n📊 CHECKING TOPIC PROGRESS:")
    print("-" * 40)
    
    # Check topic_progress table
    try:
        cursor.execute("SELECT COUNT(*) FROM topic_progress")
        progress_count = cursor.fetchone()[0]
        print(f"Total topic_progress entries: {progress_count}")
        
        # Show sample entries
        cursor.execute("""
            SELECT tp.user_id, u.full_name, tp.topic, tp.difficulty, 
                   tp.attempts, tp.best_percentage, tp.is_mastered
            FROM topic_progress tp
            JOIN users u ON tp.user_id = u.id
            ORDER BY tp.user_id, tp.topic
            LIMIT 20
        """)
        entries = cursor.fetchall()
        
        if entries:
            print("\nSample topic_progress entries:")
            current_user = None
            for user_id, name, topic, diff, attempts, best_pct, mastered in entries:
                if user_id != current_user:
                    print(f"\n  User: {name} (ID: {user_id})")
                    current_user = user_id
                status = "🏆" if mastered else ""
                print(f"    - {topic} ({diff}): {attempts} attempts, best: {best_pct:.1f}% {status}")
        else:
            print("  ⚠ No topic_progress entries found!")
            print("  This means quiz completions may not be updating topic_progress table.")
            
    except sqlite3.OperationalError as e:
        print(f"  ❌ Error: {e}")
        print("  The topic_progress table may not exist!")
    
    # =====================================================
    # PART 3: CHECK QUIZ ATTEMPTS
    # =====================================================
    print("\n📝 CHECKING QUIZ ATTEMPTS:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT u.full_name, qa.topic, qa.difficulty, COUNT(*) as attempts,
               MAX(qa.percentage) as best_pct
        FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        GROUP BY qa.user_id, qa.topic, qa.difficulty
        ORDER BY u.full_name, qa.topic
        LIMIT 30
    """)
    attempts = cursor.fetchall()
    
    if attempts:
        print(f"Found quiz attempts for {len(set(a[0] for a in attempts))} users:")
        current_user = None
        for name, topic, diff, count, best_pct in attempts:
            if name != current_user:
                print(f"\n  {name}:")
                current_user = name
            print(f"    - {topic} ({diff}): {count} attempts, best: {best_pct:.1f}%")
    else:
        print("  No quiz attempts found!")
    
    # =====================================================
    # PART 4: REBUILD TOPIC PROGRESS FROM QUIZ ATTEMPTS
    # =====================================================
    print("\n🔧 REBUILDING TOPIC PROGRESS FROM QUIZ ATTEMPTS:")
    print("-" * 40)
    
    # Get all unique user/topic/difficulty combinations from quiz_attempts
    cursor.execute("""
        SELECT 
            qa.user_id,
            qa.topic,
            qa.difficulty,
            COUNT(*) as attempts,
            MAX(qa.score) as best_score,
            MAX(qa.percentage) as best_percentage,
            SUM(qa.total_questions) as total_questions,
            SUM(qa.score) as total_correct,
            MAX(qa.completed_at) as last_attempt
        FROM quiz_attempts qa
        GROUP BY qa.user_id, qa.topic, qa.difficulty
    """)
    
    quiz_data = cursor.fetchall()
    
    rebuilt = 0
    for row in quiz_data:
        user_id, topic, difficulty, attempts, best_score, best_pct, total_q, total_correct, last_attempt = row
        
        # Calculate if mastered (90%+ with 5+ attempts)
        accuracy = (total_correct / total_q * 100) if total_q > 0 else 0
        is_mastered = 1 if (attempts >= 5 and accuracy >= 90) else 0
        
        # Check if entry exists
        cursor.execute("""
            SELECT id FROM topic_progress 
            WHERE user_id = ? AND topic = ? AND difficulty = ?
        """, (user_id, topic, difficulty))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE topic_progress
                SET attempts = ?,
                    best_score = ?,
                    best_percentage = ?,
                    total_questions_answered = ?,
                    total_correct = ?,
                    is_mastered = ?,
                    last_attempt_at = ?
                WHERE user_id = ? AND topic = ? AND difficulty = ?
            """, (attempts, best_score, best_pct, total_q, total_correct, is_mastered, last_attempt,
                  user_id, topic, difficulty))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO topic_progress 
                (user_id, topic, difficulty, attempts, best_score, best_percentage,
                 total_questions_answered, total_correct, is_mastered, last_attempt_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, topic, difficulty, attempts, best_score, best_pct, 
                  total_q, total_correct, is_mastered, last_attempt))
        
        rebuilt += 1
    
    conn.commit()
    print(f"✓ Rebuilt/updated {rebuilt} topic_progress entries")
    
    # Final check
    cursor.execute("SELECT COUNT(*) FROM topic_progress")
    final_count = cursor.fetchone()[0]
    print(f"✓ Total topic_progress entries now: {final_count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ FIX COMPLETE!")
    print("=" * 60)
    print("""
Next steps:
1. Reload the web app on PythonAnywhere
2. Go to /student/badges page
3. Badges should now show correct descriptions and points
4. Topic Progress should show all completed quizzes
""")


if __name__ == '__main__':
    main()
