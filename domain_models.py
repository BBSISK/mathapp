# ==================== DOMAIN RESTRICTION MODELS ====================
# Add these models to your app.py file after the existing models

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
