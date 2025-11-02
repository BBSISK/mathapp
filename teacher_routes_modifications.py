# ==================== MODIFY EXISTING TEACHER ROUTES ====================
# These are the modifications needed to existing routes in app.py

# ===== 1. MODIFY: @app.route('/api/teacher/students/search') =====
# FIND this function around line 1272:

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

# REPLACE WITH:

@app.route('/api/teacher/students/search')
@login_required
@role_required('teacher')
@approved_required
def search_students():
    query = request.args.get('q', '').strip()
    teacher_id = session['user_id']

    if len(query) < 2:
        return jsonify([])

    # Build base query
    students_query = User.query.filter(
        User.role == 'student',
        (User.email.ilike(f'%{query}%')) | (User.full_name.ilike(f'%{query}%'))
    )
    
    # Apply domain filtering
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    
    if accessible_domains is not None:  # Teacher has restrictions
        # Filter by accessible domains
        filtered_ids = []
        for student in students_query.all():
            student_domain = extract_domain(student.email)
            if student_domain in accessible_domains:
                filtered_ids.append(student.id)
        
        students_query = students_query.filter(User.id.in_(filtered_ids)) if filtered_ids else students_query.filter(User.id == -1)
    
    students = students_query.limit(20).all()
    return jsonify([s.to_dict() for s in students])


# ===== 2. MODIFY: @app.route('/api/teacher/available-students/<int:class_id>') =====
# FIND this function around line 1467:

@app.route('/api/teacher/available-students/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def get_available_students(class_id):
    """Get all students NOT enrolled in this class"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get IDs of students already enrolled
    enrolled_ids = db.session.query(ClassEnrollment.student_id)\
        .filter_by(class_id=class_id)\
        .all()
    enrolled_ids = [e[0] for e in enrolled_ids]

    # Get all students NOT in the enrolled list
    available_students = User.query\
        .filter(User.role == 'student')\
        .filter(~User.id.in_(enrolled_ids))\
        .order_by(User.full_name)\
        .all()

    return jsonify([{
        'id': s.id,
        'full_name': s.full_name,
        'email': s.email
    } for s in available_students])

# REPLACE WITH:

@app.route('/api/teacher/available-students/<int:class_id>')
@login_required
@role_required('teacher')
@approved_required
def get_available_students(class_id):
    """Get all students NOT enrolled in this class (filtered by domain access)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']

    # Verify teacher owns this class
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get IDs of students already enrolled
    enrolled_ids = db.session.query(ClassEnrollment.student_id)\
        .filter_by(class_id=class_id)\
        .all()
    enrolled_ids = [e[0] for e in enrolled_ids]

    # Get all students NOT in the enrolled list
    available_students_query = User.query\
        .filter(User.role == 'student')\
        .filter(~User.id.in_(enrolled_ids))
    
    # Apply domain filtering
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    
    if accessible_domains is not None:  # Teacher has restrictions
        # Filter by accessible domains
        filtered_ids = []
        for student in available_students_query.all():
            student_domain = extract_domain(student.email)
            if student_domain in accessible_domains:
                filtered_ids.append(student.id)
        
        available_students_query = available_students_query.filter(User.id.in_(filtered_ids)) if filtered_ids else available_students_query.filter(User.id == -1)
    
    available_students = available_students_query.order_by(User.full_name).all()

    return jsonify([{
        'id': s.id,
        'full_name': s.full_name,
        'email': s.email
    } for s in available_students])


# ===== 3. MODIFY: @app.route('/api/teacher/class/<int:class_id>/students-list') =====
# FIND this function around line 1551:

@app.route('/api/teacher/class/<int:class_id>/students-list')
@login_required
@role_required('teacher')
@approved_required
def get_class_students_list(class_id):
    """Get detailed list of students in a class with their progress"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify teacher owns this class
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all enrollments for this class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    
    # ... rest of the function

# REPLACE WITH:

@app.route('/api/teacher/class/<int:class_id>/students-list')
@login_required
@role_required('teacher')
@approved_required
def get_class_students_list(class_id):
    """Get detailed list of students in a class with their progress (filtered by domain)"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']

    # Verify teacher owns this class
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all enrollments for this class
    enrollments = ClassEnrollment.query.filter_by(class_id=class_id).all()
    
    # Apply domain filtering
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    
    if accessible_domains is not None:  # Teacher has restrictions
        # Filter enrollments by accessible domains
        filtered_enrollments = []
        for enrollment in enrollments:
            student = User.query.get(enrollment.student_id)
            if student:
                student_domain = extract_domain(student.email)
                if student_domain in accessible_domains:
                    filtered_enrollments.append(enrollment)
        enrollments = filtered_enrollments
    
    # ... rest of the function continues as before


# ===== 4. ADD VALIDATION: @app.route('/api/teacher/class/<int:class_id>/enroll', methods=['POST']) =====
# FIND this function around line 1289 and ADD domain check before enrollment:

@app.route('/api/teacher/class/<int:class_id>/enroll', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def enroll_student(class_id):
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']

    # Verify teacher owns this class
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400

    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return jsonify({'error': 'Invalid student'}), 400

    # ===== ADD THIS DOMAIN ACCESS CHECK =====
    student_domain = extract_domain(student.email)
    if not teacher_has_domain_access(teacher_id, student_domain):
        return jsonify({
            'error': f'Access denied. You do not have permission to enroll students from the domain: {student_domain}. Please request access from an administrator.'
        }), 403
    # ===== END OF NEW CODE =====

    # Check if already enrolled
    existing = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
    if existing:
        return jsonify({'error': 'Student already enrolled'}), 400

    enrollment = ClassEnrollment(class_id=class_id, student_id=student_id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({'message': 'Student enrolled successfully'}), 201


# ===== 5. ADD VALIDATION: @app.route('/api/teacher/class/<int:class_id>/enroll-bulk', methods=['POST']) =====
# FIND this function around line 1498 and ADD domain check in the loop:

@app.route('/api/teacher/class/<int:class_id>/enroll-bulk', methods=['POST'])
@login_required
@role_required('teacher')
@approved_required
def enroll_students_bulk(class_id):
    """Enroll multiple students at once"""
    class_obj = Class.query.get_or_404(class_id)
    teacher_id = session['user_id']

    # Verify teacher owns this class
    if class_obj.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    student_ids = data.get('student_ids', [])

    if not student_ids:
        return jsonify({'error': 'No students selected'}), 400

    enrolled_count = 0
    already_enrolled = 0
    access_denied = []  # ===== ADD THIS =====

    for student_id in student_ids:
        # ===== ADD DOMAIN CHECK =====
        student = User.query.get(student_id)
        if student:
            student_domain = extract_domain(student.email)
            if not teacher_has_domain_access(teacher_id, student_domain):
                access_denied.append({
                    'id': student_id,
                    'name': student.full_name,
                    'domain': student_domain
                })
                continue
        # ===== END NEW CODE =====
        
        # Check if already enrolled
        existing = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
        if existing:
            already_enrolled += 1
            continue

        enrollment = ClassEnrollment(class_id=class_id, student_id=student_id)
        db.session.add(enrollment)
        enrolled_count += 1

    db.session.commit()

    response = {
        'message': f'Enrolled {enrolled_count} students',
        'enrolled_count': enrolled_count,
        'already_enrolled': already_enrolled
    }
    
    # ===== ADD THIS =====
    if access_denied:
        response['access_denied'] = access_denied
        response['access_denied_count'] = len(access_denied)
    # ===== END NEW CODE =====

    return jsonify(response)


# ===== SUMMARY OF CHANGES =====
# 1. search_students: Filter search results by accessible domains
# 2. get_available_students: Only show students from accessible domains
# 3. get_class_students_list: Filter class roster by accessible domains
# 4. enroll_student: Block enrollment of students from restricted domains
# 5. enroll_students_bulk: Block bulk enrollment of students from restricted domains
