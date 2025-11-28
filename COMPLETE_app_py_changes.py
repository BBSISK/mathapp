"""
Complete app.py additions for Who Am I answer variants
Add these functions and update existing routes
"""

# =============================================================================
# SECTION 1: ADD THIS HELPER FUNCTION (add near line 6500, before Who Am I routes)
# =============================================================================

def auto_generate_variants(answer):
    """
    Auto-generate acceptable answer variants
    Returns a list of lowercase variants
    """
    variants = set()
    answer_lower = answer.lower().strip()
    variants.add(answer_lower)
    
    # Remove common titles
    titles = ['dr.', 'dr', 'sir', 'professor', 'prof.', 'prof', 'dame', 'lord', 'lady']
    for title in titles:
        if answer_lower.startswith(title + ' '):
            without_title = answer_lower.replace(title + ' ', '', 1).strip()
            variants.add(without_title)
    
    # Split into name parts
    parts = answer_lower.split()
    
    if len(parts) >= 2:
        # First name only
        variants.add(parts[0])
        
        # Last name only
        variants.add(parts[-1])
        
        # First and last (skip middle)
        if len(parts) > 2:
            variants.add(f"{parts[0]} {parts[-1]}")
        
        # Remove middle initials (e.g., "Isaac M. Newton" -> "Isaac Newton")
        filtered_parts = [p for p in parts if len(p) > 2 or not p.endswith('.')]
        if len(filtered_parts) != len(parts):
            variants.add(' '.join(filtered_parts))
    
    # Remove punctuation variants
    import string
    no_punct = answer_lower.translate(str.maketrans('', '', string.punctuation))
    if no_punct != answer_lower:
        variants.add(no_punct)
    
    return sorted(list(variants))


# =============================================================================
# SECTION 2: UPDATE admin_who_am_i() function (around line 6505)
# REPLACE the GROUP_CONCAT line in the SELECT query
# =============================================================================

# FIND THIS:
"""
        SELECT
            i.id,
            i.difficulty,
            i.image_filename,
            i.answer,
            i.hint,
            i.active,
            i.created_at,
            i.topic as primary_topic,
            GROUP_CONCAT(t.topic) as all_topics
        FROM who_am_i_images i
"""

# REPLACE WITH:
"""
        SELECT
            i.id,
            i.difficulty,
            i.image_filename,
            i.answer,
            i.hint,
            i.active,
            i.created_at,
            i.topic as primary_topic,
            i.accepted_answers,
            GROUP_CONCAT(t.topic) as all_topics
        FROM who_am_i_images i
"""

# AND UPDATE the image dict creation (around line 6533):
# FIND:
"""
        images.append({
            'id': row.id,
            'primary_topic': row.primary_topic,
            'topics': topics,
            'difficulty': row.difficulty,
            'image_filename': row.image_filename,
            'answer': row.answer,
            'hint': row.hint,
            'active': row.active,
            'created_at': row.created_at
        })
"""

# REPLACE WITH:
"""
        # Parse accepted answers to get count
        accepted_answers_count = 0
        if row.accepted_answers:
            try:
                accepted_answers_count = len(json.loads(row.accepted_answers))
            except:
                pass
        
        images.append({
            'id': row.id,
            'primary_topic': row.primary_topic,
            'topics': topics,
            'difficulty': row.difficulty,
            'image_filename': row.image_filename,
            'answer': row.answer,
            'hint': row.hint,
            'active': row.active,
            'created_at': row.created_at,
            'accepted_answers_count': accepted_answers_count  # NEW
        })
"""


# =============================================================================
# SECTION 3: UPDATE admin_who_am_i_upload() function (around line 6564)
# =============================================================================

# FIND THIS SECTION (around line 6579-6580):
"""
    answer = request.form.get('answer')
    hint = request.form.get('hint', '')
"""

# ADD AFTER IT:
"""
    # NEW: Handle accepted answers
    accepted_answers_text = request.form.get('accepted_answers', '').strip()
    if accepted_answers_text:
        # Parse from textarea (one per line)
        variants = [v.strip() for v in accepted_answers_text.split('\n') if v.strip()]
        accepted_answers_json = json.dumps(variants)
    else:
        # Auto-generate if not provided
        variants = auto_generate_variants(answer)
        accepted_answers_json = json.dumps(variants)
"""

# THEN FIND THE INSERT query (around line 6615):
"""
    result = db.session.execute(text("""
        INSERT INTO who_am_i_images (topic, difficulty, image_filename, answer, hint, active)
        VALUES (:topic, :difficulty, :filename, :answer, :hint, 1)
    """), {
"""

# REPLACE WITH:
"""
    result = db.session.execute(text("""
        INSERT INTO who_am_i_images (topic, difficulty, image_filename, answer, hint, accepted_answers, active)
        VALUES (:topic, :difficulty, :filename, :answer, :hint, :accepted_answers, 1)
    """), {
        'topic': primary_topic,
        'difficulty': difficulty,
        'filename': unique_filename,
        'answer': answer,
        'hint': hint,
        'accepted_answers': accepted_answers_json  # NEW
    })
"""


# =============================================================================
# SECTION 4: ADD NEW GET ENDPOINT (add after admin_who_am_i_upload, around line 6650)
# =============================================================================

@app.route('/admin/who-am-i/get/<int:image_id>')
@admin_required
def admin_who_am_i_get(image_id):
    """Get image details for editing (including accepted_answers)"""
    from sqlalchemy import text
    
    # Get image with topics
    query = text("""
        SELECT 
            i.id,
            i.answer,
            i.hint,
            i.difficulty,
            i.accepted_answers,
            i.active,
            GROUP_CONCAT(t.topic) as topics
        FROM who_am_i_images i
        LEFT JOIN who_am_i_image_topics t ON i.id = t.image_id
        WHERE i.id = :image_id
        GROUP BY i.id
    """)
    
    result = db.session.execute(query, {'image_id': image_id}).fetchone()
    
    if not result:
        return jsonify({'error': 'Image not found'}), 404
    
    topics = result.topics.split(',') if result.topics else []
    
    return jsonify({
        'id': result.id,
        'answer': result.answer,
        'hint': result.hint,
        'difficulty': result.difficulty,
        'accepted_answers': result.accepted_answers,  # JSON string or None
        'active': result.active,
        'topics': topics
    })


# =============================================================================
# SECTION 5: REPLACE admin_who_am_i_edit() function (around line 6680)
# Find the entire function and replace it with this:
# =============================================================================

@app.route('/admin/who-am-i/edit/<int:image_id>', methods=['GET', 'POST'])
@admin_required
def admin_who_am_i_edit(image_id):
    """Edit image details including accepted_answers"""
    from sqlalchemy import text
    
    if request.method == 'GET':
        # This is now handled by admin_who_am_i_get endpoint
        return redirect(url_for('admin_who_am_i'))
    
    # POST - handle edit
    answer = request.form.get('answer')
    hint = request.form.get('hint', '')
    difficulty = request.form.get('difficulty')
    selected_topics = request.form.getlist('topics[]')
    
    # NEW: Get accepted answers from form
    accepted_answers_json = request.form.get('accepted_answers')
    
    # If not provided or empty, auto-generate
    if not accepted_answers_json:
        variants = auto_generate_variants(answer)
        accepted_answers_json = json.dumps(variants)
    
    # Update image
    db.session.execute(text("""
        UPDATE who_am_i_images
        SET answer = :answer,
            hint = :hint,
            difficulty = :difficulty,
            accepted_answers = :accepted_answers
        WHERE id = :image_id
    """), {
        'answer': answer,
        'hint': hint,
        'difficulty': difficulty,
        'accepted_answers': accepted_answers_json,
        'image_id': image_id
    })
    
    # Update topics - delete old associations
    db.session.execute(text("""
        DELETE FROM who_am_i_image_topics WHERE image_id = :image_id
    """), {'image_id': image_id})
    
    # Insert new topic associations
    if selected_topics:
        for topic in selected_topics:
            db.session.execute(text("""
                INSERT INTO who_am_i_image_topics (image_id, topic)
                VALUES (:image_id, :topic)
            """), {'image_id': image_id, 'topic': topic})
    
    db.session.commit()
    
    flash('Image updated successfully', 'success')
    return jsonify({'success': True})


# =============================================================================
# SECTION 6: UPDATE who_am_i_guess() function (around line 6965)
# This is the CRITICAL change for checking answers
# =============================================================================

# FIND THE SELECT query (around line 6978):
"""
    result = db.session.execute(text("""
        SELECT s.tiles_revealed, s.guesses_made, s.correct_guess, s.quiz_attempt_id, i.answer
        FROM who_am_i_sessions s
        JOIN who_am_i_images i ON s.image_id = i.id
        WHERE s.id = :session_id AND s.user_id = :user_id
    """), {'session_id': session_id, 'user_id': session['user_id']}).fetchone()
"""

# REPLACE WITH:
"""
    result = db.session.execute(text("""
        SELECT s.tiles_revealed, s.guesses_made, s.correct_guess, s.quiz_attempt_id, 
               i.answer, i.accepted_answers
        FROM who_am_i_sessions s
        JOIN who_am_i_images i ON s.image_id = i.id
        WHERE s.id = :session_id AND s.user_id = :user_id
    """), {'session_id': session_id, 'user_id': session['user_id']}).fetchone()
"""

# THEN FIND (around line 6988-6992):
"""
    tiles_revealed = json.loads(result.tiles_revealed)
    guesses_made = result.guesses_made
    correct_guess = result.correct_guess
    quiz_attempt_id = result.quiz_attempt_id
    correct_answer = result.answer
"""

# REPLACE WITH:
"""
    tiles_revealed = json.loads(result.tiles_revealed)
    guesses_made = result.guesses_made
    correct_guess = result.correct_guess
    quiz_attempt_id = result.quiz_attempt_id
    correct_answer = result.answer
    accepted_answers_json = result.accepted_answers
"""

# THEN FIND (around line 7002-7003):
"""
    # Check if guess is correct (case-insensitive)
    is_correct = guess.lower() == correct_answer.lower()
"""

# REPLACE WITH:
"""
    # NEW: Flexible answer checking with variants
    # Parse accepted answers
    accepted_answers = []
    if accepted_answers_json:
        try:
            accepted_answers = json.loads(accepted_answers_json)
        except:
            pass
    
    # If no variants defined, fall back to original answer only
    if not accepted_answers:
        accepted_answers = [correct_answer.lower().strip()]
    
    # Normalize guess
    guess_normalized = guess.lower().strip()
    
    # Check if guess matches any accepted variant
    is_correct = guess_normalized in [a.lower().strip() for a in accepted_answers]
"""


# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

"""
TO DEPLOY ALL CHANGES:

1. Add auto_generate_variants() function (Section 1)
2. Update admin_who_am_i() to include accepted_answers in SELECT (Section 2)
3. Update admin_who_am_i_upload() to handle accepted_answers (Section 3)
4. Add new admin_who_am_i_get() endpoint (Section 4)
5. Replace admin_who_am_i_edit() function (Section 5)
6. Update who_am_i_guess() checking logic (Section 6)

TESTING:
1. Upload new image with custom variants
2. Upload new image with blank variants (auto-generate)
3. Edit existing image, click Auto-Generate
4. Edit existing image, add custom variant
5. Test student guessing with different variants

TIME: ~30 minutes for all changes
"""
