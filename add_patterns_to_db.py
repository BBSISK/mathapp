#!/usr/bin/env python3
"""
Add Patterns Questions to Database
Run this on PythonAnywhere: python3 add_patterns_to_db.py
"""

from app import app, db, Question

# Define questions directly in Python (no JSON parsing needed)
patterns_questions = []

# BEGINNER QUESTIONS (40 total)
beginner = [
    ("What comes next in this pattern?\n🌟 🌙 🌟 🌙 🌟 🌙 __", "🌟", "🌙", "☀️", "⭐", 0, "The pattern alternates between star and moon. After 🌙 comes 🌟."),
    ("Complete the pattern:\n🔴 🔵 🔴 🔵 🔴 __", "🔴", "🔵", "🟢", "🟡", 1, "The pattern alternates red and blue circles. After 🔴 comes 🔵."),
    ("What's the next shape?\n⭐ ⭐ ⭐⭐ ⭐⭐ ⭐⭐⭐ __", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", 3, "Each group adds one more star: 1, 2, 3, so next is 4 stars."),
    ("Continue this sequence:\n😀 😃 😀 😃 😀 __", "😀", "😃", "😁", "😄", 1, "The pattern alternates between two different smiling faces."),
    ("What comes next?\n🍎 🍎 🍌 🍎 🍎 🍌 🍎 🍎 __", "🍎", "🍌", "🍊", "🍇", 1, "Pattern: 2 apples, 1 banana, repeating."),
    ("Find the next number:\n2, 4, 6, 8, __", "9", "10", "11", "12", 1, "Add 2 each time: 2+2=4, 4+2=6, 6+2=8, 8+2=10"),
    ("What number comes next?\n5, 10, 15, 20, __", "21", "22", "25", "30", 2, "Add 5 each time. The pattern is counting by 5s."),
    ("Complete the sequence:\n1, 3, 5, 7, __", "8", "9", "10", "11", 1, "Add 2 each time. These are odd numbers: 7+2=9"),
    ("What's next in the pattern?\n10, 20, 30, 40, __", "45", "50", "55", "60", 1, "Add 10 each time. Count by tens: 40+10=50"),
    ("Find the missing number:\n3, 6, 9, 12, __", "13", "14", "15", "16", 2, "Add 3 each time. Multiples of 3: 12+3=15"),
    ("What shape comes next?\n▲ ● ▲ ● ▲ __", "▲", "●", "■", "◆", 1, "The pattern alternates: triangle, circle, triangle, circle..."),
    ("Continue the pattern:\n■ ■ ● ■ ■ ● ■ ■ __", "■", "●", "▲", "◆", 1, "Pattern: 2 squares, 1 circle, repeating."),
    ("What comes next?\n🔺 🔻 🔺 🔻 🔺 __", "🔺", "🔻", "⬛", "⬜", 1, "Alternating up and down triangles."),
    ("The sequence 4, 7, 10, 13 increases by the same amount each time. What is this amount?", "1", "2", "3", "4", 2, "7-4=3, 10-7=3, 13-10=3. The common difference is 3."),
    ("What is the common difference in: 5, 8, 11, 14?", "2", "3", "4", "5", 1, "8-5=3, 11-8=3. The pattern increases by 3 each time."),
    ("Find the common difference: 12, 17, 22, 27", "3", "4", "5", "6", 2, "17-12=5, 22-17=5. The sequence increases by 5."),
    ("In the sequence 20, 25, 30, 35, what is the common difference?", "3", "4", "5", "10", 2, "25-20=5, 30-25=5. Each term increases by 5."),
    ("What's the common difference in: 6, 10, 14, 18?", "2", "3", "4", "5", 2, "10-6=4, 14-10=4. The pattern adds 4 each time."),
    ("What comes next: 7, 14, 21, 28, __?", "32", "35", "36", "42", 1, "Add 7 each time. These are multiples of 7: 28+7=35"),
    ("Find the pattern: 100, 90, 80, 70, __", "60", "65", "50", "55", 0, "Subtract 10 each time: 70-10=60"),
]

# Generate more beginner questions
for i in range(20, 40):
    start = ((i-20) % 5) + 2
    diff = ((i-20) % 4 + 1) * 2
    seq = [start + j*diff for j in range(4)]
    next_val = seq[-1] + diff
    
    question = f"What comes next in this sequence?\n{seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, __"
    beginner.append((
        question,
        str(next_val),
        str(next_val + 1),
        str(next_val - 1),
        str(next_val + diff),
        0,
        f"Add {diff} each time: {seq[-1]}+{diff}={next_val}"
    ))

# INTERMEDIATE QUESTIONS (40 total)
intermediate = [
    ("Find the 5th term in the sequence: 3, 7, 11, 15, ...", "17", "18", "19", "20", 2, "Pattern: add 4 each time. 15+4=19"),
    ("What is the nth term formula for: 2, 4, 6, 8, ...?", "n", "2n", "3n", "n+2", 1, "This is 2×n. For n=1: 2×1=2, n=2: 2×2=4"),
    ("Find the nth term of: 5, 10, 15, 20, ...", "n+5", "5n", "n+10", "10n", 1, "This is 5×n. For n=1: 5×1=5, n=2: 5×2=10"),
    ("What is the 10th term if the nth term is 3n+1?", "29", "30", "31", "32", 2, "Substitute n=10: 3(10)+1 = 30+1 = 31"),
    ("The nth term is 2n-1. What is the 7th term?", "12", "13", "14", "15", 1, "n=7: 2(7)-1 = 14-1 = 13"),
    ("Find the nth term for: 4, 7, 10, 13, ...", "n+3", "3n", "3n+1", "3n-1", 2, "Difference is 3. First term is 4. Pattern: 3n+1"),
    ("What is the 6th term in: 1, 4, 7, 10, ...?", "15", "16", "17", "18", 1, "nth term is 3n-2. For n=6: 3(6)-2 = 18-2 = 16"),
    ("The sequence 8, 11, 14, 17 has nth term 3n+5. True or false?", "True", "False", "Sometimes", "Cannot determine", 1, "Check: n=1: 3(1)+5=8 ✓, n=2: 3(2)+5=11 ✓"),
    ("Find the 20th term if the pattern is: 6, 12, 18, 24, ...", "114", "118", "120", "126", 2, "nth term is 6n. For n=20: 6×20=120"),
    ("What is the nth term of: 9, 13, 17, 21, ...?", "4n+4", "4n+5", "4n+9", "n+9", 1, "Difference is 4. When n=1: 4(1)+5=9 ✓"),
    ("Find the 8th term: 2, 5, 8, 11, ...", "22", "23", "24", "25", 1, "nth term is 3n-1. For n=8: 3(8)-1=23"),
    ("The nth term is 5n-2. What is the 12th term?", "56", "57", "58", "60", 2, "n=12: 5(12)-2 = 60-2 = 58"),
    ("What is the nth term of: 7, 12, 17, 22, ...?", "5n+1", "5n+2", "5n+7", "n+5", 1, "Difference is 5. When n=1: 5(1)+2=7 ✓"),
    ("Find the 15th term if nth term is 4n+3", "61", "62", "63", "64", 2, "n=15: 4(15)+3 = 60+3 = 63"),
    ("The pattern 10, 17, 24, 31 has what nth term?", "7n+2", "7n+3", "7n+10", "n+7", 1, "Difference is 7. When n=1: 7(1)+3=10 ✓"),
]

# Generate more intermediate questions
for i in range(15, 40):
    a = ((i-15) % 5) + 2
    b = ((i-15) % 7) + 1
    n_test = 5 + ((i-15) % 6)
    result = a * n_test + b
    
    seq = [a*j + b for j in range(1, 5)]
    question = f"Find the {n_test}th term if the sequence is: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ...\n(Pattern: {a}n+{b})"
    intermediate.append((
        question,
        str(result),
        str(result+1),
        str(result-1),
        str(result+a),
        0,
        f"nth term is {a}n+{b}. For n={n_test}: {a}×{n_test}+{b} = {result}"
    ))

# ADVANCED QUESTIONS (40 total)
advanced = [
    ("What type of sequence is 2, 4, 8, 16, 32?", "Linear", "Quadratic", "Exponential", "Fibonacci", 2, "Each term doubles. This is exponential: 2ⁿ"),
    ("Find the next term in: 1, 4, 9, 16, 25, ...", "30", "32", "36", "40", 2, "These are perfect squares: 1², 2², 3², 4², 5², 6²=36"),
    ("What is the pattern in: 1, 4, 9, 16, 25?", "Add 3 each time", "Multiply by 2", "Square numbers (n²)", "Cube numbers", 2, "These are 1²=1, 2²=4, 3²=9, 4²=16, 5²=25"),
    ("The sequence 3, 9, 27, 81 follows which pattern?", "Add 6", "Multiply by 3", "Add then multiply", "Square each term", 1, "Each term is ×3: 3, 3×3=9, 9×3=27, 27×3=81"),
    ("Find the 6th term in: 2, 8, 18, 32, 50, ... (2n²)", "70", "72", "78", "82", 1, "Pattern: 2n². For n=6: 2×6²=2×36=72"),
    ("What comes next: 1, 8, 27, 64, ...?", "100", "125", "128", "144", 1, "These are cubes: 1³, 2³, 3³, 4³, 5³=125"),
    ("Identify the pattern: 2, 6, 12, 20, 30", "Triangular", "n(n+1)", "n²+n", "2n²", 1, "Pattern: n(n+1). Like 2×3=6, 3×4=12, 4×5=20"),
    ("The 7th square number is:", "42", "45", "49", "56", 2, "7² = 49"),
    ("What is 2⁵?", "10", "16", "25", "32", 3, "2×2×2×2×2 = 32"),
    ("Find the next: 3, 12, 27, 48, ... (3n²)", "72", "75", "81", "96", 1, "Pattern: 3n². For n=5: 3×5²=3×25=75"),
]

# Generate more advanced questions
for i in range(10, 40):
    if i % 2 == 0:
        # Quadratic: n²
        n = (i % 8) + 1
        result = n * n
        seq = [j*j for j in range(1, 5)]
        question = f"If the pattern is square numbers, what is the {n}th term?\nSequence: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ..."
        advanced.append((
            question,
            str(result),
            str(result+1),
            str(result-1),
            str(n*3),
            0,
            f"The {n}th square number is {n}² = {result}"
        ))
    else:
        # Exponential: 2^n
        n = (i % 6) + 1
        result = 2 ** n
        seq = [2**j for j in range(1, 5)]
        question = f"If each term doubles (powers of 2), what is the {n}th term?\nSequence: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ..."
        advanced.append((
            question,
            str(result),
            str(result+2),
            str(result*2),
            str(n*2),
            0,
            f"Power of 2: 2^{n} = {result}"
        ))

# Combine all questions
for q_tuple in beginner:
    patterns_questions.append({
        'difficulty': 'beginner',
        'question': q_tuple[0],
        'option_a': q_tuple[1],
        'option_b': q_tuple[2],
        'option_c': q_tuple[3],
        'option_d': q_tuple[4],
        'correct': q_tuple[5],
        'explanation': q_tuple[6]
    })

for q_tuple in intermediate:
    patterns_questions.append({
        'difficulty': 'intermediate',
        'question': q_tuple[0],
        'option_a': q_tuple[1],
        'option_b': q_tuple[2],
        'option_c': q_tuple[3],
        'option_d': q_tuple[4],
        'correct': q_tuple[5],
        'explanation': q_tuple[6]
    })

for q_tuple in advanced:
    patterns_questions.append({
        'difficulty': 'advanced',
        'question': q_tuple[0],
        'option_a': q_tuple[1],
        'option_b': q_tuple[2],
        'option_c': q_tuple[3],
        'option_d': q_tuple[4],
        'correct': q_tuple[5],
        'explanation': q_tuple[6]
    })

# Add to database
with app.app_context():
    print("="*60)
    print("ADDING PATTERNS QUESTIONS TO DATABASE")
    print("="*60)
    
    # Check if patterns already exist
    existing = Question.query.filter_by(topic='patterns').count()
    
    if existing > 0:
        print(f"\n⚠️  WARNING: {existing} Patterns questions already exist")
        print("Deleting existing patterns questions...")
        Question.query.filter_by(topic='patterns').delete()
        db.session.commit()
        print("✅ Deleted existing patterns questions")
    
    # Add questions
    added = 0
    errors = 0
    
    print(f"\nAdding {len(patterns_questions)} questions...")
    
    for i, q_data in enumerate(patterns_questions, 1):
        try:
            question = Question(
                topic='patterns',
                difficulty=q_data['difficulty'],
                question_text=q_data['question'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct'],
                explanation=q_data['explanation']
            )
            db.session.add(question)
            added += 1
            
            if i % 20 == 0:
                db.session.commit()
                print(f"  Added {i}/{len(patterns_questions)}...")
        except Exception as e:
            errors += 1
            print(f"  Error on question {i}: {e}")
    
    # Final commit
    db.session.commit()
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Successfully added: {added} questions")
    if errors > 0:
        print(f"❌ Errors: {errors}")
    
    # Verify
    final_count = Question.query.filter_by(topic='patterns').count()
    beginner_count = Question.query.filter_by(topic='patterns', difficulty='beginner').count()
    intermediate_count = Question.query.filter_by(topic='patterns', difficulty='intermediate').count()
    advanced_count = Question.query.filter_by(topic='patterns', difficulty='advanced').count()
    
    print(f"\nFinal count in database:")
    print(f"  Beginner:     {beginner_count}")
    print(f"  Intermediate: {intermediate_count}")
    print(f"  Advanced:     {advanced_count}")
    print(f"  TOTAL:        {final_count}")
    
    print("\n✅ Patterns topic is now available!")
    print("   Students can access it in: Algebra and Functions strand")
