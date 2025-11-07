"""
Fix Existing Students - Award Missing Points and Badges

This script:
1. Recalculates points for all past quizzes
2. Awards any badges that should have been earned
3. Updates topic progress
4. Fixes stats

Run this ONCE after deploying the fixed app.py
"""

from app import app, db, User, UserStats, QuizAttempt, Badge, UserBadge, TopicProgress
from datetime import datetime

def recalculate_all_student_data():
    """Recalculate points and badges for all students"""
    
    with app.app_context():
        students = User.query.filter_by(role='student').all()
        print(f"\n🔍 Found {len(students)} students to fix\n")
        
        for student in students:
            print(f"Processing: {student.full_name} ({student.email})")
            
            # Get or create stats
            stats = UserStats.query.filter_by(user_id=student.id).first()
            if not stats:
                stats = UserStats(
                    user_id=student.id,
                    total_quizzes=0,
                    total_questions_answered=0,
                    total_correct_answers=0,
                    current_streak_days=0,
                    longest_streak_days=0,
                    total_points=0,
                    level=1,
                    topics_mastered=0,
                    perfect_scores=0
                )
                db.session.add(stats)
                print("  ✅ Created UserStats")
            
            # Get all past quizzes
            quizzes = QuizAttempt.query.filter_by(user_id=student.id).order_by(QuizAttempt.completed_at).all()
            
            if not quizzes:
                print("  ℹ️  No quizzes yet")
                continue
            
            # Reset stats to recalculate from scratch
            old_points = stats.total_points
            stats.total_quizzes = 0
            stats.total_questions_answered = 0
            stats.total_correct_answers = 0
            stats.total_points = 0
            stats.perfect_scores = 0
            stats.current_streak_days = 0
            stats.longest_streak_days = 0
            stats.last_quiz_date = None
            
            # Recalculate everything
            from datetime import date
            quiz_dates = set()
            
            for quiz in quizzes:
                # Update counts
                stats.total_quizzes += 1
                stats.total_questions_answered += quiz.total_questions
                stats.total_correct_answers += quiz.score
                
                # Award points (5 base + 0-10 based on percentage)
                base_points = 5
                performance_bonus = int(quiz.percentage / 10)
                quiz_points = base_points + performance_bonus
                stats.total_points += quiz_points
                
                # Count perfect scores
                if quiz.percentage == 100:
                    stats.perfect_scores += 1
                
                # Track dates for streak
                quiz_date = quiz.completed_at.date()
                quiz_dates.add(quiz_date)
                
                # Update topic progress
                update_or_create_topic_progress(student.id, quiz)
            
            # Calculate streak
            if quiz_dates:
                sorted_dates = sorted(quiz_dates)
                stats.last_quiz_date = sorted_dates[-1]
                
                # Calculate current streak
                current_streak = 1
                today = date.today()
                check_date = today
                
                # Check if there's a quiz today or yesterday to have an active streak
                if sorted_dates[-1] >= today - timedelta(days=1):
                    current_streak = 1
                    for i in range(len(sorted_dates) - 2, -1, -1):
                        if (sorted_dates[i+1] - sorted_dates[i]).days == 1:
                            current_streak += 1
                        else:
                            break
                else:
                    current_streak = 0
                
                stats.current_streak_days = current_streak
                
                # Calculate longest streak
                longest = 1
                current = 1
                for i in range(1, len(sorted_dates)):
                    if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                        current += 1
                        longest = max(longest, current)
                    else:
                        current = 1
                stats.longest_streak_days = longest
            
            # Update topics mastered count
            mastered_count = TopicProgress.query.filter_by(
                user_id=student.id,
                is_mastered=True
            ).count()
            stats.topics_mastered = mastered_count
            
            # Calculate level
            stats.level = (stats.total_points // 100) + 1
            stats.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"  📊 Stats updated:")
            print(f"     - Quizzes: {stats.total_quizzes}")
            print(f"     - Points: {old_points} → {stats.total_points} (+{stats.total_points - old_points})")
            print(f"     - Level: {stats.level}")
            print(f"     - Perfect Scores: {stats.perfect_scores}")
            print(f"     - Topics Mastered: {stats.topics_mastered}")
            print(f"     - Streak: {stats.current_streak_days} days (longest: {stats.longest_streak_days})")
            
            # Award any missing badges
            award_missing_badges(student.id, stats)
            
            print()
        
        print("✅ All students processed!\n")

def update_or_create_topic_progress(user_id, quiz_attempt):
    """Update or create topic progress for a quiz"""
    progress = TopicProgress.query.filter_by(
        user_id=user_id,
        topic=quiz_attempt.topic,
        difficulty=quiz_attempt.difficulty
    ).first()
    
    if not progress:
        progress = TopicProgress(
            user_id=user_id,
            topic=quiz_attempt.topic,
            difficulty=quiz_attempt.difficulty,
            attempts=0,
            best_score=0,
            best_percentage=0,
            total_questions_answered=0,
            total_correct=0,
            is_mastered=False
        )
        db.session.add(progress)
    
    progress.attempts += 1
    progress.total_questions_answered += quiz_attempt.total_questions
    progress.total_correct += quiz_attempt.score
    
    # Update best score
    if quiz_attempt.score > progress.best_score:
        progress.best_score = quiz_attempt.score
    if quiz_attempt.percentage > progress.best_percentage:
        progress.best_percentage = quiz_attempt.percentage
    
    progress.last_attempt_at = quiz_attempt.completed_at
    
    # Check for mastery (90%+ accuracy with 5+ attempts)
    if progress.attempts >= 5:
        accuracy = (progress.total_correct / progress.total_questions_answered) * 100
        if accuracy >= 90:
            progress.is_mastered = True

def award_missing_badges(user_id, stats):
    """Award any badges the student should have earned"""
    # Get all badges
    all_badges = Badge.query.all()
    
    # Get already earned badges
    user_badges = UserBadge.query.filter_by(user_id=user_id).all()
    earned_badge_ids = {ub.badge_id for ub in user_badges}
    
    # FIRST: Add back points from badges already earned
    points_from_existing_badges = 0
    for user_badge in user_badges:
        badge = Badge.query.get(user_badge.badge_id)
        if badge:
            stats.total_points += badge.points
            points_from_existing_badges += badge.points
    
    if points_from_existing_badges > 0:
        print(f"  ✅ Added {points_from_existing_badges} points from {len(user_badges)} existing badges")
    
    newly_earned = []
    points_from_new_badges = 0
    
    for badge in all_badges:
        # Skip if already earned
        if badge.id in earned_badge_ids:
            continue
        
        # Check if requirements are met
        earned = False
        
        if badge.requirement_type == 'quizzes_completed':
            earned = stats.total_quizzes >= badge.requirement_value
        elif badge.requirement_type == 'perfect_scores':
            earned = stats.perfect_scores >= badge.requirement_value
        elif badge.requirement_type == 'high_scores':
            high_scores = QuizAttempt.query.filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.percentage >= 90
            ).count()
            earned = high_scores >= badge.requirement_value
        elif badge.requirement_type == 'streak_days':
            earned = stats.current_streak_days >= badge.requirement_value
        elif badge.requirement_type == 'topics_mastered':
            earned = stats.topics_mastered >= badge.requirement_value
        
        if earned:
            # Award the badge
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                progress=100,
                earned_at=datetime.utcnow()
            )
            db.session.add(user_badge)
            
            # Award points
            stats.total_points += badge.points
            points_from_new_badges += badge.points
            
            newly_earned.append(badge.name)
    
    if newly_earned:
        # Update level after badge points
        stats.level = (stats.total_points // 100) + 1
        db.session.commit()
        print(f"  🏆 Awarded {len(newly_earned)} NEW badges (+{points_from_new_badges} points):")
        for badge_name in newly_earned:
            print(f"     - {badge_name}")
    else:
        print(f"  ℹ️  No new badges to award")
    
    # Always update level and commit after adding existing badge points
    if points_from_existing_badges > 0:
        stats.level = (stats.total_points // 100) + 1
        db.session.commit()

if __name__ == '__main__':
    from datetime import timedelta
    
    print("\n" + "="*60)
    print("🔧 FIXING EXISTING STUDENT DATA")
    print("="*60)
    print("\nThis will:")
    print("  1. Recalculate all points from past quizzes")
    print("  2. Award any badges that should have been earned")
    print("  3. Update topic progress and mastery")
    print("  4. Fix stats and streaks")
    print("\n" + "="*60 + "\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        recalculate_all_student_data()
        print("✅ DONE! Students should now see their points and badges.")
        print("   Tell students to refresh their browser (Ctrl+F5)")
    else:
        print("❌ Cancelled")
