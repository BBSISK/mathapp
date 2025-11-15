#!/usr/bin/env python3
"""
Fix difficulty level mismatch in database
Changes: foundation → beginner, ordinary → intermediate, higher → advanced
"""

from app import app, db
from sqlalchemy import text

print("=" * 70)
print("FIXING DIFFICULTY LEVELS FOR NEW ALGEBRA TOPICS")
print("=" * 70)

with app.app_context():
    with db.engine.connect() as conn:
        # Update difficulty levels
        updates = [
            ('foundation', 'beginner'),
            ('ordinary', 'intermediate'),
            ('higher', 'advanced')
        ]
        
        total_updated = 0
        
        for old_diff, new_diff in updates:
            print(f"\nUpdating '{old_diff}' → '{new_diff}'...")
            
            result = conn.execute(text("""
                UPDATE questions
                SET difficulty = :new_diff
                WHERE topic IN ('solving_equations', 'simplifying_expressions', 
                               'expanding_factorising', 'patterns')
                AND difficulty = :old_diff
            """), {'old_diff': old_diff, 'new_diff': new_diff})
            
            count = result.rowcount
            total_updated += count
            print(f"  ✓ Updated {count} questions")
        
        conn.commit()
        
        print(f"\n{'=' * 70}")
        print(f"✓ TOTAL: Updated {total_updated} questions")
        print('=' * 70)
        
        # Verify
        print("\nVerifying changes...")
        result = conn.execute(text("""
            SELECT topic, difficulty, COUNT(*) as count
            FROM questions 
            WHERE topic IN ('solving_equations', 'simplifying_expressions', 
                           'expanding_factorising', 'patterns')
            GROUP BY topic, difficulty
            ORDER BY topic, 
                CASE difficulty 
                    WHEN 'beginner' THEN 1
                    WHEN 'intermediate' THEN 2
                    WHEN 'advanced' THEN 3
                END
        """))
        
        print("\nFinal question counts:")
        for row in result:
            print(f"  {row[0]} - {row[1]}: {row[2]} questions")
        
        print("\n" + "=" * 70)
        print("✓ DIFFICULTY LEVELS FIXED!")
        print("  Now reload your web app and try the topics again")
        print("=" * 70)
