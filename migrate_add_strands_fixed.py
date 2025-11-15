#!/usr/bin/env python3
"""
Migration script to add strand column to questions table - FIXED VERSION
Run this ONCE to update your database
"""

from app import app, db
from sqlalchemy import text

def migrate():
    print("Starting migration to add strand column...")
    
    with app.app_context():
        # Step 1: Verify the strand column exists
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(questions)"))
                columns = [row[1] for row in result]
                
                if 'strand' in columns:
                    print("✓ Strand column exists")
                else:
                    print("✗ Strand column missing - something went wrong")
                    return False
        except Exception as e:
            print(f"Error checking column: {e}")
            return False
        
        # Step 2: Update strand values using raw SQL
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
        
        try:
            with db.engine.connect() as conn:
                for topic, strand in topic_to_strand.items():
                    result = conn.execute(
                        text("UPDATE questions SET strand = :strand WHERE topic = :topic"),
                        {"strand": strand, "topic": topic}
                    )
                    count = result.rowcount
                    if count > 0:
                        print(f"  ✓ Updated {count} questions for topic '{topic}' → strand '{strand}'")
                        updated_count += count
                    else:
                        print(f"  ⚠ No questions found for topic '{topic}'")
                
                conn.commit()
        except Exception as e:
            print(f"  ✗ Error during update: {e}")
            return False
        
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
                
                # Show topics in Algebra and Functions strand
                print("\nTopics in 'Algebra and Functions' strand:")
                result2 = conn.execute(text("""
                    SELECT topic, COUNT(*) as count 
                    FROM questions 
                    WHERE strand = 'Algebra and Functions'
                    GROUP BY topic
                    ORDER BY topic
                """))
                for row in result2:
                    print(f"  - {row[0]}: {row[1]} questions")
        except Exception as e:
            print(f"Error in verification: {e}")
        
        return True

if __name__ == '__main__':
    success = migrate()
    if success:
        print("\n✓ Database migration successful!")
    else:
        print("\n✗ Migration failed - please check errors above")
