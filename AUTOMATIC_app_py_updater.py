#!/usr/bin/env python3
"""
Automatically update app.py with Who Am I answer variants support
This script makes ALL necessary changes - no manual editing required
"""
import sys
import os
import re

def backup_file(filepath):
    """Create backup of file"""
    backup_path = f"{filepath}.whoami_backup"
    with open(filepath, 'r') as f:
        content = f.read()
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    return backup_path

def update_app_py(filepath):
    """Update app.py with all Who Am I changes"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    print(f"Original file: {len(lines)} lines")
    
    # =============================================================================
    # CHANGE 1: Add auto_generate_variants helper function
    # Insert before admin_who_am_i function (around line 6505)
    # =============================================================================
    
    helper_function = '''
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
        
        # Remove middle initials
        filtered_parts = [p for p in parts if len(p) > 2 or not p.endswith('.')]
        if len(filtered_parts) != len(parts):
            variants.add(' '.join(filtered_parts))
    
    # Remove punctuation variants
    import string
    no_punct = answer_lower.translate(str.maketrans('', '', string.punctuation))
    if no_punct != answer_lower:
        variants.add(no_punct)
    
    return sorted(list(variants))

'''
    
    # Find the line before admin_who_am_i function
    for i, line in enumerate(lines):
        if 'def admin_who_am_i():' in line:
            # Insert helper function before this
            lines.insert(i, helper_function)
            print(f"✓ Added auto_generate_variants() at line {i}")
            break
    
    # Rejoin to work with content
    content = '\n'.join(lines)
    
    # =============================================================================
    # CHANGE 2: Update admin_who_am_i() SELECT query
    # =============================================================================
    
    # Find and replace SELECT query
    old_select = r'SELECT\s+i\.id,\s+i\.difficulty,\s+i\.image_filename,\s+i\.answer,\s+i\.hint,\s+i\.active,\s+i\.created_at,\s+i\.topic as primary_topic,\s+GROUP_CONCAT\(t\.topic\) as all_topics'
    new_select = '''SELECT
            i.id,
            i.difficulty,
            i.image_filename,
            i.answer,
            i.hint,
            i.active,
            i.created_at,
            i.topic as primary_topic,
            i.accepted_answers,
            GROUP_CONCAT(t.topic) as all_topics'''
    
    content = re.sub(old_select, new_select, content, flags=re.DOTALL)
    print("✓ Updated admin_who_am_i() SELECT query")
    
    # Add variant count to image dict
    old_dict_append = r"images\.append\(\{\s+'id': row\.id,\s+'primary_topic': row\.primary_topic,\s+'topics': topics,\s+'difficulty': row\.difficulty,\s+'image_filename': row\.image_filename,\s+'answer': row\.answer,\s+'hint': row\.hint,\s+'active': row\.active,\s+'created_at': row\.created_at\s+\}\)"
    
    new_dict_append = '''# Parse accepted answers to get count
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
            'accepted_answers_count': accepted_answers_count
        })'''
    
    content = re.sub(old_dict_append, new_dict_append, content, flags=re.DOTALL)
    print("✓ Added variant count to image dict")
    
    # =============================================================================
    # CHANGE 3: Update admin_who_am_i_upload()
    # =============================================================================
    
    # Add accepted_answers handling after getting answer and hint
    upload_insert_point = r"(answer = request\.form\.get\('answer'\)\s+hint = request\.form\.get\('hint', ''\))"
    upload_addition = r'''\1
    
    # Handle accepted answers
    accepted_answers_text = request.form.get('accepted_answers', '').strip()
    if accepted_answers_text:
        # Parse from textarea (one per line)
        variants = [v.strip() for v in accepted_answers_text.split('\\n') if v.strip()]
        accepted_answers_json = json.dumps(variants)
    else:
        # Auto-generate if not provided
        variants = auto_generate_variants(answer)
        accepted_answers_json = json.dumps(variants)'''
    
    content = re.sub(upload_insert_point, upload_addition, content)
    print("✓ Added accepted_answers handling to upload")
    
    # Update INSERT query
    old_insert = r"INSERT INTO who_am_i_images \(topic, difficulty, image_filename, answer, hint, active\)\s+VALUES \(:topic, :difficulty, :filename, :answer, :hint, 1\)"
    new_insert = "INSERT INTO who_am_i_images (topic, difficulty, image_filename, answer, hint, accepted_answers, active)\\n        VALUES (:topic, :difficulty, :filename, :answer, :hint, :accepted_answers, 1)"
    
    content = re.sub(old_insert, new_insert, content)
    
    # Update INSERT parameters
    old_params = r"'topic': primary_topic,\s+'difficulty': difficulty,\s+'filename': unique_filename,\s+'answer': answer,\s+'hint': hint"
    new_params = "'topic': primary_topic,\\n        'difficulty': difficulty,\\n        'filename': unique_filename,\\n        'answer': answer,\\n        'hint': hint,\\n        'accepted_answers': accepted_answers_json"
    
    content = re.sub(old_params, new_params, content)
    print("✓ Updated INSERT query in upload")
    
    # =============================================================================
    # CHANGE 4: Add new GET endpoint
    # =============================================================================
    
    get_endpoint = '''
@app.route('/admin/who-am-i/get/<int:image_id>')
@admin_required
def admin_who_am_i_get(image_id):
    """Get image details for editing (including accepted_answers)"""
    from sqlalchemy import text
    
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
        'accepted_answers': result.accepted_answers,
        'active': result.active,
        'topics': topics
    })

'''
    
    # Find admin_who_am_i_edit and insert GET endpoint before it
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "@app.route('/admin/who-am-i/edit/" in line:
            lines.insert(i, get_endpoint)
            print(f"✓ Added GET endpoint at line {i}")
            break
    
    content = '\n'.join(lines)
    
    # =============================================================================
    # CHANGE 5: Update admin_who_am_i_edit()
    # =============================================================================
    
    # This is complex, so let's find it and replace the entire function
    lines = content.split('\n')
    new_lines = []
    skip_until = None
    
    for i, line in enumerate(lines):
        if skip_until and i < skip_until:
            continue
        
        if "@app.route('/admin/who-am-i/edit/<int:image_id>'" in line or \
           'def admin_who_am_i_edit(image_id):' in line:
            # Found the start, now find the end
            bracket_count = 0
            started = False
            end_line = i
            
            for j in range(i, len(lines)):
                if 'def admin_who_am_i_edit' in lines[j]:
                    started = True
                if started:
                    bracket_count += lines[j].count('{')
                    bracket_count -= lines[j].count('}')
                    # Look for next function definition
                    if j > i + 5 and ('def ' in lines[j] or '@app.route' in lines[j]):
                        end_line = j
                        break
            
            # Add new implementation
            new_lines.append('''@app.route('/admin/who-am-i/edit/<int:image_id>', methods=['GET', 'POST'])
@admin_required
def admin_who_am_i_edit(image_id):
    """Edit image details including accepted_answers"""
    from sqlalchemy import text
    
    if request.method == 'GET':
        # Redirect to main page (handled by GET endpoint now)
        return redirect(url_for('admin_who_am_i'))
    
    # POST - handle edit
    answer = request.form.get('answer')
    hint = request.form.get('hint', '')
    difficulty = request.form.get('difficulty')
    selected_topics = request.form.getlist('topics[]')
    
    # Handle accepted answers from form
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
''')
            skip_until = end_line
            print(f"✓ Replaced admin_who_am_i_edit() function")
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # =============================================================================
    # CHANGE 6: Update who_am_i_guess() checking logic
    # =============================================================================
    
    # Update SELECT query to include accepted_answers
    old_guess_select = r"SELECT s\.tiles_revealed, s\.guesses_made, s\.correct_guess, s\.quiz_attempt_id, i\.answer"
    new_guess_select = "SELECT s.tiles_revealed, s.guesses_made, s.correct_guess, s.quiz_attempt_id, \\n               i.answer, i.accepted_answers"
    
    content = re.sub(old_guess_select, new_guess_select, content)
    print("✓ Updated who_am_i_guess() SELECT query")
    
    # Add accepted_answers_json variable
    old_vars = r"(correct_answer = result\.answer)"
    new_vars = r"\1\n    accepted_answers_json = result.accepted_answers"
    
    content = re.sub(old_vars, new_vars, content)
    
    # Replace simple checking with flexible checking
    old_check = r"# Check if guess is correct \(case-insensitive\)\s+is_correct = guess\.lower\(\) == correct_answer\.lower\(\)"
    
    new_check = '''# Flexible answer checking with variants
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
    is_correct = guess_normalized in [a.lower().strip() for a in accepted_answers]'''
    
    content = re.sub(old_check, new_check, content, flags=re.DOTALL)
    print("✓ Updated guess checking logic")
    
    return content

def main():
    print("=" * 80)
    print("AUTOMATIC APP.PY UPDATER - WHO AM I ANSWER VARIANTS")
    print("=" * 80)
    print()
    
    filepath = 'app.py'
    
    if not os.path.exists(filepath):
        print("❌ Error: app.py not found in current directory")
        print("   Run this script from /home/bbsisk/mathapp")
        sys.exit(1)
    
    print(f"Found: {filepath}")
    print()
    
    # Create backup
    backup_path = backup_file(filepath)
    print()
    
    try:
        # Update the file
        print("Applying changes...")
        print()
        updated_content = update_app_py(filepath)
        
        # Write updated content
        with open(filepath, 'w') as f:
            f.write(updated_content)
        
        print()
        print("=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print()
        print(f"✓ app.py has been updated with all Who Am I changes")
        print(f"✓ Backup saved to: {backup_path}")
        print()
        print("Next steps:")
        print("1. Review the changes if desired")
        print("2. Reload your web app on PythonAnywhere")
        print("3. Test the admin interface")
        print("4. Test student guessing")
        print()
        print("To revert if needed:")
        print(f"  cp {backup_path} app.py")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR!")
        print("=" * 80)
        print()
        print(f"❌ Error updating app.py: {e}")
        print()
        print(f"Your original file is safe at: {backup_path}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
