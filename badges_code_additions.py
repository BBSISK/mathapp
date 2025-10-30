# ==================== BADGES & PROGRESS TRACKING MODELS ====================
# INSERT THIS CODE AFTER QuizAttempt MODEL (around line 217, before DECORATORS section)

class Badge(db.Model):
    """Badge definitions"""
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # beginner, progress, accuracy, streak, mastery
    requirement_type = db.Column(db.String(50), nullable=False)
    requirement_value = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=10)
    color = db.Column(db.String(50), default='blue')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'points': self.points,
            'color': self.color
        }

class UserBadge(db.Model):
    """Tracks badges earned by users"""
    __tablename__ = 'user_badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)

    badge = db.relationship('Badge', backref='earned_by')
    user = db.relationship('User', backref='earned_badges')

    def to_dict(self):
        return {
            'id': self.id,
            'badge': self.badge.to_dict(),
            'earned_at': self.earned_at.isoformat(),
            'progress': self.progress
        }

class UserStats(db.Model):
    """Overall user statistics and progress"""
    __tablename__ = 'user_stats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_quizzes = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    current_streak_days = db.Column(db.Integer, default=0)
    longest_streak_days = db.Column(db.Integer, default=0)
    last_quiz_date = db.Column(db.Date)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    topics_mastered = db.Column(db.Integer, default=0)
    perfect_scores = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='stats', uselist=False)

    def to_dict(self):
        overall_accuracy = 0
        if self.total_questions_answered > 0:
            overall_accuracy = round((self.total_correct_answers / self.total_questions_answered) * 100, 1)
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_quizzes': self.total_quizzes,
            'total_questions_answered': self.total_questions_answered,
            'total_correct_answers': self.total_correct_answers,
            'overall_accuracy': overall_accuracy,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'last_quiz_date': self.last_quiz_date.isoformat() if self.last_quiz_date else None,
            'total_points': self.total_points,
            'level': self.level,
            'topics_mastered': self.topics_mastered,
            'perfect_scores': self.perfect_scores,
            'updated_at': self.updated_at.isoformat()
        }

class TopicProgress(db.Model):
    """Per-topic progress tracking"""
    __tablename__ = 'topic_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    best_percentage = db.Column(db.Float, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    is_mastered = db.Column(db.Boolean, default=False)
    last_attempt_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id', 'topic', 'difficulty', name='unique_topic_progress'),)

    user = db.relationship('User', backref='topic_progress')

    def to_dict(self):
        accuracy = 0
        if self.total_questions_answered > 0:
            accuracy = round((self.total_correct / self.total_questions_answered) * 100, 1)
        
        return {
            'id': self.id,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'attempts': self.attempts,
            'best_score': self.best_score,
            'best_percentage': self.best_percentage,
            'accuracy': accuracy,
            'is_mastered': self.is_mastered,
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None
        }


# ==================== BADGES HELPER FUNCTIONS ====================
# INSERT THIS CODE BEFORE THE ROUTES SECTION (after decorators, before @app.route)

def initialize_user_stats(user_id):
    """Create initial stats record for a user if it doesn't exist"""
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.session.add(stats)
        db.session.commit()
    return stats

def update_user_stats_after_quiz(user_id, quiz_attempt):
    """Update user stats after completing a quiz"""
    from datetime import date
    
    stats = initialize_user_stats(user_id)
    
    # Update basic stats
    stats.total_quizzes += 1
    stats.total_questions_answered += quiz_attempt.total_questions
    stats.total_correct_answers += quiz_attempt.score
    
    # Check for perfect score
    if quiz_attempt.percentage == 100:
        stats.perfect_scores += 1
    
    # Update streak
    today = date.today()
    if stats.last_quiz_date:
        days_diff = (today - stats.last_quiz_date).days
        if days_diff == 1:
            # Consecutive day
            stats.current_streak_days += 1
        elif days_diff > 1:
            # Streak broken
            stats.current_streak_days = 1
        # If same day, don't change streak
    else:
        # First quiz ever
        stats.current_streak_days = 1
    
    # Update longest streak
    if stats.current_streak_days > stats.longest_streak_days:
        stats.longest_streak_days = stats.current_streak_days
    
    stats.last_quiz_date = today
    
    # Calculate level (every 100 points = 1 level)
    stats.level = (stats.total_points // 100) + 1
    
    stats.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Update topic progress
    update_topic_progress(user_id, quiz_attempt)
    
    # Check for new badges
    newly_earned = check_and_award_badges(user_id)
    
    return stats, newly_earned

def update_topic_progress(user_id, quiz_attempt):
    """Update progress for a specific topic/difficulty"""
    progress = TopicProgress.query.filter_by(
        user_id=user_id,
        topic=quiz_attempt.topic,
        difficulty=quiz_attempt.difficulty
    ).first()
    
    if not progress:
        progress = TopicProgress(
            user_id=user_id,
            topic=quiz_attempt.topic,
            difficulty=quiz_attempt.difficulty
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
    
    # Check for mastery (80%+ accuracy over 3+ attempts)
    if progress.attempts >= 3:
        accuracy = (progress.total_correct / progress.total_questions_answered) * 100
        if accuracy >= 80:
            progress.is_mastered = True
            
            # Check if all 3 difficulties are mastered for this topic
            check_topic_mastery(user_id, quiz_attempt.topic)
    
    progress.last_attempt_at = datetime.utcnow()
    db.session.commit()

def check_topic_mastery(user_id, topic):
    """Check if user has mastered all difficulties for a topic"""
    difficulties = ['beginner', 'intermediate', 'advanced']
    mastered_count = TopicProgress.query.filter_by(
        user_id=user_id,
        topic=topic,
        is_mastered=True
    ).count()
    
    if mastered_count == 3:
        # User mastered all 3 difficulties for this topic
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if stats:
            # Count unique topics mastered
            mastered_topics = db.session.query(TopicProgress.topic).filter_by(
                user_id=user_id,
                is_mastered=True
            ).group_by(TopicProgress.topic).having(
                db.func.count(TopicProgress.difficulty) == 3
            ).count()
            
            stats.topics_mastered = mastered_topics
            db.session.commit()

def check_and_award_badges(user_id):
    """Check if user earned any new badges and award them"""
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        return []
    
    all_badges = Badge.query.all()
    newly_earned = []
    
    for badge in all_badges:
        # Check if user already has this badge
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
        if existing:
            continue
        
        # Check if requirements are met
        earned = False
        
        if badge.requirement_type == 'quizzes_completed':
            earned = stats.total_quizzes >= badge.requirement_value
        
        elif badge.requirement_type == 'quiz_percentage':
            # Check if any quiz met the percentage
            high_score_attempt = QuizAttempt.query.filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.percentage >= badge.requirement_value
            ).first()
            earned = high_score_attempt is not None
        
        elif badge.requirement_type == 'perfect_scores':
            earned = stats.perfect_scores >= badge.requirement_value
        
        elif badge.requirement_type == 'high_scores':
            # Check for 90%+ scores
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
                progress=100
            )
            db.session.add(user_badge)
            
            # Award points
            stats.total_points += badge.points
            
            newly_earned.append(badge.to_dict())
    
    if newly_earned:
        db.session.commit()
    
    return newly_earned


# ==================== BADGES API ROUTES ====================
# INSERT THESE ROUTES AFTER THE EXISTING QUIZ ROUTES (around line 680, after /api/submit-quiz)

@app.route('/api/student/badges')
@login_required
@approved_required
def get_student_badges():
    """Get all badges (earned and available) for the current student"""
    user_id = session['user_id']
    
    # Get all badges
    all_badges = Badge.query.all()
    
    # Get earned badges
    earned_badges = UserBadge.query.filter_by(user_id=user_id).all()
    earned_badge_ids = {ub.badge_id for ub in earned_badges}
    
    # Get user stats for progress on unearned badges
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = initialize_user_stats(user_id)
    
    badges_data = {
        'earned': [],
        'available': [],
        'total_points': stats.total_points,
        'level': stats.level
    }
    
    for badge in all_badges:
        badge_dict = badge.to_dict()
        
        if badge.id in earned_badge_ids:
            # Badge is earned
            user_badge = next(ub for ub in earned_badges if ub.badge_id == badge.id)
            badge_dict['earned_at'] = user_badge.earned_at.isoformat()
            badge_dict['progress'] = 100
            badges_data['earned'].append(badge_dict)
        else:
            # Badge is available - calculate progress
            progress = 0
            
            if badge.requirement_type == 'quizzes_completed':
                progress = min(100, int((stats.total_quizzes / badge.requirement_value) * 100))
            elif badge.requirement_type == 'perfect_scores':
                progress = min(100, int((stats.perfect_scores / badge.requirement_value) * 100))
            elif badge.requirement_type == 'streak_days':
                progress = min(100, int((stats.current_streak_days / badge.requirement_value) * 100))
            elif badge.requirement_type == 'topics_mastered':
                progress = min(100, int((stats.topics_mastered / badge.requirement_value) * 100))
            elif badge.requirement_type == 'high_scores':
                high_scores = QuizAttempt.query.filter(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.percentage >= 90
                ).count()
                progress = min(100, int((high_scores / badge.requirement_value) * 100))
            
            badge_dict['progress'] = progress
            badge_dict['earned_at'] = None
            badges_data['available'].append(badge_dict)
    
    return jsonify(badges_data)

@app.route('/api/student/stats')
@login_required
@approved_required
def get_student_stats():
    """Get detailed statistics for the current student"""
    user_id = session['user_id']
    
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = initialize_user_stats(user_id)
    
    # Get topic progress
    topic_progress = TopicProgress.query.filter_by(user_id=user_id).all()
    
    # Get recent quiz attempts
    recent_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(
        QuizAttempt.completed_at.desc()
    ).limit(10).all()
    
    return jsonify({
        'stats': stats.to_dict(),
        'topic_progress': [tp.to_dict() for tp in topic_progress],
        'recent_attempts': [qa.to_dict() for qa in recent_attempts]
    })

@app.route('/api/student/progress/<topic>')
@login_required
@approved_required
def get_topic_progress(topic):
    """Get progress for a specific topic"""
    user_id = session['user_id']
    
    progress = TopicProgress.query.filter_by(user_id=user_id, topic=topic).all()
    
    return jsonify({
        'topic': topic,
        'progress': [p.to_dict() for p in progress]
    })

@app.route('/api/class/<int:class_id>/leaderboard')
@login_required
@approved_required
def get_class_leaderboard(class_id):
    """Get leaderboard for a class (optional feature)"""
    # Verify user has access to this class
    user = User.query.get(session['user_id'])
    
    if user.role == 'teacher':
        # Verify teacher owns this class
        class_obj = Class.query.filter_by(id=class_id, teacher_id=user.id).first()
        if not class_obj:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user.role == 'student':
        # Verify student is in this class
        enrollment = ClassEnrollment.query.filter_by(class_id=class_id, student_id=user.id).first()
        if not enrollment:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all students in class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    student_ids = [e.student_id for e in enrollments]
    
    # Get stats for all students
    students_stats = []
    for student_id in student_ids:
        student = User.query.get(student_id)
        stats = UserStats.query.filter_by(user_id=student_id).first()
        
        if stats:
            students_stats.append({
                'student_name': student.full_name,
                'student_id': student_id,
                'total_points': stats.total_points,
                'level': stats.level,
                'total_quizzes': stats.total_quizzes,
                'current_streak': stats.current_streak_days,
                'badges_earned': UserBadge.query.filter_by(user_id=student_id).count()
            })
    
    # Sort by total points
    students_stats.sort(key=lambda x: x['total_points'], reverse=True)
    
    return jsonify({
        'class_id': class_id,
        'leaderboard': students_stats
    })


# ==================== MODIFIED SUBMIT QUIZ ROUTE ====================
# REPLACE THE EXISTING /api/submit-quiz ROUTE WITH THIS VERSION (around line 670)

@app.route('/api/submit-quiz', methods=['POST'])
@login_required
@approved_required
def submit_quiz_with_badges():
    """Submit quiz and update stats/badges"""
    data = request.json
    
    # Create quiz attempt
    quiz_attempt = QuizAttempt(
        user_id=session['user_id'],
        topic=data['topic'],
        difficulty=data['difficulty'],
        score=data['score'],
        total_questions=data['total_questions'],
        percentage=data['percentage'],
        time_taken=data.get('time_taken')
    )
    
    db.session.add(quiz_attempt)
    db.session.commit()
    
    # Update stats and check for badges
    stats, newly_earned_badges = update_user_stats_after_quiz(session['user_id'], quiz_attempt)
    
    return jsonify({
        'message': 'Quiz submitted successfully',
        'attempt_id': quiz_attempt.id,
        'stats': stats.to_dict(),
        'newly_earned_badges': newly_earned_badges
    })
