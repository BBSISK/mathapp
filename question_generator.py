"""
QUESTION GENERATOR MODULE
==========================
Uses Claude API to generate quiz questions for topics.
Integrates with the Topic Management system.

Usage in app.py:
    from question_generator import register_generator_routes
    register_generator_routes(app, db)
"""

import os
import json
from flask import jsonify, request
from sqlalchemy import text
from functools import wraps

# Try to import anthropic - it may not be installed
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

def register_generator_routes(app, db):
    """Register question generator routes with the Flask app"""
    
    # Helper function to get API key fresh each time (not cached at registration)
    def get_api_key():
        return os.environ.get('ANTHROPIC_API_KEY', '')
    
    # Helper to check if user is admin
    def admin_required_api(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            from app import User
            user = User.query.get(session['user_id'])
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/api/admin/check-api-key', methods=['GET'])
    @admin_required_api
    def check_api_key():
        """Check if Anthropic API key is configured"""
        # First check if the library is installed
        if not ANTHROPIC_AVAILABLE:
            return jsonify({
                'configured': False, 
                'valid': False, 
                'error': 'anthropic library not installed. Run: pip install anthropic --user'
            })
        
        # Get API key fresh (not from cached value)
        api_key = get_api_key()
        
        if api_key:
            # Test the key with a minimal request
            try:
                client = anthropic.Anthropic(api_key=api_key)
                # Just check if client initializes - don't make a request
                return jsonify({'configured': True, 'valid': True})
            except Exception as e:
                return jsonify({'configured': True, 'valid': False, 'error': str(e)})
        
        # Return debug info about what env vars we can see (first 10 chars only for security)
        env_keys = [k for k in os.environ.keys() if 'ANTHROPIC' in k.upper() or 'API' in k.upper()]
        return jsonify({
            'configured': False, 
            'valid': False, 
            'error': 'ANTHROPIC_API_KEY environment variable not set',
            'debug_env_keys': env_keys
        })
    
    @app.route('/api/admin/generate-questions', methods=['POST'])
    @admin_required_api
    def generate_questions():
        """Generate questions using Claude API"""
        
        if not ANTHROPIC_AVAILABLE:
            return jsonify({'error': 'Anthropic library not installed. Run: pip install anthropic --user'}), 400
        
        api_key = get_api_key()
        if not api_key:
            return jsonify({'error': 'Anthropic API key not configured. Add ANTHROPIC_API_KEY to your environment variables.'}), 400
        
        data = request.json
        topic_id = data.get('topic_id')
        topic_name = data.get('topic_name', topic_id)
        
        levels = {
            'beginner': {
                'description': data.get('beginner_description', ''),
                'count': int(data.get('beginner_count', 40))
            },
            'intermediate': {
                'description': data.get('intermediate_description', ''),
                'count': int(data.get('intermediate_count', 40))
            },
            'advanced': {
                'description': data.get('advanced_description', ''),
                'count': int(data.get('advanced_count', 40))
            }
        }
        
        # Validate inputs
        if not topic_id:
            return jsonify({'error': 'Topic ID is required'}), 400
        
        for level_name, level_data in levels.items():
            if not level_data['description']:
                return jsonify({'error': f'{level_name.title()} description is required'}), 400
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            all_questions = []
            
            for difficulty, level_data in levels.items():
                print(f"Generating {level_data['count']} {difficulty} questions for {topic_id}...")
                
                prompt = f"""Generate exactly {level_data['count']} multiple choice mathematics questions for Irish Junior Cycle students (14 year olds).

TOPIC: {topic_name}
DIFFICULTY: {difficulty.upper()}
LEVEL DESCRIPTION: {level_data['description']}

REQUIREMENTS:
1. Each question must have exactly 4 options (A, B, C, D)
2. Only ONE option should be correct
3. Include a clear, educational explanation for the correct answer
4. Questions should be appropriate for 14-year-old Irish students
5. Use Irish/European conventions (e.g., € for currency)
6. Vary the question styles (some calculations, some word problems, some conceptual)
7. Make wrong options plausible but clearly wrong when you understand the concept

OUTPUT FORMAT:
Return a JSON array with exactly {level_data['count']} question objects. Each object must have:
- "question_text": The question (string)
- "options": Array of exactly 4 strings [A, B, C, D]
- "correct": Index of correct answer (0=A, 1=B, 2=C, 3=D)
- "explanation": Why the correct answer is right (string)

Example format:
[
  {{
    "question_text": "What is 15% of 80?",
    "options": ["10", "12", "15", "8"],
    "correct": 1,
    "explanation": "To find 15% of 80: 80 × 0.15 = 12, or (80 ÷ 100) × 15 = 12"
  }}
]

IMPORTANT: 
- Return ONLY the JSON array, no other text
- Ensure all {level_data['count']} questions are unique
- Double-check that the correct answer index matches the right option"""

                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Parse the response
                response_text = response.content[0].text.strip()
                
                # Clean up response if needed (remove markdown code blocks)
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join(lines[1:-1])
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                try:
                    questions = json.loads(response_text.strip())
                except json.JSONDecodeError as e:
                    print(f"JSON parse error for {difficulty}: {e}")
                    print(f"Response was: {response_text[:500]}...")
                    return jsonify({'error': f'Failed to parse {difficulty} questions. Claude response was not valid JSON.'}), 500
                
                # Add difficulty to each question
                for q in questions:
                    q['difficulty'] = difficulty
                
                all_questions.extend(questions)
                print(f"  ✓ Generated {len(questions)} {difficulty} questions")
            
            # Save to database
            from app import Question
            
            saved = 0
            skipped = 0
            
            for q in all_questions:
                # Check for duplicate
                existing = db.session.execute(text("""
                    SELECT id FROM questions 
                    WHERE topic = :topic AND difficulty = :difficulty AND question_text = :question_text
                """), {
                    'topic': topic_id,
                    'difficulty': q['difficulty'],
                    'question_text': q['question_text']
                }).fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # Insert new question
                new_question = Question(
                    topic=topic_id,
                    difficulty=q['difficulty'],
                    question_text=q['question_text'],
                    option_a=q['options'][0],
                    option_b=q['options'][1],
                    option_c=q['options'][2],
                    option_d=q['options'][3],
                    correct_answer=q['correct'],
                    explanation=q['explanation']
                )
                db.session.add(new_question)
                saved += 1
            
            db.session.commit()
            
            # Get final counts
            counts = {}
            for difficulty in ['beginner', 'intermediate', 'advanced']:
                count = db.session.execute(text(
                    "SELECT COUNT(*) FROM questions WHERE topic = :topic AND difficulty = :difficulty"
                ), {'topic': topic_id, 'difficulty': difficulty}).fetchone()[0]
                counts[difficulty] = count
            
            total = sum(counts.values())
            
            return jsonify({
                'success': True,
                'message': f'Generated and saved {saved} questions. {skipped} duplicates skipped.',
                'saved': saved,
                'skipped': skipped,
                'counts': counts,
                'total': total
            })
            
        except anthropic.APIError as e:
            return jsonify({'error': f'Anthropic API error: {str(e)}'}), 500
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error generating questions: {str(e)}'}), 500
    
    @app.route('/api/admin/question-counts/<topic_id>', methods=['GET'])
    @admin_required_api
    def get_question_counts(topic_id):
        """Get current question counts for a topic"""
        try:
            counts = {}
            for difficulty in ['beginner', 'intermediate', 'advanced']:
                count = db.session.execute(text(
                    "SELECT COUNT(*) FROM questions WHERE topic = :topic AND difficulty = :difficulty"
                ), {'topic': topic_id, 'difficulty': difficulty}).fetchone()[0]
                counts[difficulty] = count
            
            return jsonify({
                'topic_id': topic_id,
                'counts': counts,
                'total': sum(counts.values())
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("✓ Question generator routes registered")
    return True
