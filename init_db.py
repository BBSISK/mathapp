from app import app, db, Question
import json

def init_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Load questions from JSON file
        with open('questions_data.json', 'r') as f:
            all_questions = json.load(f)
        
        # Add all questions to database
        for q_data in all_questions:
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
        
        db.session.commit()
        print(f"Database initialized with {len(all_questions)} questions!")
        
        # Print statistics
        topics = ['arithmetic', 'fractions', 'bodmas', 'functions', 'sets']
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        print("\nQuestion count by topic and difficulty:")
        for topic in topics:
            print(f"\n{topic.upper()}:")
            for difficulty in difficulties:
                count = Question.query.filter_by(topic=topic, difficulty=difficulty).count()
                print(f"  {difficulty}: {count} questions")

if __name__ == '__main__':
    init_database()
