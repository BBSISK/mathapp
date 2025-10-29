#!/usr/bin/env python3
"""
Complex Numbers Question Generator - FULLY VALIDATED
NO DUPLICATE ANSWERS - Every question validated
For Math Master - Palmerstown Community School
"""

from app import app, db, Question
import random

def ensure_unique_options(correct_answer, wrong_answers):
    """
    Ensure all answer options are unique.
    If duplicates found, regenerate wrong answers.
    """
    all_options = [correct_answer] + wrong_answers
    
    # Check for duplicates
    if len(all_options) != len(set(all_options)):
        # Remove duplicates from wrong answers
        unique_wrong = []
        for ans in wrong_answers:
            if ans != correct_answer and ans not in unique_wrong:
                unique_wrong.append(ans)
        
        # If we still don't have 3 unique wrong answers, generate new ones
        while len(unique_wrong) < 3:
            # Generate a new wrong answer based on the type of correct answer
            if 'i' in str(correct_answer):
                # Complex number answer
                new_wrong = generate_wrong_complex(correct_answer)
            else:
                # Real number answer
                new_wrong = generate_wrong_real(correct_answer)
            
            if new_wrong != correct_answer and new_wrong not in unique_wrong:
                unique_wrong.append(new_wrong)
        
        return unique_wrong[:3]
    
    return wrong_answers

def generate_wrong_real(correct):
    """Generate a wrong answer for real number questions"""
    try:
        num = float(correct)
        offset = random.choice([-2, -1, 1, 2, 0.5, -0.5])
        return str(int(num + offset)) if num + offset == int(num + offset) else str(num + offset)
    except:
        return str(random.randint(-10, 10))

def generate_wrong_complex(correct):
    """Generate a wrong answer for complex number questions"""
    # Extract real and imaginary parts
    if '+' in correct:
        parts = correct.split('+')
        try:
            real = int(parts[0].strip())
            imag = int(parts[1].replace('i', '').strip())
            new_real = real + random.choice([-2, -1, 1, 2])
            new_imag = imag + random.choice([-2, -1, 1, 2])
            return f"{new_real} + {new_imag}i"
        except:
            pass
    elif '-' in correct and correct.count('-') == 1:
        parts = correct.split('-')
        try:
            real = int(parts[0].strip())
            imag = int(parts[1].replace('i', '').strip())
            new_real = real + random.choice([-2, -1, 1, 2])
            new_imag = imag + random.choice([-2, -1, 1, 2])
            return f"{new_real} - {new_imag}i"
        except:
            pass
    
    # Default: return a random complex number
    return f"{random.randint(-5, 5)} + {random.randint(-5, 5)}i"

def validate_all_questions(questions):
    """
    Validate all questions to ensure no duplicate answers.
    Returns True if all valid, False otherwise with details.
    """
    print("\n" + "="*60)
    print("VALIDATING ALL COMPLEX NUMBERS QUESTIONS")
    print("="*60)
    
    issues_found = []
    
    for i, q in enumerate(questions, 1):
        all_options = [q['correct_answer']] + q['wrong_answers']
        unique_options = set(all_options)
        
        if len(unique_options) != 4:
            issues_found.append({
                'question_num': i,
                'section': q['section'],
                'question': q['question_text'][:50] + "...",
                'all_options': all_options,
                'unique_count': len(unique_options)
            })
    
    if issues_found:
        print(f"\n❌ FOUND {len(issues_found)} QUESTIONS WITH DUPLICATE ANSWERS:\n")
        for issue in issues_found:
            print(f"Question #{issue['question_num']} ({issue['section']})")
            print(f"   Text: {issue['question']}")
            print(f"   Options: {issue['all_options']}")
            print(f"   Unique: {issue['unique_count']}/4")
            print()
        return False
    else:
        print(f"\n✅ ALL {len(questions)} QUESTIONS VALIDATED - NO DUPLICATE ANSWERS!")
        print("="*60 + "\n")
        return True


# SECTION 1: THE BASICS (40 questions)
section1_questions = []

# i and powers of i (15 questions)
powers_of_i = [
    ("What does i represent?", "√(-1)", ["√1", "-1", "1"]),
    ("What is i²?", "-1", ["1", "i", "-i"]),
    ("What is i³?", "-i", ["i", "1", "-1"]),
    ("What is i⁴?", "1", ["-1", "i", "-i"]),
    ("What is i⁵?", "i", ["-i", "1", "-1"]),
    ("What is i⁶?", "-1", ["1", "i", "-i"]),
    ("What is i⁷?", "-i", ["i", "1", "-1"]),
    ("What is i⁸?", "1", ["-1", "i", "-i"]),
    ("What is i⁹?", "i", ["-i", "1", "-1"]),
    ("What is i¹⁰?", "-1", ["1", "i", "-i"]),
    ("What is i¹¹?", "-i", ["i", "1", "-1"]),
    ("What is i¹²?", "1", ["-1", "i", "-i"]),
    ("Simplify: i¹⁶", "1", ["-1", "i", "-i"]),
    ("Simplify: i²⁰", "1", ["-1", "i", "-i"]),
    ("Simplify: i²⁵", "i", ["-i", "1", "-1"]),
]

for q, a, w in powers_of_i:
    w_validated = ensure_unique_options(a, w)
    section1_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section1'
    })

# Real and imaginary parts (15 questions)
parts_questions = [
    ("What is the real part of 3 + 4i?", "3", ["4", "4i", "3i"]),
    ("What is the imaginary part of 3 + 4i?", "4", ["3", "4i", "3i"]),
    ("What is the real part of 5 - 2i?", "5", ["-2", "2i", "5i"]),
    ("What is the imaginary part of 5 - 2i?", "-2", ["5", "2", "-2i"]),
    ("What is the real part of -6 + 7i?", "-6", ["7", "6", "-7"]),
    ("What is the imaginary part of -6 + 7i?", "7", ["-6", "6", "-7"]),
    ("What is the real part of 8i?", "0", ["8", "8i", "1"]),
    ("What is the imaginary part of 8i?", "8", ["0", "8i", "i"]),
    ("What is the real part of 12?", "12", ["0", "12i", "1"]),
    ("What is the imaginary part of 12?", "0", ["12", "1", "12i"]),
    ("What is the real part of -3 - 5i?", "-3", ["-5", "3", "5"]),
    ("What is the imaginary part of -3 - 5i?", "-5", ["-3", "3", "5"]),
    ("What is the real part of 10 + i?", "10", ["1", "10i", "0"]),
    ("What is the imaginary part of 10 + i?", "1", ["10", "0", "i"]),
    ("In z = a + bi, what does 'a' represent?", "Real part", ["Imaginary part", "Modulus", "Conjugate"]),
]

for q, a, w in parts_questions:
    w_validated = ensure_unique_options(a, w)
    section1_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section1'
    })

# Definition questions (10 questions)
definition_questions = [
    ("In z = a + bi, what does 'b' represent?", "Imaginary part", ["Real part", "Modulus", "Argument"]),
    ("What is a complex number?", "a + bi", ["a + b", "ai + bi", "a - b"]),
    ("Which of these is a pure imaginary number?", "5i", ["5", "5 + 0i", "0"]),
    ("Which of these is a real number?", "7", ["7i", "7 + i", "i"]),
    ("What is the imaginary unit squared?", "-1", ["1", "i", "0"]),
    ("What symbol represents the imaginary unit?", "i", ["j", "x", "z"]),
    ("Is every real number also a complex number?", "Yes", ["No", "Sometimes", "Only positive ones"]),
    ("What is 0 + 5i called?", "Pure imaginary", ["Real", "Mixed", "Zero"]),
    ("What is 9 + 0i called?", "Real", ["Imaginary", "Pure imaginary", "Complex"]),
    ("Complex numbers extend which number system?", "Real numbers", ["Natural numbers", "Integers", "Rationals"]),
]

for q, a, w in definition_questions:
    w_validated = ensure_unique_options(a, w)
    section1_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section1'
    })


# SECTION 2: OPERATIONS (40 questions)
section2_questions = []

# Addition (10 questions)
addition_questions = [
    ("(3 + 4i) + (2 + 5i) = ?", "5 + 9i", ["5 + 7i", "6 + 9i", "5 + 8i"]),
    ("(5 + 2i) + (1 + 3i) = ?", "6 + 5i", ["6 + 4i", "5 + 5i", "7 + 5i"]),
    ("(7 - 3i) + (2 + 5i) = ?", "9 + 2i", ["9 - 2i", "5 + 2i", "9 + 8i"]),
    ("(-4 + 6i) + (3 - 2i) = ?", "-1 + 4i", ["-1 + 8i", "1 + 4i", "-7 + 4i"]),
    ("(8 + i) + (2 + 3i) = ?", "10 + 4i", ["10 + 3i", "6 + 4i", "10 + 2i"]),
    ("(6 - 5i) + (-2 + 3i) = ?", "4 - 2i", ["4 + 2i", "8 - 2i", "4 - 8i"]),
    ("(10 + 2i) + (5 + 8i) = ?", "15 + 10i", ["15 + 6i", "5 + 10i", "15 + 16i"]),
    ("(-3 - 4i) + (7 + 9i) = ?", "4 + 5i", ["4 - 5i", "10 + 5i", "4 + 13i"]),
    ("(9 + 7i) + (-4 - 2i) = ?", "5 + 5i", ["5 - 5i", "13 + 5i", "5 + 9i"]),
    ("(1 + i) + (1 + i) = ?", "2 + 2i", ["2 + i", "1 + 2i", "2i"]),
]

for q, a, w in addition_questions:
    w_validated = ensure_unique_options(a, w)
    section2_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section2'
    })

# Subtraction (10 questions)
subtraction_questions = [
    ("(5 + 6i) - (2 + 3i) = ?", "3 + 3i", ["3 - 3i", "7 + 3i", "3 + 9i"]),
    ("(8 + 4i) - (3 + 2i) = ?", "5 + 2i", ["5 - 2i", "11 + 2i", "5 + 6i"]),
    ("(10 - 3i) - (4 - 7i) = ?", "6 + 4i", ["6 - 4i", "14 + 4i", "6 - 10i"]),
    ("(7 + 5i) - (7 + 5i) = ?", "0", ["14 + 10i", "0 + 0i", "2i"]),
    ("(12 + 8i) - (6 + 3i) = ?", "6 + 5i", ["6 - 5i", "18 + 5i", "6 + 11i"]),
    ("(-5 + 3i) - (2 - 4i) = ?", "-7 + 7i", ["-7 - 7i", "-3 + 7i", "-7 - i"]),
    ("(9 - 2i) - (-3 + 5i) = ?", "12 - 7i", ["12 + 7i", "6 - 7i", "12 + 3i"]),
    ("(4 + 10i) - (4 + 2i) = ?", "0 + 8i", ["0 - 8i", "8 + 8i", "8i"]),
    ("(15 + i) - (10 - i) = ?", "5 + 2i", ["5 - 2i", "25 + 2i", "5"]),
    ("(6 + 4i) - (6 - 4i) = ?", "0 + 8i", ["12", "0", "8i"]),
]

for q, a, w in subtraction_questions:
    w_validated = ensure_unique_options(a, w)
    section2_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section2'
    })

# Multiplication (10 questions)
multiplication_questions = [
    ("(2 + 3i)(1 + 2i) = ?", "-4 + 7i", ["2 + 7i", "-4 + 5i", "2 + 6i"]),
    ("(3 + 2i)(2 + i) = ?", "4 + 7i", ["6 + 7i", "4 + 3i", "6 + 2i"]),
    ("(4 + i)(3 + 2i) = ?", "10 + 11i", ["12 + 11i", "10 + 5i", "12 + 2i"]),
    ("(5 + 2i)(1 + i) = ?", "3 + 7i", ["5 + 7i", "3 + 3i", "5 + 2i"]),
    ("(1 + 3i)(2 + i) = ?", "-1 + 7i", ["2 + 7i", "-1 + 5i", "2 + 3i"]),
    ("(2 + 4i)(3 + i) = ?", "2 + 14i", ["6 + 14i", "2 + 7i", "6 + 4i"]),
    ("(6 + i)(2 + 3i) = ?", "9 + 20i", ["12 + 20i", "9 + 5i", "12 + 3i"]),
    ("i × i = ?", "-1", ["1", "2i", "0"]),
    ("3i × 4i = ?", "-12", ["12i", "12", "7i"]),
    ("(1 + i)(1 - i) = ?", "2", ["0", "2i", "1"]),
]

for q, a, w in multiplication_questions:
    w_validated = ensure_unique_options(a, w)
    section2_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section2'
    })

# Conjugate (10 questions)
conjugate_questions = [
    ("What is the conjugate of 3 + 4i?", "3 - 4i", ["-3 + 4i", "3 + 4i", "-3 - 4i"]),
    ("What is the conjugate of 5 - 2i?", "5 + 2i", ["-5 - 2i", "5 - 2i", "-5 + 2i"]),
    ("What is the conjugate of 7i?", "-7i", ["7i", "7", "-7"]),
    ("What is the conjugate of 8?", "8", ["-8", "8i", "0"]),
    ("What is the conjugate of -6 + 3i?", "-6 - 3i", ["6 + 3i", "-6 + 3i", "6 - 3i"]),
    ("What is the conjugate of 10 - 5i?", "10 + 5i", ["-10 - 5i", "10 - 5i", "-10 + 5i"]),
    ("What is the conjugate of 1 + i?", "1 - i", ["-1 + i", "1 + i", "-1 - i"]),
    ("What is the conjugate of -4i?", "4i", ["-4i", "4", "-4"]),
    ("What is the conjugate of -9?", "-9", ["9", "-9i", "9i"]),
    ("If z = 2 + 5i, what is z̄?", "2 - 5i", ["-2 + 5i", "2 + 5i", "-2 - 5i"]),
]

for q, a, w in conjugate_questions:
    w_validated = ensure_unique_options(a, w)
    section2_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section2'
    })


# SECTION 3: DIVISION & QUADRATICS (40 questions)
section3_questions = []

# Division (15 questions)
division_questions = [
    ("(3 + 4i) / i = ?", "4 - 3i", ["4 + 3i", "-4 + 3i", "3 - 4i"]),
    ("(2 + 6i) / 2 = ?", "1 + 3i", ["2 + 3i", "1 + 6i", "4 + 3i"]),
    ("(10 + 5i) / 5 = ?", "2 + i", ["10 + i", "2 + 5i", "5 + 2i"]),
    ("6i / 2i = ?", "3", ["3i", "12i", "4"]),
    ("8i / 4 = ?", "2i", ["2", "8i", "4i"]),
    ("(1 + i) / (1 - i) = ?", "i", ["1", "-i", "0"]),
    ("(4 + 2i) / 2 = ?", "2 + i", ["4 + i", "2 + 2i", "6 + i"]),
    ("(9 + 3i) / 3 = ?", "3 + i", ["9 + i", "3 + 3i", "6 + i"]),
    ("12i / 3i = ?", "4", ["4i", "36i", "9"]),
    ("(6 + 12i) / 6 = ?", "1 + 2i", ["6 + 2i", "1 + 12i", "3 + 2i"]),
    ("(5 + 10i) / 5 = ?", "1 + 2i", ["5 + 2i", "1 + 10i", "2 + 5i"]),
    ("15i / 5 = ?", "3i", ["3", "15i", "5i"]),
    ("(8 + 4i) / 4 = ?", "2 + i", ["8 + i", "2 + 4i", "4 + 2i"]),
    ("20i / 10i = ?", "2", ["2i", "200i", "10"]),
    ("(14 + 7i) / 7 = ?", "2 + i", ["14 + i", "2 + 7i", "7 + 2i"]),
]

for q, a, w in division_questions:
    w_validated = ensure_unique_options(a, w)
    section3_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section3'
    })

# Quadratic equations with complex roots (15 questions)
quadratic_questions = [
    ("Solve: x² + 1 = 0", "x = ±i", ["x = ±1", "x = 0", "x = i"]),
    ("Solve: x² + 4 = 0", "x = ±2i", ["x = ±2", "x = ±4i", "x = 2i"]),
    ("Solve: x² + 9 = 0", "x = ±3i", ["x = ±3", "x = ±9i", "x = 3i"]),
    ("Solve: x² + 16 = 0", "x = ±4i", ["x = ±4", "x = ±16i", "x = 4i"]),
    ("Solve: x² + 25 = 0", "x = ±5i", ["x = ±5", "x = ±25i", "x = 5i"]),
    ("Solve: 2x² + 8 = 0", "x = ±2i", ["x = ±2", "x = ±4i", "x = 2i"]),
    ("Solve: 3x² + 12 = 0", "x = ±2i", ["x = ±2", "x = ±4i", "x = 2i"]),
    ("What type of roots does x² + 5 = 0 have?", "Complex", ["Real", "Rational", "Irrational"]),
    ("For x² + k = 0 (k > 0), roots are:", "Imaginary", ["Real", "Rational", "Zero"]),
    ("Solve: x² = -1", "x = ±i", ["x = ±1", "x = 0", "x = i"]),
    ("Solve: x² = -4", "x = ±2i", ["x = ±2", "x = ±4i", "x = 2i"]),
    ("Solve: x² = -9", "x = ±3i", ["x = ±3", "x = ±9i", "x = 3i"]),
    ("Solve: x² = -16", "x = ±4i", ["x = ±4", "x = ±16i", "x = 4i"]),
    ("Solve: x² = -25", "x = ±5i", ["x = ±5", "x = ±25i", "x = 5i"]),
    ("Solve: x² = -36", "x = ±6i", ["x = ±6", "x = ±36i", "x = 6i"]),
]

for q, a, w in quadratic_questions:
    w_validated = ensure_unique_options(a, w)
    section3_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section3'
    })

# Discriminant questions (10 questions)
discriminant_questions = [
    ("For ax² + bx + c = 0, when b² - 4ac < 0:", "Complex roots", ["Real roots", "One root", "No roots"]),
    ("If discriminant is negative:", "Complex roots", ["Two real roots", "One real root", "No solution"]),
    ("x² + 2x + 5 = 0 has what type of roots?", "Complex", ["Real", "Rational", "Equal"]),
    ("x² + x + 1 = 0 has what type of roots?", "Complex", ["Real", "Rational", "Irrational"]),
    ("For x² + 4x + 8 = 0, roots are:", "Complex", ["Real", "Rational", "Equal"]),
    ("When is √(b² - 4ac) imaginary?", "b² - 4ac < 0", ["b² - 4ac > 0", "b² - 4ac = 0", "Always"]),
    ("x² + 6x + 13 = 0 has:", "Complex roots", ["Real roots", "One root", "No solution"]),
    ("For x² + 3x + 10 = 0:", "Complex roots", ["Real roots", "Rational roots", "Equal roots"]),
    ("If discriminant = -4, roots are:", "Complex", ["Real", "Rational", "Equal"]),
    ("x² + 5x + 7 = 0 has:", "Complex roots", ["Real roots", "One root", "Rational roots"]),
]

for q, a, w in discriminant_questions:
    w_validated = ensure_unique_options(a, w)
    section3_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section3'
    })


# SECTION 4: ARGAND & MODULUS (40 questions)
section4_questions = []

# Argand diagram plotting (15 questions)
argand_questions = [
    ("On Argand diagram, 3 + 4i is at:", "(3, 4)", ["(4, 3)", "(3, -4)", "(-3, 4)"]),
    ("Point (2, 5) represents:", "2 + 5i", ["5 + 2i", "2 - 5i", "5 - 2i"]),
    ("On Argand diagram, real axis is:", "Horizontal", ["Vertical", "Diagonal", "Curved"]),
    ("On Argand diagram, imaginary axis is:", "Vertical", ["Horizontal", "Diagonal", "Curved"]),
    ("5 + 3i is plotted at:", "(5, 3)", ["(3, 5)", "(5, -3)", "(-5, 3)"]),
    ("Point (4, 7) represents:", "4 + 7i", ["7 + 4i", "4 - 7i", "7 - 4i"]),
    ("Where is 6i on Argand diagram?", "(0, 6)", ["(6, 0)", "(6, 6)", "(0, 0)"]),
    ("Where is 8 on Argand diagram?", "(8, 0)", ["(0, 8)", "(8, 8)", "(0, 0)"]),
    ("Point (-3, 2) represents:", "-3 + 2i", ["3 + 2i", "-3 - 2i", "3 - 2i"]),
    ("Point (5, -4) represents:", "5 - 4i", ["5 + 4i", "-5 - 4i", "-5 + 4i"]),
    ("Where is -7i plotted?", "(0, -7)", ["(-7, 0)", "(7, 0)", "(0, 7)"]),
    ("Where is -9 plotted?", "(-9, 0)", ["(0, -9)", "(9, 0)", "(0, 9)"]),
    ("The origin represents:", "0", ["i", "1", "-1"]),
    ("Point (1, 1) represents:", "1 + i", ["1 - i", "-1 + i", "i + 1"]),
    ("Point (-2, -3) represents:", "-2 - 3i", ["-2 + 3i", "2 - 3i", "2 + 3i"]),
]

for q, a, w in argand_questions:
    w_validated = ensure_unique_options(a, w)
    section4_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section4'
    })

# Modulus calculations (15 questions)
modulus_questions = [
    ("|3 + 4i| = ?", "5", ["7", "3", "4"]),
    ("|5 + 12i| = ?", "13", ["17", "5", "12"]),
    ("|8 + 6i| = ?", "10", ["14", "8", "6"]),
    ("|1 + i| = ?", "√2", ["2", "1", "0"]),
    ("|2 + 2i| = ?", "2√2", ["4", "2", "√2"]),
    ("|5i| = ?", "5", ["5i", "0", "√5"]),
    ("|7| = ?", "7", ["0", "7i", "√7"]),
    ("|0| = ?", "0", ["1", "i", "undefined"]),
    ("|6 - 8i| = ?", "10", ["14", "6", "8"]),
    ("|3 - 4i| = ?", "5", ["7", "3", "4"]),
    ("|12 + 5i| = ?", "13", ["17", "12", "5"]),
    ("|-3 + 4i| = ?", "5", ["7", "3", "4"]),
    ("|4 - 3i| = ?", "5", ["7", "4", "3"]),
    ("|10| = ?", "10", ["0", "10i", "√10"]),
    ("|-6i| = ?", "6", ["6i", "0", "-6"]),
]

for q, a, w in modulus_questions:
    w_validated = ensure_unique_options(a, w)
    section4_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section4'
    })

# Distance and general questions (10 questions)
distance_questions = [
    ("Modulus formula for z = a + bi:", "|z| = √(a² + b²)", ["|z| = a + b", "|z| = a² + b²", "|z| = a - b"]),
    ("Distance from origin to 3 + 4i:", "5", ["7", "3", "4"]),
    ("|z| represents:", "Distance from origin", ["Real part", "Imaginary part", "Conjugate"]),
    ("Is |z| always non-negative?", "Yes", ["No", "Sometimes", "Only for real z"]),
    ("|z| = 0 means:", "z = 0", ["z = i", "z = 1", "z is real"]),
    ("If |z| = 1, z is on:", "Unit circle", ["Real axis", "Imaginary axis", "Origin"]),
    ("Modulus of conjugate equals:", "Modulus of original", ["Negative of original", "Zero", "Double"]),
    ("|z̄| = |z| is:", "Always true", ["Sometimes true", "Never true", "Only for real z"]),
    ("For pure imaginary z = bi, |z| = ?", "|b|", ["b", "b²", "0"]),
    ("For real number z = a, |z| = ?", "|a|", ["a", "a²", "0"]),
]

for q, a, w in distance_questions:
    w_validated = ensure_unique_options(a, w)
    section4_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section4'
    })


# SECTION 5: TRANSFORMATIONS (40 questions)
section5_questions = []

# Translation (15 questions)
translation_questions = [
    ("Translate 2 + 3i by 1 + i:", "3 + 4i", ["2 + 4i", "3 + 3i", "1 + 4i"]),
    ("Translate 5 + 2i by 3 + 4i:", "8 + 6i", ["8 + 2i", "5 + 6i", "2 + 6i"]),
    ("Translate 4 + 7i by -2 + i:", "2 + 8i", ["6 + 8i", "2 + 6i", "6 + 7i"]),
    ("Translate 6 + i by 2 + 2i:", "8 + 3i", ["8 + i", "6 + 3i", "4 + 3i"]),
    ("Translate 10 + 5i by -3 - 2i:", "7 + 3i", ["13 + 7i", "7 + 7i", "13 + 3i"]),
    ("Translate 1 + 1i by 1 + 1i:", "2 + 2i", ["1 + 2i", "2 + 1i", "2i"]),
    ("To translate z, we:", "Add a constant", ["Multiply by i", "Take conjugate", "Find modulus"]),
    ("Translation preserves:", "Shape and size", ["Only shape", "Only size", "Neither"]),
    ("Translate 3i by 4:", "4 + 3i", ["4i", "7i", "12i"]),
    ("Translate 5 by 2i:", "5 + 2i", ["7i", "10i", "5"]),
    ("Translate 7 + 8i by -7 - 8i:", "0", ["14 + 16i", "7 + 8i", "i"]),
    ("Adding 1 to z moves point:", "Right", ["Left", "Up", "Down"]),
    ("Adding i to z moves point:", "Up", ["Down", "Right", "Left"]),
    ("Adding -1 to z moves point:", "Left", ["Right", "Up", "Down"]),
    ("Adding -i to z moves point:", "Down", ["Up", "Right", "Left"]),
]

for q, a, w in translation_questions:
    w_validated = ensure_unique_options(a, w)
    section5_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section5'
    })

# Rotation (15 questions)
rotation_questions = [
    ("Multiply z by i rotates by:", "90° counterclockwise", ["90° clockwise", "180°", "45°"]),
    ("i × (1 + i) = ?", "-1 + i", ["1 + i", "i - 1", "1 - i"]),
    ("i × 2 = ?", "2i", ["-2i", "2", "-2"]),
    ("i × 3i = ?", "-3", ["3i", "3", "-3i"]),
    ("i × (2 + 3i) = ?", "-3 + 2i", ["2 + 3i", "3 + 2i", "-2 + 3i"]),
    ("Multiply by i² rotates by:", "180°", ["90°", "270°", "360°"]),
    ("Multiply by i³ rotates by:", "270° counterclockwise", ["90°", "180°", "360°"]),
    ("Multiply by i⁴ rotates by:", "360° (no rotation)", ["90°", "180°", "270°"]),
    ("i × 4 = ?", "4i", ["-4i", "4", "-4"]),
    ("i × 5i = ?", "-5", ["5i", "5", "-5i"]),
    ("i × (1 + 2i) = ?", "-2 + i", ["1 + 2i", "2 + i", "-1 + 2i"]),
    ("i × (3 + 4i) = ?", "-4 + 3i", ["3 + 4i", "4 + 3i", "-3 + 4i"]),
    ("Rotating by -90° is same as:", "Multiply by -i", ["Multiply by i", "Multiply by i²", "Add i"]),
    ("i × 6 = ?", "6i", ["-6i", "6", "-6"]),
    ("i × (5 + i) = ?", "-1 + 5i", ["5 + i", "1 + 5i", "-5 + i"]),
]

for q, a, w in rotation_questions:
    w_validated = ensure_unique_options(a, w)
    section5_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section5'
    })

# Scaling (10 questions)
scaling_questions = [
    ("2 × (3 + 4i) = ?", "6 + 8i", ["6 + 4i", "3 + 8i", "5 + 6i"]),
    ("3 × (1 + 2i) = ?", "3 + 6i", ["3 + 2i", "1 + 6i", "4 + 5i"]),
    ("5 × (2 + i) = ?", "10 + 5i", ["10 + i", "2 + 5i", "7 + 6i"]),
    ("Multiply by 2 means:", "Scale by factor 2", ["Rotate 2°", "Translate by 2", "Add 2"]),
    ("4 × (1 + 3i) = ?", "4 + 12i", ["4 + 3i", "1 + 12i", "5 + 7i"]),
    ("0.5 × (4 + 6i) = ?", "2 + 3i", ["4 + 3i", "2 + 6i", "4.5 + 6.5i"]),
    ("Scaling preserves:", "Angles", ["Distances", "Position", "All properties"]),
    ("10 × (1 + i) = ?", "10 + 10i", ["10 + i", "1 + 10i", "11 + 11i"]),
    ("2 × 5i = ?", "10i", ["5i", "10", "7i"]),
    ("3 × (2 - i) = ?", "6 - 3i", ["6 + 3i", "2 - 3i", "5 - 4i"]),
]

for q, a, w in scaling_questions:
    w_validated = ensure_unique_options(a, w)
    section5_questions.append({
        'question_text': q,
        'correct_answer': a,
        'wrong_answers': w_validated,
        'section': 'section5'
    })


# Combine all questions
all_questions = (
    section1_questions +  # 40
    section2_questions +  # 40
    section3_questions +  # 40
    section4_questions +  # 40
    section5_questions    # 40
)

print(f"\nTotal questions generated: {len(all_questions)}")
print(f"Section 1: {len(section1_questions)}")
print(f"Section 2: {len(section2_questions)}")
print(f"Section 3: {len(section3_questions)}")
print(f"Section 4: {len(section4_questions)}")
print(f"Section 5: {len(section5_questions)}")

# Validate ALL questions before adding to database
if not validate_all_questions(all_questions):
    print("\n❌ VALIDATION FAILED - Questions NOT added to database")
    print("Please review the issues above.")
    exit(1)

# Add questions to database
with app.app_context():
    # First, remove any existing Complex Numbers questions
    existing_count = Question.query.filter_by(topic='complex_numbers').count()
    if existing_count > 0:
        Question.query.filter_by(topic='complex_numbers').delete()
        db.session.commit()
        print(f"\nRemoved {existing_count} existing Complex Numbers questions")
    
    # Add new questions
    for q_data in all_questions:
        question = Question(
            topic='complex_numbers',
            difficulty=q_data['section'],
            question_text=q_data['question_text'],
            correct_answer=q_data['correct_answer'],
            wrong_answer1=q_data['wrong_answers'][0],
            wrong_answer2=q_data['wrong_answers'][1],
            wrong_answer3=q_data['wrong_answers'][2]
        )
        db.session.add(question)
    
    db.session.commit()
    print(f"\n✅ Successfully added {len(all_questions)} Complex Numbers questions to database!")
    
    # Verify
    final_count = Question.query.filter_by(topic='complex_numbers').count()
    print(f"Total Complex Numbers questions in database: {final_count}")
    
    # Show breakdown by section
    for section_num in range(1, 6):
        section_name = f'section{section_num}'
        count = Question.query.filter_by(topic='complex_numbers', difficulty=section_name).count()
        print(f"  {section_name}: {count} questions")

print("\n" + "="*60)
print("DEPLOYMENT COMPLETE!")
print("="*60)
