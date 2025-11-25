#!/usr/bin/env python3
"""
Check Who Am I images for hints in the database
"""

import sqlite3
import sys

def check_hints():
    # Connect to database
    conn = sqlite3.connect('instance/mathquiz.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("WHO AM I - HINT CHECK")
    print("=" * 80)
    
    # Get all images with their hints
    cursor.execute("""
        SELECT 
            i.id,
            i.topic,
            i.difficulty,
            i.answer,
            i.hint,
            i.active,
            GROUP_CONCAT(t.topic, ', ') as assigned_topics
        FROM who_am_i_images i
        LEFT JOIN who_am_i_image_topics t ON i.id = t.image_id
        GROUP BY i.id
        ORDER BY i.id
    """)
    
    images = cursor.fetchall()
    
    print(f"\nTotal images in database: {len(images)}")
    print("-" * 80)
    
    images_with_hints = 0
    images_without_hints = 0
    
    for img in images:
        img_id, topic, difficulty, answer, hint, active, assigned_topics = img
        
        has_hint = hint is not None and hint.strip() != ''
        if has_hint:
            images_with_hints += 1
        else:
            images_without_hints += 1
        
        status = "✅ HAS HINT" if has_hint else "❌ NO HINT"
        active_status = "🟢 ACTIVE" if active == 1 else "⚪ INACTIVE"
        
        print(f"\nImage ID: {img_id} {active_status}")
        print(f"  Answer: {answer}")
        print(f"  Difficulty: {difficulty}")
        print(f"  Assigned Topics: {assigned_topics or 'None'}")
        print(f"  {status}")
        if has_hint:
            print(f"  Hint: '{hint}'")
        else:
            print(f"  Hint: (empty or NULL)")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"  Images with hints:    {images_with_hints}")
    print(f"  Images without hints: {images_without_hints}")
    print(f"  Total images:         {len(images)}")
    print("=" * 80)
    
    # Check for introductory_algebra specifically
    print("\n" + "=" * 80)
    print("CHECKING INTRODUCTORY_ALGEBRA TOPIC:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            i.id,
            i.answer,
            i.hint,
            i.active
        FROM who_am_i_images i
        JOIN who_am_i_image_topics t ON i.id = t.image_id
        WHERE t.topic = 'introductory_algebra' AND i.active = 1
    """)
    
    intro_algebra_images = cursor.fetchall()
    
    if intro_algebra_images:
        print(f"\nFound {len(intro_algebra_images)} active image(s) for introductory_algebra:")
        for img in intro_algebra_images:
            img_id, answer, hint, active = img
            has_hint = hint is not None and hint.strip() != ''
            status = "✅ HAS HINT" if has_hint else "❌ NO HINT"
            print(f"\n  Image ID {img_id}: {answer} - {status}")
            if has_hint:
                print(f"    Hint: '{hint}'")
    else:
        print("\n⚠️  No active images assigned to 'introductory_algebra' topic!")
    
    conn.close()

if __name__ == "__main__":
    try:
        check_hints()
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
