"""
Test script to manually insert a guest flag
This will help us see what the actual error is
"""
import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

from app import app, db, QuestionFlag, Question

with app.app_context():
    print("Testing guest flag creation...")
    
    # Get a test question
    question = Question.query.first()
    if not question:
        print("ERROR: No questions in database")
        exit(1)
    
    print(f"Using question ID: {question.id}")
    
    try:
        # Try to create a guest flag
        flag = QuestionFlag(
            question_id=question.id,
            user_id=None,  # Guest user
            guest_identifier="test_guest_123",
            guest_email="test@example.com",
            flag_type="incorrect",
            description="Test flag from guest user"
        )
        
        db.session.add(flag)
        db.session.commit()
        
        print("✓ SUCCESS! Guest flag created:")
        print(f"  Flag ID: {flag.id}")
        print(f"  Question ID: {flag.question_id}")
        print(f"  Guest Identifier: {flag.guest_identifier}")
        print(f"  Description: {flag.description}")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Check if columns exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('question_flags')]
        print(f"\nCurrent columns in question_flags: {columns}")
        
        if 'guest_identifier' not in columns:
            print("\n⚠️  guest_identifier column is missing!")
            print("Run: python3 allow_guest_flagging.py")
        
        if 'guest_email' not in columns:
            print("\n⚠️  guest_email column is missing!")
            print("Run: python3 allow_guest_flagging.py")
