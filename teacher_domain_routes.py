# ==================== TEACHER DOMAIN ACCESS ROUTES ====================
# Add these routes to your app.py in the Teacher Routes section

@app.route('/api/teacher/my-domain-access')
@login_required
@role_required('teacher')
@approved_required
def get_my_domain_access():
    """Get current teacher's domain access information"""
    teacher_id = session['user_id']
    
    # Get assigned domains
    access_records = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).all()
    
    # Get statistics
    stats = get_teacher_domain_statistics(teacher_id)
    
    # Get pending requests
    pending_requests = DomainAccessRequest.query.filter_by(
        teacher_id=teacher_id,
        status='pending'
    ).all()
    
    # Get all domains in system
    all_domains = get_all_domains_in_system()
    
    # Filter out domains already assigned or requested
    assigned_domains = [r.email_domain for r in access_records]
    requested_domains = [r.email_domain for r in pending_requests]
    
    available_to_request = [
        d for d in all_domains 
        if d['domain'] not in assigned_domains and d['domain'] not in requested_domains
    ]
    
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
    
    # Validate domain format
    if '.' not in domain or '@' in domain:
        return jsonify({'error': 'Invalid domain format. Use format like: school.edu'}), 400
    
    # Check if already has access
    existing_access = TeacherDomainAccess.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain
    ).first()
    
    if existing_access:
        return jsonify({'error': 'You already have access to this domain'}), 400
    
    # Check if already has pending request
    existing_request = DomainAccessRequest.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'You already have a pending request for this domain'}), 400
    
    # Create new request
    access_request = DomainAccessRequest(
        teacher_id=teacher_id,
        email_domain=domain,
        reason=reason
    )
    
    db.session.add(access_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Domain access request submitted successfully',
        'request': access_request.to_dict()
    }), 201


@app.route('/api/teacher/domain-requests')
@login_required
@role_required('teacher')
@approved_required
def get_my_domain_requests():
    """Get all domain access requests by the current teacher"""
    teacher_id = session['user_id']
    
    requests = DomainAccessRequest.query.filter_by(
        teacher_id=teacher_id
    ).order_by(DomainAccessRequest.requested_at.desc()).all()
    
    return jsonify({
        'requests': [r.to_dict() for r in requests]
    })


@app.route('/api/teacher/domain-requests/<int:request_id>', methods=['DELETE'])
@login_required
@role_required('teacher')
@approved_required
def cancel_domain_request(request_id):
    """Cancel a pending domain access request"""
    teacher_id = session['user_id']
    
    access_request = DomainAccessRequest.query.get_or_404(request_id)
    
    # Verify ownership
    if access_request.teacher_id != teacher_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Can only cancel pending requests
    if access_request.status != 'pending':
        return jsonify({'error': 'Can only cancel pending requests'}), 400
    
    db.session.delete(access_request)
    db.session.commit()
    
    return jsonify({'message': 'Request cancelled successfully'})
