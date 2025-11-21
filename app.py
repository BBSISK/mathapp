from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os
import random
import re
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/bbsisk/mathapp/instance/mathquiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration for guest mode
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'admin'
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    classes_enrolled = db.relationship('ClassEnrollment', backref='student', lazy=True)
    classes_teaching = db.relationship('Class', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat()
        }

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = db.relationship('ClassEnrollment', backref='class_obj', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'student_count': len(self.enrollments),
            'created_at': self.created_at.isoformat()
        }

class ClassEnrollment(db.Model):
    __tablename__ = 'class_enrollments'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('class_id', 'student_id', name='unique_enrollment'),)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'question': self.question_text,
            'options': [self.option_a, self.option_b, self.option_c, self.option_d],
            'correct': self.correct_answer,
            'explanation': self.explanation
        }

class QuestionFlag(db.Model):
    """Track user-reported issues with questions - supports both registered and guest users"""
    __tablename__ = 'question_flags'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Now nullable for guests
    guest_identifier = db.Column(db.String(100), nullable=True)  # For guest users
    guest_email = db.Column(db.String(120), nullable=True)  # Optional guest email
    flag_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    question = db.relationship('Question', backref='flags')
    reporter = db.relationship('User', foreign_keys=[user_id], backref='flags_reported')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='flags_resolved')

    def to_dict(self):
        # Determine reporter name
        if self.user_id:
            reporter_name = self.reporter.full_name if self.reporter else 'Unknown User'
        else:
            reporter_name = f"Guest ({self.guest_identifier or 'Anonymous'})"

        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'user_name': reporter_name,
            'guest_email': self.guest_email,
            'flag_type': self.flag_type,
            'description': self.description,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolver_name': self.resolver.full_name if self.resolver else None
        }

class QuestionEdit(db.Model):
    """Track all edits made to questions"""
    __tablename__ = 'question_edits'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    edited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    edit_type = db.Column(db.String(50), nullable=False)

    old_question_text = db.Column(db.Text)
    old_option_a = db.Column(db.String(100))
    old_option_b = db.Column(db.String(100))
    old_option_c = db.Column(db.String(100))
    old_option_d = db.Column(db.String(100))
    old_correct_answer = db.Column(db.Integer)
    old_explanation = db.Column(db.Text)

    new_question_text = db.Column(db.Text)
    new_option_a = db.Column(db.String(100))
    new_option_b = db.Column(db.String(100))
    new_option_c = db.Column(db.String(100))
    new_option_d = db.Column(db.String(100))
    new_correct_answer = db.Column(db.Integer)
    new_explanation = db.Column(db.Text)

    edit_notes = db.Column(db.Text)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', backref='edit_history')
    editor = db.relationship('User', backref='question_edits')

    def to_dict(self):
        changes = {}
        if self.old_question_text != self.new_question_text:
            changes['question_text'] = {'old': self.old_question_text, 'new': self.new_question_text}
        if self.old_option_a != self.new_option_a:
            changes['option_a'] = {'old': self.old_option_a, 'new': self.new_option_a}
        if self.old_option_b != self.new_option_b:
            changes['option_b'] = {'old': self.old_option_b, 'new': self.new_option_b}
        if self.old_option_c != self.new_option_c:
            changes['option_c'] = {'old': self.old_option_c, 'new': self.new_option_c}
        if self.old_option_d != self.new_option_d:
            changes['option_d'] = {'old': self.old_option_d, 'new': self.new_option_d}
        if self.old_correct_answer != self.new_correct_answer:
            changes['correct_answer'] = {'old': self.old_correct_answer, 'new': self.new_correct_answer}
        if self.old_explanation != self.new_explanation:
            changes['explanation'] = {'old': self.old_explanation, 'new': self.new_explanation}

        return {
            'id': self.id,
            'question_id': self.question_id,
            'edited_by': self.editor.full_name,
            'edit_type': self.edit_type,
            'edit_notes': self.edit_notes,
            'edited_at': self.edited_at.isoformat(),
            'changes': changes
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer)  # seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': self.percentage,
            'time_taken': self.time_taken,
            'completed_at': self.completed_at.isoformat()
        }

# ==================== BADGES & PROGRESS TRACKING MODELS ====================

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

# ==================== DOMAIN RESTRICTION MODELS ====================

class TeacherDomainAccess(db.Model):
    """Tracks which email domains a teacher can access"""
    __tablename__ = 'teacher_domain_access'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_domain = db.Column(db.String(100), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='domain_access')
    granter = db.relationship('User', foreign_keys=[granted_by], backref='domains_granted')

    # Unique constraint: one teacher can only have one record per domain
    __table_args__ = (db.UniqueConstraint('teacher_id', 'email_domain', name='unique_teacher_domain'),)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name,
            'teacher_email': self.teacher.email,
            'email_domain': self.email_domain,
            'granted_by': self.granter.full_name,
            'granted_at': self.granted_at.isoformat(),
            'notes': self.notes
        }

class DomainAccessRequest(db.Model):
    """Tracks teacher requests for domain access"""
    __tablename__ = 'domain_access_requests'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_domain = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, denied
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)

    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='domain_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='domain_requests_reviewed')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name,
            'teacher_email': self.teacher.email,
            'email_domain': self.email_domain,
            'reason': self.reason,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'reviewed_by': self.reviewer.full_name if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'admin_notes': self.admin_notes
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

# ==================== DECORATORS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow full accounts (user_id), casual guests (is_guest + user_id), and repeat guests (guest_code)
        if 'user_id' not in session and 'guest_code' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Repeat guests are considered students
            if 'guest_code' in session and 'student' in roles:
                return f(*args, **kwargs)

            # Full accounts and casual guests
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            user = User.query.get(session['user_id'])
            if not user or user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def approved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow casual guests through
        if 'is_guest' in session:
            return f(*args, **kwargs)

        # Allow repeat guests through
        if 'guest_code' in session:
            return f(*args, **kwargs)

        # For regular users, check authentication and approval
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.role == 'teacher' and not user.is_approved:
            return jsonify({'error': 'Teacher account pending approval'}), 403
        return f(*args, **kwargs)
    return decorated_function

def guest_or_login_required(f):
    """Allow both guest users and logged-in users"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_guest' not in session and 'user_id' not in session and 'guest_code' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== BADGES HELPER FUNCTIONS ====================

def initialize_user_stats(user_id):
    """Create initial stats record for a user if it doesn't exist"""
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = UserStats(
            user_id=user_id,
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

    # Award points for quiz completion (base points + performance bonus)
    base_points = 5  # Base points for completing any quiz
    performance_bonus = int(quiz_attempt.percentage / 10)  # 0-10 points based on score
    quiz_points = base_points + performance_bonus
    stats.total_points += quiz_points

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

    progress.last_attempt_at = datetime.utcnow()

    # Check for mastery (90%+ accuracy with 5+ attempts)
    if progress.attempts >= 5:
        accuracy = (progress.total_correct / progress.total_questions_answered) * 100
        if accuracy >= 90 and not progress.is_mastered:
            progress.is_mastered = True

            # Update user's mastered topics count
            stats = UserStats.query.filter_by(user_id=user_id).first()
            if stats:
                # Count total mastered topics across all difficulties
                mastered_count = TopicProgress.query.filter_by(
                    user_id=user_id,
                    is_mastered=True
                ).count()
                stats.topics_mastered = mastered_count

    db.session.commit()

def check_and_award_badges(user_id):
    """Check if user has earned any new badges"""
    # Get all badges
    all_badges = Badge.query.all()

    # Get already earned badges
    earned_badge_ids = {ub.badge_id for ub in UserBadge.query.filter_by(user_id=user_id).all()}

    # Get user stats
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        return []

    newly_earned = []

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
            # Count quizzes with 90%+
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

# ==================== ROUTES ====================

def generate_options_for_answer(correct_answer, count=4, range_size=10, allow_negative=False):
    """
    Helper function to generate multiple choice options

    Args:
        correct_answer: The correct answer
        count: Number of options to generate (default 4)
        range_size: Range for generating wrong answers
        allow_negative: Whether to allow negative wrong answers

    Returns:
        List of options shuffled with correct answer included
    """
    options = [correct_answer]

    # Generate wrong answers
    attempts = 0
    max_attempts = 100

    while len(options) < count and attempts < max_attempts:
        attempts += 1

        # Create wrong answer within range
        offset = random.randint(-range_size, range_size)
        if offset == 0:
            offset = random.choice([-1, 1]) * random.randint(1, range_size)

        wrong_answer = correct_answer + offset

        # Apply negative restriction if needed
        if not allow_negative and wrong_answer < 0:
            wrong_answer = abs(wrong_answer)

        # Ensure unique and not zero (unless correct answer is zero)
        if wrong_answer not in options and (wrong_answer != 0 or correct_answer == 0):
            options.append(wrong_answer)

    # If we couldn't generate enough unique options, add some calculated ones
    while len(options) < count:
        # Generate wrong answers based on common mistakes
        if correct_answer > 0:
            wrong = correct_answer + random.choice([1, -1, 2, -2, 5, -5, 10, -10])
        else:
            wrong = correct_answer + random.choice([1, -1, 2, -2])

        if wrong not in options:
            options.append(wrong)

    # Shuffle so correct answer isn't always first
    random.shuffle(options)

    return options


def generate_multiplication_division_beginner():
    """
    Generate beginner level multiplication and division questions
    - Single digit × single digit (2 × 3 = ?)
    - Simple division with no remainders (6 ÷ 2 = ?)
    - NO NEGATIVE NUMBERS
    """
    operation = random.choice(['multiply', 'divide'])

    if operation == 'multiply':
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        answer = a * b
        question = f"{a} × {b}"
    else:  # divide
        divisor = random.randint(1, 10)
        quotient = random.randint(1, 10)
        dividend = divisor * quotient
        answer = quotient
        question = f"{dividend} ÷ {divisor}"

    options = generate_options_for_answer(answer, count=4, range_size=10)

    return {
        'question': question,
        'answer': answer,
        'options': options,
        'explanation': f"The correct answer is {answer}"
    }


def generate_multiplication_division_intermediate():
    """
    Generate intermediate level multiplication and division questions
    - INCLUDES SINGLE NEGATIVE NUMBERS with low value integers
    """
    operation = random.choice(['multiply', 'divide'])
    include_negative = random.choice([True, False])

    if operation == 'multiply':
        if include_negative:
            a = random.choice(list(range(-10, 0)) + list(range(1, 11)))
            b = random.choice(list(range(-10, 0)) + list(range(1, 11)))

            # Ensure only ONE is negative
            if a < 0 and b < 0:
                b = abs(b)
            elif a > 0 and b > 0:
                if random.choice([True, False]):
                    a = -a
                else:
                    b = -b
        else:
            a = random.randint(10, 25)
            b = random.randint(2, 12)

        answer = a * b
        question = f"{a} × {b}"
    else:  # divide
        if include_negative:
            divisor = random.choice(list(range(-10, 0)) + list(range(2, 11)))
            quotient = random.choice(list(range(-10, 0)) + list(range(1, 11)))

            # Ensure only ONE is negative
            if divisor < 0 and quotient < 0:
                quotient = abs(quotient)
            elif divisor > 0 and quotient > 0:
                if random.choice([True, False]):
                    divisor = -divisor
                else:
                    quotient = -quotient

            dividend = divisor * quotient
            answer = quotient
        else:
            divisor = random.randint(2, 12)
            quotient = random.randint(10, 50)
            dividend = divisor * quotient
            answer = quotient

        question = f"{dividend} ÷ {divisor}"

    options = generate_options_for_answer(answer, count=4, range_size=20, allow_negative=True)

    return {
        'question': question,
        'answer': answer,
        'options': options,
        'explanation': f"The correct answer is {answer}"
    }


def generate_multiplication_division_advanced():
    """
    Generate advanced level multiplication and division questions
    - DOUBLE NEGATIVE CALCULATIONS
    - THREE DIGIT COMPUTATIONS
    """
    operation = random.choice(['multiply', 'divide', 'mixed', 'three_digit'])

    if operation == 'multiply':
        neg_type = random.choices(['double_neg', 'single_neg', 'positive'], weights=[0.4, 0.4, 0.2])[0]

        if neg_type == 'double_neg':
            a = random.randint(-50, -10)
            b = random.randint(-20, -2)
            answer = a * b
            question = f"({a}) × ({b})"
        elif neg_type == 'single_neg':
            a = random.randint(10, 50)
            b = random.randint(2, 25)
            if random.choice([True, False]):
                a = -a
            else:
                b = -b
            answer = a * b
            question = f"{a} × {b}"
        else:
            a = random.randint(20, 99)
            b = random.randint(11, 25)
            answer = a * b
            question = f"{a} × {b}"

    elif operation == 'divide':
        neg_type = random.choices(['double_neg', 'single_neg', 'positive'], weights=[0.4, 0.4, 0.2])[0]

        if neg_type == 'double_neg':
            divisor = random.randint(-25, -2)
            quotient = random.randint(-50, -5)
            dividend = divisor * quotient
            answer = quotient
            question = f"({dividend}) ÷ ({divisor})"
        elif neg_type == 'single_neg':
            divisor = random.randint(2, 25)
            quotient = random.randint(5, 50)
            if random.choice([True, False]):
                divisor = -divisor
            else:
                quotient = -quotient
            dividend = divisor * quotient
            answer = quotient
            question = f"{dividend} ÷ {divisor}"
        else:
            divisor = random.randint(11, 25)
            quotient = random.randint(20, 100)
            dividend = divisor * quotient
            answer = quotient
            question = f"{dividend} ÷ {divisor}"

    elif operation == 'mixed':
        mix_type = random.choice(['mult_then_div', 'div_then_mult'])

        if mix_type == 'mult_then_div':
            a = random.randint(-30, 30)
            if a == 0:
                a = random.choice([-15, 15])
            b = random.randint(2, 10)
            c = random.randint(-10, 10)
            if c == 0:
                c = random.choice([-5, 5])

            temp = a * b
            if temp % c != 0:
                quotient = temp // c
                temp = quotient * c
                a = temp // b

            answer = (a * b) // c
            a_str = f"({a})" if a < 0 else str(a)
            b_str = f"({b})" if b < 0 else str(b)
            c_str = f"({c})" if c < 0 else str(c)
            question = f"({a_str} × {b_str}) ÷ {c_str}"
        else:
            a = random.randint(-100, 100)
            if a == 0:
                a = random.choice([-48, 48])
            b = random.randint(-10, 10)
            if b == 0:
                b = random.choice([-6, 6])
            quotient = random.randint(-20, 20)
            if quotient == 0:
                quotient = random.choice([-8, 8])
            a = quotient * b
            c = random.randint(-10, 10)
            if c == 0:
                c = random.choice([-3, 3])

            answer = (a // b) * c
            a_str = f"({a})" if a < 0 else str(a)
            b_str = f"({b})" if b < 0 else str(b)
            c_str = f"({c})" if c < 0 else str(c)
            question = f"({a_str} ÷ {b_str}) × {c_str}"

    else:  # three_digit
        sub_type = random.choice(['mult_3digit', 'div_3digit'])

        if sub_type == 'mult_3digit':
            a = random.randint(100, 999)
            b = random.randint(10, 99)
            answer = a * b
            question = f"{a} × {b}"
        else:
            divisor = random.randint(10, 99)
            quotient = random.randint(10, 99)
            dividend = divisor * quotient
            answer = quotient
            question = f"{dividend} ÷ {divisor}"

    options = generate_options_for_answer(answer, count=4, range_size=50, allow_negative=True)

    return {
        'question': question,
        'answer': answer,
        'options': options,
        'explanation': f"The correct answer is {answer}"
    }

# ==================== AUTHENTICATION ROUTES ====================

# ==================== DOMAIN RESTRICTION HELPER FUNCTIONS ====================

def extract_domain(email):
    """Extract domain from email address"""
    if not email or '@' not in email:
        return None
    return email.split('@')[1].lower()

def get_all_domains_in_system():
    """Get all unique email domains from both students and teachers"""
    domains = {}

    # Get student domains
    students = User.query.filter_by(role='student').all()
    for student in students:
        domain = extract_domain(student.email)
        if domain:
            if domain not in domains:
                domains[domain] = {
                    'domain': domain,
                    'student_count': 0,
                    'teacher_count': 0,
                    'teachers_with_access': []
                }
            domains[domain]['student_count'] += 1

    # Get teacher domains
    teachers = User.query.filter_by(role='teacher').all()
    for teacher in teachers:
        domain = extract_domain(teacher.email)
        if domain:
            if domain not in domains:
                domains[domain] = {
                    'domain': domain,
                    'student_count': 0,
                    'teacher_count': 0,
                    'teachers_with_access': []
                }
            domains[domain]['teacher_count'] += 1

    # Get teachers with access to each domain
    for domain_name in domains.keys():
        access_records = TeacherDomainAccess.query.filter_by(email_domain=domain_name).all()
        for record in access_records:
            domains[domain_name]['teachers_with_access'].append({
                'id': record.teacher_id,
                'name': record.teacher.full_name,
                'email': record.teacher.email
            })

    return list(domains.values())

def teacher_has_domain_access(teacher_id, domain):
    """Check if a teacher has access to a specific domain"""
    if not domain:
        return True

    # Check if teacher has any domain restrictions
    has_any_restrictions = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).first()

    # If teacher has NO restrictions at all, they can see ALL students (backward compatible)
    if not has_any_restrictions:
        return True

    # If teacher has restrictions, check if they have access to THIS specific domain
    access = TeacherDomainAccess.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain
    ).first()

    return access is not None

def get_teacher_accessible_domains(teacher_id):
    """Get all domains a teacher has access to"""
    # Check if teacher has any restrictions
    restrictions = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).all()

    if not restrictions:
        # No restrictions = access to all domains
        return None  # None means "all domains"

    # Return list of accessible domains
    return [r.email_domain for r in restrictions]

def filter_students_by_domain_access(students_query, teacher_id):
    """Filter a SQLAlchemy query of students based on teacher's domain access"""
    accessible_domains = get_teacher_accessible_domains(teacher_id)

    # If None, teacher has access to all domains
    if accessible_domains is None:
        return students_query

    # If empty list, teacher has no access to any domains
    if not accessible_domains:
        return students_query.filter(User.id == -1)

    # Filter students by accessible domains
    filtered_students = []
    for student in students_query.all():
        student_domain = extract_domain(student.email)
        if student_domain in accessible_domains:
            filtered_students.append(student.id)

    if not filtered_students:
        return students_query.filter(User.id == -1)

    return students_query.filter(User.id.in_(filtered_students))

def get_teacher_domain_statistics(teacher_id):
    """Get statistics about a teacher's domain access"""
    accessible_domains = get_teacher_accessible_domains(teacher_id)

    if accessible_domains is None:
        # Teacher has access to all
        total_students = User.query.filter_by(role='student').count()
        all_domains = set()
        for student in User.query.filter_by(role='student').all():
            domain = extract_domain(student.email)
            if domain:
                all_domains.add(domain)

        return {
            'has_restrictions': False,
            'accessible_domains': list(all_domains),
            'accessible_student_count': total_students,
            'restricted_domains': []
        }

    # Count students in accessible domains
    accessible_count = 0
    all_domains = set()

    for student in User.query.filter_by(role='student').all():
        domain = extract_domain(student.email)
        if domain:
            all_domains.add(domain)
            if domain in accessible_domains:
                accessible_count += 1

    restricted_domains = list(all_domains - set(accessible_domains))

    return {
        'has_restrictions': True,
        'accessible_domains': accessible_domains,
        'accessible_student_count': accessible_count,
        'restricted_domains': restricted_domains
    }

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'teacher':
                if not user.is_approved:
                    return render_template('pending_approval.html')
                return redirect(url_for('teacher_dashboard'))
            else:
                return render_template('student_app.html')
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'student')

    # Validation
    if not email or not password or not full_name:
        return jsonify({'error': 'All fields are required'}), 400

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if role not in ['student', 'teacher']:
        return jsonify({'error': 'Invalid role'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Create user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        is_approved=(role == 'student')  # Students auto-approved, teachers need approval
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    message = 'Registration successful!' if role == 'student' else 'Registration successful! Your teacher account is pending admin approval.'

    return jsonify({
        'message': message,
        'user': user.to_dict()
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_name'] = user.full_name

    return jsonify({
        'message': 'Login successful',
        'role': user.role,
        'is_approved': user.is_approved,
        'user': user.to_dict()
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


# ==================== FIXED GUEST ROUTES ====================
# REPLACE your existing guest routes (lines ~1185-1208) with these:

@app.route('/api/guest-start', methods=['POST'])
def guest_start():
    """Initialize guest session with proper user_id"""
    import uuid

    try:
        session.clear()

        # Get or create the guest user in database
        guest_user = User.query.filter_by(email='guest@mathmaster.app').first()

        if not guest_user:
            # Create guest user if it doesn't exist
            guest_user = User(
                email='guest@mathmaster.app',
                password_hash='no_password_required',
                full_name='Guest User',
                role='student',
                is_approved=True
            )
            db.session.add(guest_user)
            db.session.commit()

        # Set up guest session properly
        session['is_guest'] = True
        session['guest_session_id'] = str(uuid.uuid4())
        session['user_id'] = guest_user.id  # CRITICAL: Set user_id
        session['role'] = 'student'

        # Try to create guest_sessions table if it doesn't exist
        try:
            from sqlalchemy import text
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS guest_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    quiz_attempts INTEGER DEFAULT 0
                )
            """))

            # Insert this guest session
            db.session.execute(
                text("INSERT OR IGNORE INTO guest_sessions (session_id) VALUES (:sid)"),
                {"sid": session['guest_session_id']}
            )
            db.session.commit()
        except Exception as e:
            print(f"Note: Could not create guest_sessions table: {e}")
            # Not critical, continue anyway

        return jsonify({
            'success': True,
            'message': 'Guest session started',
            'redirect': '/student'
        }), 200

    except Exception as e:
        print(f"Error starting guest session: {e}")
        db.session.rollback()
        return jsonify({'error': f'Failed to start guest session: {str(e)}'}), 500


@app.route('/guest')
def guest_app():
    """Guest mode redirect - initializes session if needed"""
    import uuid

    # If not already a guest, set up guest session
    if 'is_guest' not in session or 'user_id' not in session:
        try:
            # Get or create guest user
            guest_user = User.query.filter_by(email='guest@mathmaster.app').first()

            if not guest_user:
                guest_user = User(
                    email='guest@mathmaster.app',
                    password_hash='no_password_required',
                    full_name='Guest User',
                    role='student',
                    is_approved=True
                )
                db.session.add(guest_user)
                db.session.commit()

            # Set up session
            session['is_guest'] = True
            session['guest_session_id'] = str(uuid.uuid4())
            session['user_id'] = guest_user.id
            session['role'] = 'student'

        except Exception as e:
            print(f"Error setting up guest session: {e}")
            return redirect('/')

    # Redirect to student app
    return redirect('/student')


@app.route('/api/guest-info')
def guest_info():
    """Return guest session information"""
    if session.get('is_guest'):
        return jsonify({
            'is_guest': True,
            'guest_id': session.get('guest_session_id', 'unknown'),
            'user_id': session.get('user_id')
        }), 200
    return jsonify({'is_guest': False}), 200


@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Allow users to change their own password"""
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    # Validation
    if not current_password or not new_password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400

    if new_password != confirm_password:
        return jsonify({'error': 'New passwords do not match'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    # Get current user
    user = User.query.get(session['user_id'])

    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    # Update password
    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200

@app.route('/api/current-user')
def current_user():
    """Get current user info - supports both regular and guest users"""
    if 'is_guest' in session:
        return jsonify({
            'is_guest': True,
            'full_name': 'Guest User',
            'email': 'guest@example.com',
            'role': 'student'
        }), 200

    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

# ==================== STUDENT ROUTES ====================

@app.route('/student')
@login_required
@approved_required
def student_redirect():
    """Redirect /student to /app for backwards compatibility"""
    return redirect(url_for('student_app'))

@app.route('/app')
@login_required
@approved_required
def student_app():
    # Handle repeat guests (they don't have user_id)
    if 'guest_code' in session:
        return render_template('student_app.html')

    # Handle full accounts and casual guests
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return redirect(url_for('index'))
    return render_template('student_app.html')

@app.route('/api/topics')
@guest_or_login_required
@approved_required
def get_topics():
    """Get topics grouped by Junior Cycle strands"""

    # Topic metadata (icons and display titles)
    topic_info = {
        'arithmetic': {'title': 'Arithmetic', 'icon': 'calculator'},
        'fractions': {'title': 'Fractions', 'icon': 'divide'},
        'decimals': {'title': 'Decimals', 'icon': 'percent'},
        'multiplication_division': {'title': 'Multiplication & Division', 'icon': 'x'},
        'number_systems': {'title': 'Number Systems', 'icon': 'hash'},
        'bodmas': {'title': 'BODMAS', 'icon': 'book'},
        'introductory_algebra': {'title': 'Introductory Algebra', 'icon': 'book-open'},
        'functions': {'title': 'Functions', 'icon': 'chart'},
        'patterns': {'title': 'Patterns', 'icon': 'trending-up'},
        'solving_equations': {'title': 'Solving Equations', 'icon': 'equals'},
        'simplifying_expressions': {'title': 'Simplifying Expressions', 'icon': 'calculator'},
        'expanding_factorising': {'title': 'Expanding & Factorising', 'icon': 'brackets'},
        'probability': {'title': 'Probability', 'icon': 'dice'},
        'descriptive_statistics': {'title': 'Descriptive Statistics', 'icon': 'chart-bar'},
        'sets': {'title': 'Sets', 'icon': 'layers'},
        'surds': {'title': 'Surds', 'icon': 'radical'},
        'complex_numbers_intro': {'title': 'Complex Numbers Intro', 'icon': 'infinity'},
        'complex_numbers_expanded': {'title': 'Complex Numbers - Expanded', 'icon': 'rotate'}
    }

    # Build response with strands
    strands = {}
    topics_flat = {}

    # Try to query database for topics with their strands
    try:
        from sqlalchemy import text
        topics_query = db.session.execute(text("""
            SELECT DISTINCT topic, strand
            FROM questions
            WHERE strand IS NOT NULL
            ORDER BY
                CASE strand
                    WHEN 'Number' THEN 1
                    WHEN 'Algebra and Functions' THEN 2
                    WHEN 'Statistics and Probability' THEN 3
                    WHEN 'Senior Cycle - Algebra' THEN 4
                    WHEN 'Geometry and Trigonometry' THEN 5
                    ELSE 6
                END,
                CASE topic
                    -- Order for Number strand
                    WHEN 'arithmetic' THEN 1
                    WHEN 'multiplication_division' THEN 2
                    WHEN 'number_systems' THEN 3
                    WHEN 'bodmas' THEN 4
                    WHEN 'fractions' THEN 5
                    WHEN 'decimals' THEN 6
                    WHEN 'sets' THEN 7
                    -- Order for Algebra and Functions strand (Junior Cycle)
                    WHEN 'introductory_algebra' THEN 1
                    WHEN 'functions' THEN 2
                    WHEN 'patterns' THEN 3
                    WHEN 'solving_equations' THEN 4
                    WHEN 'simplifying_expressions' THEN 5
                    WHEN 'expanding_factorising' THEN 6
                    -- Order for Statistics and Probability strand
                    WHEN 'probability' THEN 1
                    WHEN 'descriptive_statistics' THEN 2
                    -- Order for Senior Cycle - Algebra strand
                    WHEN 'surds' THEN 1
                    WHEN 'complex_numbers_intro' THEN 2
                    WHEN 'complex_numbers_expanded' THEN 3
                    -- Default order for other topics
                    ELSE 10
                END,
                topic
        """)).fetchall()

        for topic, strand in topics_query:
            if strand not in strands:
                strands[strand] = []

            # Add topic to strand list
            strands[strand].append(topic)

            # Add topic metadata to flat dict
            if topic in topic_info:
                topics_flat[topic] = topic_info[topic]
            else:
                # Fallback for topics not in metadata
                topics_flat[topic] = {
                    'title': topic.replace('_', ' ').title(),
                    'icon': 'book'
                }
    except Exception as e:
        # If strand column doesn't exist or query fails, use fallback
        print(f"Warning: Could not query strand column: {e}")
        strands = {}

    # If no strands found (before migration or error), use fallback
    if not strands:
        strands = {
            'Number': ['arithmetic', 'multiplication_division', 'number_systems',
                      'bodmas', 'fractions', 'decimals', 'sets'],
            'Algebra and Functions': ['introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising'],
            'Statistics and Probability': ['probability', 'descriptive_statistics'],
            'Senior Cycle - Algebra': ['surds', 'complex_numbers_intro',
                                        'complex_numbers_expanded']
        }
        topics_flat = topic_info

    # Strand colors and descriptions
    strand_info = {
        'Number': {
            'color': '#667eea',
            'icon': '📊',
            'description': 'Master the fundamentals of numbers and operations'
        },
        'Algebra and Functions': {
            'color': '#f093fb',
            'icon': '🔢',
            'description': 'Discover patterns, equations, and functions'
        },
        'Statistics and Probability': {
            'color': '#4facfe',
            'icon': '📈',
            'description': 'Analyze data and understand probability'
        },
        'Senior Cycle - Algebra': {
            'color': '#fa709a',
            'icon': '🎓',
            'description': 'Advanced algebraic concepts for senior students'
        },
        'Geometry and Trigonometry': {
            'color': '#764ba2',
            'icon': '📐',
            'description': 'Explore shapes, measurements, and spatial reasoning'
        }
    }

    return jsonify({
        'topics': topics_flat,
        'strands': strands,
        'strand_info': strand_info
    })

@app.route('/api/questions/<topic>/<difficulty>')
@guest_or_login_required
@approved_required
def get_questions(topic, difficulty):
    """
    Get 25 random questions from the pool of 40 available questions
    for the given topic and difficulty level.
    Each student gets a different random selection.
    """
    questions = Question.query.filter_by(topic=topic, difficulty=difficulty).all()
    questions_list = [q.to_dict() for q in questions]

    # Shuffle to randomize order
    random.shuffle(questions_list)

    # Return 25 questions (or all available if less than 25)
    return jsonify(questions_list[:25])

@app.route('/api/submit-quiz', methods=['POST'])
@guest_or_login_required
@approved_required
def submit_quiz():
    """Submit quiz - works for guests, repeat guests, and registered users"""
    data = request.json

    # Normalize topic and difficulty to lowercase
    topic = data.get('topic', '').lower().strip()
    difficulty = data.get('difficulty', '').lower().strip()
    score = data.get('score', 0)
    total = data.get('total_questions', 25)
    percentage = data.get('percentage', 0)
    time_taken = data.get('time_taken', 0)

    # Validate topic and difficulty
    valid_topics = [
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems',
        'bodmas', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'sets', 'probability', 'descriptive_statistics', 'surds',
        'complex_numbers_intro', 'complex_numbers_expanded'
    ]
    valid_difficulties = ['beginner', 'intermediate', 'advanced']

    if topic not in valid_topics:
        return jsonify({'error': f'Invalid topic: {topic}'}), 400

    if difficulty not in valid_difficulties:
        return jsonify({'error': f'Invalid difficulty: {difficulty}'}), 400

    # Handle repeat guests - save to guest tables
    if 'guest_code' in session:
        from sqlalchemy import text
        guest_code = session['guest_code']

        # Save quiz attempt
        db.session.execute(text("""
            INSERT INTO guest_quiz_attempts (guest_code, topic, difficulty, score, total_questions, time_spent)
            VALUES (:code, :topic, :diff, :score, :total, :time)
        """), {
            "code": guest_code,
            "topic": topic,
            "diff": difficulty,
            "score": score,
            "total": total,
            "time": time_taken
        })

        # Update guest stats
        db.session.execute(text("""
            UPDATE guest_users
            SET total_score = total_score + :score,
                quizzes_completed = quizzes_completed + 1,
                last_active = :now
            WHERE guest_code = :code
        """), {
            "score": score,
            "now": datetime.utcnow(),
            "code": guest_code
        })

        db.session.commit()

        return jsonify({
            'message': 'Quiz completed!',
            'score': score,
            'total': total,
            'percentage': percentage,
            'is_repeat_guest': True
        }), 200

    # For casual guests, just return results without saving
    if 'is_guest' in session:
        return jsonify({
            'message': 'Quiz completed!',
            'score': score,
            'total': total,
            'percentage': percentage,
            'is_guest': True,
            'prompt_register': True
        }), 200

    # For registered users, save to database
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=session['user_id'],
        topic=topic,
        difficulty=difficulty,
        score=score,
        total_questions=total,
        percentage=percentage,
        time_taken=time_taken
    )

    db.session.add(attempt)
    db.session.commit()

    # Update stats and check for badges
    stats, newly_earned_badges = update_user_stats_after_quiz(session['user_id'], attempt)

    return jsonify({
        'message': 'Quiz submitted successfully',
        'attempt': attempt.to_dict(),
        'stats': stats.to_dict(),
        'newly_earned_badges': newly_earned_badges
    }), 201

@app.route('/api/my-progress')
@guest_or_login_required
def my_progress():
    # Guest users have no progress
    if 'is_guest' in session:
        return jsonify([]), 200

    attempts = QuizAttempt.query.filter_by(user_id=session['user_id']).order_by(QuizAttempt.completed_at.desc()).all()
    return jsonify([a.to_dict() for a in attempts])

# ==================== BADGES API ROUTES ====================

@app.route('/api/student/badges')
@login_required
@approved_required
def get_student_badges():
    """Get all badges (earned and available) for the current student"""
    # Guest users don't have badges
    if 'is_guest' in session:
        return jsonify({
            'earned': [],
            'available': [],
            'level': 1,
            'total_points': 0,
            'total_badges': 0
        }), 200

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

    # Handle repeat guests - fetch from guest tables
    if 'guest_code' in session:
        from sqlalchemy import text
        guest_code = session['guest_code']

        # Get guest stats
        guest_stats = db.session.execute(text("""
            SELECT total_score, quizzes_completed
            FROM guest_users
            WHERE guest_code = :code
        """), {"code": guest_code}).fetchone()

        # Get guest quiz attempts
        attempts = db.session.execute(text("""
            SELECT topic, difficulty, score, total_questions, completed_at
            FROM guest_quiz_attempts
            WHERE guest_code = :code
            ORDER BY completed_at DESC
            LIMIT 10
        """), {"code": guest_code}).fetchall()

        # Calculate accuracy
        total_correct = sum(a[2] for a in attempts) if attempts else 0
        total_questions = sum(a[3] for a in attempts) if attempts else 0
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

        # Get badge count
        badge_count = db.session.execute(text("""
            SELECT COUNT(*) FROM guest_badges WHERE guest_code = :code
        """), {"code": guest_code}).fetchone()[0]

        return jsonify({
            'stats': {
                'total_quizzes': guest_stats[1] if guest_stats else 0,
                'total_questions_answered': total_questions,
                'total_correct_answers': total_correct,
                'overall_accuracy': round(accuracy, 1),
                'current_streak_days': 0,
                'longest_streak_days': 0,
                'total_points': guest_stats[0] if guest_stats else 0,
                'level': 1,
                'topics_mastered': 0,
                'perfect_scores': 0,
                'badges_earned': badge_count
            },
            'topic_progress': [],
            'recent_attempts': [{
                'topic': a[0],
                'difficulty': a[1],
                'score': a[2],
                'total_questions': a[3],
                'completed_at': a[4]
            } for a in attempts]
        }), 200

    # Handle casual guests - no stats
    if 'is_guest' in session:
        return jsonify({
            'stats': {
                'total_quizzes': 0,
                'total_questions_answered': 0,
                'total_correct_answers': 0,
                'overall_accuracy': 0,
                'current_streak_days': 0,
                'longest_streak_days': 0,
                'total_points': 0,
                'level': 1,
                'topics_mastered': 0,
                'perfect_scores': 0
            },
            'topic_progress': [],
            'recent_attempts': []
        }), 200

    # Handle full accounts
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

@app.route('/api/student/mastery')
@login_required
@approved_required
def get_student_mastery():
    """
    Get student's mastery status for all topics and difficulties.
    Returns best score for each topic/difficulty combination.
    Mastery threshold: >80%
    OPTIMIZED: Single query instead of 36 separate queries
    """
    # Guest users don't have mastery data
    if 'is_guest' in session:
        return jsonify({}), 200

    user_id = session['user_id']

    # Get all topics - MUST match topics in get_topics() API
    topics = [
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems', 'bodmas', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'probability', 'descriptive_statistics', 'sets',
        'surds', 'complex_numbers_intro', 'complex_numbers_expanded'
    ]
    difficulties = ['beginner', 'intermediate', 'advanced']

    # OPTIMIZED: Get all best scores in a single query
    from sqlalchemy import text
    query = text("""
        SELECT topic, difficulty, MAX(percentage) as best_score
        FROM quiz_attempts
        WHERE user_id = :user_id
        GROUP BY topic, difficulty
    """)

    results = db.session.execute(query, {'user_id': user_id}).fetchall()

    # Build lookup dictionary from query results
    best_scores = {}
    for row in results:
        topic, difficulty, best_score = row
        if topic not in best_scores:
            best_scores[topic] = {}
        best_scores[topic][difficulty] = best_score

    # Build mastery data structure
    mastery_data = {}

    for topic in topics:
        mastery_data[topic] = {
            'difficulties': {},
            'topic_mastered': False
        }

        mastered_count = 0

        for difficulty in difficulties:
            best_score = best_scores.get(topic, {}).get(difficulty, 0)

            if best_score > 80:
                mastery_data[topic]['difficulties'][difficulty] = {
                    'mastered': True,
                    'best_score': round(best_score, 1)
                }
                mastered_count += 1
            else:
                mastery_data[topic]['difficulties'][difficulty] = {
                    'mastered': False,
                    'best_score': round(best_score, 1)
                }

        # Topic is mastered if all 3 difficulties are mastered
        mastery_data[topic]['topic_mastered'] = (mastered_count == 3)

    return jsonify(mastery_data)



@app.route('/student/badges')
@login_required
@approved_required
def student_badges_page():
    """Student badges and progress dashboard page"""
    return render_template('student_badges_dashboard.html')

@app.route('/api/class/<int:class_id>/leaderboard')
@login_required
@approved_required
def get_class_leaderboard(class_id):
    """Get leaderboard for a class"""
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

# ==================== TEACHER ROUTES ====================

@app.route('/teacher')
@login_required
@role_required('teacher')
@approved_required
def teacher_dashboard():
    """Redirect to the new visual class selector"""
    return redirect(url_for('teacher_classes_page'))

@app.route('/teacher/class-monitor')
@login_required
@role_required('teacher')
@approved_required
def class_monitor():
    """
    Class Monitor Dashboard - Live monitoring view for teachers
    Shows performance matrix for all students in teacher's classes
    """
    return render_template('class_monitor.html')

@app.route('/api/teacher/my-classes')
@login_required
@role_required('teacher')
@approved_required
def teacher_classes():
    classes = Class.query.filter_by(teacher_id=session['user_id']).all()
    return jsonify([c.to_dict() for c in classes])

@app.route('/api/teacher/create-class', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def create_class():
    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Class name is required'}), 400

    new_class = Class(
        name=name,
        teacher_id=session['user_id']
    )

    db.session.add(new_class)
    db.session.commit()

    return jsonify({
        'message': 'Class created successfully',
        'class': new_class.to_dict()
    }), 201

@app.route('/api/teacher/students/search')
@login_required
@role_required('teacher')
@approved_required
def search_students():
    """Search for students (filtered by teacher's domain access)"""
    query = request.args.get('q', '').strip()
    teacher_id = session['user_id']
    if len(query) < 2:
        return jsonify([])
    students_query = User.query.filter(
        User.role == 'student',
        (User.email.ilike(f'%{query}%')) | (User.full_name.ilike(f'%{query}%'))
    )
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    if accessible_domains is not None:
        filtered_ids = []
        for student in students_query.all():
            student_domain = extract_domain(student.email)
            if student_domain in accessible_domains:
                filtered_ids.append(student.id)
        students_query = students_query.filter(User.id.in_(filtered_ids)) if filtered_ids else students_query.filter(User.id == -1)
    students = students_query.limit(20).all()
    return jsonify([s.to_dict() for s in students])
@app.route('/api/teacher/class/<int:class_id>/enroll', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def enroll_student(class_id):
    """Enroll a student in a class (with domain access check)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return jsonify({'error': 'Invalid student'}), 400
    student_domain = extract_domain(student.email)
    if not teacher_has_domain_access(teacher_id, student_domain):
        return jsonify({'error': f'Access denied. You do not have permission to enroll students from the domain: {student_domain}. Please request access from an administrator.'}), 403
    existing = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
    if existing:
        return jsonify({'error': 'Student already enrolled'}), 400
    enrollment = ClassEnrollment(class_id=class_id, student_id=student_id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({'message': 'Student enrolled successfully'}), 201

@app.route('/api/teacher/class/<int:class_id>/students')
@login_required
@role_required('teacher')
@approved_required
def class_students(class_id):
    """Get students in class - FILTERED BY DOMAIN ACCESS"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']

    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403

    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()

    # Filter by domain access
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    if accessible_domains is not None:
        filtered_enrollments = []
        for enrollment in enrollments:
            student = enrollment.student
            if student:
                student_domain = extract_domain(student.email)
                if student_domain in accessible_domains:
                    filtered_enrollments.append(enrollment)
        enrollments = filtered_enrollments

    students_data = []
    for enrollment in enrollments:
        student = enrollment.student
        if not student:  # Safety check
            continue
        attempts = QuizAttempt.query.filter_by(user_id=student.id).all()

        students_data.append({
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'total_quizzes': len(attempts),
            'average_score': sum(a.percentage for a in attempts) / len(attempts) if attempts else 0,
            'last_activity': max([a.completed_at for a in attempts]).isoformat() if attempts else None
        })

    return jsonify(students_data)

@app.route('/api/teacher/class/<int:class_id>/progress')
@login_required
@role_required('teacher')
@approved_required
def class_progress(class_id):
    class_obj = Class.query.get_or_404(class_id)

    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    student_ids = [e.student_id for e in enrollments]

    # Get all attempts for students in this class
    attempts = QuizAttempt.query.filter(QuizAttempt.user_id.in_(student_ids)).order_by(QuizAttempt.completed_at.desc()).all()

    return jsonify([a.to_dict() for a in attempts])

@app.route('/api/teacher/class/<int:class_id>/remove-student/<int:student_id>', methods=['DELETE'])
@login_required
@role_required('teacher')
@approved_required
def remove_student(class_id, student_id):
    class_obj = Class.query.get_or_404(class_id)

    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    enrollment = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify({'message': 'Student removed successfully'})

# ==================== NEW ENHANCED TEACHER ROUTES ====================

@app.route('/teacher/classes')
@login_required
@role_required('teacher')
@approved_required
def teacher_classes_page():
    """Visual class selector page"""
    return render_template('teacher_classes_selector.html')

@app.route('/api/teacher/classes', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
@approved_required
def teacher_classes_api():
    """Get all classes for teacher or create new class"""
    teacher_id = session['user_id']

    if request.method == 'GET':
        # Get all classes for this teacher
        classes = Class.query.filter_by(teacher_id=teacher_id).order_by(Class.created_at.desc()).all()
        teacher = User.query.get(teacher_id)

        return jsonify({
            'classes': [c.to_dict() for c in classes],
            'teacher': teacher.to_dict() if teacher else None
        })

    elif request.method == 'POST':
        # Create new class
        data = request.json
        class_name = data.get('name', '').strip()

        if not class_name:
            return jsonify({'error': 'Class name is required'}), 400

        new_class = Class(
            name=class_name,
            teacher_id=teacher_id
        )

        db.session.add(new_class)
        db.session.commit()

        return jsonify({
            'message': 'Class created successfully',
            'class': new_class.to_dict()
        }), 201

@app.route('/api/teacher/class/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def get_class_info(class_id):
    """Get basic class information"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(class_obj.to_dict())

@app.route('/teacher/class-manage/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def class_manage_page(class_id):
    """Student management page for a class"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        flash('Unauthorized access to class', 'error')
        return redirect(url_for('teacher_classes_page'))

    return render_template('teacher_class_manage_students.html',
                         class_id=class_id,
                         class_name=class_obj.name)

@app.route('/api/teacher/available-students/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def get_available_students(class_id):
    """Get all students NOT enrolled in this class (filtered by domain access)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    enrolled_ids = db.session.query(ClassEnrollment.student_id).filter_by(class_id=class_id).all()
    enrolled_ids = [e[0] for e in enrolled_ids]
    available_students_query = User.query.filter(User.role == 'student').filter(~User.id.in_(enrolled_ids))
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    if accessible_domains is not None:
        filtered_ids = []
        for student in available_students_query.all():
            student_domain = extract_domain(student.email)
            if student_domain in accessible_domains:
                filtered_ids.append(student.id)
        available_students_query = available_students_query.filter(User.id.in_(filtered_ids)) if filtered_ids else available_students_query.filter(User.id == -1)
    available_students = available_students_query.order_by(User.full_name).all()
    return jsonify([{'id': s.id, 'full_name': s.full_name, 'email': s.email} for s in available_students])

@app.route('/api/teacher/class/<int:class_id>/enroll-bulk', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def enroll_students_bulk(class_id):
    """Enroll multiple students at once (with domain access checks)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    student_ids = data.get('student_ids', [])
    if not student_ids:
        return jsonify({'error': 'No students selected'}), 400
    enrolled_count = 0
    already_enrolled = 0
    access_denied = []
    for student_id in student_ids:
        student = User.query.get(student_id)
        if student:
            student_domain = extract_domain(student.email)
            if not teacher_has_domain_access(teacher_id, student_domain):
                access_denied.append({'id': student_id, 'name': student.full_name, 'domain': student_domain})
                continue
        existing = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
        if existing:
            already_enrolled += 1
            continue
        enrollment = ClassEnrollment(class_id=class_id, student_id=student_id)
        db.session.add(enrollment)
        enrolled_count += 1
    db.session.commit()
    response = {'message': f'Enrolled {enrolled_count} students', 'enrolled_count': enrolled_count, 'already_enrolled': already_enrolled}
    if access_denied:
        response['access_denied'] = access_denied
        response['access_denied_count'] = len(access_denied)
    return jsonify(response)

@app.route('/api/teacher/class/<int:class_id>/students-list')
@login_required
@role_required('teacher')
@approved_required
def get_class_students_list(class_id):
    """Get detailed list of students in a class with their progress (filtered by domain)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    if accessible_domains is not None:
        filtered_enrollments = []
        for enrollment in enrollments:
            student = User.query.get(enrollment.student_id)
            if student:
                student_domain = extract_domain(student.email)
                if student_domain in accessible_domains:
                    filtered_enrollments.append(enrollment)
        enrollments = filtered_enrollments
    students_data = []
    for enrollment in enrollments:
        student = User.query.get(enrollment.student_id)
        if not student:
            continue
        attempts = QuizAttempt.query.filter_by(user_id=student.id).all()
        total_quizzes = len(attempts)
        if attempts:
            avg_score = sum(a.percentage for a in attempts) / len(attempts)
            recent_attempts = sorted(attempts, key=lambda x: x.completed_at, reverse=True)[:5]
        else:
            avg_score = 0
            recent_attempts = []
        students_data.append({'id': student.id, 'full_name': student.full_name, 'email': student.email, 'total_quizzes': total_quizzes, 'avg_score': round(avg_score, 1), 'recent_attempts': [a.to_dict() for a in recent_attempts], 'enrolled_at': enrollment.enrolled_at.isoformat()})
    return jsonify({'class': class_obj.to_dict(), 'students': students_data})

@app.route('/api/teacher/class/<int:class_id>/performance-matrix')
@login_required
@role_required('teacher')
@approved_required
def get_class_performance_matrix(class_id):
    """
    Get performance matrix for all students in a class
    Returns: percentage correct and attempts for each topic/difficulty combination
    Used by: Class Monitor Dashboard for live performance tracking
    """
    # Verify teacher owns this class
    class_obj = Class.query.filter_by(id=class_id, teacher_id=session['user_id']).first()
    if not class_obj:
        return jsonify({'error': 'Class not found or access denied'}), 403

    # Get all students in class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = User.query.filter(User.id.in_(student_ids)).all()

    # Get all topics and difficulties
    topics = ['arithmetic', 'fractions', 'decimals', 'multiplication_division', 'number_systems', 'bodmas', 'probability', 'descriptive_statistics', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'sets', 'surds', 'complex_numbers_intro', 'complex_numbers_expanded']
    difficulties = ['beginner', 'intermediate', 'advanced']

    students_data = []

    for student in students:
        performance = {}

        for topic in topics:
            for difficulty in difficulties:
                key = f"{topic}_{difficulty}"

                # Get all attempts for this topic/difficulty
                attempts = QuizAttempt.query.filter_by(
                    user_id=student.id,
                    topic=topic,
                    difficulty=difficulty
                ).all()

                if attempts:
                    # Calculate average percentage
                    avg_percentage = sum(a.percentage for a in attempts) / len(attempts)
                    performance[key] = {
                        'percentage': round(avg_percentage, 1),
                        'attempts': len(attempts)
                    }
                else:
                    performance[key] = {
                        'percentage': None,
                        'attempts': 0
                    }

        students_data.append({
            'student_id': student.id,
            'student_name': student.full_name,
            'performance': performance
        })

    return jsonify({
        'class_name': class_obj.name,
        'total_students': len(students_data),
        'students': students_data,
        'topics': topics,
        'difficulties': difficulties
    })

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/admin/pending-teachers')
@login_required
@role_required('admin')
def pending_teachers():
    teachers = User.query.filter_by(role='teacher', is_approved=False).all()
    return jsonify([t.to_dict() for t in teachers])

@app.route('/api/admin/approve-teacher/<int:teacher_id>', methods=['POST'])
@login_required
@role_required('admin')
def approve_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)

    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400

    teacher.is_approved = True
    db.session.commit()

    return jsonify({'message': 'Teacher approved successfully'})

@app.route('/api/admin/all-users')
@login_required
@role_required('admin')
def all_users():
    role_filter = request.args.get('role')

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)

    users = query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/admin/all-classes')
@login_required
@role_required('admin')
def all_classes():
    classes = Class.query.all()
    return jsonify([c.to_dict() for c in classes])

@app.route('/api/admin/rename-class/<int:class_id>', methods=['PUT'])
@login_required
@role_required('admin')
def rename_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    data = request.json
    new_name = data.get('name', '').strip()

    if not new_name:
        return jsonify({'error': 'Class name required'}), 400

    class_obj.name = new_name
    db.session.commit()

    return jsonify({'message': 'Class renamed successfully', 'class': class_obj.to_dict()})

@app.route('/api/admin/reassign-student', methods=['POST'])
@login_required
@role_required('admin')
def reassign_student():
    data = request.json
    student_id = data.get('student_id')
    from_class_id = data.get('from_class_id')
    to_class_id = data.get('to_class_id')

    if not all([student_id, from_class_id, to_class_id]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Remove from old class
    old_enrollment = ClassEnrollment.query.filter_by(class_id=from_class_id, student_id=student_id).first()
    if old_enrollment:
        db.session.delete(old_enrollment)

    # Add to new class
    new_enrollment = ClassEnrollment(class_id=to_class_id, student_id=student_id)
    db.session.add(new_enrollment)
    db.session.commit()

    return jsonify({'message': 'Student reassigned successfully'})

@app.route('/api/admin/class-comparison')
@login_required
@role_required('admin')
def class_comparison():
    classes = Class.query.all()
    comparison_data = []

    for class_obj in classes:
        enrollments = ClassEnrollment.query.filter_by(class_id=class_obj.id).all()
        student_ids = [e.student_id for e in enrollments]

        attempts = QuizAttempt.query.filter(QuizAttempt.user_id.in_(student_ids)).all()

        avg_score = sum(a.percentage for a in attempts) / len(attempts) if attempts else 0

        comparison_data.append({
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'teacher_name': class_obj.teacher.full_name,
            'student_count': len(enrollments),
            'total_quizzes': len(attempts),
            'average_score': round(avg_score, 2)
        })

    return jsonify(comparison_data)


# ==================== USER MANAGEMENT ADMIN ROUTES ====================

@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_user_management():
    """Admin page for managing all users"""
    return render_template('admin_user_management.html')

@app.route('/api/admin/user/<int:user_id>', methods=['GET'])
@login_required
@role_required('admin')
def get_user_details(user_id):
    """Get detailed user information"""
    user = User.query.get_or_404(user_id)

    # Get additional stats
    stats = UserStats.query.filter_by(user_id=user_id).first()
    quiz_count = QuizAttempt.query.filter_by(user_id=user_id).count()

    # Get class enrollments if student
    classes = []
    if user.role == 'student':
        enrollments = ClassEnrollment.query.filter_by(student_id=user_id).all()
        classes = [{'id': e.class_obj.id, 'name': e.class_obj.name,
                   'teacher': e.class_obj.teacher.full_name} for e in enrollments]

    # Get classes teaching if teacher
    elif user.role == 'teacher':
        teaching_classes = Class.query.filter_by(teacher_id=user_id).all()
        classes = [{'id': c.id, 'name': c.name,
                   'student_count': len(c.enrollments)} for c in teaching_classes]

    return jsonify({
        'user': user.to_dict(),
        'stats': {
            'total_points': stats.total_points if stats else 0,
            'level': stats.level if stats else 1,
            'quiz_count': quiz_count
        },
        'classes': classes
    })

@app.route('/api/admin/user/<int:user_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_user(user_id):
    """Update user details (name, email)"""
    user = User.query.get_or_404(user_id)
    data = request.json

    # Update name
    if 'full_name' in data:
        new_name = data['full_name'].strip()
        if new_name:
            user.full_name = new_name

    # Update email (check for duplicates)
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if new_email and new_email != user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = new_email

    # Update approval status
    if 'is_approved' in data:
        user.is_approved = data['is_approved']

    db.session.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    })

@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Delete a user and all associated data"""
    try:
        user = User.query.get_or_404(user_id)

        # Don't allow deleting yourself
        if user.id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        # Don't allow deleting other admins
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin accounts'}), 403

        # Delete associated data in proper order to avoid foreign key violations

        # 1. Quiz attempts
        QuizAttempt.query.filter_by(user_id=user_id).delete()

        # 2. User stats
        UserStats.query.filter_by(user_id=user_id).delete()

        # 3. Topic progress
        TopicProgress.query.filter_by(user_id=user_id).delete()

        # 4. User badges
        UserBadge.query.filter_by(user_id=user_id).delete()

        # 5. Question flags - BOTH as reporter AND as resolver
        QuestionFlag.query.filter_by(user_id=user_id).delete()
        # Set resolved_by to NULL for flags this user resolved
        QuestionFlag.query.filter_by(resolved_by=user_id).update({'resolved_by': None})

        # 6. Question edits - Set editor to NULL (keep edit history but anonymize)
        QuestionEdit.query.filter_by(edited_by=user_id).update({'edited_by': None})

        # 7. Domain access records (for teachers)
        TeacherDomainAccess.query.filter_by(teacher_id=user_id).delete()
        # Set granted_by to NULL for domain access this admin granted
        TeacherDomainAccess.query.filter_by(granted_by=user_id).update({'granted_by': None})

        # 8. Domain access requests
        DomainAccessRequest.query.filter_by(teacher_id=user_id).delete()
        # Set reviewed_by to NULL for requests this admin reviewed
        DomainAccessRequest.query.filter_by(reviewed_by=user_id).update({'reviewed_by': None})

        # 9. Class enrollments (if student)
        ClassEnrollment.query.filter_by(student_id=user_id).delete()

        # 10. Classes (if teacher) - also delete all enrollments
        if user.role == 'teacher':
            classes = Class.query.filter_by(teacher_id=user_id).all()
            for class_obj in classes:
                ClassEnrollment.query.filter_by(class_id=class_obj.id).delete()
                db.session.delete(class_obj)

        # Finally, delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': f'User {user.full_name} deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user {user_id}: {str(e)}")  # Log the error
        return jsonify({
            'error': f'Failed to delete user: {str(e)}'
        }), 500

@app.route('/api/admin/users/bulk-delete', methods=['POST'])
@login_required
@role_required('admin')
def bulk_delete_users():
    """Delete multiple users at once"""
    try:
        data = request.json
        user_ids = data.get('user_ids', [])

        if not user_ids:
            return jsonify({'error': 'No users selected'}), 400

        deleted_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = User.query.get(user_id)

                if not user:
                    errors.append(f"User {user_id} not found")
                    continue

                # Don't allow deleting yourself
                if user.id == session['user_id']:
                    errors.append(f"Cannot delete your own account")
                    continue

                # Don't allow deleting other admins
                if user.role == 'admin':
                    errors.append(f"Cannot delete admin account: {user.full_name}")
                    continue

                # Delete associated data (same as single delete)
                QuizAttempt.query.filter_by(user_id=user_id).delete()
                UserStats.query.filter_by(user_id=user_id).delete()
                TopicProgress.query.filter_by(user_id=user_id).delete()
                UserBadge.query.filter_by(user_id=user_id).delete()

                QuestionFlag.query.filter_by(user_id=user_id).delete()
                QuestionFlag.query.filter_by(resolved_by=user_id).update({'resolved_by': None})

                QuestionEdit.query.filter_by(edited_by=user_id).update({'edited_by': None})

                TeacherDomainAccess.query.filter_by(teacher_id=user_id).delete()
                TeacherDomainAccess.query.filter_by(granted_by=user_id).update({'granted_by': None})

                DomainAccessRequest.query.filter_by(teacher_id=user_id).delete()
                DomainAccessRequest.query.filter_by(reviewed_by=user_id).update({'reviewed_by': None})

                ClassEnrollment.query.filter_by(student_id=user_id).delete()

                if user.role == 'teacher':
                    classes = Class.query.filter_by(teacher_id=user_id).all()
                    for class_obj in classes:
                        ClassEnrollment.query.filter_by(class_id=class_obj.id).delete()
                        db.session.delete(class_obj)

                # Delete the user
                db.session.delete(user)
                deleted_count += 1

            except Exception as e:
                errors.append(f"Error deleting user {user_id}: {str(e)}")
                continue

        # Commit all deletions
        db.session.commit()

        response_data = {
            'deleted_count': deleted_count,
            'total_requested': len(user_ids)
        }

        if errors:
            response_data['errors'] = errors

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk delete: {str(e)}")
        return jsonify({
            'error': f'Failed to delete users: {str(e)}'
        }), 500

@app.route('/api/admin/user/<int:user_id>/toggle-approval', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_approval(user_id):
    """Toggle user approval status"""
    user = User.query.get_or_404(user_id)

    user.is_approved = not user.is_approved
    db.session.commit()

    status = 'approved' if user.is_approved else 'unapproved'

    return jsonify({
        'message': f'User {status} successfully',
        'is_approved': user.is_approved
    })



# ==================== DOMAIN MANAGEMENT ADMIN ROUTES ====================

@app.route('/api/admin/domains')
@login_required
@role_required('admin')
def get_all_domains():
    """Get all email domains in the system with statistics"""
    domains = get_all_domains_in_system()
    domains.sort(key=lambda x: x['student_count'], reverse=True)
    return jsonify({
        'domains': domains,
        'total_domains': len(domains)
    })


@app.route('/api/admin/teacher/<int:teacher_id>/domains')
@login_required
@role_required('admin')
def get_teacher_domains(teacher_id):
    """Get all domains assigned to a specific teacher"""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400
    access_records = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).all()
    stats = get_teacher_domain_statistics(teacher_id)
    all_domains = get_all_domains_in_system()
    return jsonify({
        'teacher': teacher.to_dict(),
        'assigned_domains': [r.to_dict() for r in access_records],
        'statistics': stats,
        'available_domains': all_domains
    })


@app.route('/api/admin/teacher/<int:teacher_id>/domains', methods=['POST'])
@login_required
@role_required('admin')
def assign_domain_to_teacher(teacher_id):
    """Assign a domain to a teacher"""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400
    data = request.json
    domain = data.get('domain', '').strip().lower()
    notes = data.get('notes', '').strip()
    if not domain:
        return jsonify({'error': 'Domain is required'}), 400
    if '.' not in domain or '@' in domain:
        return jsonify({'error': 'Invalid domain format. Use format like: school.edu'}), 400
    existing = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id, email_domain=domain).first()
    if existing:
        return jsonify({'error': 'Domain already assigned to this teacher'}), 400
    access = TeacherDomainAccess(teacher_id=teacher_id, email_domain=domain, granted_by=session['user_id'], notes=notes)
    db.session.add(access)
    pending_request = DomainAccessRequest.query.filter_by(teacher_id=teacher_id, email_domain=domain, status='pending').first()
    if pending_request:
        pending_request.status = 'approved'
        pending_request.reviewed_by = session['user_id']
        pending_request.reviewed_at = datetime.utcnow()
        pending_request.admin_notes = 'Automatically approved when domain was granted'
    db.session.commit()
    return jsonify({'message': 'Domain access granted successfully', 'access': access.to_dict()}), 201


@app.route('/api/admin/teacher/<int:teacher_id>/domains/<domain>', methods=['DELETE'])
@login_required
@role_required('admin')
def revoke_domain_from_teacher(teacher_id, domain):
    """Revoke a domain from a teacher"""
    domain = domain.lower()
    access = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id, email_domain=domain).first()
    if not access:
        return jsonify({'error': 'Domain access not found'}), 404
    db.session.delete(access)
    db.session.commit()
    return jsonify({'message': 'Domain access revoked successfully'})


@app.route('/api/admin/teacher/<int:teacher_id>/domains/bulk', methods=['POST'])
@login_required
@role_required('admin')
def assign_domains_bulk(teacher_id):
    """Assign multiple domains to a teacher at once"""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400
    data = request.json
    domains = data.get('domains', [])
    notes = data.get('notes', '').strip()
    if not domains:
        return jsonify({'error': 'No domains provided'}), 400
    added, already_assigned, invalid = [], [], []
    for domain in domains:
        domain = domain.strip().lower()
        if '.' not in domain or '@' in domain:
            invalid.append(domain)
            continue
        existing = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id, email_domain=domain).first()
        if existing:
            already_assigned.append(domain)
            continue
        access = TeacherDomainAccess(teacher_id=teacher_id, email_domain=domain, granted_by=session['user_id'], notes=notes)
        db.session.add(access)
        added.append(domain)
        pending_request = DomainAccessRequest.query.filter_by(teacher_id=teacher_id, email_domain=domain, status='pending').first()
        if pending_request:
            pending_request.status = 'approved'
            pending_request.reviewed_by = session['user_id']
            pending_request.reviewed_at = datetime.utcnow()
            pending_request.admin_notes = 'Automatically approved in bulk assignment'
    db.session.commit()
    return jsonify({'message': f'Processed {len(domains)} domains', 'added': added, 'already_assigned': already_assigned, 'invalid': invalid, 'added_count': len(added)})


@app.route('/api/admin/domain-requests')
@login_required
@role_required('admin')
def get_domain_requests():
    """Get all domain access requests"""
    status_filter = request.args.get('status', 'pending')
    query = DomainAccessRequest.query
    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)
    requests = query.order_by(DomainAccessRequest.requested_at.desc()).all()
    return jsonify({'requests': [r.to_dict() for r in requests], 'total': len(requests)})


@app.route('/api/admin/domain-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_domain_request(request_id):
    """Approve a domain access request"""
    access_request = DomainAccessRequest.query.get_or_404(request_id)
    if access_request.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
    data = request.json
    admin_notes = data.get('admin_notes', '').strip()
    access = TeacherDomainAccess(teacher_id=access_request.teacher_id, email_domain=access_request.email_domain, granted_by=session['user_id'], notes=f"Requested: {access_request.reason}")
    access_request.status = 'approved'
    access_request.reviewed_by = session['user_id']
    access_request.reviewed_at = datetime.utcnow()
    access_request.admin_notes = admin_notes
    db.session.add(access)
    db.session.commit()
    return jsonify({'message': 'Domain access request approved', 'access': access.to_dict(), 'request': access_request.to_dict()})


@app.route('/api/admin/domain-requests/<int:request_id>/deny', methods=['POST'])
@login_required
@role_required('admin')
def deny_domain_request(request_id):
    """Deny a domain access request"""
    access_request = DomainAccessRequest.query.get_or_404(request_id)
    if access_request.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
    data = request.json
    admin_notes = data.get('admin_notes', '').strip()
    if not admin_notes:
        return jsonify({'error': 'Please provide a reason for denial'}), 400
    access_request.status = 'denied'
    access_request.reviewed_by = session['user_id']
    access_request.reviewed_at = datetime.utcnow()
    access_request.admin_notes = admin_notes
    db.session.commit()
    return jsonify({'message': 'Domain access request denied', 'request': access_request.to_dict()})


@app.route('/api/admin/teacher/<int:teacher_id>/remove-all-restrictions', methods=['POST'])
@login_required
@role_required('admin')
def remove_all_teacher_restrictions(teacher_id):
    """Remove all domain restrictions from a teacher (grant full access)"""
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400
    TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).delete()
    db.session.commit()
    return jsonify({'message': 'All domain restrictions removed. Teacher now has full access to all students.'})


# ==================== TEACHER DOMAIN ACCESS ROUTES ====================

@app.route('/api/teacher/my-domain-access')
@login_required
@role_required('teacher')
@approved_required
def get_my_domain_access():
    """Get current teacher's domain access information"""
    teacher_id = session['user_id']
    access_records = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).all()
    stats = get_teacher_domain_statistics(teacher_id)
    pending_requests = DomainAccessRequest.query.filter_by(teacher_id=teacher_id, status='pending').all()
    all_domains = get_all_domains_in_system()
    assigned_domains = [r.email_domain for r in access_records]
    requested_domains = [r.email_domain for r in pending_requests]
    available_to_request = [d for d in all_domains if d['domain'] not in assigned_domains and d['domain'] not in requested_domains]
    return jsonify({
        'has_restrictions': stats['has_restrictions'],
        'assigned_domains': [r.to_dict() for r in access_records],
        'accessible_student_count': stats['accessible_student_count'],
        'restricted_domains': stats['restricted_domains'],
        'pending_requests': [r.to_dict() for r in pending_requests],
        'available_to_request': available_to_request
    })


@app.route('/api/teacher/request-domain-access', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def request_domain_access():
    """Request access to a specific email domain"""
    teacher_id = session['user_id']
    data = request.json
    domain = data.get('domain', '').strip().lower()
    reason = data.get('reason', '').strip()
    if not domain:
        return jsonify({'error': 'Domain is required'}), 400
    if not reason:
        return jsonify({'error': 'Please provide a reason for this request'}), 400
    if '.' not in domain or '@' in domain:
        return jsonify({'error': 'Invalid domain format. Use format like: school.edu'}), 400
    existing_access = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id, email_domain=domain).first()
    if existing_access:
        return jsonify({'error': 'You already have access to this domain'}), 400
    existing_request = DomainAccessRequest.query.filter_by(teacher_id=teacher_id, email_domain=domain, status='pending').first()
    if existing_request:
        return jsonify({'error': 'You already have a pending request for this domain'}), 400
    access_request = DomainAccessRequest(teacher_id=teacher_id, email_domain=domain, reason=reason)
    db.session.add(access_request)
    db.session.commit()
    return jsonify({'message': 'Domain access request submitted successfully', 'request': access_request.to_dict()}), 201


@app.route('/api/teacher/domain-requests')
@login_required
@role_required('teacher')
@approved_required
def get_my_domain_requests():
    """Get all domain access requests by the current teacher"""
    teacher_id = session['user_id']
    requests = DomainAccessRequest.query.filter_by(teacher_id=teacher_id).order_by(DomainAccessRequest.requested_at.desc()).all()
    return jsonify({'requests': [r.to_dict() for r in requests]})


@app.route('/api/teacher/domain-requests/<int:request_id>', methods=['DELETE'])
@login_required
@role_required('teacher')
@approved_required
def cancel_domain_request(request_id):
    """Cancel a pending domain access request"""
    teacher_id = session['user_id']
    access_request = DomainAccessRequest.query.get_or_404(request_id)
    if access_request.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if access_request.status != 'pending':
        return jsonify({'error': 'Can only cancel pending requests'}), 400
    db.session.delete(access_request)
    db.session.commit()
    return jsonify({'message': 'Request cancelled successfully'})


@app.route('/api/admin/statistics')
@login_required
@role_required('admin')
def admin_statistics():
    stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_teachers': User.query.filter_by(role='teacher', is_approved=True).count(),
        'pending_teachers': User.query.filter_by(role='teacher', is_approved=False).count(),
        'total_classes': Class.query.count(),
        'total_quizzes': QuizAttempt.query.count(),
        'total_questions': Question.query.count()
    }
    return jsonify(stats)

# ==================== REAL-TIME CLASS DASHBOARD ROUTES ====================

@app.route('/teacher/class-dashboard/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def class_dashboard(class_id):
    """
    Enhanced Class Performance Dashboard
    - Shows ALL students by default
    - Smart search and filtering
    - Student selection for export
    - Hover tooltips with recommendations
    """
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        flash('Unauthorized access to class', 'error')
        return redirect(url_for('teacher_classes_page'))

    return render_template('teacher_class_dashboard_v2.html',
                         class_id=class_id,
                         class_name=class_obj.name)

@app.route('/api/teacher/class/<int:class_id>/matrix-data')
@login_required
@role_required('teacher')
@approved_required
def get_class_matrix_data(class_id):
    """Get matrix data for class dashboard with Junior Cycle strands"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all students in class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()

    # NEW: Get topics grouped by strand from database
    try:
        from sqlalchemy import text
        topics_query = db.session.execute(text("""
            SELECT DISTINCT strand, topic
            FROM questions
            WHERE strand IS NOT NULL
            ORDER BY
                CASE strand
                    WHEN 'Number' THEN 1
                    WHEN 'Algebra and Functions' THEN 2
                    WHEN 'Statistics and Probability' THEN 3
                    WHEN 'Senior Cycle - Algebra' THEN 4
                    WHEN 'Geometry and Trigonometry' THEN 5
                    ELSE 6
                END,
                CASE topic
                    -- Order for Number strand
                    WHEN 'arithmetic' THEN 1
                    WHEN 'multiplication_division' THEN 2
                    WHEN 'number_systems' THEN 3
                    WHEN 'bodmas' THEN 4
                    WHEN 'fractions' THEN 5
                    WHEN 'decimals' THEN 6
                    WHEN 'sets' THEN 7
                    -- Order for Algebra and Functions strand (Junior Cycle)
                    WHEN 'introductory_algebra' THEN 1
                    WHEN 'functions' THEN 2
                    WHEN 'patterns' THEN 3
                    WHEN 'solving_equations' THEN 4
                    WHEN 'simplifying_expressions' THEN 5
                    WHEN 'expanding_factorising' THEN 6
                    -- Order for Statistics and Probability strand
                    WHEN 'probability' THEN 1
                    WHEN 'descriptive_statistics' THEN 2
                    -- Order for Senior Cycle - Algebra strand
                    WHEN 'surds' THEN 1
                    WHEN 'complex_numbers_intro' THEN 2
                    WHEN 'complex_numbers_expanded' THEN 3
                    -- Default order for other topics
                    ELSE 10
                END,
                topic
        """)).fetchall()
    except Exception as e:
        print(f"Warning: Could not query strand column in matrix-data: {e}")
        topics_query = []

    # Build strands structure
    strands = {}
    all_topics = []

    for strand, topic in topics_query:
        if strand not in strands:
            strands[strand] = []
        strands[strand].append(topic)
        all_topics.append(topic)

    # If no strands found (strands not yet added), fall back to hardcoded list
    if not all_topics:
        all_topics = ['arithmetic', 'multiplication_division', 'number_systems',
                      'bodmas', 'fractions', 'decimals', 'sets',
                      'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'surds', 'complex_numbers_intro', 'complex_numbers_expanded',
                      'probability', 'descriptive_statistics']
        strands = {
            'Number': ['arithmetic', 'multiplication_division', 'number_systems',
                      'bodmas', 'fractions', 'decimals', 'sets'],
            'Algebra and Functions': ['functions', 'patterns', 'solving_equations',
                                      'simplifying_expressions', 'expanding_factorising',
                                      'surds', 'complex_numbers_intro', 'complex_numbers_expanded'],
        }

    difficulties = ['beginner', 'intermediate', 'advanced']

    # Build matrix data
    matrix_data = []

    for enrollment in enrollments:
        student = enrollment.student

        # Get student stats
        stats = UserStats.query.filter_by(user_id=student.id).first()

        student_data = {
            'student_id': student.id,
            'student_name': student.full_name,
            'total_points': stats.total_points if stats else 0,
            'level': stats.level if stats else 1,
            'modules': {}
        }

        # For each topic/difficulty combination
        for topic in all_topics:
            for difficulty in difficulties:
                module_key = f"{topic}_{difficulty}"

                # Get all attempts for this module
                attempts = QuizAttempt.query.filter_by(
                    user_id=student.id,
                    topic=topic,
                    difficulty=difficulty
                ).all()

                if attempts:
                    # Calculate average percentage
                    avg_percentage = sum(a.percentage for a in attempts) / len(attempts)
                    total_attempts = len(attempts)

                    # Determine color based on performance
                    if avg_percentage < 20:
                        color = 'grey'
                    elif avg_percentage <= 80:
                        color = 'yellow'
                    else:
                        color = 'green'

                    student_data['modules'][module_key] = {
                        'percentage': round(avg_percentage, 1),
                        'attempts': total_attempts,
                        'color': color,
                        'completed': True
                    }
                else:
                    # Not attempted yet
                    student_data['modules'][module_key] = {
                        'percentage': 0,
                        'attempts': 0,
                        'color': 'grey',
                        'completed': False
                    }

        matrix_data.append(student_data)

    return jsonify({
        'students': matrix_data,
        'topics': all_topics,
        'difficulties': difficulties,
        'strands': strands,  # NEW: Include strand grouping
        'class_name': class_obj.name,
        'total_students': len(matrix_data)
    })

@app.route('/api/teacher/class/<int:class_id>/dashboard-settings', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
@approved_required
def dashboard_settings(class_id):
    """Save/load dashboard display settings"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        settings = request.json
        return jsonify({'message': 'Settings saved', 'settings': settings})
    else:
        # Return default settings
        return jsonify({
            'visible_modules': {
                'arithmetic': True,
                'fractions': True,
                'decimals': True,
                'bodmas': True,
                'functions': True,
                'sets': True
            },
            'visible_difficulties': {
                'beginner': True,
                'intermediate': True,
                'advanced': True
            },
            'refresh_rate': 10,
            'students_per_page': 12
        })

# ==================== QUESTION FLAGGING ROUTES ====================

@app.route('/api/student/flag-question', methods=['POST'])
def flag_question():
    """Flag a question - works for both registered and guest users"""
    data = request.json

    question_id = data.get('question_id')
    flag_type = data.get('flag_type')
    description = data.get('description', '').strip()
    guest_email = data.get('guest_email', '').strip()  # Optional for guests

    if not all([question_id, flag_type, description]):
        return jsonify({'error': 'Question ID, flag type, and description are required'}), 400

    if flag_type not in ['incorrect', 'ambiguous', 'typo', 'other']:
        return jsonify({'error': 'Invalid flag type'}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    # Check if user is logged in
    if 'user_id' in session:
        # Registered user
        flag = QuestionFlag(
            question_id=question_id,
            user_id=session['user_id'],
            flag_type=flag_type,
            description=description
        )
    else:
        # Guest user - use IP address or session ID as identifier
        import hashlib
        guest_id = request.remote_addr or 'unknown'
        # Create a hash of IP + user agent for better privacy
        user_agent = request.headers.get('User-Agent', '')
        guest_identifier = hashlib.md5(f"{guest_id}{user_agent}".encode()).hexdigest()[:16]

        flag = QuestionFlag(
            question_id=question_id,
            user_id=None,
            guest_identifier=guest_identifier,
            guest_email=guest_email if guest_email else None,
            flag_type=flag_type,
            description=description
        )

    db.session.add(flag)
    db.session.commit()

    return jsonify({
        'message': 'Question flagged successfully. An administrator will review it.',
        'flag': flag.to_dict()
    }), 201

@app.route('/api/student/my-flags')
def get_my_flags():
    """Get all flags submitted by current user or guest"""
    if 'user_id' in session:
        # Registered user
        flags = QuestionFlag.query.filter_by(user_id=session['user_id']).order_by(QuestionFlag.created_at.desc()).all()
    else:
        # Guest user - use their identifier
        import hashlib
        guest_id = request.remote_addr or 'unknown'
        user_agent = request.headers.get('User-Agent', '')
        guest_identifier = hashlib.md5(f"{guest_id}{user_agent}".encode()).hexdigest()[:16]

        flags = QuestionFlag.query.filter_by(guest_identifier=guest_identifier).order_by(QuestionFlag.created_at.desc()).all()
    return jsonify([f.to_dict() for f in flags])

@app.route('/api/admin/flags/pending')
@login_required
@role_required('admin')
def get_pending_flags():
    """Get all pending question flags"""
    flags = QuestionFlag.query.filter_by(status='pending').order_by(QuestionFlag.created_at.desc()).all()

    flags_with_questions = []
    for flag in flags:
        flag_dict = flag.to_dict()
        flag_dict['question'] = flag.question.to_dict()
        flags_with_questions.append(flag_dict)

    return jsonify(flags_with_questions)

@app.route('/api/admin/flags/all')
@login_required
@role_required('admin')
def get_all_flags():
    """Get all question flags"""
    status_filter = request.args.get('status')

    query = QuestionFlag.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    flags = query.order_by(QuestionFlag.created_at.desc()).all()

    flags_with_questions = []
    for flag in flags:
        flag_dict = flag.to_dict()
        flag_dict['question'] = flag.question.to_dict()
        flags_with_questions.append(flag_dict)

    return jsonify(flags_with_questions)

@app.route('/api/admin/flag/<int:flag_id>/dismiss', methods=['POST'])
@login_required
@role_required('admin')
def dismiss_flag(flag_id):
    """Dismiss a flag without making changes"""
    flag = QuestionFlag.query.get_or_404(flag_id)
    data = request.json

    flag.status = 'dismissed'
    flag.admin_notes = data.get('notes', '')
    flag.resolved_at = datetime.utcnow()
    flag.resolved_by = session['user_id']

    db.session.commit()

    return jsonify({
        'message': 'Flag dismissed',
        'flag': flag.to_dict()
    })

@app.route('/api/admin/question/<int:question_id>')
@login_required
@role_required('admin')
def get_question_for_edit(question_id):
    """Get question details for editing"""
    question = Question.query.get_or_404(question_id)
    flags = QuestionFlag.query.filter_by(question_id=question_id).order_by(QuestionFlag.created_at.desc()).all()
    edits = QuestionEdit.query.filter_by(question_id=question_id).order_by(QuestionEdit.edited_at.desc()).all()

    return jsonify({
        'question': question.to_dict(),
        'flags': [f.to_dict() for f in flags],
        'edit_history': [e.to_dict() for e in edits]
    })

@app.route('/api/admin/all-questions')
@login_required
@role_required('admin')
def get_all_questions():
    """Get all questions with optional filters for management"""
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')

    query = Question.query

    if topic:
        query = query.filter_by(topic=topic)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    questions = query.order_by(Question.topic, Question.difficulty, Question.id).all()
    return jsonify([q.to_dict() for q in questions])

@app.route('/api/admin/question/<int:question_id>/edit', methods=['PUT'])
@login_required
@role_required('admin')
def edit_question(question_id):
    """Edit a question and track the changes"""
    question = Question.query.get_or_404(question_id)
    data = request.json

    edit_record = QuestionEdit(
        question_id=question_id,
        edited_by=session['user_id'],
        edit_type=data.get('edit_type', 'correction'),
        old_question_text=question.question_text,
        old_option_a=question.option_a,
        old_option_b=question.option_b,
        old_option_c=question.option_c,
        old_option_d=question.option_d,
        old_correct_answer=question.correct_answer,
        old_explanation=question.explanation,
        edit_notes=data.get('notes', '')
    )

    # Update topic if provided
    if 'topic' in data:
        question.topic = data['topic']

    # Update difficulty if provided
    if 'difficulty' in data:
        question.difficulty = data['difficulty']

    if 'question_text' in data:
        question.question_text = data['question_text']
        edit_record.new_question_text = data['question_text']
    else:
        edit_record.new_question_text = question.question_text

    if 'option_a' in data:
        question.option_a = data['option_a']
        edit_record.new_option_a = data['option_a']
    else:
        edit_record.new_option_a = question.option_a

    if 'option_b' in data:
        question.option_b = data['option_b']
        edit_record.new_option_b = data['option_b']
    else:
        edit_record.new_option_b = question.option_b

    if 'option_c' in data:
        question.option_c = data['option_c']
        edit_record.new_option_c = data['option_c']
    else:
        edit_record.new_option_c = question.option_c

    if 'option_d' in data:
        question.option_d = data['option_d']
        edit_record.new_option_d = data['option_d']
    else:
        edit_record.new_option_d = question.option_d

    if 'correct_answer' in data:
        question.correct_answer = data['correct_answer']
        edit_record.new_correct_answer = data['correct_answer']
    else:
        edit_record.new_correct_answer = question.correct_answer

    if 'explanation' in data:
        question.explanation = data['explanation']
        edit_record.new_explanation = data['explanation']
    else:
        edit_record.new_explanation = question.explanation

    db.session.add(edit_record)
    db.session.commit()

    if 'resolve_flag_ids' in data:
        for flag_id in data['resolve_flag_ids']:
            flag = QuestionFlag.query.get(flag_id)
            if flag and flag.question_id == question_id:
                flag.status = 'resolved'
                flag.resolved_at = datetime.utcnow()
                flag.resolved_by = session['user_id']
                flag.admin_notes = f"Question edited: {edit_record.edit_notes}"
        db.session.commit()

    return jsonify({
        'message': 'Question updated successfully',
        'question': question.to_dict(),
        'edit': edit_record.to_dict()
    })

@app.route('/api/admin/question/<int:question_id>/history')
@login_required
@role_required('admin')
def get_question_history(question_id):
    """Get complete edit history for a question"""
    question = Question.query.get_or_404(question_id)
    edits = QuestionEdit.query.filter_by(question_id=question_id).order_by(QuestionEdit.edited_at.desc()).all()

    return jsonify({
        'question': question.to_dict(),
        'edit_history': [e.to_dict() for e in edits]
    })

@app.route('/api/admin/questions/flagged')
@login_required
@role_required('admin')
def get_flagged_questions():
    """Get all questions that have pending flags"""
    flagged_question_ids = db.session.query(QuestionFlag.question_id).filter_by(status='pending').distinct().all()
    question_ids = [q[0] for q in flagged_question_ids]

    questions_with_flags = []
    for qid in question_ids:
        question = Question.query.get(qid)
        flags = QuestionFlag.query.filter_by(question_id=qid, status='pending').all()

        questions_with_flags.append({
            'question': question.to_dict(),
            'flag_count': len(flags),
            'flags': [f.to_dict() for f in flags]
        })

    return jsonify(questions_with_flags)

@app.route('/api/admin/flags/statistics')
@login_required
@role_required('admin')
def flag_statistics():
    """Get statistics about question flags"""
    stats = {
        'total_flags': QuestionFlag.query.count(),
        'pending_flags': QuestionFlag.query.filter_by(status='pending').count(),
        'resolved_flags': QuestionFlag.query.filter_by(status='resolved').count(),
        'dismissed_flags': QuestionFlag.query.filter_by(status='dismissed').count(),
        'flagged_questions': db.session.query(QuestionFlag.question_id).filter_by(status='pending').distinct().count(),
        'total_edits': QuestionEdit.query.count(),
        'by_flag_type': {}
    }

    for flag_type in ['incorrect', 'ambiguous', 'typo', 'other']:
        stats['by_flag_type'][flag_type] = QuestionFlag.query.filter_by(flag_type=flag_type, status='pending').count()

    return jsonify(stats)



# GET all users endpoint (frontend expects /api/admin/users plural)
@app.route('/api/admin/users', methods=['GET'])
@login_required
@role_required('admin')
def admin_get_all_users():
    """Get all users for admin management"""
    users = User.query.order_by(User.created_at.desc()).all()

    users_data = []
    for user in users:
        stats = UserStats.query.filter_by(user_id=user.id).first()
        quiz_count = QuizAttempt.query.filter_by(user_id=user.id).count()

        users_data.append({
            'id': user.id,
            'username': user.full_name,  # FIXED: Use full_name instead of username
            'email': user.email,
            'role': user.role,
            'is_approved': user.is_approved,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'total_quizzes': quiz_count,
            'total_points': stats.total_points if stats else 0,
            'level': stats.level if stats else 1
        })

    return jsonify(users_data), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default admin if doesn't exist
        admin = User.query.filter_by(email='admin@mathmaster.com').first()
        if not admin:
            admin = User(
                email='admin@mathmaster.com',
                full_name='System Administrator',
                role='admin',
                is_approved=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@mathmaster.com / admin123")

        # Create default badges if they don't exist
        if Badge.query.count() == 0:
            default_badges = [
                # Beginner badges
                Badge(name='First Steps', description='Complete your first quiz', icon='fa-star',
                      category='beginner', requirement_type='quizzes_completed', requirement_value=1,
                      points=10, color='yellow'),
                Badge(name='Curious Learner', description='Complete 5 quizzes', icon='fa-book',
                      category='progress', requirement_type='quizzes_completed', requirement_value=5,
                      points=20, color='blue'),
                Badge(name='Dedicated Student', description='Complete 10 quizzes', icon='fa-graduation-cap',
                      category='progress', requirement_type='quizzes_completed', requirement_value=10,
                      points=30, color='purple'),
                Badge(name='Math Enthusiast', description='Complete 25 quizzes', icon='fa-heart',
                      category='progress', requirement_type='quizzes_completed', requirement_value=25,
                      points=50, color='red'),
                Badge(name='Quiz Master', description='Complete 50 quizzes', icon='fa-trophy',
                      category='progress', requirement_type='quizzes_completed', requirement_value=50,
                      points=100, color='gold'),

                # Streak badges
                Badge(name='Week Warrior', description='Practice 7 days in a row', icon='fa-bolt',
                      category='streak', requirement_type='streak_days', requirement_value=7,
                      points=40, color='orange'),
                Badge(name='Unstoppable', description='Practice 14 days in a row', icon='fa-rocket',
                      category='streak', requirement_type='streak_days', requirement_value=14,
                      points=75, color='red'),

                # Mastery badges
                Badge(name='Topic Master', description='Master any topic (all 3 difficulties)', icon='fa-certificate',
                      category='mastery', requirement_type='topics_mastered', requirement_value=1,
                      points=30, color='green'),
                Badge(name='Subject Expert', description='Master 3 different topics', icon='fa-brain',
                      category='mastery', requirement_type='topics_mastered', requirement_value=3,
                      points=75, color='purple'),
                Badge(name='Mathematics Genius', description='Master 5 different topics', icon='fa-infinity',
                      category='mastery', requirement_type='topics_mastered', requirement_value=5,
                      points=150, color='gold'),

                # Accuracy badges
                Badge(name='Perfect Score', description='Get 100% on a quiz', icon='fa-gem',
                      category='accuracy', requirement_type='perfect_scores', requirement_value=1,
                      points=15, color='cyan'),
                Badge(name='Perfectionist', description='Get 5 perfect scores', icon='fa-star',
                      category='accuracy', requirement_type='perfect_scores', requirement_value=5,
                      points=50, color='gold'),
                Badge(name='High Achiever', description='Score 90%+ on 10 quizzes', icon='fa-bullseye',
                      category='accuracy', requirement_type='high_scores', requirement_value=10,
                      points=40, color='green'),
                Badge(name='Excellence Personified', description='Score 90%+ on 25 quizzes', icon='fa-crown',
                      category='accuracy', requirement_type='high_scores', requirement_value=25,
                      points=100, color='gold'),
            ]

            for badge in default_badges:
                db.session.add(badge)

            db.session.commit()
            print(f"✅ Created {len(default_badges)} default badges")

    app.run(debug=True)


# ============================================================
# Minimal class actions via simple HTML forms (stable)
# ============================================================

@app.route('/logout', methods=['GET'])
def logout_simple():
    session.clear()
    try:
        return redirect(url_for('index'))
    except Exception:
        return redirect('/')

@app.route('/teacher/class/<int:class_id>/rename', methods=['POST'], endpoint='teacher_simple_rename_class')
@login_required
@role_required('teacher')
@approved_required
def teacher_simple_rename_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403

    new_name = (request.form.get('new_name') or '').strip()
    if not new_name:
        flash('Class name cannot be empty.', 'error')
        return redirect('/teacher/classes')

    existing = Class.query.filter(
        Class.teacher_id == session['user_id'],
        Class.name == new_name,
        Class.id != class_id
    ).first()
    if existing:
        flash('You already have a class with that name.', 'error')
        return redirect('/teacher/classes')

    class_obj.name = new_name
    db.session.commit()
    flash('Class renamed successfully.', 'success')
    return redirect('/teacher/classes')

@app.route('/teacher/class/<int:class_id>/delete', methods=['POST'], endpoint='teacher_simple_delete_class')
@login_required
@role_required('teacher')
@approved_required
def teacher_simple_delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403

    ClassEnrollment.query.filter_by(class_id=class_id).delete()
    db.session.delete(class_obj)
    db.session.commit()
    flash('Class deleted.', 'success')
    return redirect('/teacher/classes')

# ==================== DUAL GUEST SYSTEM ====================
# Supports both casual guests and repeat guests with codes

# Animal codes for repeat guests
ANIMALS = [
    'ant', 'ape', 'bat', 'bear', 'bee', 'bird', 'cat', 'clam', 'cod', 'cow',
    'crab', 'crow', 'deer', 'dog', 'dove', 'duck', 'eagle', 'eel', 'elk', 'fish',
    'fly', 'fox', 'frog', 'gnat', 'goat', 'goose', 'hawk', 'hog', 'horse', 'jay',
    'lark', 'lion', 'loon', 'lynx', 'mink', 'mole', 'moth', 'mouse', 'mule', 'newt',
    'orca', 'owl', 'ox', 'panda', 'pig', 'puma', 'rat', 'ray', 'seal', 'shark',
    'sheep', 'shrew', 'sloth', 'slug', 'snail', 'snake', 'swan', 'tiger', 'toad', 'trout',
    'viper', 'vole', 'wasp', 'whale', 'wolf', 'worm', 'yak', 'zebra', 'bison', 'boar',
    'bunny', 'camel', 'cobra', 'coral', 'crane', 'dingo', 'drake', 'gecko', 'hippo', 'hyena',
    'koala', 'lemur', 'llama', 'moose', 'otter', 'pony', 'quail', 'raven', 'rhino', 'robin',
    'skunk', 'squid', 'stork', 'tapir', 'tern', 'tuna', 'weasel', 'betta', 'finch', 'guppy'
]

def generate_guest_code():
    """Generate unique animal code (e.g., panda42)"""
    max_attempts = 100

    for _ in range(max_attempts):
        animal = random.choice(ANIMALS)
        number = random.randint(0, 99)
        code = f"{animal}{number:02d}"

        # Check if code is already taken
        from sqlalchemy import text
        existing = db.session.execute(
            text("SELECT 1 FROM guest_users WHERE guest_code = :code"),
            {"code": code}
        ).fetchone()

        if not existing:
            return code

    raise Exception("Could not generate unique guest code. Please try again.")


def get_current_user_info():
    """
    Get user info for either full account, repeat guest, or casual guest
    Returns dict with user data or None
    """
    # Check full account
    if 'user_id' in session and 'guest_code' not in session and not session.get('is_guest'):
        user = User.query.get(session['user_id'])
        if user and user.email != 'guest@mathmaster.app':
            return {
                'type': 'full',
                'id': user.id,
                'name': user.full_name,
                'email': user.email,
                'role': user.role,
                'total_score': getattr(user, 'total_score', 0),
                'quizzes_completed': getattr(user, 'quizzes_completed', 0)
            }

    # Check repeat guest
    if 'guest_code' in session:
        from sqlalchemy import text
        result = db.session.execute(
            text("""SELECT guest_code, total_score, quizzes_completed, created_at, last_active
               FROM guest_users WHERE guest_code = :code AND is_active = 1"""),
            {"code": session['guest_code']}
        ).fetchone()

        if result:
            return {
                'type': 'repeat_guest',
                'guest_code': result[0],
                'name': f"Guest {result[0].title()}",
                'total_score': result[1] or 0,
                'quizzes_completed': result[2] or 0,
                'created_at': result[3],
                'last_active': result[4]
            }

    # Check casual guest (shared guest@mathmaster.app user)
    if session.get('is_guest') and 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.email == 'guest@mathmaster.app':
            return {
                'type': 'casual_guest',
                'name': 'Guest User',
                'session_id': session.get('guest_session_id', 'unknown')
            }

    return None


def update_guest_last_active(guest_code):
    """Update last_active timestamp for repeat guest"""
    from sqlalchemy import text
    db.session.execute(
        text("UPDATE guest_users SET last_active = :now WHERE guest_code = :code"),
        {"now": datetime.utcnow(), "code": guest_code}
    )
    db.session.commit()


# ==================== CASUAL GUEST ROUTES ====================

@app.route('/api/casual-guest-start', methods=['POST'])
def casual_guest_start():
    """Initialize casual guest session (temporary, no code)"""
    try:
        session.clear()

        # Get or create the shared casual guest user
        guest_user = User.query.filter_by(email='guest@mathmaster.app').first()

        if not guest_user:
            guest_user = User(
                email='guest@mathmaster.app',
                password_hash='no_password_required',
                full_name='Guest User',
                role='student',
                is_approved=True
            )
            db.session.add(guest_user)
            db.session.commit()

        # Set up casual guest session
        session['is_guest'] = True
        session['guest_session_id'] = str(uuid.uuid4())
        session['user_id'] = guest_user.id
        session['role'] = 'student'
        session['guest_type'] = 'casual'

        return jsonify({
            'success': True,
            'message': 'Casual guest session started',
            'redirect': '/student'
        }), 200

    except Exception as e:
        print(f"Error starting casual guest session: {e}")
        db.session.rollback()
        return jsonify({'error': f'Failed to start guest session: {str(e)}'}), 500


# ==================== REPEAT GUEST ROUTES ====================

@app.route('/api/repeat-guest/generate', methods=['POST'])
def generate_repeat_guest():
    """Generate new repeat guest code"""
    try:
        from sqlalchemy import text

        # Generate unique code
        code = generate_guest_code()

        # Create guest user in database
        db.session.execute(text("""
            INSERT INTO guest_users (guest_code, created_at, last_active)
            VALUES (:code, :now, :now)
        """), {"code": code, "now": datetime.utcnow()})
        db.session.commit()

        return jsonify({
            'success': True,
            'guest_code': code,
            'message': f'Your code is: {code}'
        }), 200

    except Exception as e:
        print(f"Error generating guest code: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to generate code. Please try again.'}), 500


@app.route('/api/repeat-guest/login', methods=['POST'])
def repeat_guest_login():
    """Login with repeat guest code"""
    try:
        from sqlalchemy import text
        data = request.json
        code = data.get('guest_code', '').strip().lower()

        if not code:
            return jsonify({'error': 'Please enter your guest code'}), 400

        # Check if code exists and is active
        result = db.session.execute(
            text("SELECT guest_code FROM guest_users WHERE guest_code = :code AND is_active = 1"),
            {"code": code}
        ).fetchone()

        if not result:
            return jsonify({'error': 'Code not found. Please check and try again.'}), 404

        # Get or create the shared guest user for repeat guests
        guest_user = User.query.filter_by(email='guest@mathmaster.app').first()

        if not guest_user:
            guest_user = User(
                email='guest@mathmaster.app',
                password_hash='no_password_required',
                full_name='Guest User',
                role='student',
                is_approved=True
            )
            db.session.add(guest_user)
            db.session.commit()

        # Set up repeat guest session
        session.clear()
        session['guest_code'] = code
        session['user_id'] = guest_user.id  # CRITICAL: Set user_id for @login_required
        session['role'] = 'student'
        session['guest_type'] = 'repeat'

        # Update last active
        update_guest_last_active(code)

        return jsonify({
            'success': True,
            'message': 'Welcome back!',
            'redirect': '/student'
        }), 200

    except Exception as e:
        print(f"Error logging in guest: {e}")
        db.session.rollback()
        return jsonify({'error': 'Login failed. Please try again.'}), 500


@app.route('/api/repeat-guest/stats')
def repeat_guest_stats():
    """Get stats for current repeat guest"""
    if 'guest_code' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        from sqlalchemy import text
        code = session['guest_code']

        # Get stats
        result = db.session.execute(text("""
            SELECT
                total_score,
                quizzes_completed,
                (SELECT COUNT(*) FROM guest_badges WHERE guest_code = :code) as badges_earned
            FROM guest_users
            WHERE guest_code = :code
        """), {"code": code}).fetchone()

        if result:
            return jsonify({
                'total_score': result[0] or 0,
                'quizzes_completed': result[1] or 0,
                'badges_earned': result[2] or 0
            }), 200

        return jsonify({'error': 'Stats not found'}), 404

    except Exception as e:
        print(f"Error getting guest stats: {e}")
        return jsonify({'error': 'Failed to load stats'}), 500


@app.route('/api/repeat-guest/convert', methods=['POST'])
def convert_guest_to_full():
    """Convert repeat guest to full account"""
    if 'guest_code' not in session:
        return jsonify({'error': 'Not logged in as guest'}), 401

    try:
        from sqlalchemy import text
        data = request.json

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()

        # Validation
        if not email or not password or not full_name:
            return jsonify({'error': 'All fields required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Check if email already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 400

        guest_code = session['guest_code']

        # Get guest data
        guest_data = db.session.execute(text("""
            SELECT total_score, quizzes_completed
            FROM guest_users
            WHERE guest_code = :code
        """), {"code": guest_code}).fetchone()

        # Create new full user account
        new_user = User(
            email=email,
            full_name=full_name,
            role='student',
            is_approved=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Migrate quiz attempts
        db.session.execute(text("""
            INSERT INTO quiz_attempts (user_id, topic, difficulty, score, total_questions, completed_at)
            SELECT :user_id, topic, difficulty, score, total_questions, completed_at
            FROM guest_quiz_attempts
            WHERE guest_code = :code
        """), {"user_id": new_user.id, "code": guest_code})

        # Migrate badges
        db.session.execute(text("""
            INSERT INTO user_badges (user_id, badge_id, earned_at)
            SELECT :user_id, badge_id, earned_at
            FROM guest_badges
            WHERE guest_code = :code
        """), {"user_id": new_user.id, "code": guest_code})

        # Deactivate guest account
        db.session.execute(
            text("UPDATE guest_users SET is_active = 0 WHERE guest_code = :code"),
            {"code": guest_code}
        )

        db.session.commit()

        # Switch session to full account
        session.clear()
        session['user_id'] = new_user.id
        session['role'] = 'student'

        return jsonify({
            'success': True,
            'message': 'Account upgraded successfully!',
            'redirect': '/student'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error converting guest account: {e}")
        return jsonify({'error': 'Upgrade failed. Please try again.'}), 500


@app.route('/api/guest-leaderboard')
def guest_leaderboard():
    """
    Universal leaderboard showing top 20 guest users across all codes.
    Ranked by total score (sum of all correct answers).
    Public endpoint - no authentication required.
    """
    try:
        from sqlalchemy import text

        # Query to get aggregated stats for each guest_code
        query = text("""
            SELECT
                guest_code,
                COUNT(*) as total_quizzes,
                SUM(score) as total_score,
                SUM(total_questions) as total_questions_attempted,
                ROUND(AVG(CAST(score AS FLOAT) / CAST(total_questions AS FLOAT) * 100), 1) as avg_percentage,
                MIN(completed_at) as first_quiz_date,
                MAX(completed_at) as last_quiz_date
            FROM guest_quiz_attempts
            WHERE guest_code IS NOT NULL
            GROUP BY guest_code
            HAVING COUNT(*) > 0
            ORDER BY total_score DESC
            LIMIT 20
        """)

        results = db.session.execute(query).fetchall()

        leaderboard = []
        for rank, row in enumerate(results, start=1):
            # Use array indexing [0], [1], etc. instead of row.attribute
            guest_code = row[0]
            total_quizzes = row[1]
            total_score = row[2]
            total_questions = row[3]
            avg_percentage = row[4]
            first_quiz_date = row[5]
            last_quiz_date = row[6]

            # Generate guest display name from code
            guest_display = f"Guest-{guest_code[:6]}"

            # Handle dates safely (they might be strings already)
            first_quiz = str(first_quiz_date)[:10] if first_quiz_date else None
            last_quiz = str(last_quiz_date)[:10] if last_quiz_date else None

            leaderboard.append({
                'rank': rank,
                'guest_code': guest_code,
                'display_name': guest_display,
                'total_quizzes': int(total_quizzes),
                'total_score': int(total_score),
                'total_questions': int(total_questions),
                'avg_percentage': float(avg_percentage) if avg_percentage else 0.0,
                'first_quiz': first_quiz,
                'last_quiz': last_quiz
            })

        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'total_guests': len(leaderboard)
        })

    except Exception as e:
        print(f"❌ Error fetching guest leaderboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to load leaderboard',
            'leaderboard': []
        }), 500


def cleanup_inactive_guests(days=30):
    """
    Delete guest accounts that haven't been used in X days
    Returns number of deleted accounts
    """
    from sqlalchemy import text
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    result = db.session.execute(text("""
        DELETE FROM guest_users
        WHERE last_active < :cutoff AND is_active = 1
    """), {"cutoff": cutoff_date})

    db.session.commit()
    return result.rowcount

