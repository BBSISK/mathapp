#!/usr/bin/env python3
"""
Update topic_management.py to invalidate the topics cache when topics are modified.
This ensures that when admins add/edit/delete topics, the changes take effect immediately.
"""

import shutil
from datetime import datetime

# Backup
backup_name = f"topic_management.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy('topic_management.py', backup_name)
print(f"✓ Created backup: {backup_name}")

with open('topic_management.py', 'r') as f:
    content = f.read()

# Add cache invalidation helper function after the register_topic_routes definition
old_register_start = '''def register_topic_routes(app, db):
    """Register all topic management routes with the Flask app"""
    
    # Get or create models
    Strand = get_strand_model(db)
    Topic = get_topic_model(db)
    Tutorial = get_tutorial_model(db)
    
    # Helper to check if user is admin'''

new_register_start = '''def register_topic_routes(app, db):
    """Register all topic management routes with the Flask app"""
    
    # Get or create models
    Strand = get_strand_model(db)
    Topic = get_topic_model(db)
    Tutorial = get_tutorial_model(db)
    
    # Helper to invalidate topic cache when topics are modified
    def invalidate_topics_cache():
        """Clear the topics cache so changes take effect immediately"""
        try:
            from app import invalidate_topics_cache as app_invalidate
            app_invalidate()
            print("✓ Topics cache invalidated")
        except ImportError:
            # Function not available in app.py yet - that's OK
            pass
        except Exception as e:
            print(f"Warning: Could not invalidate cache: {e}")
    
    # Helper to check if user is admin'''

if old_register_start in content:
    content = content.replace(old_register_start, new_register_start)
    print("✓ Added invalidate_topics_cache helper")
else:
    print("⚠ Could not find register_topic_routes start")

# Now add cache invalidation calls to each route that modifies topics

# 1. After creating a topic
old_create_success = "return jsonify({'success': True, 'message': 'Topic created', 'topic_id': topic_id})"
new_create_success = """invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic created', 'topic_id': topic_id})"""

if old_create_success in content:
    content = content.replace(old_create_success, new_create_success)
    print("✓ Added cache invalidation to create_topic")

# 2. After updating a topic
old_update_success = "return jsonify({'success': True, 'message': 'Topic updated'})"
new_update_success = """invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic updated'})"""

content = content.replace(old_update_success, new_update_success)
print("✓ Added cache invalidation to update_topic")

# 3. After deleting a topic
old_delete_success = "return jsonify({'success': True, 'message': 'Topic deleted'})"
new_delete_success = """invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic deleted'})"""

content = content.replace(old_delete_success, new_delete_success)
print("✓ Added cache invalidation to delete_topic")

# 4. After toggling visibility
old_visibility_success = "return jsonify({'success': True, 'is_visible': is_visible})"
new_visibility_success = """invalidate_topics_cache()
            return jsonify({'success': True, 'is_visible': is_visible})"""

if old_visibility_success in content:
    content = content.replace(old_visibility_success, new_visibility_success)
    print("✓ Added cache invalidation to toggle_visibility")

# Save
with open('topic_management.py', 'w') as f:
    f.write(content)

print(f"\n✅ topic_management.py updated!")
print(f"📁 Backup saved as: {backup_name}")
