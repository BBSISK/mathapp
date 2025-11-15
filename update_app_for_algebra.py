#!/usr/bin/env python3
"""
Automatically update app.py to include 3 new Algebra topics
This script modifies your existing app.py file in place.

BACKUP YOUR app.py BEFORE RUNNING THIS!
"""

import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✓ Created backup: {backup_path}")
    return backup_path

def update_topics_dictionary(content):
    """Add new topics to TOPICS dictionary"""
    # Find the TOPICS dictionary
    pattern = r"(    'patterns': \{'title': 'Patterns', 'icon': '[^']+'\},)"
    
    new_topics = """    'solving_equations': {'title': 'Solving Equations', 'icon': 'equals'},
    'simplifying_expressions': {'title': 'Simplifying Expressions', 'icon': 'calculator'},
    'expanding_factorising': {'title': 'Expanding & Factorising', 'icon': 'brackets'},"""
    
    replacement = r"\1\n" + new_topics
    content = re.sub(pattern, replacement, content)
    
    return content

def update_topic_order(content):
    """Update the CASE statement for topic ordering"""
    # Find patterns ordering and add new topics after it
    pattern = r"(WHEN 'patterns' THEN \d+)"
    
    # This will add the new topics with sequential numbers
    new_order = r"\1\n                    WHEN 'solving_equations' THEN 3\n                    WHEN 'simplifying_expressions' THEN 4\n                    WHEN 'expanding_factorising' THEN 5"
    
    content = re.sub(pattern, new_order, content)
    
    return content

def update_strand_topics(content):
    """Update Algebra and Functions strand to include new topics"""
    # Pattern to match the Algebra and Functions line
    pattern = r"('Algebra and Functions': \['functions', 'patterns'\])"
    
    replacement = "'Algebra and Functions': ['functions', 'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising']"
    
    content = re.sub(pattern, replacement, content)
    
    return content

def update_topic_lists(content):
    """Update any topic lists that include patterns"""
    # Find topic lists that have both functions and patterns
    # Pattern: list with 'functions' and 'patterns'
    pattern = r"(\[.*?'functions'.*?'patterns'.*?\])"
    
    def add_new_topics(match):
        list_str = match.group(1)
        if 'solving_equations' not in list_str:
            # Add new topics before the closing bracket
            list_str = list_str.replace("'patterns'", "'patterns', 'solving_equations', 'simplifying_expressions', 'expanding_factorising'")
        return list_str
    
    content = re.sub(pattern, add_new_topics, content, flags=re.DOTALL)
    
    return content

def main():
    print("=" * 70)
    print("AUTO-UPDATE APP.PY FOR NEW ALGEBRA TOPICS")
    print("=" * 70)
    
    filepath = 'app.py'
    
    try:
        # Create backup
        print("\n1. Creating backup...")
        backup_path = backup_file(filepath)
        
        # Read current app.py
        print("\n2. Reading app.py...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   File size: {len(content)} characters")
        
        # Apply updates
        print("\n3. Applying updates...")
        
        print("   - Updating TOPICS dictionary...")
        content = update_topics_dictionary(content)
        
        print("   - Updating topic ordering...")
        content = update_topic_order(content)
        
        print("   - Updating strand topics...")
        content = update_strand_topics(content)
        
        print("   - Updating topic lists...")
        content = update_topic_lists(content)
        
        # Write updated content
        print("\n4. Writing updated app.py...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✓ Updated file size: {len(content)} characters")
        
        # Verify changes
        print("\n5. Verifying changes...")
        with open(filepath, 'r') as f:
            updated_content = f.read()
        
        checks = [
            ("'solving_equations'", "Solving Equations topic"),
            ("'simplifying_expressions'", "Simplifying Expressions topic"),
            ("'expanding_factorising'", "Expanding & Factorising topic"),
        ]
        
        all_good = True
        for check_str, description in checks:
            if check_str in updated_content:
                print(f"   ✓ {description} found")
            else:
                print(f"   ✗ {description} NOT found")
                all_good = False
        
        if all_good:
            print("\n" + "=" * 70)
            print("✓ APP.PY SUCCESSFULLY UPDATED!")
            print(f"  Backup saved at: {backup_path}")
            print("\n  Next steps:")
            print("  1. Upload the updated app.py to PythonAnywhere")
            print("  2. Run add_algebra_topics.py to add questions")
            print("  3. Reload your web app")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠ SOME UPDATES MAY HAVE FAILED")
            print(f"  Please check the updated app.py manually")
            print(f"  Backup is available at: {backup_path}")
            print("=" * 70)
        
    except FileNotFoundError:
        print(f"\n✗ Error: app.py not found in current directory")
        print(f"   Please run this script from your mathapp directory")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
