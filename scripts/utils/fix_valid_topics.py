"""
Quick Fix for app.py - Add number_systems to valid_topics

Run this script to automatically fix the valid_topics list in app.py
"""

import os
import re

def fix_app_py_valid_topics():
    print("\n" + "="*70)
    print("FIXING app.py - Adding number_systems to valid_topics")
    print("="*70 + "\n")
    
    filepath = 'app.py'
    
    if not os.path.exists(filepath):
        print(f"❌ ERROR: {filepath} not found!")
        print("   Make sure you're in the mathapp-main directory.\n")
        return False
    
    # Backup
    backup_path = filepath + '.backup_validtopics'
    with open(filepath, 'r') as f:
        content = f.read()
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    
    # Check if already fixed
    if "'number_systems'" in content or '"number_systems"' in content:
        # Check if it's in the valid_topics list
        # Look for the valid_topics list in submit_quiz function
        pattern = r'valid_topics\s*=\s*\[\s*([^\]]+)\]'
        match = re.search(pattern, content)
        
        if match:
            topics_block = match.group(0)
            topics_content = match.group(1)
            
            if 'number_systems' in topics_content:
                print("✓ number_systems already in valid_topics list!")
                print("   No changes needed.\n")
                return True
            else:
                # Add number_systems after multiplication_division
                print("Found valid_topics list, adding number_systems...")
                
                # Find where to insert (after multiplication_division)
                if "'multiplication_division'" in topics_content:
                    new_topics_content = topics_content.replace(
                        "'multiplication_division'",
                        "'multiplication_division', 'number_systems'"
                    )
                elif '"multiplication_division"' in topics_content:
                    new_topics_content = topics_content.replace(
                        '"multiplication_division"',
                        '"multiplication_division", "number_systems"'
                    )
                else:
                    # Just add it at the end before closing bracket
                    new_topics_content = topics_content.rstrip() + ", 'number_systems'\n    "
                
                new_topics_block = topics_block.replace(topics_content, new_topics_content)
                content = content.replace(topics_block, new_topics_block)
                
                print("✓ Added 'number_systems' to valid_topics list")
        else:
            print("⚠️  WARNING: Could not find valid_topics list in expected format")
            print("   You may need to add it manually.\n")
            print("Find this section in app.py (in submit_quiz function):")
            print("")
            print("    valid_topics = [")
            print("        'arithmetic', 'fractions', 'decimals', 'multiplication_division',")
            print("        'bodmas', 'functions', 'sets', 'probability', 'surds',")
            print("        'complex_numbers_intro', 'complex_numbers_expanded'")
            print("    ]")
            print("")
            print("Add this line after 'multiplication_division',:")
            print("        'number_systems',")
            print("")
            return False
    else:
        print("⚠️  'number_systems' not found anywhere in app.py")
        print("   This is unusual. Please check your app.py file.\n")
        return False
    
    # Write the updated content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}\n")
    print("="*70)
    print("✅ FIX COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("   - PythonAnywhere: Web tab → Click 'Reload'")
    print("   - Local: Ctrl+C then python3 app.py")
    print("")
    print("2. Clear browser cache: Ctrl+Shift+R")
    print("")
    print("3. Test Number Systems topic!")
    print("")
    print("="*70 + "\n")
    
    return True

if __name__ == '__main__':
    try:
        if not os.path.exists('app.py'):
            print("\n❌ ERROR: app.py not found!")
            print("Please run this from your mathapp-main directory.\n")
        else:
            fix_app_py_valid_topics()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
