#!/usr/bin/env python3
"""
Migration script to add strand column to questions table
Run this ONCE to update your database
"""

from app import app, db, Question
from sqlalchemy import text

def migrate():
    print("Starting migration to add strand column...")
    
    with app.app_context():
        # Step 1: Add the strand column if it doesn't exist
        try:
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text("PRAGMA table_info(questions)"))
                columns = [row[1] for row in result]
                
                if 'strand' not in columns:
                    print("Adding strand column...")
                    conn.execute(text("ALTER TABLE questions ADD COLUMN strand VARCHAR(100)"))
                    conn.commit()
                    print("✓ Strand column added")
                else:
                    print("✓ Strand column already exists")
        except Exception as e:
            print(f"Error adding column: {e}")
            return False
        
        # Step 2: Update strand values based on topic
        topic_to_strand = {
            # Number strand
            'arithmetic': 'Number',
            'multiplication_division': 'Number',
            'number_systems': 'Number',
            'bodmas': 'Number',
            'fractions': 'Number',
            'decimals': 'Number',
            'sets': 'Number',
            
            # Algebra and Functions strand
            'functions': 'Algebra and Functions',
            'patterns': 'Algebra and Functions',
            
            # Statistics and Probability strand
            'probability': 'Statistics and Probability',
            'descriptive_statistics': 'Statistics and Probability',
            
            # Senior Cycle - Algebra strand
            'surds': 'Senior Cycle - Algebra',
            'complex_numbers_intro': 'Senior Cycle - Algebra',
            'complex_numbers_expanded': 'Senior Cycle - Algebra',
        }
        
        print("\nUpdating strand values for each topic...")
        updated_count = 0
        
        for topic, strand in topic_to_strand.items():
            try:
                count = Question.query.filter_by(topic=topic).update({'strand': strand})
                db.session.commit()
                if count > 0:
                    print(f"  ✓ Updated {count} questions for topic '{topic}' → strand '{strand}'")
                    updated_count += count
                else:
                    print(f"  ⚠ No questions found for topic '{topic}'")
            except Exception as e:
                print(f"  ✗ Error updating topic '{topic}': {e}")
                db.session.rollback()
        
        print(f"\n✓ Migration complete! Updated {updated_count} questions")
        
        # Step 3: Verify the results
        print("\nVerification - Questions by strand:")
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT strand, COUNT(*) as count 
                    FROM questions 
                    WHERE strand IS NOT NULL
                    GROUP BY strand 
                    ORDER BY strand
                """))
                for row in result:
                    print(f"  {row[0]}: {row[1]} questions")
        except Exception as e:
            print(f"Error in verification: {e}")
        
        return True

if __name__ == '__main__':
    success = migrate()
    if success:
        print("\n✓ Database migration successful!")
    else:
        print("\n✗ Migration failed - please check errors above")
