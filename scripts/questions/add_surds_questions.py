"""
Script to populate the database with surds questions
"""
import sys
sys.path.insert(0, '/home/claude/mathapp-main')

from app import app, db, Question
from surds_questions import generate_all_questions

def add_surds_questions():
    """Add surds questions to the database"""
    with app.app_context():
        # First, check if surds questions already exist
        existing = Question.query.filter_by(topic='surds').count()
        print(f"Existing surds questions in database: {existing}")
        
        if existing > 0:
            response = input(f"There are already {existing} surds questions. Delete them and regenerate? (yes/no): ")
            if response.lower() == 'yes':
                deleted = Question.query.filter_by(topic='surds').delete()
                db.session.commit()
                print(f"Deleted {deleted} existing surds questions")
            else:
                print("Keeping existing questions. Exiting.")
                return
        
        # Generate new questions
        print("\nGenerating surds questions...")
        questions = generate_all_questions()
        
        # Add to database
        print(f"\nAdding {len(questions)} questions to database...")
        added_count = 0
        
        for q_data in questions:
            question = Question(
                topic=q_data['topic'],
                difficulty=q_data['difficulty'],
                question_text=q_data['question'],
                option_a=q_data['options'][0],
                option_b=q_data['options'][1],
                option_c=q_data['options'][2],
                option_d=q_data['options'][3],
                correct_answer=q_data['correct'],
                explanation=q_data['explanation']
            )
            db.session.add(question)
            added_count += 1
            
            if added_count % 20 == 0:
                print(f"  Added {added_count} questions...")
        
        # Commit all questions
        db.session.commit()
        print(f"\n✓ Successfully added {added_count} surds questions to the database!")
        
        # Verify counts by difficulty
        print("\nQuestions per difficulty level:")
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = Question.query.filter_by(topic='surds', difficulty=difficulty).count()
            print(f"  {difficulty}: {count} questions")

if __name__ == "__main__":
    add_surds_questions()
