# ADD THIS ROUTE TO YOUR app.py
# This allows you to manually trigger badge awarding for testing

@app.route('/api/award-badges-now')
@login_required
def award_badges_now():
    """Manually trigger badge awarding for current user (for testing)"""
    from sqlalchemy import text
    
    if 'guest_code' not in session:
        return jsonify({'error': 'Only for guest code users'}), 400
        
    guest_code = session['guest_code']
    
    # Get guest stats
    try:
        guest_stats = db.session.execute(text("""
            SELECT total_score, quizzes_completed
            FROM guest_users
            WHERE guest_code = :code
        """), {"code": guest_code}).fetchone()
        
        if not guest_stats:
            return jsonify({'error': 'Guest not found'}), 404
            
        quizzes = guest_stats[1]
        points = guest_stats[0]
        
        # Get all badges
        all_badges = Badge.query.all()
        
        awarded = []
        skipped = []
        
        for badge in all_badges:
            # Calculate if badge is earned
            earned = False
            
            if badge.requirement_type == 'quizzes_completed':
                if quizzes >= badge.requirement_value:
                    earned = True
                    
            elif badge.requirement_type == 'perfect_scores':
                perfect_count = db.session.execute(text("""
                    SELECT COUNT(*) FROM guest_quiz_attempts
                    WHERE guest_code = :code AND score = total_questions
                """), {"code": guest_code}).fetchone()[0]
                if perfect_count >= badge.requirement_value:
                    earned = True
                    
            elif badge.requirement_type == 'high_scores':
                high_scores = db.session.execute(text("""
                    SELECT COUNT(*) FROM guest_quiz_attempts
                    WHERE guest_code = :code
                    AND CAST(score AS FLOAT) / total_questions >= 0.9
                """), {"code": guest_code}).fetchone()[0]
                if high_scores >= badge.requirement_value:
                    earned = True
            
            if earned:
                # Check if already awarded
                existing = db.session.execute(text("""
                    SELECT COUNT(*) FROM guest_badges
                    WHERE guest_code = :code AND badge_name = :name
                """), {"code": guest_code, "name": badge.name}).fetchone()[0]
                
                if existing == 0:
                    # Award it!
                    db.session.execute(text("""
                        INSERT INTO guest_badges (guest_code, badge_name, earned_at)
                        VALUES (:code, :name, :now)
                    """), {
                        "code": guest_code,
                        "name": badge.name,
                        "now": datetime.utcnow()
                    })
                    db.session.commit()
                    awarded.append(badge.name)
                else:
                    skipped.append(f"{badge.name} (already awarded)")
        
        return jsonify({
            'message': 'Badge check complete',
            'guest_code': guest_code,
            'quizzes_completed': quizzes,
            'total_points': points,
            'newly_awarded': awarded,
            'skipped': skipped
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# HOW TO USE:
# 1. Add this route to your app.py
# 2. Restart Flask
# 3. While logged in as guest, visit: https://yoursite.com/api/award-badges-now
# 4. You'll see JSON response showing which badges were awarded
# 5. Refresh badge page - badges should appear in "Earned Badges"!

# OR call from JavaScript console:
# fetch('/api/award-badges-now').then(r => r.json()).then(console.log)
