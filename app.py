from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import random
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mathquiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    """Track user-reported issues with questions"""
    __tablename__ = 'question_flags'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'user_name': self.reporter.full_name,
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
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
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
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.role == 'teacher' and not user.is_approved:
            return jsonify({'error': 'Teacher account pending approval'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== BADGES HELPER FUNCTIONS ====================

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
        'user': user.to_dict()
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/current-user')
@login_required
def current_user():
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict()), 200

# ==================== STUDENT ROUTES ====================

@app.route('/app')
@login_required
@approved_required
def student_app():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return redirect(url_for('index'))
    return render_template('student_app.html')

@app.route('/api/topics')
@login_required
@approved_required
def get_topics():
    topics = {
        'arithmetic': {'title': 'Arithmetic', 'icon': 'calculator', 'color': 'bg-red-500'},
        'fractions': {'title': 'Fractions', 'icon': 'divide', 'color': 'bg-blue-500'},
        'decimals': {'title': 'Decimals', 'icon': 'percent', 'color': 'bg-teal-500'},
        'multiplication_division': {'title': 'Multiplication & Division', 'icon': 'x', 'color': 'bg-indigo-500'},
        'bodmas': {'title': 'BODMAS', 'icon': 'book', 'color': 'bg-green-500'},
        'functions': {'title': 'Functions', 'icon': 'chart', 'color': 'bg-purple-500'},
        'sets': {'title': 'Sets', 'icon': 'layers', 'color': 'bg-orange-500'},
        'probability': {'title': 'Probability', 'icon': 'dice', 'color': 'bg-yellow-500'},
        'complex_numbers_intro': {'title': 'Complex Numbers Intro', 'icon': 'infinity', 'color': 'bg-pink-500'},
        'complex_numbers_expanded': {'title': 'Complex Numbers - Expanded', 'icon': 'rotate', 'color': 'bg-fuchsia-600'}
    }
    return jsonify(topics)

@app.route('/api/questions/<topic>/<difficulty>')
@login_required
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
@login_required
@approved_required
def submit_quiz():
    """Submit quiz and update stats/badges"""
    data = request.json

    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=session['user_id'],
        topic=data.get('topic'),
        difficulty=data.get('difficulty'),
        score=data.get('score'),
        total_questions=data.get('total_questions'),
        percentage=data.get('percentage'),
        time_taken=data.get('time_taken')
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
@login_required
def my_progress():
    attempts = QuizAttempt.query.filter_by(user_id=session['user_id']).order_by(QuizAttempt.completed_at.desc()).all()
    return jsonify([a.to_dict() for a in attempts])

# ==================== BADGES API ROUTES ====================

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

@app.route('/api/student/mastery')
@login_required
@approved_required
def get_student_mastery():
    """
    Get student's mastery status for all topics and difficulties.
    Returns best score for each topic/difficulty combination.
    Mastery threshold: >80%
    """
    user_id = session['user_id']

    # Get all topics
    topics = [
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'bodmas', 'functions', 'sets', 'probability', 'complex_numbers_intro', 'complex_numbers_expanded'
    ]
    difficulties = ['beginner', 'intermediate', 'advanced']

    mastery_data = {}

    for topic in topics:
        mastery_data[topic] = {
            'difficulties': {},
            'topic_mastered': False
        }

        mastered_count = 0

        for difficulty in difficulties:
            # Get best score for this topic/difficulty
            best_attempt = QuizAttempt.query.filter_by(
                user_id=user_id,
                topic=topic,
                difficulty=difficulty
            ).order_by(QuizAttempt.percentage.desc()).first()

            if best_attempt and best_attempt.percentage > 80:
                mastery_data[topic]['difficulties'][difficulty] = {
                    'mastered': True,
                    'best_score': round(best_attempt.percentage, 1)
                }
                mastered_count += 1
            else:
                mastery_data[topic]['difficulties'][difficulty] = {
                    'mastered': False,
                    'best_score': round(best_attempt.percentage, 1) if best_attempt else 0
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
    topics = ['arithmetic', 'fractions', 'decimals', 'multiplication_division', 'bodmas', 'functions', 'sets', 'probability', 'complex_numbers_intro', 'complex_numbers_expanded']
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

    return render_template('teacher_class_dashboard_improved.html',
                         class_id=class_id,
                         class_name=class_obj.name)

@app.route('/api/teacher/class/<int:class_id>/matrix-data')
@login_required
@role_required('teacher')
@approved_required
def get_class_matrix_data(class_id):
    """Get matrix data for class dashboard"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all students in class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()

    # All topics and difficulties
    topics = ['arithmetic', 'fractions', 'decimals', 'multiplication_division', 'bodmas', 'functions', 'sets', 'probability', 'complex_numbers_intro', 'complex_numbers_expanded']
    difficulties = ['beginner', 'intermediate', 'advanced']

    # Build matrix data
    matrix_data = []

    for enrollment in enrollments:
        student = enrollment.student
        student_data = {
            'student_id': student.id,
            'student_name': student.full_name,
            'modules': {}
        }

        # For each topic/difficulty combination
        for topic in topics:
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
        'topics': topics,
        'difficulties': difficulties,
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
@login_required
def flag_question():
    """Student/Teacher flags a question as incorrect or ambiguous"""
    data = request.json

    question_id = data.get('question_id')
    flag_type = data.get('flag_type')
    description = data.get('description', '').strip()

    if not all([question_id, flag_type, description]):
        return jsonify({'error': 'Question ID, flag type, and description are required'}), 400

    if flag_type not in ['incorrect', 'ambiguous', 'typo', 'other']:
        return jsonify({'error': 'Invalid flag type'}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    flag = QuestionFlag(
        question_id=question_id,
        user_id=session['user_id'],
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
@login_required
def get_my_flags():
    """Get all flags submitted by current user"""
    flags = QuestionFlag.query.filter_by(user_id=session['user_id']).order_by(QuestionFlag.created_at.desc()).all()
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
