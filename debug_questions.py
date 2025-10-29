#!/usr/bin/env python3
"""
Debug script to check questions in database and verify the app is working
"""

from app import app, db, Question
import json

def check_database():
    """Check if questions exist in database"""
    with app.app_context():
        print("=" * 60)
        print("CHECKING DATABASE")
        print("=" * 60)
        
        # Check if questions table exists
        try:
            total_questions = Question.query.count()
            print(f"\n✓ Questions table exists")
            print(f"✓ Total questions in database: {total_questions}")
        except Exception as e:
            print(f"\n✗ Error accessing questions table: {e}")
            print("\nRun this to create tables:")
            print("  python init_db.py")
            return False
        
        if total_questions == 0:
            print("\n✗ No questions found in database!")
            print("\nRun this to load questions:")
            print("  python init_db.py")
            return False
        
        # Check questions by topic and difficulty
        print("\n" + "=" * 60)
        print("QUESTIONS BY TOPIC AND DIFFICULTY")
        print("=" * 60)
        
        topics = ['arithmetic', 'fractions', 'bodmas', 'functions', 'sets']
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        all_good = True
        for topic in topics:
            for difficulty in difficulties:
                count = Question.query.filter_by(topic=topic, difficulty=difficulty).count()
                status = "✓" if count > 0 else "✗"
                print(f"{status} {topic:12} - {difficulty:12}: {count:3} questions")
                if count == 0:
                    all_good = False
        
        if not all_good:
            print("\n✗ Some topic/difficulty combinations have no questions!")
            print("   Run: python init_db.py")
            return False
        
        # Show sample question
        print("\n" + "=" * 60)
        print("SAMPLE QUESTION")
        print("=" * 60)
        
        sample = Question.query.first()
        if sample:
            print(f"\nID: {sample.id}")
            print(f"Topic: {sample.topic}")
            print(f"Difficulty: {sample.difficulty}")
            print(f"Question: {sample.question_text}")
            print(f"Options: {sample.option_a}, {sample.option_b}, {sample.option_c}, {sample.option_d}")
            print(f"Correct: {sample.correct_answer}")
            print(f"Explanation: {sample.explanation}")
        
        print("\n" + "=" * 60)
        print("DATABASE CHECK: ✓ ALL GOOD!")
        print("=" * 60)
        return True

def test_api():
    """Test the questions API endpoint"""
    with app.test_client() as client:
        print("\n" + "=" * 60)
        print("TESTING API ENDPOINT")
        print("=" * 60)
        
        # Try to get questions
        response = client.get('/api/questions/arithmetic/beginner')
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Endpoint requires authentication (this is correct)")
            print("  Users must be logged in to access questions")
        elif response.status_code == 200:
            data = response.get_json()
            print(f"✓ Endpoint returned {len(data)} questions")
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"  Response: {response.get_data(as_text=True)}")

def check_questions_file():
    """Check if questions_data.json exists and is valid"""
    print("\n" + "=" * 60)
    print("CHECKING QUESTIONS FILE")
    print("=" * 60)
    
    try:
        with open('questions_data.json', 'r') as f:
            data = json.load(f)
            print(f"\n✓ questions_data.json found")
            print(f"✓ Contains {len(data)} questions")
            
            # Check structure
            if len(data) > 0:
                sample = data[0]
                required_keys = ['topic', 'difficulty', 'question', 'options', 'correct', 'explanation']
                missing = [key for key in required_keys if key not in sample]
                
                if missing:
                    print(f"✗ Sample question missing keys: {missing}")
                else:
                    print(f"✓ Question structure looks correct")
                    
    except FileNotFoundError:
        print("\n✗ questions_data.json not found!")
        print("   Make sure questions_data.json is in the same directory as app.py")
    except json.JSONDecodeError as e:
        print(f"\n✗ Error parsing questions_data.json: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("MATH MASTER - DATABASE DEBUG TOOL")
    print("=" * 60)
    
    # Check questions file
    check_questions_file()
    
    # Check database
    db_ok = check_database()
    
    # Test API
    test_api()
    
    print("\n" + "=" * 60)
    
    if db_ok:
        print("✓ EVERYTHING LOOKS GOOD!")
        print("\nIf students still can't load questions:")
        print("1. Make sure they're logged in")
        print("2. Check browser console (F12) for errors")
        print("3. Check Flask terminal for error messages")
    else:
        print("✗ ISSUES FOUND - RUN THIS:")
        print("\n  python init_db.py")
    
    print("=" * 60 + "\n")
