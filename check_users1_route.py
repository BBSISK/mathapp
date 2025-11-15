#!/usr/bin/env python3
"""
Check for /users1 route and potential errors
"""

import sys

# Read app.py and look for /users1 route
with open('app.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 80)
print("SEARCHING FOR /users1 ROUTE")
print("=" * 80)

# Find the route
found = False
for i, line in enumerate(lines, 1):
    if '/users1' in line or '@app.route' in line and i < len(lines) and 'users1' in lines[i]:
        print(f"\nFound at line {i}:")
        # Print surrounding lines for context
        start = max(0, i - 5)
        end = min(len(lines), i + 30)
        for j in range(start, end):
            prefix = ">>> " if j == i - 1 else "    "
            print(f"{prefix}{j+1}: {lines[j]}")
        found = True
        break

if not found:
    print("\n❌ /users1 route NOT FOUND in app.py")
    print("\nSearching for similar user management routes...")
    for i, line in enumerate(lines, 1):
        if 'def' in line and ('user' in line.lower() or 'admin' in line.lower()):
            if 'route' in lines[max(0, i-2):i]:
                print(f"\nLine {i}: {line.strip()}")
