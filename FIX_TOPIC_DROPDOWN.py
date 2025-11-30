#!/usr/bin/env python3
"""
Fix the admin topics-list dropdown to include ALL topics from the topics table,
not just topics that have questions.

This ensures that when a new topic is added via Admin Dashboard,
it immediately appears in all topic filter dropdowns.
"""

import shutil
from datetime import datetime

# Backup
backup_name = f"app.py.backup_dropdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy('app.py', backup_name)
print(f"✓ Created backup: {backup_name}")

with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the admin_topics_list function
old_function = '''@app.route('/api/admin/topics-list')
@login_required
@role_required('admin')
def admin_topics_list():
    """Get all distinct topics from questions table with counts"""
    from sqlalchemy import func

    # Query to get topics and their question counts
    topics_query = db.session.query(
        Question.topic,
        func.count(Question.id).label('count')
    ).group_by(Question.topic).order_by(Question.topic).all()

    # Format topic names for display
    def format_topic_name(topic):
        """Convert topic key to display name"""
        return topic.replace('_', ' ').title()

    topics = [
        {
            'value': topic,
            'name': format_topic_name(topic),
            'count': count
        }
        for topic, count in topics_query
    ]

    return jsonify({'topics': topics})'''

new_function = '''@app.route('/api/admin/topics-list')
@login_required
@role_required('admin')
def admin_topics_list():
    """
    Get all topics for dropdown - combines topics from:
    1. The topics table (admin-managed, authoritative)
    2. The questions table (for topics with questions but not yet in topics table)
    
    This ensures new topics added via Admin Dashboard appear immediately.
    """
    from sqlalchemy import func, text
    
    topics_dict = {}  # Use dict to avoid duplicates
    
    # First, get all topics from the topics table (admin-managed)
    try:
        db_topics = db.session.execute(text("""
            SELECT t.topic_id, t.display_name, 
                   (SELECT COUNT(*) FROM questions q WHERE q.topic = t.topic_id) as question_count
            FROM topics t
            WHERE t.is_visible = 1
            ORDER BY t.sort_order, t.display_name
        """)).fetchall()
        
        for topic_id, display_name, count in db_topics:
            topics_dict[topic_id] = {
                'value': topic_id,
                'name': display_name,
                'count': count or 0
            }
    except Exception as e:
        print(f"Warning: Could not load from topics table: {e}")
    
    # Also get topics from questions table (for any topics not yet in topics table)
    try:
        questions_topics = db.session.query(
            Question.topic,
            func.count(Question.id).label('count')
        ).group_by(Question.topic).all()
        
        for topic, count in questions_topics:
            if topic not in topics_dict:
                # Topic exists in questions but not in topics table
                topics_dict[topic] = {
                    'value': topic,
                    'name': topic.replace('_', ' ').title(),
                    'count': count
                }
            else:
                # Update count if questions table has more (shouldn't happen, but safety)
                if count > topics_dict[topic]['count']:
                    topics_dict[topic]['count'] = count
    except Exception as e:
        print(f"Warning: Could not load from questions table: {e}")
    
    # Convert to list and sort
    topics = sorted(topics_dict.values(), key=lambda x: x['name'])
    
    return jsonify({'topics': topics})'''

if old_function in content:
    content = content.replace(old_function, new_function)
    print("✓ Updated admin_topics_list to read from topics table")
else:
    print("⚠ Could not find exact admin_topics_list function")
    print("  Trying alternative approach...")
    
    # Try to find and replace just the core query part
    if "Get all distinct topics from questions table with counts" in content:
        # Find the function by docstring and replace
        import re
        pattern = r'(@app\.route\(\'/api/admin/topics-list\'\).*?return jsonify\(\{\'topics\': topics\}\))'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_function, content, flags=re.DOTALL)
            print("✓ Updated admin_topics_list using regex")
        else:
            print("⚠ Could not update - manual intervention needed")

# Save
with open('app.py', 'w') as f:
    f.write(content)

print("✓ Saved updated app.py")
print(f"📁 Backup: {backup_name}")
print("\nThe topic dropdown in Admin > Flag Questions will now show ALL topics from the topics table!")
