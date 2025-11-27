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

# ==================== AUTHENTICATION ROUTES ====================

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
        'bodmas': {'title': 'BODMAS', 'icon': 'book', 'color': 'bg-green-500'},
        'functions': {'title': 'Functions', 'icon': 'chart', 'color': 'bg-purple-500'},
        'sets': {'title': 'Sets', 'icon': 'layers', 'color': 'bg-orange-500'}
    }
    return jsonify(topics)

@app.route('/api/questions/<topic>/<difficulty>')
@login_required
@approved_required
def get_questions(topic, difficulty):
    questions = Question.query.filter_by(topic=topic, difficulty=difficulty).all()
    questions_list = [q.to_dict() for q in questions]
    random.shuffle(questions_list)
    return jsonify(questions_list[:20])

@app.route('/api/submit-quiz', methods=['POST'])
@login_required
@approved_required
def submit_quiz():
    data = request.json
    
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
    
    return jsonify({
        'message': 'Quiz submitted successfully',
        'attempt': attempt.to_dict()
    }), 201

@app.route('/api/my-progress')
@login_required
def my_progress():
    attempts = QuizAttempt.query.filter_by(user_id=session['user_id']).order_by(QuizAttempt.completed_at.desc()).all()
    return jsonify([a.to_dict() for a in attempts])

# ==================== TEACHER ROUTES ====================

@app.route('/teacher')
@login_required
@role_required('teacher')
@approved_required
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

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
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    students = User.query.filter(
        User.role == 'student',
        (User.email.ilike(f'%{query}%')) | (User.full_name.ilike(f'%{query}%'))
    ).limit(20).all()
    
    return jsonify([s.to_dict() for s in students])

@app.route('/api/teacher/class/<int:class_id>/enroll', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def enroll_student(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return jsonify({'error': 'Invalid student'}), 400
    
    # Check if already enrolled
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
    class_obj = Class.query.get_or_404(class_id)
    
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    
    students_data = []
    for enrollment in enrollments:
        student = enrollment.student
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
    """Real-time class performance dashboard"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return render_template('class_dashboard_matrix.html', class_id=class_id, class_name=class_obj.name)

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
    topics = ['arithmetic', 'fractions', 'bodmas', 'functions', 'sets']
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin if doesn't exist
        admin = User.query.filter_by(email='admin@agentmath.app').first()
        if not admin:
            admin = User(
                email='admin@agentmath.app',
                full_name='System Administrator',
                role='admin',
                is_approved=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@agentmath.app / admin123")
    
    app.run(debug=True)
