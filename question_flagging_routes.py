# Add these new models and routes to app_with_matrix.py

# ==================== NEW DATABASE MODELS ====================

# Add after the Question model (around line 101):

class QuestionFlag(db.Model):
    """Track user-reported issues with questions"""
    __tablename__ = 'question_flags'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flag_type = db.Column(db.String(50), nullable=False)  # 'incorrect', 'ambiguous', 'typo', 'other'
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'resolved', 'dismissed'
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
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
    edit_type = db.Column(db.String(50), nullable=False)  # 'correction', 'clarification', 'update'
    
    # Store old values
    old_question_text = db.Column(db.Text)
    old_option_a = db.Column(db.String(100))
    old_option_b = db.Column(db.String(100))
    old_option_c = db.Column(db.String(100))
    old_option_d = db.Column(db.String(100))
    old_correct_answer = db.Column(db.Integer)
    old_explanation = db.Column(db.Text)
    
    # Store new values
    new_question_text = db.Column(db.Text)
    new_option_a = db.Column(db.String(100))
    new_option_b = db.Column(db.String(100))
    new_option_c = db.Column(db.String(100))
    new_option_d = db.Column(db.String(100))
    new_correct_answer = db.Column(db.Integer)
    new_explanation = db.Column(db.Text)
    
    edit_notes = db.Column(db.Text)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='edit_history')
    editor = db.relationship('User', backref='question_edits')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'edited_by': self.editor.full_name,
            'edit_type': self.edit_type,
            'edit_notes': self.edit_notes,
            'edited_at': self.edited_at.isoformat(),
            'changes': self.get_changes()
        }
    
    def get_changes(self):
        """Return only the fields that changed"""
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
        return changes

# ==================== STUDENT FLAG ROUTES ====================

@app.route('/api/student/flag-question', methods=['POST'])
@login_required
def flag_question():
    """Student/Teacher flags a question as incorrect or ambiguous"""
    data = request.json
    
    question_id = data.get('question_id')
    flag_type = data.get('flag_type')  # 'incorrect', 'ambiguous', 'typo', 'other'
    description = data.get('description', '').strip()
    
    if not all([question_id, flag_type, description]):
        return jsonify({'error': 'Question ID, flag type, and description are required'}), 400
    
    if flag_type not in ['incorrect', 'ambiguous', 'typo', 'other']:
        return jsonify({'error': 'Invalid flag type'}), 400
    
    # Check if question exists
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Create flag
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

# ==================== ADMIN FLAG MANAGEMENT ROUTES ====================

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
    """Get all question flags (pending, resolved, dismissed)"""
    status_filter = request.args.get('status')  # Optional filter
    
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

# ==================== ADMIN QUESTION EDITING ROUTES ====================

@app.route('/api/admin/question/<int:question_id>')
@login_required
@role_required('admin')
def get_question_for_edit(question_id):
    """Get question details for editing"""
    question = Question.query.get_or_404(question_id)
    
    # Get flags for this question
    flags = QuestionFlag.query.filter_by(question_id=question_id).order_by(QuestionFlag.created_at.desc()).all()
    
    # Get edit history
    edits = QuestionEdit.query.filter_by(question_id=question_id).order_by(QuestionEdit.edited_at.desc()).all()
    
    return jsonify({
        'question': question.to_dict(),
        'flags': [f.to_dict() for f in flags],
        'edit_history': [e.to_dict() for e in edits]
    })

@app.route('/api/admin/question/<int:question_id>/edit', methods=['PUT'])
@login_required
@role_required('admin')
def edit_question(question_id):
    """Edit a question and track the changes"""
    question = Question.query.get_or_404(question_id)
    data = request.json
    
    # Create edit record with old values
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
    
    # Update question with new values
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
    
    # Save edit record and updated question
    db.session.add(edit_record)
    db.session.commit()
    
    # If this was in response to a flag, mark flags as resolved
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
    # Get unique question IDs with pending flags
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

# ==================== STATISTICS ROUTES ====================

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
    
    # Count by flag type
    for flag_type in ['incorrect', 'ambiguous', 'typo', 'other']:
        stats['by_flag_type'][flag_type] = QuestionFlag.query.filter_by(flag_type=flag_type, status='pending').count()
    
    return jsonify(stats)
