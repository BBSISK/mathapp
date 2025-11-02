#!/usr/bin/env python3
"""
Automated fix for domain filtering in class_students route
Run this script to automatically patch app.py
"""

import sys
import os
from datetime import datetime

def apply_fix():
    """Apply domain filtering fix to app.py"""
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found in current directory")
        print("   Please run this script from your mathapp-main directory")
        return False
    
    # Backup first
    backup_name = f'app.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_name}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Find and replace the function
    old_code = '''def class_students(class_id):
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

    return jsonify(students_data)'''
    
    new_code = '''def class_students(class_id):
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

    return jsonify(students_data)'''
    
    # Check if the old code exists
    if old_code not in content:
        print("⚠️  Warning: Could not find exact code to replace")
        print("   The function may have already been patched or modified")
        print("   Please apply the fix manually using DOMAIN_FILTERING_FIX.md")
        return False
    
    # Apply the fix
    content = content.replace(old_code, new_code)
    
    # Write back
    try:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fix applied successfully!")
        print()
        print("📋 Changes made:")
        print("   - Added domain filtering to class_students() function")
        print("   - Added safety check for null students")
        print("   - Teachers now only see students from authorized domains")
        print()
        print("🔄 Next steps:")
        print("   1. Restart your Flask app")
        print("   2. Test by logging in as a teacher with domain restrictions")
        print("   3. Verify you only see students from authorized domains")
        print()
        return True
    except Exception as e:
        print(f"❌ Failed to write changes: {e}")
        print(f"   Restoring from backup: {backup_name}")
        try:
            with open(backup_name, 'r', encoding='utf-8') as f:
                original = f.read()
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(original)
            print("✅ Backup restored")
        except:
            print("❌ Failed to restore backup - please restore manually")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  Domain Filtering Fix for class_students Route")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Create a backup of your current app.py")
    print("  2. Add domain filtering to the class_students() function")
    print("  3. Verify the changes were applied")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    success = apply_fix()
    
    if success:
        print("🎉 Domain filtering fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Fix failed - please apply manually")
        sys.exit(1)
