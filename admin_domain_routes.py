# ==================== ADMIN DOMAIN MANAGEMENT ROUTES ====================
# Add these routes to your app.py in the Admin Routes section

@app.route('/api/admin/domains')
@login_required
@role_required('admin')
def get_all_domains():
    """Get all email domains in the system with statistics"""
    domains = get_all_domains_in_system()
    
    # Sort by student count descending
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
    
    # Get assigned domains
    access_records = TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).all()
    
    # Get statistics
    stats = get_teacher_domain_statistics(teacher_id)
    
    # Get all available domains
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
    
    # Validate domain format (basic check)
    if '.' not in domain or '@' in domain:
        return jsonify({'error': 'Invalid domain format. Use format like: school.edu'}), 400
    
    # Check if already assigned
    existing = TeacherDomainAccess.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain
    ).first()
    
    if existing:
        return jsonify({'error': 'Domain already assigned to this teacher'}), 400
    
    # Create new access record
    access = TeacherDomainAccess(
        teacher_id=teacher_id,
        email_domain=domain,
        granted_by=session['user_id'],
        notes=notes
    )
    
    db.session.add(access)
    
    # If there's a pending request for this domain, mark it as approved
    pending_request = DomainAccessRequest.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain,
        status='pending'
    ).first()
    
    if pending_request:
        pending_request.status = 'approved'
        pending_request.reviewed_by = session['user_id']
        pending_request.reviewed_at = datetime.utcnow()
        pending_request.admin_notes = 'Automatically approved when domain was granted'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Domain access granted successfully',
        'access': access.to_dict()
    }), 201


@app.route('/api/admin/teacher/<int:teacher_id>/domains/<domain>', methods=['DELETE'])
@login_required
@role_required('admin')
def revoke_domain_from_teacher(teacher_id, domain):
    """Revoke a domain from a teacher"""
    domain = domain.lower()
    
    access = TeacherDomainAccess.query.filter_by(
        teacher_id=teacher_id,
        email_domain=domain
    ).first()
    
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
    
    added = []
    already_assigned = []
    invalid = []
    
    for domain in domains:
        domain = domain.strip().lower()
        
        # Validate domain format
        if '.' not in domain or '@' in domain:
            invalid.append(domain)
            continue
        
        # Check if already assigned
        existing = TeacherDomainAccess.query.filter_by(
            teacher_id=teacher_id,
            email_domain=domain
        ).first()
        
        if existing:
            already_assigned.append(domain)
            continue
        
        # Create new access record
        access = TeacherDomainAccess(
            teacher_id=teacher_id,
            email_domain=domain,
            granted_by=session['user_id'],
            notes=notes
        )
        db.session.add(access)
        added.append(domain)
        
        # Auto-approve any pending requests
        pending_request = DomainAccessRequest.query.filter_by(
            teacher_id=teacher_id,
            email_domain=domain,
            status='pending'
        ).first()
        
        if pending_request:
            pending_request.status = 'approved'
            pending_request.reviewed_by = session['user_id']
            pending_request.reviewed_at = datetime.utcnow()
            pending_request.admin_notes = 'Automatically approved in bulk assignment'
    
    db.session.commit()
    
    return jsonify({
        'message': f'Processed {len(domains)} domains',
        'added': added,
        'already_assigned': already_assigned,
        'invalid': invalid,
        'added_count': len(added)
    })


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
    
    return jsonify({
        'requests': [r.to_dict() for r in requests],
        'total': len(requests)
    })


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
    
    # Create the domain access
    access = TeacherDomainAccess(
        teacher_id=access_request.teacher_id,
        email_domain=access_request.email_domain,
        granted_by=session['user_id'],
        notes=f"Requested: {access_request.reason}"
    )
    
    # Update request status
    access_request.status = 'approved'
    access_request.reviewed_by = session['user_id']
    access_request.reviewed_at = datetime.utcnow()
    access_request.admin_notes = admin_notes
    
    db.session.add(access)
    db.session.commit()
    
    return jsonify({
        'message': 'Domain access request approved',
        'access': access.to_dict(),
        'request': access_request.to_dict()
    })


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
    
    # Update request status
    access_request.status = 'denied'
    access_request.reviewed_by = session['user_id']
    access_request.reviewed_at = datetime.utcnow()
    access_request.admin_notes = admin_notes
    
    db.session.commit()
    
    return jsonify({
        'message': 'Domain access request denied',
        'request': access_request.to_dict()
    })


@app.route('/api/admin/teacher/<int:teacher_id>/remove-all-restrictions', methods=['POST'])
@login_required
@role_required('admin')
def remove_all_teacher_restrictions(teacher_id):
    """Remove all domain restrictions from a teacher (grant full access)"""
    teacher = User.query.get_or_404(teacher_id)
    
    if teacher.role != 'teacher':
        return jsonify({'error': 'User is not a teacher'}), 400
    
    # Delete all domain access records for this teacher
    TeacherDomainAccess.query.filter_by(teacher_id=teacher_id).delete()
    db.session.commit()
    
    return jsonify({
        'message': 'All domain restrictions removed. Teacher now has full access to all students.'
    })
