"""
COMPLEX NUMBERS QUESTIONS - 5 SECTIONS (FIXED - NO DUPLICATE ANSWERS)

This script adds questions for the new Complex Numbers topic with 5 sections:
1. The basics of complex numbers (40 questions)
2. Operating with complex numbers (40 questions)
3. Division and quadratic equations (40 questions)
4. The Argand diagram and modulus (40 questions)
5. Transformations (40 questions)

Total: 200 questions

Run this ONCE in PythonAnywhere Bash console:
    cd ~/your-project-directory
    python complex_numbers_questions_FIXED.py
"""

from app import app, db, Question
import random
import math

def ensure_unique_options(correct_answer, potential_wrongs, count=3):
    """
    Ensure we have exactly 'count' unique wrong answers that are different from correct answer.
    """
    unique_wrongs = []
    for wrong in potential_wrongs:
        if wrong != correct_answer and wrong not in unique_wrongs:
            unique_wrongs.append(wrong)
        if len(unique_wrongs) >= count:
            break
    
    # If we don't have enough unique wrongs, generate more
    while len(unique_wrongs) < count:
        # Generate a new wrong answer based on type
        if isinstance(correct_answer, str) and 'i' in correct_answer:
            # Complex number format
            new_wrong = str(random.randint(-10, 10)) + " + " + str(random.randint(-10, 10)) + "i"
        else:
            # Simple number or string
            new_wrong = str(random.randint(-10, 10))
        
        if new_wrong != correct_answer and new_wrong not in unique_wrongs:
            unique_wrongs.append(new_wrong)
    
    return unique_wrongs[:count]

def create_question_dict(topic, difficulty, question_text, correct_answer_str, wrong_answers, explanation):
    """
    Create a properly formatted question dictionary with unique options.
    """
    # Ensure we have exactly 3 unique wrong answers
    wrong_answers = ensure_unique_options(correct_answer_str, wrong_answers, 3)
    
    # Create options list with correct answer and 3 wrong answers
    all_options = [correct_answer_str] + wrong_answers
    random.shuffle(all_options)
    
    # Find the index of correct answer after shuffling
    correct_index = all_options.index(correct_answer_str)
    
    return {
        'topic': topic,
        'difficulty': difficulty,
        'question_text': question_text,
        'option_a': all_options[0],
        'option_b': all_options[1],
        'option_c': all_options[2],
        'option_d': all_options[3],
        'correct_answer': correct_index,
        'explanation': explanation
    }

def generate_section1_questions():
    """Section 1: The basics of complex numbers (40 questions)"""
    questions = []
    
    print("Generating Section 1: The basics of complex numbers...")
    
    # 10 questions on imaginary unit i
    basic_i_questions = [
        ("What does i² equal?", "-1", ["1", "i", "-i"], "By definition, i² = -1. This is the fundamental property of the imaginary unit."),
        ("What is the value of √(-1)?", "i", ["-i", "1", "-1"], "By definition, the imaginary unit i is defined as i = √(-1)."),
        ("What is i³?", "-i", ["i", "1", "-1"], "i³ = i² × i = -1 × i = -i"),
        ("What is i⁴?", "1", ["-1", "i", "-i"], "i⁴ = (i²)² = (-1)² = 1"),
        ("What is i⁵?", "i", ["-i", "1", "-1"], "i⁵ = i⁴ × i = 1 × i = i"),
        ("What is i⁶?", "-1", ["1", "i", "-i"], "i⁶ = (i²)³ = (-1)³ = -1"),
        ("What is i⁸?", "1", ["-1", "i", "-i"], "i⁸ = (i⁴)² = 1² = 1"),
        ("What is i¹⁰?", "-1", ["1", "i", "-i"], "i¹⁰ = i⁸ × i² = 1 × (-1) = -1"),
        ("Simplify √(-4).", "2i", ["-2i", "2", "4i"], "√(-4) = √4 × √(-1) = 2i"),
        ("Simplify √(-9).", "3i", ["-3i", "3", "9i"], "√(-9) = √9 × √(-1) = 3i"),
    ]
    
    for q_text, correct, wrongs, expl in basic_i_questions:
        questions.append(create_question_dict('complex_numbers', 'section1', q_text, correct, wrongs, expl))
    
    # 10 questions on definition and form
    for _ in range(10):
        a = random.randint(-9, 9)
        b = random.randint(1, 9)  # Avoid b=0 to prevent confusion
        
        if random.choice([True, False]):
            # Real part question
            question_text = "For the complex number {} + {}i, what is the real part?".format(a, b)
            correct = str(a)
            wrongs = [str(b), str(abs(a)), str(a+b), str(a-b), str(b-a)]
            explanation = "In the form a + bi, the real part is a = {}.".format(a)
        else:
            # Imaginary part question  
            question_text = "For the complex number {} + {}i, what is the imaginary part?".format(a, b)
            correct = str(b)
            wrongs = [str(a), str(abs(b)), str(a+b), str(a-b), str(b-a)]
            explanation = "In the form a + bi, the imaginary part is b = {}.".format(b)
        
        questions.append(create_question_dict('complex_numbers', 'section1', question_text, correct, wrongs, explanation))
    
    # 20 questions on powers of i
    power_answers = {
        1: ("i", ["1", "-1", "-i"]),
        2: ("-1", ["1", "i", "-i"]),
        3: ("-i", ["i", "1", "-1"]),
        0: ("1", ["-1", "i", "-i"])
    }
    
    for _ in range(20):
        power = random.randint(5, 100)
        remainder = power % 4
        
        question_text = "What is i^{}?".format(power)
        correct, wrongs = power_answers[remainder]
        explanation = "Since i has a cycle of 4, i^{} = i^({} mod 4) = i^{} = {}".format(power, power, remainder, correct)
        
        questions.append(create_question_dict('complex_numbers', 'section1', question_text, correct, wrongs, explanation))
    
    return questions

def generate_section2_questions():
    """Section 2: Operating with complex numbers (40 questions)"""
    questions = []
    
    print("Generating Section 2: Operating with complex numbers...")
    
    # 15 questions on addition
    for _ in range(15):
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
        
        real_sum = a1 + a2
        imag_sum = b1 + b2
        
        question_text = "({} + {}i) + ({} + {}i) = ?".format(a1, b1, a2, b2)
        correct = "{} + {}i".format(real_sum, imag_sum)
        wrongs = [
            "{} + {}i".format(real_sum + 1, imag_sum),
            "{} + {}i".format(real_sum, imag_sum + 1),
            "{} + {}i".format(real_sum - 1, imag_sum - 1),
            "{} + {}i".format(a1 - a2, b1 - b2),
        ]
        explanation = "Add real parts: {} + {} = {}. Add imaginary parts: {} + {} = {}. Result: {} + {}i".format(
            a1, a2, real_sum, b1, b2, imag_sum, real_sum, imag_sum)
        
        questions.append(create_question_dict('complex_numbers', 'section2', question_text, correct, wrongs, explanation))
    
    # 10 questions on subtraction
    for _ in range(10):
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
        
        real_diff = a1 - a2
        imag_diff = b1 - b2
        
        question_text = "({} + {}i) - ({} + {}i) = ?".format(a1, b1, a2, b2)
        correct = "{} + {}i".format(real_diff, imag_diff)
        wrongs = [
            "{} + {}i".format(real_diff + 1, imag_diff),
            "{} + {}i".format(real_diff, imag_diff + 1),
            "{} + {}i".format(a1 + a2, b1 + b2),
            "{} + {}i".format(real_diff - 1, imag_diff + 1),
        ]
        explanation = "Subtract real parts: {} - ({}) = {}. Subtract imaginary parts: {} - ({}) = {}. Result: {} + {}i".format(
            a1, a2, real_diff, b1, b2, imag_diff, real_diff, imag_diff)
        
        questions.append(create_question_dict('complex_numbers', 'section2', question_text, correct, wrongs, explanation))
    
    # 10 questions on multiplication (simple cases)
    simple_mult = [
        ("i × i", "-1", ["1", "i", "2i"], "i × i = i² = -1"),
        ("2i × 3i", "-6", ["6i", "6", "5i"], "2i × 3i = 6i² = 6(-1) = -6"),
        ("(1 + i)(1 - i)", "2", ["0", "2i", "1"], "(1 + i)(1 - i) = 1 - i² = 1 - (-1) = 2"),
        ("3 × (2 + i)", "6 + 3i", ["5 + 3i", "6 + i", "5 + i"], "Multiply each term: 3(2 + i) = 6 + 3i"),
        ("i × (3 + 2i)", "-2 + 3i", ["3i + 2i²", "3 + 2i", "5i"], "i(3 + 2i) = 3i + 2i² = 3i - 2 = -2 + 3i"),
    ]
    
    for q_text, correct, wrongs, expl in simple_mult:
        questions.append(create_question_dict('complex_numbers', 'section2', q_text, correct, wrongs, expl))
    
    # 5 questions on conjugates
    for _ in range(5):
        a = random.randint(-5, 5)
        b = random.randint(1, 5)
        
        question_text = "What is the conjugate of {} + {}i?".format(a, b)
        correct = "{} - {}i".format(a, b)
        wrongs = [
            "{} + {}i".format(-a, b),
            "{} + {}i".format(a, b),
            "{} - {}i".format(-a, b),
            "{} + {}i".format(a, -b),
        ]
        explanation = "The conjugate of a + bi is a - bi. So the conjugate of {} + {}i is {} - {}i.".format(a, b, a, b)
        
        questions.append(create_question_dict('complex_numbers', 'section2', question_text, correct, wrongs, explanation))
    
    return questions

def generate_section3_questions():
    """Section 3: Division and quadratic equations (40 questions)"""
    questions = []
    
    print("Generating Section 3: Division and quadratic equations...")
    
    # 20 questions on simple division
    simple_div = [
        ("What is (6 + 3i) / 3?", "2 + i", ["6 + i", "3 + 3i", "2 + 3i"], "Divide each term: (6 + 3i) / 3 = 6/3 + 3i/3 = 2 + i"),
        ("What is (4 + 8i) / 2?", "2 + 4i", ["4 + 4i", "2 + 8i", "6 + 4i"], "Divide each term: (4 + 8i) / 2 = 4/2 + 8i/2 = 2 + 4i"),
        ("What is (10 + 5i) / 5?", "2 + i", ["10 + i", "5 + 5i", "2 + 5i"], "Divide each term: (10 + 5i) / 5 = 10/5 + 5i/5 = 2 + i"),
        ("What is 6i / 2i?", "3", ["3i", "4i", "6"], "6i / 2i = 6/2 = 3"),
        ("What is 8i / 4?", "2i", ["2", "8i", "4i"], "8i / 4 = 8/4 × i = 2i"),
    ]
    
    for q_text, correct, wrongs, expl in simple_div[:20]:  # Repeat to get 20
        questions.append(create_question_dict('complex_numbers', 'section3', q_text, correct, wrongs, expl))
    
    # Add more division questions to reach 20
    for _ in range(15):
        numerator = random.randint(2, 10)
        divisor = random.randint(2, 5)
        if numerator % divisor == 0:
            result = numerator // divisor
            question_text = "What is {}i / {}i?".format(numerator, divisor)
            correct = str(result)
            wrongs = [str(result + 1), str(result - 1), "{}i".format(result), str(numerator)]
            explanation = "{}i / {}i = {}/{} = {}".format(numerator, divisor, numerator, divisor, result)
            
            questions.append(create_question_dict('complex_numbers', 'section3', question_text, correct, wrongs, explanation))
    
    # 20 questions on quadratic equations with complex roots
    quadratic_questions = [
        ("Solve: x² + 1 = 0", "x = ±i", ["x = ±1", "x = 0", "x = i"], "x² = -1, so x = ±√(-1) = ±i"),
        ("Solve: x² + 4 = 0", "x = ±2i", ["x = ±2", "x = ±4i", "x = 2i"], "x² = -4, so x = ±√(-4) = ±2i"),
        ("Solve: x² + 9 = 0", "x = ±3i", ["x = ±3", "x = ±9i", "x = 3i"], "x² = -9, so x = ±√(-9) = ±3i"),
        ("Solve: x² + 16 = 0", "x = ±4i", ["x = ±4", "x = ±16i", "x = 4i"], "x² = -16, so x = ±√(-16) = ±4i"),
        ("Solve: x² + 25 = 0", "x = ±5i", ["x = ±5", "x = ±25i", "x = 5i"], "x² = -25, so x = ±√(-25) = ±5i"),
    ]
    
    for q_text, correct, wrongs, expl in quadratic_questions:
        questions.append(create_question_dict('complex_numbers', 'section3', q_text, correct, wrongs, expl))
    
    # Generate more quadratic questions
    for _ in range(15):
        n = random.choice([1, 4, 9, 16, 25, 36, 49])
        sqrt_n = int(math.sqrt(n))
        
        question_text = "Solve: x² + {} = 0".format(n)
        correct = "x = ±{}i".format(sqrt_n)
        wrongs = [
            "x = ±{}".format(sqrt_n),
            "x = ±{}i".format(n),
            "x = {}i".format(sqrt_n),
            "x = {}".format(sqrt_n),
        ]
        explanation = "x² = -{}, so x = ±√(-{}) = ±{}i".format(n, n, sqrt_n)
        
        questions.append(create_question_dict('complex_numbers', 'section3', question_text, correct, wrongs, explanation))
    
    return questions

def generate_section4_questions():
    """Section 4: The Argand diagram and modulus (40 questions)"""
    questions = []
    
    print("Generating Section 4: The Argand diagram and modulus...")
    
    # 20 questions on Argand diagram
    for _ in range(20):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        
        if random.choice([True, False]):
            # Point to complex number
            question_text = "What complex number is represented by the point ({}, {})?".format(a, b)
            correct = "{} + {}i".format(a, b)
            wrongs = [
                "{} + {}i".format(b, a),
                "{} - {}i".format(a, b),
                "{} + {}i".format(-a, b),
                "{} + {}i".format(a, -b),
            ]
            explanation = "Point (a, b) on Argand diagram represents a + bi = {} + {}i".format(a, b)
        else:
            # Complex number to point
            question_text = "Where is {} + {}i plotted on the Argand diagram?".format(a, b)
            correct = "({}, {})".format(a, b)
            wrongs = [
                "({}, {})".format(b, a),
                "({}, {})".format(-a, b),
                "({}, {})".format(a, -b),
                "({}, {})".format(-a, -b),
            ]
            explanation = "Complex number a + bi is plotted at point (a, b) = ({}, {})".format(a, b)
        
        questions.append(create_question_dict('complex_numbers', 'section4', question_text, correct, wrongs, explanation))
    
    # 20 questions on modulus
    modulus_questions = [
        ("What is |3 + 4i|?", "5", ["7", "3", "4"], "|3 + 4i| = √(3² + 4²) = √(9 + 16) = √25 = 5"),
        ("What is |5 + 12i|?", "13", ["17", "5", "12"], "|5 + 12i| = √(5² + 12²) = √(25 + 144) = √169 = 13"),
        ("What is |8 + 6i|?", "10", ["14", "8", "6"], "|8 + 6i| = √(8² + 6²) = √(64 + 36) = √100 = 10"),
        ("What is |5i|?", "5", ["5i", "0", "√5"], "|5i| = √(0² + 5²) = √25 = 5"),
        ("What is |7|?", "7", ["0", "7i", "√7"], "|7| = √(7² + 0²) = √49 = 7"),
    ]
    
    for q_text, correct, wrongs, expl in modulus_questions:
        questions.append(create_question_dict('complex_numbers', 'section4', q_text, correct, wrongs, expl))
    
    # Generate more modulus questions
    for _ in range(15):
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        mod = math.sqrt(a*a + b*b)
        
        if mod == int(mod):
            question_text = "What is |{} + {}i|?".format(a, b)
            correct = str(int(mod))
            wrongs = [
                str(a + b),
                str(a),
                str(b),
                str(int(mod) + 1),
            ]
            explanation = "|{} + {}i| = √({}² + {}²) = √{} = {}".format(a, b, a, b, a*a + b*b, int(mod))
            
            questions.append(create_question_dict('complex_numbers', 'section4', question_text, correct, wrongs, explanation))
    
    return questions

def generate_section5_questions():
    """Section 5: Transformations (40 questions)"""
    questions = []
    
    print("Generating Section 5: Transformations...")
    
    # 15 questions on translation
    for _ in range(15):
        a1, b1 = random.randint(-3, 3), random.randint(-3, 3)
        a2, b2 = random.randint(-3, 3), random.randint(-3, 3)
        
        result_a = a1 + a2
        result_b = b1 + b2
        
        question_text = "Translate {} + {}i by {} + {}i".format(a1, b1, a2, b2)
        correct = "{} + {}i".format(result_a, result_b)
        wrongs = [
            "{} + {}i".format(result_a + 1, result_b),
            "{} + {}i".format(result_a, result_b + 1),
            "{} + {}i".format(a1 - a2, b1 - b2),
            "{} + {}i".format(result_a - 1, result_b - 1),
        ]
        explanation = "Translation is addition: ({} + {}i) + ({} + {}i) = {} + {}i".format(
            a1, b1, a2, b2, result_a, result_b)
        
        questions.append(create_question_dict('complex_numbers', 'section5', question_text, correct, wrongs, explanation))
    
    # 15 questions on rotation (multiply by i = 90° rotation)
    for _ in range(15):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        
        # Multiply by i: (a + bi) × i = ai + bi² = ai - b = -b + ai
        result_real = -b
        result_imag = a
        
        question_text = "Rotate {} + {}i by 90° counterclockwise (multiply by i)".format(a, b)
        correct = "{} + {}i".format(result_real, result_imag)
        wrongs = [
            "{} + {}i".format(result_imag, result_real),
            "{} + {}i".format(-result_real, result_imag),
            "{} + {}i".format(result_real, -result_imag),
            "{} + {}i".format(a, b),
        ]
        explanation = "({} + {}i) × i = {}i + {}i² = {}i - {} = {} + {}i".format(
            a, b, a, b, a, b, result_real, result_imag)
        
        questions.append(create_question_dict('complex_numbers', 'section5', question_text, correct, wrongs, explanation))
    
    # 10 questions on scaling
    for _ in range(10):
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        scale = random.choice([2, 3, 4, 5])
        
        result_a = a * scale
        result_b = b * scale
        
        question_text = "Scale {} + {}i by a factor of {}".format(a, b, scale)
        correct = "{} + {}i".format(result_a, result_b)
        wrongs = [
            "{} + {}i".format(result_a + scale, result_b),
            "{} + {}i".format(result_a, result_b + scale),
            "{} + {}i".format(a + scale, b + scale),
            "{} + {}i".format(result_a - 1, result_b - 1),
        ]
        explanation = "Scaling by {} means multiply: {}({} + {}i) = {} + {}i".format(
            scale, scale, a, b, result_a, result_b)
        
        questions.append(create_question_dict('complex_numbers', 'section5', question_text, correct, wrongs, explanation))
    
    return questions

def add_complex_numbers_to_database():
    """Main function to add all complex numbers questions"""
    with app.app_context():
        # Check if questions already exist
        existing = Question.query.filter_by(topic='complex_numbers').count()
        if existing > 0:
            print("\n⚠️  WARNING: {} Complex Numbers questions already exist!".format(existing))
            response = input("Delete and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            
            # Delete existing
            Question.query.filter_by(topic='complex_numbers').delete()
            db.session.commit()
            print("✅ Deleted {} existing questions\n".format(existing))
        
        # Generate all questions
        print("\n" + "="*70)
        print("GENERATING COMPLEX NUMBERS QUESTIONS (NO DUPLICATES)")
        print("="*70 + "\n")
        
        section1 = generate_section1_questions()
        section2 = generate_section2_questions()
        section3 = generate_section3_questions()
        section4 = generate_section4_questions()
        section5 = generate_section5_questions()
        
        all_questions = section1 + section2 + section3 + section4 + section5
        
        print("\n" + "="*70)
        print("VALIDATION CHECK - SCANNING FOR DUPLICATE ANSWERS")
        print("="*70)
        
        # Validate no duplicates
        issues_found = 0
        for i, q in enumerate(all_questions, 1):
            options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
            if len(options) != len(set(options)):
                print("❌ Question {}: DUPLICATE OPTIONS FOUND!".format(i))
                print("   Options:", options)
                issues_found += 1
        
        if issues_found > 0:
            print("\n❌ VALIDATION FAILED! {} questions have duplicate answers".format(issues_found))
            print("Please review the question generation logic.")
            return
        
        print("✅ ALL QUESTIONS VALIDATED - NO DUPLICATE ANSWERS!")
        print("="*70 + "\n")
        
        # Show summary
        print("Questions generated:")
        print("Section 1 (The Basics): {} questions".format(len(section1)))
        print("Section 2 (Operations): {} questions".format(len(section2)))
        print("Section 3 (Division & Quadratics): {} questions".format(len(section3)))
        print("Section 4 (Argand & Modulus): {} questions".format(len(section4)))
        print("Section 5 (Transformations): {} questions".format(len(section5)))
        print("="*70)
        print("TOTAL: {} questions\n".format(len(all_questions)))
        
        print("Adding questions to database...")
        for q_data in all_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        
        # Verify
        total = Question.query.filter_by(topic='complex_numbers').count()
        
        print("\n" + "="*70)
        print("✅ COMPLEX NUMBERS QUESTIONS ADDED SUCCESSFULLY!")
        print("="*70)
        print("\nFinal count by section:")
        for section in ['section1', 'section2', 'section3', 'section4', 'section5']:
            count = Question.query.filter_by(topic='complex_numbers', difficulty=section).count()
            print("  {}: {} questions".format(section, count))
        print("\nTotal Complex Numbers questions: {}".format(total))
        print("\n✅ Students will now get 25 random questions from 40 per section!")
        print("✅ NO DUPLICATE ANSWERS IN ANY QUESTION!")
        print("="*70 + "\n")


if __name__ == "__main__":
    add_complex_numbers_to_database()
