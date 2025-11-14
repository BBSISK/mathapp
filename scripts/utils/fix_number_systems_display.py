"""
Fix Script for Number Systems Topic Display

This script will update your template files to include Number Systems.
Run this in your mathapp-main directory.
"""

import os
import re

def backup_file(filepath):
    """Create a backup of the file"""
    backup_path = filepath + '.backup'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✓ Backed up {filepath}")
        return True
    return False

def fix_student_app():
    """Fix student_app.html to include number_systems"""
    filepath = 'templates/student_app.html'
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix 1: Add to path1Topics array (after multiplication_division)
    if "'number_systems'" not in content and '"number_systems"' not in content:
        # Look for the pattern with multiplication_division
        pattern = r"('multiplication_division'|\"multiplication_division\"),\s*\n"
        replacement = r"\1,\n                    'number_systems',\n"
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
            print("✓ Added 'number_systems' to path1Topics array")
        else:
            print("⚠️  Could not find insertion point for path1Topics")
    
    # Fix 2: Add color mapping
    if "'number_systems': '#" not in content and '"number_systems": "#' not in content:
        # Look for multiplication_division color
        pattern = r"('multiplication_division'|\"multiplication_division\"):\s*'#[0-9a-fA-F]{6}',\s*\n"
        replacement = r"\1: '#3b82f6',\n                'number_systems': '#06b6d4',\n"
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
            print("✓ Added color mapping for number_systems")
        else:
            print("⚠️  Could not find insertion point for color mapping")
    
    # Write the updated content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}")
    return True

def fix_admin_dashboard():
    """Fix admin_dashboard.html to include number_systems"""
    filepath = 'templates/admin_dashboard.html'
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    changes_made = False
    
    # Fix 1: Add to filter dropdown (first select)
    if 'value="number_systems"' not in content:
        pattern = r'(<option value="multiplication_division">Multiplication & Division</option>\s*\n)'
        replacement = r'\1                            <option value="number_systems">Number Systems</option>\n'
        
        new_content = re.sub(pattern, replacement, content, count=1)
        if new_content != content:
            content = new_content
            changes_made = True
            print("✓ Added number_systems to filter dropdown")
    
    # Fix 2: Add to edit dropdown (if there's a second occurrence)
    pattern = r'(<option value="multiplication_division">Multiplication & Division</option>\s*\n)'
    matches = list(re.finditer(pattern, content))
    
    if len(matches) > 1:
        # There's a second dropdown, add to it too
        pos = matches[1].end()
        insertion = '                            <option value="number_systems">Number Systems</option>\n'
        content = content[:pos] + insertion + content[pos:]
        changes_made = True
        print("✓ Added number_systems to edit dropdown")
    
    # Fix 3: Add icon mapping
    if "'number_systems':" not in content and '"number_systems":' not in content:
        pattern = r"('multiplication_division'|\"multiplication_division\"):\s*'fa-[^']+',\s*\n"
        replacement = r"\1: 'fa-times',\n                    'number_systems': 'fa-hashtag',\n"
        
        new_content = re.sub(pattern, replacement, content, count=1)
        if new_content != content:
            content = new_content
            changes_made = True
            print("✓ Added icon mapping for number_systems")
    
    if changes_made:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Updated {filepath}")
    else:
        print(f"ℹ️  {filepath} already has number_systems or couldn't be updated")
    
    return True

def fix_app_py():
    """Fix app.py to include number_systems in valid_topics"""
    filepath = 'app.py'
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already in valid_topics
    if "'number_systems'" in content:
        # Check if it's in the valid_topics list in submit_quiz
        pattern = r"valid_topics\s*=\s*\[([^\]]+)\]"
        match = re.search(pattern, content)
        
        if match:
            topics_str = match.group(1)
            if 'number_systems' in topics_str:
                print("✓ number_systems already in valid_topics list")
                return True
            else:
                # Add it after multiplication_division
                new_topics = topics_str.replace(
                    "'multiplication_division',",
                    "'multiplication_division',\n        'number_systems',"
                )
                content = content.replace(topics_str, new_topics)
                print("✓ Added number_systems to valid_topics list")
        else:
            print("⚠️  Could not find valid_topics list in submit_quiz")
            return False
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}")
    return True

def main():
    print("\n" + "="*70)
    print("NUMBER SYSTEMS FIX SCRIPT")
    print("="*70 + "\n")
    
    print("This script will add Number Systems to your template files.\n")
    
    # Check we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ ERROR: app.py not found!")
        print("   Please run this script from your mathapp-main directory.\n")
        return
    
    print("Starting fixes...\n")
    
    # Fix each file
    success_count = 0
    
    if fix_student_app():
        success_count += 1
    
    print()
    
    if fix_admin_dashboard():
        success_count += 1
    
    print()
    
    if fix_app_py():
        success_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("FIX SUMMARY")
    print("="*70)
    
    if success_count == 3:
        print("✅ All files updated successfully!\n")
        print("Next steps:")
        print("1. Restart your Flask application")
        print("   - PythonAnywhere: Go to Web tab → Click 'Reload'")
        print("   - Local: Stop (Ctrl+C) and restart (python3 app.py)")
        print("2. Clear your browser cache (Ctrl+Shift+R)")
        print("3. Test the Number Systems topic!\n")
        
        print("📝 Backup files created:")
        print("   - templates/student_app.html.backup")
        print("   - templates/admin_dashboard.html.backup")
        print("   - app.py.backup")
    else:
        print("⚠️  Some files could not be updated.")
        print("   Please check the errors above and fix manually.\n")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
