# ==================== DOMAIN RESTRICTION HELPER FUNCTIONS ====================
# Add these helper functions to your app.py

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
        return True  # If no domain specified, allow access
    
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
    """
    Filter a SQLAlchemy query of students based on teacher's domain access
    
    Args:
        students_query: SQLAlchemy query object for User (students)
        teacher_id: ID of the teacher
    
    Returns:
        Filtered query object
    """
    accessible_domains = get_teacher_accessible_domains(teacher_id)
    
    # If None, teacher has access to all domains
    if accessible_domains is None:
        return students_query
    
    # If empty list, teacher has no access to any domains
    if not accessible_domains:
        # Return empty query
        return students_query.filter(User.id == -1)  # Impossible condition
    
    # Filter students by accessible domains
    # We need to extract domain from each student's email and check if it's in accessible_domains
    filtered_students = []
    for student in students_query.all():
        student_domain = extract_domain(student.email)
        if student_domain in accessible_domains:
            filtered_students.append(student.id)
    
    if not filtered_students:
        # No students in accessible domains
        return students_query.filter(User.id == -1)  # Impossible condition
    
    # Return query filtered by student IDs
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
