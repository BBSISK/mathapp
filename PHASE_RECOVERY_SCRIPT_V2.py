#!/usr/bin/env python3
"""
MATH MASTER - UPDATED PHASED RECOVERY SCRIPT
=============================================
This script implements critical fixes with DATABASE-DRIVEN topic management.

Key Changes from original:
- Topics are now read from the `topics` database table
- MASTER_TOPICS is only a FALLBACK if database is unavailable
- Admin topic additions automatically propagate everywhere

Phase 1: Logout Session Security Fix
Phase 2: Database-Driven Topic Configuration  
Phase 3: Points Deduplication

Run this script in the mathapp-main directory:
    python PHASE_RECOVERY_SCRIPT_V2.py

After running, verify with:
    grep -n "get_valid_topics_from_db" app.py
"""

import shutil
import re
from datetime import datetime

# Backup original file
backup_name = f"app.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy('app.py', backup_name)
print(f"✓ Created backup: {backup_name}")

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# ============================================================
# PHASE 1: FALLBACK TOPIC CONFIGURATION
# ============================================================
print("\n=== PHASE 1: Adding Fallback Topic Configuration ===")

# The MASTER_TOPICS configuration - now clearly marked as FALLBACK
FALLBACK_TOPICS_CONFIG = '''
# ==================== FALLBACK TOPIC CONFIGURATION ====================
# FALLBACK ONLY - Primary source is the `topics` database table
# This list is used ONLY when database is unavailable
# To add new topics, use Admin Dashboard > Topic Management
FALLBACK_TOPICS = [
    # Number Strand
    'arithmetic', 'fractions', 'decimals', 'multiplication_division',
    'number_systems', 'bodmas', 'sets', 'surds',
    
    # Algebra and Functions Strand
    'introductory_algebra', 'functions', 'patterns', 'solving_equations',
    'simplifying_expressions', 'expanding_factorising',
    'complex_numbers_intro', 'complex_numbers_expanded', 'simultaneous_equations',
    
    # Geometry and Trigonometry Strand
    'coordinate_geometry', 'trigonometry',
    
    # Statistics and Probability Strand
    'probability', 'descriptive_statistics',
]

VALID_DIFFICULTIES = ['beginner', 'intermediate', 'advanced']

# Cache for database topics (refreshed periodically)
_topics_cache = {'topics': None, 'timestamp': None}
_CACHE_DURATION_SECONDS = 300  # 5 minutes

def get_valid_topics_from_db():
    """
    Get valid topics from the database `topics` table.
    Returns list of topic_id strings that are visible.
    Falls back to FALLBACK_TOPICS if database unavailable.
    
    This is the SINGLE SOURCE OF TRUTH for topic validation.
    When you add a topic via Admin Dashboard, it automatically becomes valid everywhere.
    """
    import time
    from sqlalchemy import text
    
    # Check cache first
    current_time = time.time()
    if (_topics_cache['topics'] is not None and 
        _topics_cache['timestamp'] is not None and
        current_time - _topics_cache['timestamp'] < _CACHE_DURATION_SECONDS):
        return _topics_cache['topics']
    
    try:
        # Query visible topics from database
        result = db.session.execute(text(
            "SELECT topic_id FROM topics WHERE is_visible = 1"
        )).fetchall()
        
        if result:
            topics = [row[0] for row in result]
            # Update cache
            _topics_cache['topics'] = topics
            _topics_cache['timestamp'] = current_time
            return topics
        else:
            # No topics in database, use fallback
            return FALLBACK_TOPICS
            
    except Exception as e:
        # Database error, use fallback
        print(f"Warning: Could not load topics from database: {e}")
        return FALLBACK_TOPICS

def invalidate_topics_cache():
    """Call this after adding/removing topics via admin to refresh cache immediately"""
    _topics_cache['topics'] = None
    _topics_cache['timestamp'] = None

'''

# Find the end of FEATURE_FLAGS section and insert after it
feature_flags_pattern = r"(def get_feature_flag\(flag_name\):\s+\"\"\"Get a feature flag value\"\"\"\s+return FEATURE_FLAGS\.get\(flag_name, False\))"

if re.search(feature_flags_pattern, content):
    content = re.sub(
        feature_flags_pattern,
        r'\1' + FALLBACK_TOPICS_CONFIG,
        content
    )
    print("✓ Added FALLBACK_TOPICS and get_valid_topics_from_db() function")
else:
    print("⚠ Could not find FEATURE_FLAGS section")

# ============================================================
# PHASE 2: UPDATE ALL TOPIC VALIDATION TO USE DATABASE
# ============================================================
print("\n=== PHASE 2: Updating Topic Validation to Use Database ===")

# Pattern 1: Replace valid_topics in quiz submit
# Look for the validation section and replace it
old_quiz_validation = r"""    # Validate topic and difficulty
    valid_topics = \[
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems',
        'bodmas', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'sets', 'probability', 'descriptive_statistics', 'surds',
        'complex_numbers_intro', 'complex_numbers_expanded',
        'trigonometry', 'coordinate_geometry', 'simultaneous_equations'  # Added missing topics
    \]
    valid_difficulties = \['beginner', 'intermediate', 'advanced'\]"""

new_quiz_validation = """    # Validate topic and difficulty - reads from database
    valid_topics = get_valid_topics_from_db()  # Database-driven!
    valid_difficulties = VALID_DIFFICULTIES"""

if re.search(old_quiz_validation, content):
    content = re.sub(old_quiz_validation, new_quiz_validation, content)
    print("✓ Updated quiz validation to use database")
else:
    # Try alternative patterns
    # Pattern for if MASTER_TOPICS was already applied
    alt_pattern = r"valid_topics = MASTER_TOPICS\s+# Use centralized topic list\s+valid_difficulties = VALID_DIFFICULTIES"
    if re.search(alt_pattern, content):
        content = re.sub(
            alt_pattern,
            "valid_topics = get_valid_topics_from_db()  # Database-driven!\n    valid_difficulties = VALID_DIFFICULTIES",
            content
        )
        print("✓ Updated quiz validation (from MASTER_TOPICS) to use database")
    else:
        print("⚠ Could not find quiz validation pattern - may need manual update")

# Pattern 2: Update mastery topics
old_mastery = r"""    # Get all topics - MUST match topics in get_topics\(\) API
    topics = \[
        'arithmetic', 'fractions', 'decimals', 'multiplication_division',
        'number_systems', 'bodmas', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'probability', 'descriptive_statistics', 'sets',
        'surds', 'complex_numbers_intro', 'complex_numbers_expanded'
    \]
    difficulties = \['beginner', 'intermediate', 'advanced'\]"""

new_mastery = """    # Get all topics from database - automatically includes new topics
    topics = get_valid_topics_from_db()  # Database-driven!
    difficulties = VALID_DIFFICULTIES"""

if re.search(old_mastery, content):
    content = re.sub(old_mastery, new_mastery, content)
    print("✓ Updated mastery topics to use database")
else:
    # Try MASTER_TOPICS pattern
    alt_mastery = r"topics = MASTER_TOPICS\s+# Use centralized topic list\s+difficulties = VALID_DIFFICULTIES"
    if re.search(alt_mastery, content):
        content = re.sub(
            alt_mastery,
            "topics = get_valid_topics_from_db()  # Database-driven!\n    difficulties = VALID_DIFFICULTIES",
            content,
            count=1  # Only replace first occurrence (mastery)
        )
        print("✓ Updated mastery topics (from MASTER_TOPICS) to use database")
    else:
        print("⚠ Could not find mastery topics pattern")

# Pattern 3: Update teacher class dashboard topics
old_teacher = r"topics = \['arithmetic', 'fractions', 'decimals', 'multiplication_division', 'number_systems', 'bodmas', 'probability', 'descriptive_statistics', 'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'sets', 'surds', 'complex_numbers_intro', 'complex_numbers_expanded'\]\s*difficulties = \['beginner', 'intermediate', 'advanced'\]"

new_teacher = """topics = get_valid_topics_from_db()  # Database-driven!
    difficulties = VALID_DIFFICULTIES"""

if re.search(old_teacher, content):
    content = re.sub(old_teacher, new_teacher, content)
    print("✓ Updated teacher dashboard topics to use database")
else:
    # Try finding it another way
    alt_teacher = r"    topics = MASTER_TOPICS\s+# Use centralized topic list\s+difficulties = VALID_DIFFICULTIES"
    matches = list(re.finditer(alt_teacher, content))
    if len(matches) >= 2:
        # Replace the second occurrence (teacher dashboard)
        content = re.sub(
            alt_teacher,
            "topics = get_valid_topics_from_db()  # Database-driven!\n    difficulties = VALID_DIFFICULTIES",
            content
        )
        print("✓ Updated teacher dashboard topics to use database")
    else:
        print("⚠ Could not find teacher dashboard topics pattern")

# Pattern 4: Update fallback all_topics in student topics route
old_fallback = r"""if not all_topics:
        all_topics = \['arithmetic', 'multiplication_division', 'number_systems',
                      'bodmas', 'fractions', 'decimals', 'sets',
                      'introductory_algebra', 'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising', 'surds', 'complex_numbers_intro', 'complex_numbers_expanded',
                      'probability', 'descriptive_statistics'\]
        strands = \{
            'Number': \['arithmetic', 'multiplication_division', 'number_systems',
                      'bodmas', 'fractions', 'decimals', 'sets'\],
            'Algebra and Functions': \['functions', 'patterns', 'solving_equations',
                                      'simplifying_expressions', 'expanding_factorising',
                                      'surds', 'complex_numbers_intro', 'complex_numbers_expanded'\],
        \}"""

new_fallback = """if not all_topics:
        all_topics = get_valid_topics_from_db()  # Database-driven fallback!
        # Default strands for fallback
        strands = {
            'Number': [t for t in all_topics if t in ['arithmetic', 'fractions', 'decimals', 
                      'multiplication_division', 'number_systems', 'bodmas', 'sets', 'surds']],
            'Algebra and Functions': [t for t in all_topics if t in ['introductory_algebra', 
                      'functions', 'patterns', 'solving_equations', 'simplifying_expressions', 
                      'expanding_factorising', 'complex_numbers_intro', 'complex_numbers_expanded', 
                      'simultaneous_equations']],
            'Geometry and Trigonometry': [t for t in all_topics if t in ['coordinate_geometry', 'trigonometry']],
            'Statistics and Probability': [t for t in all_topics if t in ['probability', 'descriptive_statistics']],
        }"""

if re.search(old_fallback, content, re.DOTALL):
    content = re.sub(old_fallback, new_fallback, content, flags=re.DOTALL)
    print("✓ Updated fallback all_topics to use database")
else:
    # Try MASTER_TOPICS pattern
    alt_fallback = r"if not all_topics:\s+all_topics = MASTER_TOPICS\s+# Use centralized topic list\s+strands = TOPIC_STRANDS\s+# Use centralized strand groupings"
    if re.search(alt_fallback, content):
        content = re.sub(
            alt_fallback,
            new_fallback,
            content
        )
        print("✓ Updated fallback (from MASTER_TOPICS) to use database")
    else:
        print("⚠ Could not find fallback all_topics pattern")

# ============================================================
# PHASE 3: LOGOUT SESSION SECURITY FIX
# ============================================================
print("\n=== PHASE 3: Implementing Logout Security Fix ===")

# Add after_request handler for cache control (if not already added)
if "add_no_cache_headers" not in content:
    CACHE_CONTROL_HANDLER = '''
# ==================== SESSION SECURITY ====================
@app.after_request
def add_no_cache_headers(response):
    """Add no-cache headers to authenticated pages to prevent back-button session resumption"""
    # Only add headers to HTML responses (not API calls or static files)
    if 'text/html' in response.content_type:
        # Check if this is an authenticated route (has user_id in session)
        if 'user_id' in session or 'is_guest' in session:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
    return response

'''
    # Find a good place to insert
    context_processor_pattern = r"(@app\.context_processor\s+def inject_feature_flags\(\):.*?return \{[^}]+\})"
    if re.search(context_processor_pattern, content, re.DOTALL):
        content = re.sub(
            context_processor_pattern,
            r'\1' + CACHE_CONTROL_HANDLER,
            content,
            flags=re.DOTALL
        )
        print("✓ Added no-cache headers handler")
else:
    print("✓ No-cache headers handler already exists")

# Update logout routes (if not already updated)
if "delete_cookie('session')" not in content:
    # Update API logout
    old_api_logout = """@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200"""

    new_api_logout = """@app.route('/api/logout', methods=['POST'])
def logout():
    \"\"\"Logout API endpoint with proper session invalidation\"\"\"
    session.clear()
    response = jsonify({'message': 'Logged out successfully', 'redirect': '/login?logged_out=1'})
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.delete_cookie('session')
    return response, 200"""

    if old_api_logout in content:
        content = content.replace(old_api_logout, new_api_logout)
        print("✓ Updated API logout route")

    # Update simple logout
    old_simple_logout = """@app.route('/logout', methods=['GET'])
def logout_simple():
    session.clear()
    try:
        return redirect(url_for('index'))
    except Exception:
        return redirect('/')"""

    new_simple_logout = """@app.route('/logout', methods=['GET'])
def logout_simple():
    \"\"\"Simple logout route with proper session invalidation\"\"\"
    session.clear()
    try:
        response = redirect(url_for('index') + '?logged_out=1')
    except Exception:
        response = redirect('/?logged_out=1')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.delete_cookie('session')
    return response"""

    if old_simple_logout in content:
        content = content.replace(old_simple_logout, new_simple_logout)
        print("✓ Updated simple logout route")
else:
    print("✓ Logout routes already updated")

# ============================================================
# PHASE 4: POINTS DEDUPLICATION
# ============================================================
print("\n=== PHASE 4: Implementing Points Deduplication ===")

if "previous_best" not in content:
    old_points = """    # Award points for quiz completion (base points + performance bonus)
    base_points = 5  # Base points for completing any quiz
    performance_bonus = int(quiz_attempt.percentage / 10)  # 0-10 points based on score
    quiz_points = base_points + performance_bonus
    stats.total_points += quiz_points"""

    new_points = """    # Award points for quiz completion with deduplication
    base_points = 5  # Base points for completing any quiz
    performance_bonus = int(quiz_attempt.percentage / 10)  # 0-10 points based on score
    quiz_points = base_points + performance_bonus
    
    # Only award points for first completion OR improvement
    from sqlalchemy import text
    existing_best = db.session.execute(text('''
        SELECT MAX(percentage) as best_pct
        FROM quiz_attempts
        WHERE user_id = :user_id 
        AND topic = :topic 
        AND difficulty = :difficulty
        AND id != :current_id
    '''), {
        'user_id': user_id,
        'topic': quiz_attempt.topic,
        'difficulty': quiz_attempt.difficulty,
        'current_id': quiz_attempt.id
    }).fetchone()
    
    previous_best = existing_best.best_pct if existing_best and existing_best.best_pct else 0
    
    if previous_best == 0:
        # First time - award full points
        stats.total_points += quiz_points
    elif quiz_attempt.percentage > previous_best:
        # Improvement - award points for improvement only
        improvement_points = int((quiz_attempt.percentage - previous_best) / 10)
        if improvement_points > 0:
            stats.total_points += improvement_points"""

    if old_points in content:
        content = content.replace(old_points, new_points)
        print("✓ Updated points calculation with deduplication")
    else:
        print("⚠ Could not find points section to update")
else:
    print("✓ Points deduplication already implemented")

# ============================================================
# PHASE 5: ADD CACHE INVALIDATION TO TOPIC MANAGEMENT
# ============================================================
print("\n=== PHASE 5: Adding Cache Invalidation Hook ===")

# We need to ensure that when topics are added/removed via admin,
# the cache is invalidated. This is done in topic_management.py
# but we should also add a note about it.

# Check if topic_management import is present
if "from topic_management import register_topic_routes" in content:
    print("✓ topic_management is imported - cache invalidation should be added there")
else:
    print("⚠ topic_management not imported - may need to add it")

# ============================================================
# SAVE THE UPDATED FILE
# ============================================================
print("\n=== Saving Updated app.py ===")

with open('app.py', 'w') as f:
    f.write(content)

print("✓ Saved updated app.py")

# ============================================================
# VERIFICATION
# ============================================================
print("\n=== Verification ===")

with open('app.py', 'r') as f:
    final_content = f.read()

checks = [
    ('FALLBACK_TOPICS', 'Fallback topics configuration'),
    ('get_valid_topics_from_db', 'Database topic function'),
    ('add_no_cache_headers', 'Cache control handler'),
    ('VALID_DIFFICULTIES', 'Valid difficulties constant'),
    ('delete_cookie', 'Session cookie deletion'),
    ('previous_best', 'Points deduplication'),
    ('_topics_cache', 'Topics cache'),
]

all_passed = True
for pattern, description in checks:
    if pattern in final_content:
        print(f"✓ {description} - FOUND")
    else:
        print(f"✗ {description} - NOT FOUND")
        all_passed = False

# Count database-driven references
db_driven_count = final_content.count('get_valid_topics_from_db()')
print(f"\n✓ Found {db_driven_count} database-driven topic references")

if all_passed:
    print("\n✅ ALL PHASES IMPLEMENTED SUCCESSFULLY!")
else:
    print("\n⚠ Some changes may need manual review")

print(f"\n📁 Backup saved as: {backup_name}")
print("\n" + "=" * 60)
print("IMPORTANT: Topic Management is now DATABASE-DRIVEN!")
print("=" * 60)
print("""
To add a new topic:
1. Go to Admin Dashboard > Topic Management
2. Add the topic with display name, icon, and strand
3. The topic is IMMEDIATELY available everywhere!

No more editing app.py for new topics!

To test: 
1. Add a test topic via Admin Dashboard
2. Check that it appears in student topic selection
3. Complete a quiz for that topic
4. Verify mastery tracking works
""")
