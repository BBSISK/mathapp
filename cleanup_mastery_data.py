#!/usr/bin/env python3
"""
Database Cleanup Script for Mastery Tracking
Fixes any inconsistent data in quiz_attempts and topic_progress tables
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, QuizAttempt, TopicProgress, UserStats

def cleanup_database():
    """Clean up and normalize database entries"""
    with app.app_context():
        print("=" * 70)
        print("DATABASE CLEANUP - MASTERY TRACKING")
        print("=" * 70)
        print()
        
        # Valid values
        valid_topics = [
            'arithmetic', 'fractions', 'decimals', 'multiplication_division',
            'bodmas', 'functions', 'sets', 'probability',
            'complex_numbers_intro', 'complex_numbers_expanded'
        ]
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        
        # 1. Check and fix quiz_attempts
        print("1. Checking quiz_attempts table...")
        attempts = QuizAttempt.query.all()
        fixed_attempts = 0
        invalid_attempts = []
        
        for attempt in attempts:
            changed = False
            
            # Normalize topic
            if attempt.topic:
                normalized_topic = attempt.topic.lower().strip()
                if normalized_topic != attempt.topic:
                    print(f"   Fixing topic: '{attempt.topic}' -> '{normalized_topic}'")
                    attempt.topic = normalized_topic
                    changed = True
                
                # Check if valid
                if normalized_topic not in valid_topics:
                    invalid_attempts.append(f"Invalid topic '{normalized_topic}' in attempt ID {attempt.id}")
            
            # Normalize difficulty
            if attempt.difficulty:
                normalized_difficulty = attempt.difficulty.lower().strip()
                if normalized_difficulty != attempt.difficulty:
                    print(f"   Fixing difficulty: '{attempt.difficulty}' -> '{normalized_difficulty}'")
                    attempt.difficulty = normalized_difficulty
                    changed = True
                
                # Check if valid
                if normalized_difficulty not in valid_difficulties:
                    invalid_attempts.append(f"Invalid difficulty '{normalized_difficulty}' in attempt ID {attempt.id}")
            
            if changed:
                fixed_attempts += 1
        
        if fixed_attempts > 0:
            db.session.commit()
            print(f"   ✓ Fixed {fixed_attempts} quiz attempts")
        else:
            print(f"   ✓ All quiz attempts are clean")
        
        if invalid_attempts:
            print(f"   ⚠️  WARNING: Found {len(invalid_attempts)} invalid attempts:")
            for msg in invalid_attempts[:10]:  # Show first 10
                print(f"      - {msg}")
        print()
        
        # 2. Check and fix topic_progress
        print("2. Checking topic_progress table...")
        progress_records = TopicProgress.query.all()
        fixed_progress = 0
        invalid_progress = []
        
        for progress in progress_records:
            changed = False
            
            # Normalize topic
            if progress.topic:
                normalized_topic = progress.topic.lower().strip()
                if normalized_topic != progress.topic:
                    print(f"   Fixing topic: '{progress.topic}' -> '{normalized_topic}'")
                    progress.topic = normalized_topic
                    changed = True
                
                if normalized_topic not in valid_topics:
                    invalid_progress.append(f"Invalid topic '{normalized_topic}' in progress ID {progress.id}")
            
            # Normalize difficulty
            if progress.difficulty:
                normalized_difficulty = progress.difficulty.lower().strip()
                if normalized_difficulty != progress.difficulty:
                    print(f"   Fixing difficulty: '{progress.difficulty}' -> '{normalized_difficulty}'")
                    progress.difficulty = normalized_difficulty
                    changed = True
                
                if normalized_difficulty not in valid_difficulties:
                    invalid_progress.append(f"Invalid difficulty '{normalized_difficulty}' in progress ID {progress.id}")
            
            if changed:
                fixed_progress += 1
        
        if fixed_progress > 0:
            db.session.commit()
            print(f"   ✓ Fixed {fixed_progress} progress records")
        else:
            print(f"   ✓ All progress records are clean")
        
        if invalid_progress:
            print(f"   ⚠️  WARNING: Found {len(invalid_progress)} invalid progress records:")
            for msg in invalid_progress[:10]:
                print(f"      - {msg}")
        print()
        
        # 3. Recalculate topic progress statistics
        print("3. Recalculating topic progress statistics...")
        recalculated = 0
        
        for progress in progress_records:
            # Recalculate accuracy
            if progress.total_questions_answered > 0:
                old_accuracy = (progress.total_correct / progress.total_questions_answered) * 100 if progress.total_questions_answered > 0 else 0
                
                # Check mastery status (90%+ accuracy with 5+ attempts)
                should_be_mastered = (progress.attempts >= 5 and old_accuracy >= 90)
                
                if progress.is_mastered != should_be_mastered:
                    print(f"   Updating mastery for {progress.topic}/{progress.difficulty}: {progress.is_mastered} -> {should_be_mastered}")
                    progress.is_mastered = should_be_mastered
                    recalculated += 1
        
        if recalculated > 0:
            db.session.commit()
            print(f"   ✓ Recalculated {recalculated} mastery statuses")
        else:
            print(f"   ✓ All mastery statuses are correct")
        print()
        
        # 4. Update user stats - topics_mastered count
        print("4. Updating user statistics...")
        users_updated = 0
        
        all_users = UserStats.query.all()
        for user_stats in all_users:
            # Count mastered topics for this user
            actual_mastered = TopicProgress.query.filter_by(
                user_id=user_stats.user_id,
                is_mastered=True
            ).count()
            
            if user_stats.topics_mastered != actual_mastered:
                print(f"   Updating user {user_stats.user_id}: {user_stats.topics_mastered} -> {actual_mastered} mastered topics")
                user_stats.topics_mastered = actual_mastered
                users_updated += 1
        
        if users_updated > 0:
            db.session.commit()
            print(f"   ✓ Updated {users_updated} user statistics")
        else:
            print(f"   ✓ All user statistics are correct")
        print()
        
        # 5. Summary
        print("=" * 70)
        print("CLEANUP SUMMARY")
        print("=" * 70)
        print(f"Quiz attempts fixed: {fixed_attempts}")
        print(f"Progress records fixed: {fixed_progress}")
        print(f"Mastery statuses recalculated: {recalculated}")
        print(f"User statistics updated: {users_updated}")
        
        if invalid_attempts or invalid_progress:
            print()
            print(f"⚠️  WARNING: Found invalid data that needs manual review:")
            print(f"   - {len(invalid_attempts)} invalid quiz attempts")
            print(f"   - {len(invalid_progress)} invalid progress records")
            print()
            print("   These may be from old test data or diagnostic tests.")
            print("   Review and delete manually if needed.")
        
        print()
        print("=" * 70)
        print("✓ CLEANUP COMPLETE!")
        print("=" * 70)

if __name__ == "__main__":
    cleanup_database()
