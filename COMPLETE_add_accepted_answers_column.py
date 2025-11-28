#!/usr/bin/env python3
"""
Add accepted_answers column to who_am_i_images table
Then auto-populate with generated variants for all existing images
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

def auto_generate_variants(answer):
    """Auto-generate acceptable answer variants"""
    variants = set()
    answer_lower = answer.lower().strip()
    variants.add(answer_lower)
    
    # Remove titles
    titles = ['dr.', 'dr', 'sir', 'professor', 'prof.', 'prof', 'dame', 'lord', 'lady']
    for title in titles:
        if answer_lower.startswith(title + ' '):
            variants.add(answer_lower.replace(title + ' ', '', 1).strip())
    
    # Name parts
    parts = answer_lower.split()
    if len(parts) >= 2:
        variants.add(parts[0])  # First name
        variants.add(parts[-1])  # Last name
        if len(parts) > 2:
            variants.add(f"{parts[0]} {parts[-1]}")  # First + Last
            # Remove middle initials
            filtered = [p for p in parts if len(p) > 2 or not p.endswith('.')]
            if len(filtered) != len(parts):
                variants.add(' '.join(filtered))
    
    # Remove punctuation
    import string
    no_punct = answer_lower.translate(str.maketrans('', '', string.punctuation))
    if no_punct != answer_lower:
        variants.add(no_punct)
    
    return sorted(list(variants))

print("=" * 80)
print("WHO AM I - ADD ACCEPTED_ANSWERS COLUMN")
print("=" * 80)
print()

with app.app_context():
    try:
        # Check if column already exists
        result = db.session.execute(text("PRAGMA table_info(who_am_i_images)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'accepted_answers' in columns:
            print("✓ Column 'accepted_answers' already exists")
        else:
            print("Adding 'accepted_answers' column...")
            db.session.execute(text("""
                ALTER TABLE who_am_i_images 
                ADD COLUMN accepted_answers TEXT
            """))
            db.session.commit()
            print("✓ Column 'accepted_answers' added successfully")
        
        print()
        print("Populating variants for existing images...")
        
        # Get all images
        images = db.session.execute(text("""
            SELECT id, answer, accepted_answers FROM who_am_i_images
        """)).fetchall()
        
        updated = 0
        for img in images:
            if not img.accepted_answers:
                variants = auto_generate_variants(img.answer)
                variants_json = json.dumps(variants)
                
                db.session.execute(text("""
                    UPDATE who_am_i_images 
                    SET accepted_answers = :variants 
                    WHERE id = :id
                """), {'variants': variants_json, 'id': img.id})
                
                print(f"  ✓ Image {img.id} ({img.answer}): {len(variants)} variants")
                updated += 1
        
        db.session.commit()
        
        print()
        print(f"✓ Updated {updated} images with auto-generated variants")
        print()
        print("=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Deploy updated admin_who_am_i.html template")
        print("2. Deploy updated app.py routes")
        print("3. Test the admin interface")
        print()
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
