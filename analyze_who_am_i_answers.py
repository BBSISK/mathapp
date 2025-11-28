#!/usr/bin/env python3
"""
Who Am I - Answer Variants Generator
Analyzes each mystery image and generates multiple acceptable answer variants
"""
import sys
import os
import json

project_home = '/home/bbsisk/mathapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['PRIZE_SYSTEM_ENABLED'] = 'true'
os.environ['AVATAR_SYSTEM_ENABLED'] = 'true'

from app import app, db
from sqlalchemy import text

print("=" * 80)
print("WHO AM I - ANSWER VARIANTS ANALYSIS")
print("=" * 80)
print()

def generate_answer_variants(answer):
    """
    Generate acceptable answer variants for a given answer
    Returns a list of acceptable variations
    """
    variants = set()
    
    # Original answer
    variants.add(answer.lower().strip())
    
    # Common variations to handle:
    # 1. With/without titles (Dr., Sir, Professor, etc.)
    # 2. First name only, last name only, full name
    # 3. Different name formats
    # 4. With/without middle names or initials
    # 5. Nicknames or alternative names
    
    answer_lower = answer.lower().strip()
    
    # Remove common titles
    titles = ['dr.', 'dr', 'sir', 'professor', 'prof.', 'prof', 'dame', 'lord', 'lady']
    for title in titles:
        if answer_lower.startswith(title + ' '):
            without_title = answer_lower.replace(title + ' ', '', 1).strip()
            variants.add(without_title)
    
    # Split into parts
    parts = answer_lower.split()
    
    if len(parts) >= 2:
        # First name only
        variants.add(parts[0])
        
        # Last name only
        variants.add(parts[-1])
        
        # First and last (skip middle)
        if len(parts) > 2:
            variants.add(f"{parts[0]} {parts[-1]}")
        
        # Last, First (some people might type it this way)
        variants.add(f"{parts[-1]}, {parts[0]}")
        
        # Remove middle initials (e.g., "Isaac M. Newton" -> "Isaac Newton")
        filtered_parts = [p for p in parts if len(p) > 2 or not p.endswith('.')]
        if len(filtered_parts) != len(parts):
            variants.add(' '.join(filtered_parts))
    
    # Remove any punctuation variants
    import string
    no_punct = answer_lower.translate(str.maketrans('', '', string.punctuation))
    if no_punct != answer_lower:
        variants.add(no_punct)
    
    return sorted(list(variants))

# Known mathematicians and their common variants
KNOWN_VARIANTS = {
    'pythagoras': ['pythagoras', 'pythagoras of samos'],
    'euclid': ['euclid', 'euclid of alexandria'],
    'archimedes': ['archimedes', 'archimedes of syracuse'],
    'isaac newton': ['newton', 'isaac newton', 'sir isaac newton', 'i. newton'],
    'leonhard euler': ['euler', 'leonhard euler', 'leonard euler'],
    'carl friedrich gauss': ['gauss', 'carl gauss', 'friedrich gauss', 'carl friedrich gauss', 'c.f. gauss'],
    'pierre de fermat': ['fermat', 'pierre fermat', 'pierre de fermat'],
    'blaise pascal': ['pascal', 'blaise pascal'],
    'rené descartes': ['descartes', 'rene descartes', 'rené descartes', 'renee descartes'],
    'gottfried leibniz': ['leibniz', 'gottfried leibniz', 'gottfried wilhelm leibniz'],
    'ada lovelace': ['lovelace', 'ada lovelace', 'lady lovelace', 'augusta ada lovelace'],
    'alan turing': ['turing', 'alan turing', 'alan mathison turing', 'a.m. turing'],
    'emmy noether': ['noether', 'emmy noether', 'amalie noether'],
    'srinivasa ramanujan': ['ramanujan', 'srinivasa ramanujan', 'ramanuj an'],
    'john von neumann': ['neumann', 'von neumann', 'john neumann', 'john von neumann'],
    'kurt gödel': ['godel', 'gödel', 'kurt godel', 'kurt gödel'],
    'andrew wiles': ['wiles', 'andrew wiles', 'andrew john wiles'],
    'benoit mandelbrot': ['mandelbrot', 'benoit mandelbrot', 'benoît mandelbrot'],
    'john nash': ['nash', 'john nash', 'john forbes nash'],
    'sophie germain': ['germain', 'sophie germain', 'marie-sophie germain'],
    'hypatia': ['hypatia', 'hypatia of alexandria'],
    'fibonacci': ['fibonacci', 'leonardo fibonacci', 'leonardo of pisa'],
    'maria agnesi': ['agnesi', 'maria agnesi', 'maria gaetana agnesi'],
    'george boole': ['boole', 'george boole'],
    'augustin-louis cauchy': ['cauchy', 'augustin cauchy', 'louis cauchy', 'augustin-louis cauchy'],
}

with app.app_context():
    # Get all Who Am I images
    query = text("""
        SELECT id, answer, hint, difficulty, image_filename, active
        FROM who_am_i_images
        ORDER BY id
    """)
    
    images = db.session.execute(query).fetchall()
    
    if not images:
        print("❌ No Who Am I images found in database!")
        sys.exit(1)
    
    print(f"Found {len(images)} images")
    print()
    print("=" * 80)
    print("ANALYZING EACH IMAGE")
    print("=" * 80)
    print()
    
    analysis_results = []
    
    for img in images:
        print(f"Image ID {img.id}:")
        print(f"  Filename: {img.image_filename}")
        print(f"  Current Answer: {img.answer}")
        print(f"  Difficulty: {img.difficulty}")
        print(f"  Active: {'Yes' if img.active else 'No'}")
        
        # Generate variants
        auto_variants = generate_answer_variants(img.answer)
        
        # Check if this matches a known mathematician
        answer_lower = img.answer.lower().strip()
        known_variants = KNOWN_VARIANTS.get(answer_lower, [])
        
        # Combine auto-generated and known variants
        all_variants = sorted(list(set(auto_variants + known_variants)))
        
        print(f"  Acceptable Answers ({len(all_variants)}):")
        for i, variant in enumerate(all_variants, 1):
            print(f"    {i}. {variant}")
        
        analysis_results.append({
            'id': img.id,
            'answer': img.answer,
            'hint': img.hint,
            'difficulty': img.difficulty,
            'filename': img.image_filename,
            'variants': all_variants
        })
        
        print()
    
    # Export results
    print("=" * 80)
    print("EXPORT RESULTS")
    print("=" * 80)
    print()
    
    # Save to JSON
    with open('/tmp/who_am_i_variants.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print("✓ Exported to: /tmp/who_am_i_variants.json")
    print()
    
    # Generate SQL update script
    with open('/tmp/update_who_am_i_variants.sql', 'w') as f:
        f.write("-- Update Who Am I images with acceptable answer variants\n")
        f.write("-- Generated automatically from analysis\n\n")
        
        for result in analysis_results:
            variants_json = json.dumps(result['variants'])
            f.write(f"-- Image ID {result['id']}: {result['answer']}\n")
            f.write(f"UPDATE who_am_i_images SET accepted_answers = '{variants_json}' WHERE id = {result['id']};\n\n")
    
    print("✓ Generated SQL: /tmp/update_who_am_i_variants.sql")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total images analyzed: {len(analysis_results)}")
    print(f"Average variants per image: {sum(len(r['variants']) for r in analysis_results) / len(analysis_results):.1f}")
    print()
    print("Most variants:")
    sorted_by_variants = sorted(analysis_results, key=lambda x: len(x['variants']), reverse=True)
    for result in sorted_by_variants[:5]:
        print(f"  • {result['answer']}: {len(result['variants'])} variants")
    print()
    
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Review the variants in: /tmp/who_am_i_variants.json")
    print("2. Add any missing variants manually if needed")
    print("3. Run the migration to add 'accepted_answers' column")
    print("4. Run the SQL update script to populate variants")
    print("5. Update the guess checking logic to use variants")
    print()
