#!/usr/bin/env python3
"""
Check what's in app.py for topic configuration
"""

import re

print("=" * 70)
print("CHECKING APP.PY CONFIGURATION")
print("=" * 70)

# Read app.py
with open('app.py', 'r') as f:
    content = f.read()

print("\n1. Searching for topic definitions...")

# Search for the new topics
topics_to_find = [
    'solving_equations',
    'simplifying_expressions', 
    'expanding_factorising'
]

for topic in topics_to_find:
    count = content.count(f"'{topic}'")
    if count > 0:
        print(f"   ✓ '{topic}' found {count} times in app.py")
    else:
        print(f"   ✗ '{topic}' NOT FOUND in app.py")

print("\n2. Checking Algebra and Functions strand configuration...")

# Find all mentions of 'Algebra and Functions'
matches = re.findall(r"'Algebra and Functions':\s*\[([^\]]+)\]", content)

if matches:
    print(f"   Found {len(matches)} configuration(s) for 'Algebra and Functions':")
    for i, match in enumerate(matches, 1):
        topics_list = [t.strip().strip("'\"") for t in match.split(',')]
        print(f"\n   Configuration {i}:")
        for topic in topics_list:
            print(f"     - {topic}")
else:
    print("   ✗ No 'Algebra and Functions' configuration found")

print("\n3. Checking for topic title definitions...")

# Look for topic titles
for topic in topics_to_find:
    # Search for patterns like 'solving_equations': {'title': 'Solving Equations'
    pattern = f"'{topic}':\\s*{{[^}}]+}}"
    match = re.search(pattern, content)
    if match:
        print(f"   ✓ {topic} configuration found: {match.group(0)[:80]}...")
    else:
        print(f"   ✗ {topic} configuration NOT FOUND")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)

if all(content.count(f"'{topic}'") == 0 for topic in topics_to_find):
    print("\n❌ NONE of the new topics are in app.py")
    print("\nYou need to update app.py. Two options:")
    print("\n  OPTION 1 - Automatic:")
    print("    python3 update_app_for_algebra.py")
    print("\n  OPTION 2 - Manual:")
    print("    Follow instructions in UPDATE_APP_INSTRUCTIONS.txt")
    print("\n  Then reload your web app on PythonAnywhere")
    
elif any(content.count(f"'{topic}'") == 0 for topic in topics_to_find):
    print("\n⚠️  SOME topics are in app.py but not all")
    print("\nYou may have partially updated app.py.")
    print("Run: python3 update_app_for_algebra.py")
    print("Then reload your web app")
    
else:
    print("\n✓ All topics appear to be in app.py")
    print("\nIf questions still don't load:")
    print("  1. Make sure you reloaded your web app")
    print("  2. Check browser console for errors")
    print("  3. Clear browser cache and try again")

print("=" * 70)
