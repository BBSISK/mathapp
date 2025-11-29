#!/usr/bin/env python3
"""
Recalculate Mastery Data for All Users

This script:
1. Recalculates best scores for all registered users from quiz_attempts
2. Updates TopicProgress records with correct best_score and is_mastered (>80%)
3. Updates UserStats.topics_mastered counts
4. Recalculates mastery for guest_code users from guest_quiz_attempts

Run on PythonAnywhere:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python recalculate_mastery.py
"""

import sys
import os

# Add the app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app, db
from sqlalchemy import text

def recalculate_registered_users():
    """Recalculate mastery for all registered users"""
    print("\n" + "="*60)
    print("RECALCULATING MASTERY FOR REGISTERED USERS")
    print("="*60)
    
    # Get all users with quiz attempts
    users_query = text("""
        SELECT DISTINCT user_id FROM quiz_attempts WHERE user_id IS NOT NULL
    """)
    users = db.session.execute(users_query).fetchall()
    print(f"\nFound {len(users)} users with quiz attempts")
    
    topics = [
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems', 'bodmas', 'introductory_algebra', 'functions', 
        'patterns', 'solving_equations', 'simplifying_expressions', 
        'expanding_factorising', 'probability', 'descriptive_statistics', 
        'sets', 'surds', 'complex_numbers_intro', 'complex_numbers_expanded'
    ]
    difficulties = ['beginner', 'intermediate', 'advanced']
    
    total_updated = 0
    total_mastered = 0
    
    for (user_id,) in users:
        # Get best scores for this user
        scores_query = text("""
            SELECT topic, difficulty, MAX(percentage) as best_score
            FROM quiz_attempts
            WHERE user_id = :user_id
            GROUP BY topic, difficulty
        """)
        scores = db.session.execute(scores_query, {'user_id': user_id}).fetchall()
        
        # Build lookup
        best_scores = {}
        for topic, difficulty, best_score in scores:
            if topic not in best_scores:
                best_scores[topic] = {}
            best_scores[topic][difficulty] = best_score or 0
        
        # Count mastered topics (all 3 difficulties >80%)
        topics_mastered = 0
        
        for topic in topics:
            topic_scores = best_scores.get(topic, {})
            mastered_count = sum(1 for d in difficulties if topic_scores.get(d, 0) > 80)
            
            if mastered_count == 3:
                topics_mastered += 1
            
            # Update TopicProgress for each difficulty
            for difficulty in difficulties:
                best_score = topic_scores.get(difficulty, 0)
                is_mastered = best_score > 80
                
                if best_score > 0:
                    # Check if TopicProgress exists
                    check_query = text("""
                        SELECT id, best_score, is_mastered FROM topic_progress
                        WHERE user_id = :user_id AND topic = :topic AND difficulty = :difficulty
                    """)
                    existing = db.session.execute(check_query, {
                        'user_id': user_id, 
                        'topic': topic, 
                        'difficulty': difficulty
                    }).fetchone()
                    
                    if existing:
                        # Update if needed
                        if existing[1] != best_score or existing[2] != is_mastered:
                            update_query = text("""
                                UPDATE topic_progress 
                                SET best_score = :best_score, is_mastered = :is_mastered
                                WHERE id = :id
                            """)
                            db.session.execute(update_query, {
                                'id': existing[0],
                                'best_score': int(best_score),
                                'is_mastered': is_mastered
                            })
                            total_updated += 1
                            if is_mastered:
                                total_mastered += 1
                    else:
                        # Insert new record
                        insert_query = text("""
                            INSERT INTO topic_progress (user_id, topic, difficulty, best_score, is_mastered, attempts)
                            VALUES (:user_id, :topic, :difficulty, :best_score, :is_mastered, 1)
                        """)
                        db.session.execute(insert_query, {
                            'user_id': user_id,
                            'topic': topic,
                            'difficulty': difficulty,
                            'best_score': int(best_score),
                            'is_mastered': is_mastered
                        })
                        total_updated += 1
                        if is_mastered:
                            total_mastered += 1
        
        # Update UserStats.topics_mastered
        update_stats_query = text("""
            UPDATE user_stats SET topics_mastered = :topics_mastered
            WHERE user_id = :user_id
        """)
        db.session.execute(update_stats_query, {
            'user_id': user_id,
            'topics_mastered': topics_mastered
        })
    
    db.session.commit()
    print(f"✓ Updated {total_updated} TopicProgress records")
    print(f"✓ Found {total_mastered} mastered topic/difficulty combinations")
    print(f"✓ Updated topics_mastered count for {len(users)} users")


def recalculate_guest_users():
    """Recalculate mastery summary for guest_code users"""
    print("\n" + "="*60)
    print("RECALCULATING MASTERY FOR GUEST CODE USERS")
    print("="*60)
    
    # Check if guest_quiz_attempts table exists
    try:
        check_query = text("SELECT COUNT(*) FROM guest_quiz_attempts")
        count = db.session.execute(check_query).fetchone()[0]
        print(f"\nFound {count} total guest quiz attempts")
    except Exception as e:
        print(f"guest_quiz_attempts table not found or empty: {e}")
        return
    
    # Get all guest codes with attempts
    guests_query = text("""
        SELECT DISTINCT guest_code FROM guest_quiz_attempts WHERE guest_code IS NOT NULL
    """)
    guests = db.session.execute(guests_query).fetchall()
    print(f"Found {len(guests)} guest codes with quiz attempts")
    
    difficulties = ['beginner', 'intermediate', 'advanced']
    
    mastery_summary = {
        'total_guests': len(guests),
        'guests_with_mastery': 0,
        'total_mastered_difficulties': 0,
        'total_mastered_topics': 0
    }
    
    for (guest_code,) in guests:
        # Get best scores for this guest
        scores_query = text("""
            SELECT topic, difficulty, 
                   MAX(CAST(score AS FLOAT) / total_questions * 100) as best_score
            FROM guest_quiz_attempts
            WHERE guest_code = :guest_code
            GROUP BY topic, difficulty
        """)
        scores = db.session.execute(scores_query, {'guest_code': guest_code}).fetchall()
        
        # Count mastery
        guest_mastered_diffs = 0
        topics_data = {}
        
        for topic, difficulty, best_score in scores:
            if topic not in topics_data:
                topics_data[topic] = {}
            topics_data[topic][difficulty] = best_score or 0
            
            if best_score and best_score > 80:
                guest_mastered_diffs += 1
        
        # Count fully mastered topics
        guest_mastered_topics = 0
        for topic, diffs in topics_data.items():
            mastered_count = sum(1 for d in difficulties if diffs.get(d, 0) > 80)
            if mastered_count == 3:
                guest_mastered_topics += 1
        
        if guest_mastered_diffs > 0:
            mastery_summary['guests_with_mastery'] += 1
            mastery_summary['total_mastered_difficulties'] += guest_mastered_diffs
            mastery_summary['total_mastered_topics'] += guest_mastered_topics
    
    print(f"\n✓ Guest Mastery Summary:")
    print(f"  - {mastery_summary['guests_with_mastery']} guests have at least one mastered difficulty")
    print(f"  - {mastery_summary['total_mastered_difficulties']} total mastered difficulties across all guests")
    print(f"  - {mastery_summary['total_mastered_topics']} total fully mastered topics across all guests")
    
    # Note: Guest mastery is calculated dynamically, no storage needed
    print("\n  (Guest mastery is calculated on-the-fly from guest_quiz_attempts)")


def show_mastery_report():
    """Show a summary report of mastery across the system"""
    print("\n" + "="*60)
    print("MASTERY SUMMARY REPORT")
    print("="*60)
    
    # Registered users mastery by topic
    report_query = text("""
        SELECT topic, difficulty, 
               COUNT(*) as attempts,
               SUM(CASE WHEN percentage > 80 THEN 1 ELSE 0 END) as mastered
        FROM quiz_attempts
        WHERE user_id IS NOT NULL
        GROUP BY topic, difficulty
        ORDER BY topic, difficulty
    """)
    
    results = db.session.execute(report_query).fetchall()
    
    print("\nRegistered Users - Mastery by Topic/Difficulty:")
    print("-" * 60)
    current_topic = None
    for topic, difficulty, attempts, mastered in results:
        if topic != current_topic:
            if current_topic is not None:
                print()
            print(f"\n{topic}:")
            current_topic = topic
        pct = (mastered / attempts * 100) if attempts > 0 else 0
        print(f"  {difficulty:15} - {mastered:3}/{attempts:3} mastered ({pct:.1f}%)")
    
    # Top performers
    top_query = text("""
        SELECT u.username, COUNT(DISTINCT qa.topic || qa.difficulty) as mastered_count
        FROM users u
        JOIN quiz_attempts qa ON u.id = qa.user_id
        WHERE qa.percentage > 80
        GROUP BY u.id, u.username
        ORDER BY mastered_count DESC
        LIMIT 10
    """)
    
    top_users = db.session.execute(top_query).fetchall()
    
    print("\n\nTop 10 Users by Mastered Difficulties:")
    print("-" * 40)
    for i, (username, count) in enumerate(top_users, 1):
        print(f"  {i:2}. {username:20} - {count} mastered")


def main():
    print("\n" + "="*60)
    print("  MASTERY RECALCULATION SCRIPT")
    print("  AgentMath.app")
    print("="*60)
    
    with app.app_context():
        # Ask for confirmation
        print("\nThis script will:")
        print("  1. Recalculate best scores for all registered users")
        print("  2. Update TopicProgress records with mastery status")
        print("  3. Update UserStats.topics_mastered counts")
        print("  4. Show mastery summary for guest users")
        print("  5. Generate a mastery report")
        
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        try:
            recalculate_registered_users()
            recalculate_guest_users()
            show_mastery_report()
            
            print("\n" + "="*60)
            print("✅ MASTERY RECALCULATION COMPLETE!")
            print("="*60)
            print("\nUsers will now see updated trophies and progress indicators.")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == '__main__':
    main()
