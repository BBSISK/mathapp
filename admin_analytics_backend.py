"""
ADMIN USER ANALYTICS API ROUTES
Add these routes to app.py

Features:
- Overview statistics
- Registered users list
- Repeat guests list
- Inactive users tracking
- Individual user details
- Guest code recycling
- Automatic cleanup system
"""

from datetime import datetime, timedelta
from sqlalchemy import text

# =============================================================================
# ANALYTICS OVERVIEW
# =============================================================================

@app.route('/api/admin/analytics/overview')
@login_required
@role_required('admin')
def admin_analytics_overview():
    """Get overview statistics"""
    
    # Count registered users (exclude guest accounts)
    registered_count = db.session.execute(text("""
        SELECT COUNT(*) 
        FROM users 
        WHERE email NOT LIKE 'guest%@%' 
        AND role = 'student'
    """)).scalar()
    
    # Count repeat guests
    repeat_guests_count = db.session.execute(text("""
        SELECT COUNT(*) FROM guest_users
    """)).scalar()
    
    # Count inactive guests (60+ days)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    inactive_guests = db.session.execute(text("""
        SELECT COUNT(*) 
        FROM guest_users 
        WHERE last_active < :cutoff
    """), {'cutoff': sixty_days_ago}).scalar()
    
    # Count casual sessions today (approximate from guest_sessions if exists)
    try:
        casual_today = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM guest_sessions 
            WHERE DATE(created_at) = DATE('now')
        """)).scalar()
    except:
        casual_today = 0
    
    return jsonify({
        'registered_users': registered_count,
        'repeat_guests': repeat_guests_count,
        'inactive_guests': inactive_guests,
        'casual_sessions_today': casual_today
    })


# =============================================================================
# REGISTERED USERS LIST
# =============================================================================

@app.route('/api/admin/analytics/registered-users')
@login_required
@role_required('admin')
def admin_analytics_registered_users():
    """Get list of all registered users with stats"""
    
    users = db.session.execute(text("""
        SELECT 
            u.id,
            u.email,
            u.full_name,
            u.created_at,
            COALESCE(us.total_points, 0) as points,
            COALESCE(us.total_quizzes, 0) as quizzes,
            us.updated_at as last_active
        FROM users u
        LEFT JOIN user_stats us ON u.id = us.user_id
        WHERE u.email NOT LIKE 'guest%@%'
        AND u.role = 'student'
        ORDER BY us.updated_at DESC NULLS LAST
    """)).fetchall()
    
    result = []
    now = datetime.utcnow()
    
    for user in users:
        last_active = user.last_active if user.last_active else user.created_at
        days_inactive = (now - last_active).days if last_active else 999
        
        # Determine activity status
        if days_inactive < 7:
            activity_status = 'active'
            activity_label = 'Active'
        elif days_inactive < 30:
            activity_status = 'stale'
            activity_label = 'Inactive'
        else:
            activity_status = 'inactive'
            activity_label = f'{days_inactive}d ago'
        
        result.append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'points': user.points,
            'quizzes': user.quizzes,
            'last_active': last_active.isoformat() if last_active else None,
            'activity_status': activity_status,
            'activity_label': activity_label
        })
    
    return jsonify(result)


# =============================================================================
# REPEAT GUESTS LIST
# =============================================================================

@app.route('/api/admin/analytics/repeat-guests')
@login_required
@role_required('admin')
def admin_analytics_repeat_guests():
    """Get list of all repeat guests with stats"""
    
    guests = db.session.execute(text("""
        SELECT 
            guest_code,
            nickname,
            total_score,
            quizzes_completed,
            created_at,
            last_active
        FROM guest_users
        ORDER BY last_active DESC
    """)).fetchall()
    
    result = []
    now = datetime.utcnow()
    
    for guest in guests:
        days_inactive = (now - guest.last_active).days if guest.last_active else 999
        
        # Determine activity status
        if days_inactive < 7:
            activity_status = 'active'
            activity_label = 'Active'
        elif days_inactive < 60:
            activity_status = 'stale'
            activity_label = f'{days_inactive}d ago'
        else:
            activity_status = 'inactive'
            activity_label = f'Inactive {days_inactive}d'
        
        result.append({
            'guest_code': guest.guest_code,
            'nickname': guest.nickname,
            'total_score': guest.total_score,
            'quizzes_completed': guest.quizzes_completed,
            'created_at': guest.created_at.isoformat() if guest.created_at else None,
            'last_active': guest.last_active.isoformat() if guest.last_active else None,
            'days_inactive': days_inactive,
            'activity_status': activity_status,
            'activity_label': activity_label
        })
    
    return jsonify(result)


# =============================================================================
# INACTIVE USERS LIST
# =============================================================================

@app.route('/api/admin/analytics/inactive-users')
@login_required
@role_required('admin')
def admin_analytics_inactive_users():
    """Get list of inactive users (60+ days)"""
    
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    
    # Get inactive repeat guests
    inactive_guests = db.session.execute(text("""
        SELECT 
            'Guest' as type,
            guest_code as identifier,
            last_active,
            total_score as points
        FROM guest_users
        WHERE last_active < :cutoff
        ORDER BY last_active ASC
    """), {'cutoff': sixty_days_ago}).fetchall()
    
    result = []
    now = datetime.utcnow()
    
    for user in inactive_guests:
        days_inactive = (now - user.last_active).days if user.last_active else 999
        
        result.append({
            'type': user.type,
            'identifier': user.identifier,
            'last_active': user.last_active.isoformat() if user.last_active else None,
            'days_inactive': days_inactive,
            'points': user.points
        })
    
    return jsonify(result)


# =============================================================================
# USER DETAIL VIEW
# =============================================================================

@app.route('/api/admin/analytics/user-detail')
@login_required
@role_required('admin')
def admin_analytics_user_detail():
    """Get detailed info about a specific user"""
    
    user_type = request.args.get('type')
    user_id = request.args.get('id')
    
    if user_type == 'registered':
        # Get registered user details
        user = User.query.get(user_id)
        stats = UserStats.query.filter_by(user_id=user_id).first()
        
        # Get recent activity
        recent_attempts = db.session.execute(text("""
            SELECT topic, difficulty, score, total_questions, completed_at
            FROM quiz_attempts
            WHERE user_id = :user_id
            ORDER BY completed_at DESC
            LIMIT 10
        """), {'user_id': user_id}).fetchall()
        
        recent_activity_html = '<ul>' + ''.join([
            f'<li>{att.topic} ({att.difficulty}): {att.score}/{att.total_questions} - {att.completed_at}</li>'
            for att in recent_attempts
        ]) + '</ul>' if recent_attempts else '<p>No recent activity</p>'
        
        return jsonify({
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'points': stats.total_points if stats else 0,
            'level': stats.level if stats else 1,
            'quizzes': stats.total_quizzes if stats else 0,
            'accuracy': round((stats.total_correct_answers / stats.total_questions_answered * 100), 1) if stats and stats.total_questions_answered > 0 else 0,
            'streak': stats.current_streak_days if stats else 0,
            'recent_activity': recent_activity_html
        })
    
    else:  # guest
        # Get guest details
        guest = db.session.execute(text("""
            SELECT * FROM guest_users WHERE guest_code = :code
        """), {'code': user_id}).fetchone()
        
        # Get recent quizzes
        recent_quizzes = db.session.execute(text("""
            SELECT topic, difficulty, score, total_questions, completed_at
            FROM guest_quiz_attempts
            WHERE guest_code = :code
            ORDER BY completed_at DESC
            LIMIT 10
        """), {'code': user_id}).fetchall()
        
        recent_quizzes_html = '<ul>' + ''.join([
            f'<li>{quiz.topic} ({quiz.difficulty}): {quiz.score}/{quiz.total_questions}</li>'
            for quiz in recent_quizzes
        ]) + '</ul>' if recent_quizzes else '<p>No quizzes yet</p>'
        
        now = datetime.utcnow()
        days_old = (now - guest.created_at).days if guest.created_at else 0
        days_inactive = (now - guest.last_active).days if guest.last_active else 999
        
        return jsonify({
            'guest_code': guest.guest_code,
            'nickname': guest.nickname,
            'total_score': guest.total_score,
            'quizzes_completed': guest.quizzes_completed,
            'days_old': days_old,
            'days_inactive': days_inactive,
            'recent_quizzes': recent_quizzes_html
        })


# =============================================================================
# RECYCLE GUEST CODE
# =============================================================================

@app.route('/api/admin/analytics/recycle-guest', methods=['POST'])
@login_required
@role_required('admin')
def admin_analytics_recycle_guest():
    """Manually recycle a guest code (delete all data)"""
    
    data = request.json
    guest_code = data.get('guest_code')
    
    try:
        # Delete guest quiz attempts
        db.session.execute(text("""
            DELETE FROM guest_quiz_attempts WHERE guest_code = :code
        """), {'code': guest_code})
        
        # Delete guest badges
        db.session.execute(text("""
            DELETE FROM guest_badges WHERE guest_code = :code
        """), {'code': guest_code})
        
        # Delete guest user record
        db.session.execute(text("""
            DELETE FROM guest_users WHERE guest_code = :code
        """), {'code': guest_code})
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Guest code {guest_code} recycled'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# RUN CLEANUP NOW
# =============================================================================

@app.route('/api/admin/analytics/run-cleanup', methods=['POST'])
@login_required
@role_required('admin')
def admin_analytics_run_cleanup():
    """Run cleanup process now"""
    
    # Get cleanup threshold from settings (default 60 days)
    cleanup_days = int(SystemSetting.get('cleanup_days_threshold', '60'))
    cutoff_date = datetime.utcnow() - timedelta(days=cleanup_days)
    
    # Find inactive guest codes
    inactive_codes = db.session.execute(text("""
        SELECT guest_code 
        FROM guest_users 
        WHERE last_active < :cutoff
    """), {'cutoff': cutoff_date}).fetchall()
    
    recycled_count = 0
    
    for row in inactive_codes:
        guest_code = row.guest_code
        
        try:
            # Delete all related data
            db.session.execute(text("""
                DELETE FROM guest_quiz_attempts WHERE guest_code = :code
            """), {'code': guest_code})
            
            db.session.execute(text("""
                DELETE FROM guest_badges WHERE guest_code = :code
            """), {'code': guest_code})
            
            db.session.execute(text("""
                DELETE FROM guest_users WHERE guest_code = :code
            """), {'code': guest_code})
            
            recycled_count += 1
        except Exception as e:
            print(f"Error recycling {guest_code}: {e}")
            continue
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'recycled_count': recycled_count,
        'message': f'Recycled {recycled_count} inactive guest codes'
    })


# =============================================================================
# CLEANUP SETTINGS
# =============================================================================

@app.route('/api/admin/analytics/cleanup-settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_analytics_cleanup_settings():
    """Get or update cleanup settings"""
    
    if request.method == 'GET':
        return jsonify({
            'days_threshold': int(SystemSetting.get('cleanup_days_threshold', '60')),
            'auto_enabled': SystemSetting.get('auto_cleanup_enabled', 'false') == 'true'
        })
    
    else:  # POST
        data = request.json
        user_id = session.get('user_id')
        
        SystemSetting.set(
            'cleanup_days_threshold',
            str(data.get('days_threshold', 60)),
            'Days of inactivity before guest code cleanup',
            user_id
        )
        
        SystemSetting.set(
            'auto_cleanup_enabled',
            'true' if data.get('auto_enabled') else 'false',
            'Enable automatic daily cleanup',
            user_id
        )
        
        return jsonify({'success': True})


# =============================================================================
# SCHEDULED CLEANUP TASK (Optional - for automated cleanup)
# =============================================================================

def scheduled_cleanup_task():
    """
    Run this function daily via cron or scheduler
    
    Add to crontab:
    0 3 * * * cd /home/bbsisk/mathapp && python3 -c "from app import app, scheduled_cleanup_task; import sys; sys.path.insert(0, '/home/bbsisk/mathapp'); with app.app_context(): scheduled_cleanup_task()"
    """
    
    # Check if auto-cleanup is enabled
    auto_enabled = SystemSetting.get('auto_cleanup_enabled', 'false') == 'true'
    
    if not auto_enabled:
        print("Auto-cleanup is disabled")
        return
    
    cleanup_days = int(SystemSetting.get('cleanup_days_threshold', '60'))
    cutoff_date = datetime.utcnow() - timedelta(days=cleanup_days)
    
    # Find and recycle inactive guest codes
    inactive_codes = db.session.execute(text("""
        SELECT guest_code 
        FROM guest_users 
        WHERE last_active < :cutoff
    """), {'cutoff': cutoff_date}).fetchall()
    
    recycled_count = 0
    
    for row in inactive_codes:
        guest_code = row.guest_code
        
        try:
            db.session.execute(text("""
                DELETE FROM guest_quiz_attempts WHERE guest_code = :code
            """), {'code': guest_code})
            
            db.session.execute(text("""
                DELETE FROM guest_badges WHERE guest_code = :code
            """), {'code': guest_code})
            
            db.session.execute(text("""
                DELETE FROM guest_users WHERE guest_code = :code
            """), {'code': guest_code})
            
            recycled_count += 1
        except Exception as e:
            print(f"Error recycling {guest_code}: {e}")
            continue
    
    db.session.commit()
    
    print(f"Scheduled cleanup complete: Recycled {recycled_count} guest codes")
    return recycled_count


print("""
=============================================================================
ADMIN USER ANALYTICS - BACKEND ROUTES COMPLETE
=============================================================================

Add these routes to app.py:
- /api/admin/analytics/overview
- /api/admin/analytics/registered-users
- /api/admin/analytics/repeat-guests
- /api/admin/analytics/inactive-users
- /api/admin/analytics/user-detail
- /api/admin/analytics/recycle-guest (POST)
- /api/admin/analytics/run-cleanup (POST)
- /api/admin/analytics/cleanup-settings (GET/POST)

Optional: Set up daily cron job for automatic cleanup
""")
