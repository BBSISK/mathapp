#!/usr/bin/env python3
"""
Complex Numbers Question Generator - RESTRUCTURED
Two topics: Complex Numbers Intro & Complex Numbers Expanded
For AgentMath.app - Palmerstown Community School

STRUCTURE:
Topic 1: Complex Numbers Intro
  - Beginner: Section 1 (The Basics - 40 questions)
  - Intermediate: Section 2 (Operations - 40 questions)  
  - Advanced: Section 3 (Division & Quadratics - 40 questions)

Topic 2: Complex Numbers - Expanded
  - Beginner: Section 4 (Argand & Modulus - 40 questions)
  - Intermediate: Section 5 (Transformations - 40 questions)
  - Advanced: Mixed Revision (40 questions sampled from all sections)
"""

from app import app, db, Question
import random

def ensure_unique_options(correct_answer, wrong_answers):
    """Ensure all answer options are unique."""
    all_options = [correct_answer] + wrong_answers
    
    if len(all_options) != len(set(all_options)):
        unique_wrong = []
        for ans in wrong_answers:
            if ans != correct_answer and ans not in unique_wrong:
                unique_wrong.append(ans)
        
        while len(unique_wrong) < 3:
            if 'i' in str(correct_answer):
                new_wrong = generate_wrong_complex(correct_answer)
            else:
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
    
    return f"{random.randint(-5, 5)} + {random.randint(-5, 5)}i"

def create_question_dict(text, correct, wrong_list, topic, difficulty, explanation):
    """
    Create a question dictionary in the standard format.
    Randomly shuffles options and returns proper structure.
    """
    wrong_validated = ensure_unique_options(correct, wrong_list)
    
    # Create all options with correct answer
    options = [correct] + wrong_validated
    random.shuffle(options)
    
    return {
        'topic': topic,
        'difficulty': difficulty,
        'question_text': text,
        'option_a': str(options[0]),
        'option_b': str(options[1]),
        'option_c': str(options[2]),
        'option_d': str(options[3]),
        'correct_answer': options.index(correct),
        'explanation': explanation
    }


# ==============================================================================
# TOPIC 1: COMPLEX NUMBERS INTRO
# ==============================================================================

# ------------------------------------------------------------------------------
# BEGINNER: Section 1 - The Basics (40 questions)
# ------------------------------------------------------------------------------
intro_beginner = []

# Powers of i (15 questions)
powers_of_i = [
    ("What does i represent?", "√(-1)", ["√1", "-1", "1"], "The imaginary unit i is defined as the square root of -1."),
    ("What is i²?", "-1", ["1", "i", "-i"], "i² = (√-1)² = -1"),
    ("What is i³?", "-i", ["i", "1", "-1"], "i³ = i² × i = -1 × i = -i"),
    ("What is i⁴?", "1", ["-1", "i", "-i"], "i⁴ = i² × i² = -1 × -1 = 1"),
    ("What is i⁵?", "i", ["-i", "1", "-1"], "i⁵ = i⁴ × i = 1 × i = i"),
    ("What is i⁶?", "-1", ["1", "i", "-i"], "i⁶ = i⁴ × i² = 1 × -1 = -1"),
    ("What is i⁷?", "-i", ["i", "1", "-1"], "i⁷ = i⁴ × i³ = 1 × -i = -i"),
    ("What is i⁸?", "1", ["-1", "i", "-i"], "i⁸ = (i⁴)² = 1² = 1"),
    ("What is i⁹?", "i", ["-i", "1", "-1"], "i⁹ = i⁸ × i = 1 × i = i"),
    ("What is i¹⁰?", "-1", ["1", "i", "-i"], "i¹⁰ = i⁸ × i² = 1 × -1 = -1"),
    ("What is i¹¹?", "-i", ["i", "1", "-1"], "i¹¹ = i⁸ × i³ = 1 × -i = -i"),
    ("What is i¹²?", "1", ["-1", "i", "-i"], "i¹² = (i⁴)³ = 1³ = 1"),
    ("Simplify: i¹⁶", "1", ["-1", "i", "-i"], "i¹⁶ = (i⁴)⁴ = 1⁴ = 1"),
    ("Simplify: i²⁰", "1", ["-1", "i", "-i"], "i²⁰ = (i⁴)⁵ = 1⁵ = 1"),
    ("Simplify: i²⁵", "i", ["-i", "1", "-1"], "i²⁵ = i²⁴ × i = (i⁴)⁶ × i = 1 × i = i"),
]

for q, a, w, exp in powers_of_i:
    intro_beginner.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'beginner', exp))

# Real and imaginary parts (15 questions)
parts_questions = [
    ("What is the real part of 3 + 4i?", "3", ["4", "4i", "3i"], "In a + bi form, 'a' is the real part. Here a = 3."),
    ("What is the imaginary part of 3 + 4i?", "4", ["3", "4i", "3i"], "In a + bi form, 'b' is the imaginary part coefficient. Here b = 4."),
    ("What is the real part of 5 - 2i?", "5", ["-2", "2i", "5i"], "The real part is 5."),
    ("What is the imaginary part of 5 - 2i?", "-2", ["5", "2", "-2i"], "The imaginary part coefficient is -2."),
    ("What is the real part of -6 + 7i?", "-6", ["7", "6", "-7"], "The real part is -6."),
    ("What is the imaginary part of -6 + 7i?", "7", ["-6", "6", "-7"], "The imaginary part coefficient is 7."),
    ("What is the real part of 8i?", "0", ["8", "8i", "1"], "8i = 0 + 8i, so the real part is 0."),
    ("What is the imaginary part of 8i?", "8", ["0", "8i", "i"], "8i = 0 + 8i, so the imaginary part coefficient is 8."),
    ("What is the real part of 12?", "12", ["0", "12i", "1"], "12 = 12 + 0i, so the real part is 12."),
    ("What is the imaginary part of 12?", "0", ["12", "1", "12i"], "12 = 12 + 0i, so the imaginary part coefficient is 0."),
    ("What is the real part of -3 - 5i?", "-3", ["-5", "3", "5"], "The real part is -3."),
    ("What is the imaginary part of -3 - 5i?", "-5", ["-3", "3", "5"], "The imaginary part coefficient is -5."),
    ("What is the real part of 10 + i?", "10", ["1", "10i", "0"], "10 + i = 10 + 1i, so the real part is 10."),
    ("What is the imaginary part of 10 + i?", "1", ["10", "0", "i"], "10 + i = 10 + 1i, so the imaginary part coefficient is 1."),
    ("In z = a + bi, what does 'a' represent?", "Real part", ["Imaginary part", "Modulus", "Conjugate"], "The letter 'a' represents the real part of the complex number."),
]

for q, a, w, exp in parts_questions:
    intro_beginner.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'beginner', exp))

# Definition questions (10 questions)
definition_questions = [
    ("In z = a + bi, what does 'b' represent?", "Imaginary part", ["Real part", "Modulus", "Argument"], "The letter 'b' is the coefficient of i, representing the imaginary part."),
    ("What is a complex number?", "a + bi", ["a + b", "ai + bi", "a - b"], "A complex number has the form a + bi where a and b are real."),
    ("Which of these is a pure imaginary number?", "5i", ["5", "5 + 0i", "0"], "A pure imaginary number has the form bi with a = 0."),
    ("Which of these is a real number?", "7", ["7i", "7 + i", "i"], "Real numbers have the form a + 0i, so 7 is real."),
    ("What is the imaginary unit squared?", "-1", ["1", "i", "0"], "By definition, i² = -1."),
    ("What symbol represents the imaginary unit?", "i", ["j", "x", "z"], "The imaginary unit is denoted by the letter i."),
    ("Is every real number also a complex number?", "Yes", ["No", "Sometimes", "Only positive"], "Yes, real numbers are complex numbers with b = 0."),
    ("What is 0 + 5i called?", "Pure imaginary", ["Real", "Mixed", "Zero"], "When a = 0, the number is pure imaginary."),
    ("What is 9 + 0i called?", "Real", ["Imaginary", "Pure imaginary", "Complex"], "When b = 0, the complex number is real."),
    ("Complex numbers extend which system?", "Real numbers", ["Natural numbers", "Integers", "Rationals"], "Complex numbers extend the real number system to include √-1."),
]

for q, a, w, exp in definition_questions:
    intro_beginner.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'beginner', exp))

print(f"✓ Complex Numbers Intro - Beginner: {len(intro_beginner)} questions")


# ------------------------------------------------------------------------------
# INTERMEDIATE: Section 2 - Operations (40 questions)
# ------------------------------------------------------------------------------
intro_intermediate = []

# Addition (10 questions)
addition_questions = [
    ("(2 + 3i) + (4 + 5i) = ?", "6 + 8i", ["6 + 2i", "8 + 6i", "6 + 5i"], "Add real parts: 2+4=6. Add imaginary parts: 3+5=8. Result: 6 + 8i."),
    ("(5 + 2i) + (3 + 4i) = ?", "8 + 6i", ["8 + 2i", "2 + 6i", "5 + 4i"], "Add real parts: 5+3=8. Add imaginary parts: 2+4=6. Result: 8 + 6i."),
    ("(1 + i) + (1 + i) = ?", "2 + 2i", ["2 + i", "1 + 2i", "2i"], "Add real parts: 1+1=2. Add imaginary parts: 1+1=2. Result: 2 + 2i."),
    ("(7 - 2i) + (3 + 5i) = ?", "10 + 3i", ["10 - 3i", "4 + 3i", "10 + 7i"], "Add real parts: 7+3=10. Add imaginary parts: -2+5=3. Result: 10 + 3i."),
    ("(4 + 6i) + (-2 + 3i) = ?", "2 + 9i", ["6 + 9i", "2 + 3i", "2 + 6i"], "Add real parts: 4+(-2)=2. Add imaginary parts: 6+3=9. Result: 2 + 9i."),
    ("(-3 + 4i) + (5 - 2i) = ?", "2 + 2i", ["2 - 2i", "8 + 2i", "2 + 6i"], "Add real parts: -3+5=2. Add imaginary parts: 4+(-2)=2. Result: 2 + 2i."),
    ("(6 + i) + (2 + 3i) = ?", "8 + 4i", ["8 + i", "8 + 3i", "6 + 3i"], "Add real parts: 6+2=8. Add imaginary parts: 1+3=4. Result: 8 + 4i."),
    ("(10 - 5i) + (0 + 5i) = ?", "10", ["10 + 5i", "10 - 5i", "5i"], "Add real parts: 10+0=10. Add imaginary parts: -5+5=0. Result: 10."),
    ("(0 + 2i) + (0 + 3i) = ?", "5i", ["2i", "3i", "0"], "Add imaginary parts: 2+3=5. Result: 5i (or 0 + 5i)."),
    ("(-4 - 3i) + (4 + 3i) = ?", "0", ["8", "6i", "-8"], "Add real parts: -4+4=0. Add imaginary parts: -3+3=0. Result: 0."),
]

for q, a, w, exp in addition_questions:
    intro_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'intermediate', exp))

# Subtraction (10 questions)
subtraction_questions = [
    ("(5 + 7i) - (2 + 3i) = ?", "3 + 4i", ["7 + 10i", "3 + 10i", "7 + 4i"], "Subtract real parts: 5-2=3. Subtract imaginary: 7-3=4. Result: 3 + 4i."),
    ("(8 + 4i) - (3 + 2i) = ?", "5 + 2i", ["11 + 6i", "5 + 6i", "5 - 2i"], "Subtract real parts: 8-3=5. Subtract imaginary: 4-2=2. Result: 5 + 2i."),
    ("(6 + 5i) - (6 + 3i) = ?", "2i", ["0", "12 + 8i", "6 + 2i"], "Subtract real parts: 6-6=0. Subtract imaginary: 5-3=2. Result: 2i."),
    ("(4 - 2i) - (1 - 5i) = ?", "3 + 3i", ["3 - 7i", "5 + 3i", "3 - 3i"], "Subtract: 4-1=3, -2-(-5)=3. Result: 3 + 3i."),
    ("(9 + 3i) - (4 + 8i) = ?", "5 - 5i", ["13 + 11i", "5 + 5i", "5 - 11i"], "Subtract: 9-4=5, 3-8=-5. Result: 5 - 5i."),
    ("(7 - i) - (2 + 2i) = ?", "5 - 3i", ["9 + i", "5 + i", "5 - i"], "Subtract: 7-2=5, -1-2=-3. Result: 5 - 3i."),
    ("(10 + 6i) - (10 + 6i) = ?", "0", ["20 + 12i", "6i", "10"], "Subtracting a number from itself gives 0."),
    ("(3 + 2i) - (5 - 4i) = ?", "-2 + 6i", ["8 - 2i", "-2 - 2i", "2 + 6i"], "Subtract: 3-5=-2, 2-(-4)=6. Result: -2 + 6i."),
    ("(0 + 8i) - (0 + 3i) = ?", "5i", ["11i", "-5i", "8i"], "Subtract imaginary parts: 8-3=5. Result: 5i."),
    ("(12) - (3 + 4i) = ?", "9 - 4i", ["15 + 4i", "9 + 4i", "12 - 4i"], "Subtract: 12-3=9, 0-4=-4. Result: 9 - 4i."),
]

for q, a, w, exp in subtraction_questions:
    intro_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'intermediate', exp))

# Multiplication (10 questions)
multiplication_questions = [
    ("(2 + i)(3 + 2i) = ?", "4 + 7i", ["6 + 2i", "6 + 7i", "4 + 2i"], "Expand: 6 + 4i + 3i + 2i² = 6 + 7i - 2 = 4 + 7i."),
    ("(1 + i)(1 - i) = ?", "2", ["0", "2i", "1 - i²"], "(1+i)(1-i) = 1 - i² = 1-(-1) = 2."),
    ("(3 + 2i)(2 - i) = ?", "8 + i", ["6 - 2i", "6 + i", "8 - i"], "Expand: 6 - 3i + 4i - 2i² = 6 + i + 2 = 8 + i."),
    ("i(4 + 3i) = ?", "-3 + 4i", ["4i + 3i", "4 + 3i²", "3 + 4i"], "Distribute: 4i + 3i² = 4i - 3 = -3 + 4i."),
    ("(2i)(3i) = ?", "-6", ["6i", "6i²", "5i"], "2i × 3i = 6i² = 6(-1) = -6."),
    ("(1 + 2i)(1 + 2i) = ?", "-3 + 4i", ["1 + 4i", "3 + 4i", "1 + 4i²"], "Expand: 1 + 2i + 2i + 4i² = 1 + 4i - 4 = -3 + 4i."),
    ("(4 - i)(2 + 3i) = ?", "11 + 10i", ["8 - 3i", "8 + 10i", "11 - 10i"], "Expand: 8 + 12i - 2i - 3i² = 8 + 10i + 3 = 11 + 10i."),
    ("3(2 + i) = ?", "6 + 3i", ["5 + i", "6 + i", "2 + 3i"], "Distribute: 3×2 + 3×i = 6 + 3i."),
    ("(5 + i)(5 - i) = ?", "26", ["24", "25 - i²", "10"], "(5+i)(5-i) = 25 - i² = 25 + 1 = 26."),
    ("(2 + 3i)(0) = ?", "0", ["2 + 3i", "2", "3i"], "Any number multiplied by 0 equals 0."),
]

for q, a, w, exp in multiplication_questions:
    intro_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'intermediate', exp))

# Conjugates (10 questions)
conjugate_questions = [
    ("What is the conjugate of 3 + 4i?", "3 - 4i", ["3 + 4i", "-3 - 4i", "-3 + 4i"], "Change the sign of the imaginary part: 3 - 4i."),
    ("What is the conjugate of 5 - 2i?", "5 + 2i", ["5 - 2i", "-5 + 2i", "-5 - 2i"], "Change the sign of the imaginary part: 5 + 2i."),
    ("What is the conjugate of -7 + 3i?", "-7 - 3i", ["-7 + 3i", "7 - 3i", "7 + 3i"], "Change the sign of the imaginary part: -7 - 3i."),
    ("What is the conjugate of 6i?", "-6i", ["6i", "6", "-6"], "The conjugate of 0 + 6i is 0 - 6i = -6i."),
    ("What is the conjugate of 8?", "8", ["-8", "8i", "0"], "Real numbers are their own conjugates: 8."),
    ("If z = 2 + i, what is z̄?", "2 - i", ["2 + i", "-2 - i", "-2 + i"], "The conjugate z̄ changes the sign of i: 2 - i."),
    ("What is the conjugate of -4 - 5i?", "-4 + 5i", ["-4 - 5i", "4 + 5i", "4 - 5i"], "Change the sign of the imaginary part: -4 + 5i."),
    ("What is the conjugate of i?", "-i", ["i", "1", "-1"], "The conjugate of 0 + i is 0 - i = -i."),
    ("If z̄ = 3 + 2i, what is z?", "3 - 2i", ["3 + 2i", "-3 - 2i", "-3 + 2i"], "If z̄ = 3 + 2i, then z = 3 - 2i."),
    ("What is (2 + 3i) + (2 - 3i)?", "4", ["4 + 6i", "6i", "0"], "A number plus its conjugate: (2+2) + (3i-3i) = 4."),
]

for q, a, w, exp in conjugate_questions:
    intro_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'intermediate', exp))

print(f"✓ Complex Numbers Intro - Intermediate: {len(intro_intermediate)} questions")


# ------------------------------------------------------------------------------
# ADVANCED: Section 3 - Division & Quadratics (40 questions)
# ------------------------------------------------------------------------------
intro_advanced = []

# Division (15 questions)
division_questions = [
    ("(4 + 2i) ÷ (1 - i) = ?", "1 + 3i", ["2 + i", "1 - 3i", "2 - i"], "Multiply by conjugate: (4+2i)(1+i)/(1-i)(1+i) = (4+6i+2i²)/2 = (2+6i)/2 = 1+3i."),
    ("(6 + 3i) ÷ 3 = ?", "2 + i", ["6 + i", "2 + 3i", "3 + i"], "Divide both parts by 3: 6/3 + 3i/3 = 2 + i."),
    ("(5 + 10i) ÷ 5 = ?", "1 + 2i", ["5 + 2i", "1 + 5i", "5 + 10i"], "Divide both parts by 5: 5/5 + 10i/5 = 1 + 2i."),
    ("i ÷ i = ?", "1", ["i", "-1", "0"], "Any non-zero number divided by itself equals 1."),
    ("(2 + 2i) ÷ (1 + i) = ?", "2", ["2i", "1 + i", "2 + 2i"], "Multiply by conjugate: (2+2i)(1-i)/(1+i)(1-i) = (2+2i-2i-2i²)/2 = 4/2 = 2."),
    ("(3 + 4i) ÷ i = ?", "4 - 3i", ["3i + 4i²", "-4 + 3i", "3 + 4i"], "Multiply by -i: (3+4i)(-i)/(-i²) = (-3i-4i²)/1 = 4-3i."),
    ("(10i) ÷ (2i) = ?", "5", ["5i", "8i", "20i²"], "10i ÷ 2i = 10/2 = 5."),
    ("(8 - 6i) ÷ 2 = ?", "4 - 3i", ["8 - 3i", "4 - 6i", "6 - 4i"], "Divide both parts by 2: 8/2 - 6i/2 = 4 - 3i."),
    ("(1 + i) ÷ (1 - i) = ?", "i", ["1", "-i", "1 + i"], "Multiply by conjugate: (1+i)(1+i)/(1-i)(1+i) = (1+2i+i²)/2 = 2i/2 = i."),
    ("(6) ÷ (2 + i) = ?", "2.4 - 1.2i", ["3", "2 + i", "6 - 3i"], "Multiply by conjugate: 6(2-i)/(2+i)(2-i) = (12-6i)/5 = 2.4-1.2i."),
    ("(3 - 3i) ÷ (1 + i) = ?", "-3i", ["3", "3i", "3 - 3i"], "Multiply by conjugate: (3-3i)(1-i)/(1+i)(1-i) = (3-6i+3i²)/2 = -6i/2 = -3i."),
    ("(5i) ÷ (1 + 2i) = ?", "2 + i", ["5i", "1 + 2i", "2 - i"], "Multiply by conjugate: 5i(1-2i)/(1+2i)(1-2i) = (5i-10i²)/5 = (10+5i)/5 = 2+i."),
    ("(4 + 8i) ÷ (2 - 2i) = ?", "-1 + 3i", ["2 + 4i", "1 + 3i", "-1 - 3i"], "Multiply by conjugate: (4+8i)(2+2i)/(2-2i)(2+2i) = (8+24i+16i²)/8 = (-8+24i)/8 = -1+3i."),
    ("(7 + 7i) ÷ (1 - i) = ?", "7i", ["7", "7 + 7i", "-7i"], "Multiply by conjugate: (7+7i)(1+i)/(1-i)(1+i) = (7+14i+7i²)/2 = 14i/2 = 7i."),
    ("(9 - 3i) ÷ (3) = ?", "3 - i", ["9 - i", "3 - 3i", "6 - i"], "Divide both parts by 3: 9/3 - 3i/3 = 3 - i."),
]

for q, a, w, exp in division_questions:
    intro_advanced.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'advanced', exp))

# Quadratic equations (15 questions)
quadratic_questions = [
    ("Solve: x² + 4 = 0", "±2i", ["±4i", "±2", "No solution"], "x² = -4, so x = ±√(-4) = ±2i."),
    ("Solve: x² + 9 = 0", "±3i", ["±9i", "±3", "No solution"], "x² = -9, so x = ±√(-9) = ±3i."),
    ("Solve: x² + 1 = 0", "±i", ["±1", "No solution", "0"], "x² = -1, so x = ±√(-1) = ±i."),
    ("Solve: x² + 16 = 0", "±4i", ["±16i", "±4", "±8i"], "x² = -16, so x = ±√(-16) = ±4i."),
    ("Solve: x² + 25 = 0", "±5i", ["±25i", "±5", "No solution"], "x² = -25, so x = ±√(-25) = ±5i."),
    ("Solve: 2x² + 8 = 0", "±2i", ["±4i", "±2", "±8i"], "2x² = -8, x² = -4, so x = ±2i."),
    ("Solve: x² + 2x + 2 = 0", "-1 ± i", ["1 ± i", "-1 ± 2i", "No solution"], "Using quadratic formula: x = (-2±√(4-8))/2 = (-2±2i)/2 = -1±i."),
    ("Solve: x² - 2x + 5 = 0", "1 ± 2i", ["1 ± i", "-1 ± 2i", "2 ± i"], "Using quadratic formula: x = (2±√(4-20))/2 = (2±4i)/2 = 1±2i."),
    ("Solve: x² + 6x + 10 = 0", "-3 ± i", ["3 ± i", "-3 ± 2i", "No solution"], "Using quadratic formula: x = (-6±√(36-40))/2 = (-6±2i)/2 = -3±i."),
    ("Solve: x² + 100 = 0", "±10i", ["±100i", "±10", "No solution"], "x² = -100, so x = ±√(-100) = ±10i."),
    ("Solve: x² + 4x + 5 = 0", "-2 ± i", ["2 ± i", "-2 ± 2i", "No solution"], "Using quadratic formula: x = (-4±√(16-20))/2 = (-4±2i)/2 = -2±i."),
    ("Solve: 3x² + 12 = 0", "±2i", ["±4i", "±6i", "±2"], "3x² = -12, x² = -4, so x = ±2i."),
    ("Solve: x² + 2x + 3 = 0", "-1 ± √2i", ["-1 ± i", "1 ± √2i", "No solution"], "Using quadratic formula: x = (-2±√(4-12))/2 = (-2±√(-8))/2 = -1±√2i."),
    ("Solve: x² + 49 = 0", "±7i", ["±49i", "±7", "No solution"], "x² = -49, so x = ±√(-49) = ±7i."),
    ("Solve: x² + 6 = 0", "±√6i", ["±6i", "±√6", "No solution"], "x² = -6, so x = ±√(-6) = ±√6i."),
]

for q, a, w, exp in quadratic_questions:
    intro_advanced.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'advanced', exp))

# Powers and roots (10 questions)
powers_roots = [
    ("What is (1 + i)²?", "2i", ["1 + i²", "1 + 2i", "2"], "Expand: 1 + 2i + i² = 1 + 2i - 1 = 2i."),
    ("What is (2i)²?", "-4", ["4i", "4", "-4i"], "(2i)² = 4i² = 4(-1) = -4."),
    ("What is (1 - i)²?", "-2i", ["1 - i²", "1 - 2i", "2"], "Expand: 1 - 2i + i² = 1 - 2i - 1 = -2i."),
    ("What is √(-16)?", "4i", ["4", "-4", "16i"], "√(-16) = √(16 × -1) = 4√(-1) = 4i."),
    ("What is √(-25)?", "5i", ["5", "-5", "25i"], "√(-25) = √(25 × -1) = 5√(-1) = 5i."),
    ("What is (3i)²?", "-9", ["9i", "9", "6i"], "(3i)² = 9i² = 9(-1) = -9."),
    ("What is √(-100)?", "10i", ["10", "-10", "100i"], "√(-100) = √(100 × -1) = 10√(-1) = 10i."),
    ("What is (i)³?", "-i", ["i", "1", "-1"], "i³ = i² × i = -1 × i = -i."),
    ("What is √(-1)?", "i", ["1", "-1", "-i"], "By definition, √(-1) = i."),
    ("What is (2 + i)² - (2 - i)²?", "8i", ["0", "4i", "8"], "Difference of squares: (2+i)² - (2-i)² = [(2+i)+(2-i)][(2+i)-(2-i)] = 4(2i) = 8i."),
]

for q, a, w, exp in powers_roots:
    intro_advanced.append(create_question_dict(q, a, w, 'complex_numbers_intro', 'advanced', exp))

print(f"✓ Complex Numbers Intro - Advanced: {len(intro_advanced)} questions")


# ==============================================================================
# TOPIC 2: COMPLEX NUMBERS - EXPANDED
# ==============================================================================

# ------------------------------------------------------------------------------
# BEGINNER: Section 4 - Argand Diagram & Modulus (40 questions)
# ------------------------------------------------------------------------------
expanded_beginner = []

# Argand diagram (20 questions)
argand_questions = [
    ("On an Argand diagram, what axis represents the real part?", "x-axis", ["y-axis", "Both axes", "Neither"], "The horizontal x-axis represents the real part."),
    ("On an Argand diagram, what axis represents the imaginary part?", "y-axis", ["x-axis", "Both axes", "Neither"], "The vertical y-axis represents the imaginary part."),
    ("Where is 3 + 4i on an Argand diagram?", "(3, 4)", ["(4, 3)", "(3, -4)", "(-3, 4)"], "Plot real part on x-axis (3) and imaginary part on y-axis (4)."),
    ("Where is 2 - 5i on an Argand diagram?", "(2, -5)", ["(-2, 5)", "(2, 5)", "(5, -2)"], "Plot real=2 on x-axis and imaginary=-5 on y-axis."),
    ("Where is -3 + 2i on an Argand diagram?", "(-3, 2)", ["(3, -2)", "(-3, -2)", "(2, -3)"], "Plot real=-3 on x-axis and imaginary=2 on y-axis."),
    ("What complex number is at point (5, 3)?", "5 + 3i", ["3 + 5i", "5 - 3i", "(5, 3)"], "x-coordinate is real part, y-coordinate is imaginary part."),
    ("What complex number is at point (0, 4)?", "4i", ["4", "0", "0 + 4"], "This is on the imaginary axis: 0 + 4i = 4i."),
    ("What complex number is at point (7, 0)?", "7", ["7i", "0", "7 + 0"], "This is on the real axis: 7 + 0i = 7."),
    ("What complex number is at point (-2, -3)?", "-2 - 3i", ["-2 + 3i", "2 - 3i", "(-2, -3)"], "x=-2 (real), y=-3 (imaginary): -2 - 3i."),
    ("Which quadrant contains 4 + 5i?", "First", ["Second", "Third", "Fourth"], "Both parts positive: first quadrant."),
    ("Which quadrant contains -3 + 2i?", "Second", ["First", "Third", "Fourth"], "Real negative, imaginary positive: second quadrant."),
    ("Which quadrant contains -4 - 6i?", "Third", ["First", "Second", "Fourth"], "Both parts negative: third quadrant."),
    ("Which quadrant contains 5 - 3i?", "Fourth", ["First", "Second", "Third"], "Real positive, imaginary negative: fourth quadrant."),
    ("The origin represents which number?", "0", ["i", "1", "∞"], "The origin (0,0) represents the complex number 0."),
    ("Where is the conjugate of 2 + 3i?", "(2, -3)", ["(2, 3)", "(-2, 3)", "(-2, -3)"], "Conjugate reflects across x-axis: 2 - 3i at (2, -3)."),
    ("What transformation maps z to z̄?", "Reflect in x-axis", ["Reflect in y-axis", "Rotate 180°", "Translate"], "Conjugate reflects across the real (x) axis."),
    ("Distance from origin to 3 + 4i?", "5", ["7", "√7", "25"], "Distance = √(3² + 4²) = √25 = 5."),
    ("On Argand diagram, what does |z| represent?", "Distance from origin", ["Angle", "Real part", "Imaginary part"], "The modulus |z| is the distance from the origin."),
    ("Where would -i be plotted?", "(0, -1)", ["(0, 1)", "(-1, 0)", "(1, 0)"], "-i = 0 - 1i, so plot at (0, -1)."),
    ("Where would 5 be plotted?", "(5, 0)", ["(0, 5)", "(5, 5)", "(0, 0)"], "5 = 5 + 0i, so plot at (5, 0) on the real axis."),
]

for q, a, w, exp in argand_questions:
    expanded_beginner.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'beginner', exp))

# Modulus (20 questions)
modulus_questions = [
    ("What is |3 + 4i|?", "5", ["7", "12", "√7"], "|z| = √(3² + 4²) = √(9 + 16) = √25 = 5."),
    ("What is |5 - 12i|?", "13", ["17", "√13", "7"], "|z| = √(5² + 12²) = √(25 + 144) = √169 = 13."),
    ("What is |8 + 6i|?", "10", ["14", "√14", "48"], "|z| = √(8² + 6²) = √(64 + 36) = √100 = 10."),
    ("What is |i|?", "1", ["0", "i", "√-1"], "|i| = |0 + 1i| = √(0² + 1²) = 1."),
    ("What is |5|?", "5", ["0", "√5", "25"], "|5| = |5 + 0i| = √(5² + 0²) = 5."),
    ("What is |-3 + 4i|?", "5", ["7", "1", "√7"], "|z| = √((-3)² + 4²) = √(9 + 16) = 5."),
    ("What is |6 - 8i|?", "10", ["14", "2", "√14"], "|z| = √(6² + 8²) = √(36 + 64) = 10."),
    ("What is |1 + i|?", "√2", ["2", "1", "√1"], "|z| = √(1² + 1²) = √2."),
    ("What is |2i|?", "2", ["2i", "4", "0"], "|2i| = |0 + 2i| = √(0² + 2²) = 2."),
    ("What is |-5|?", "5", ["-5", "0", "25"], "The modulus is always non-negative: |-5| = 5."),
    ("What is |12 + 5i|?", "13", ["17", "√13", "60"], "|z| = √(12² + 5²) = √(144 + 25) = 13."),
    ("What is |7 - 24i|?", "25", ["31", "17", "√25"], "|z| = √(7² + 24²) = √(49 + 576) = 25."),
    ("What is |0|?", "0", ["1", "Undefined", "∞"], "The modulus of zero is zero."),
    ("If |z| = 0, what is z?", "0", ["i", "1", "Undefined"], "Only the zero complex number has modulus 0."),
    ("What is |3 - 3i|?", "3√2", ["6", "0", "3"], "|z| = √(3² + (-3)²) = √18 = 3√2."),
    ("What is |4|?", "4", ["-4", "0", "16"], "|4| = |4 + 0i| = 4."),
    ("What is |2 + 2i|?", "2√2", ["4", "2", "8"], "|z| = √(2² + 2²) = √8 = 2√2."),
    ("What is |-i|?", "1", ["-1", "i", "0"], "|-i| = |0 - 1i| = √(0² + 1²) = 1."),
    ("What is |5 + 12i|?", "13", ["17", "7", "√13"], "|z| = √(5² + 12²) = √(25 + 144) = 13."),
    ("What is |9 - 40i|?", "41", ["49", "31", "√41"], "|z| = √(9² + 40²) = √(81 + 1600) = 41."),
]

for q, a, w, exp in modulus_questions:
    expanded_beginner.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'beginner', exp))

print(f"✓ Complex Numbers Expanded - Beginner: {len(expanded_beginner)} questions")


# ------------------------------------------------------------------------------
# INTERMEDIATE: Section 5 - Transformations (40 questions)
# ------------------------------------------------------------------------------
expanded_intermediate = []

# Multiplication by i (rotation) (15 questions)
rotation_questions = [
    ("What is i × (3 + 4i)?", "-4 + 3i", ["3i + 4i²", "3 + 4i", "4 + 3i"], "Distribute: 3i + 4i² = 3i - 4 = -4 + 3i. This rotates 90° counterclockwise."),
    ("What is i × (1 + 0i)?", "i", ["1", "-i", "1 + i"], "i × 1 = i. Multiplying by i rotates 90° counterclockwise."),
    ("What is i × (2 - 3i)?", "3 + 2i", ["2i - 3i²", "2 - 3i", "-3 + 2i"], "Distribute: 2i - 3i² = 2i + 3 = 3 + 2i."),
    ("What is i² × (1 + i)?", "-1 - i", ["1 + i", "-1 + i", "i + i²"], "i² × (1+i) = -1 × (1+i) = -1 - i. This rotates 180°."),
    ("What is i × i?", "-1", ["1", "i²", "2i"], "i × i = i² = -1."),
    ("Multiplying by i rotates by how many degrees?", "90°", ["45°", "180°", "270°"], "Multiplying by i rotates 90° counterclockwise."),
    ("What is i³ × (2 + i)?", "-1 + 2i", ["2 + i", "1 + 2i", "-2 - i"], "i³ × (2+i) = -i × (2+i) = -2i - i² = 1 - 2i. Wait, recalculating: -2i + 1 = 1 - 2i. Actually -i(2+i) = -2i - i² = -2i + 1. Hmm, let me be careful: i³ = -i, so -i(2+i) = -2i - i² = -2i - (-1) = -2i + 1 = 1 - 2i. But the answer given is -1 + 2i. Let me check: actually if we do -i × 2 = -2i, and -i × i = -i² = -(-1) = 1. So we get 1 - 2i. This doesn't match. Let me recalculate: i³ = -i. So i³(2+i) = -i(2+i) = -2i - i² = -2i + 1 = 1 - 2i. The listed answer is wrong."),
    ("What is i × (5)?", "5i", ["5", "-5i", "5 + i"], "i × 5 = 5i."),
    ("What is i × (-2 + i)?", "-1 - 2i", ["-2i + i²", "-2 + i", "1 - 2i"], "Distribute: -2i + i² = -2i - 1 = -1 - 2i."),
    ("What is i⁴ × (3 + 2i)?", "3 + 2i", ["-3 - 2i", "3i + 2i²", "2 + 3i"], "i⁴ = 1, so 1 × (3+2i) = 3 + 2i. No rotation."),
    ("What is i × (4 + 4i)?", "-4 + 4i", ["4i + 4i²", "4 + 4i", "4 - 4i"], "Distribute: 4i + 4i² = 4i - 4 = -4 + 4i."),
    ("What is i × (0 + i)?", "-1", ["i²", "i", "0"], "i × i = i² = -1."),
    ("What is i × (6 - 2i)?", "2 + 6i", ["6i - 2i²", "-2 + 6i", "6 - 2i"], "Distribute: 6i - 2i² = 6i + 2 = 2 + 6i."),
    ("Multiplying by -1 rotates by?", "180°", ["90°", "270°", "0°"], "Multiplying by -1 rotates 180°."),
    ("What is i × (1 - i)?", "1 + i", ["i - i²", "1 - i", "-1 + i"], "Distribute: i - i² = i + 1 = 1 + i."),
]

# I need to fix question 7 above - let me recalculate
rotation_questions[6] = ("What is i³ × (2 + i)?", "1 - 2i", ["2 + i", "-1 + 2i", "-2 - i"], "i³ = -i, so -i × (2+i) = -2i - i² = -2i + 1 = 1 - 2i. Rotates 270°.")

for q, a, w, exp in rotation_questions:
    expanded_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'intermediate', exp))

# Polar form and argument (15 questions)
polar_questions = [
    ("What is the argument of 1 + i?", "45°", ["90°", "135°", "0°"], "arg(1+i) = arctan(1/1) = 45° (first quadrant)."),
    ("What is the argument of -1 + i?", "135°", ["45°", "90°", "225°"], "arg(-1+i) = 180° - 45° = 135° (second quadrant)."),
    ("What is the argument of -1 - i?", "225°", ["135°", "315°", "45°"], "arg(-1-i) = 180° + 45° = 225° (third quadrant)."),
    ("What is the argument of 1 - i?", "315°", ["45°", "225°", "270°"], "arg(1-i) = 360° - 45° = 315° (fourth quadrant)."),
    ("What is the argument of i?", "90°", ["0°", "180°", "270°"], "arg(i) = arg(0+i) = 90° (positive imaginary axis)."),
    ("What is the argument of -i?", "270°", ["90°", "180°", "0°"], "arg(-i) = 270° (negative imaginary axis)."),
    ("What is the argument of 1?", "0°", ["90°", "180°", "Undefined"], "arg(1) = 0° (positive real axis)."),
    ("What is the argument of -1?", "180°", ["0°", "90°", "270°"], "arg(-1) = 180° (negative real axis)."),
    ("What is the argument of √3 + i?", "30°", ["60°", "45°", "90°"], "arg(√3+i) = arctan(1/√3) = 30°."),
    ("What is the argument of 1 + √3i?", "60°", ["30°", "45°", "90°"], "arg(1+√3i) = arctan(√3/1) = 60°."),
    ("What is the polar form of |z| = 2, arg = 0°?", "2", ["2i", "2 + 0i", "0"], "Polar form r(cos θ + i sin θ) = 2(1 + 0i) = 2."),
    ("What is the polar form of |z| = 1, arg = 90°?", "i", ["1", "-i", "1 + i"], "1(cos 90° + i sin 90°) = 1(0 + i) = i."),
    ("What is the polar form of |z| = 3, arg = 180°?", "-3", ["3", "3i", "-3i"], "3(cos 180° + i sin 180°) = 3(-1 + 0i) = -3."),
    ("What is the polar form of |z| = 2, arg = 270°?", "-2i", ["2i", "-2", "2"], "2(cos 270° + i sin 270°) = 2(0 - i) = -2i."),
    ("In polar form r(cos θ + i sin θ), what is r?", "Modulus", ["Argument", "Real part", "Imaginary part"], "r represents the modulus |z|."),
]

for q, a, w, exp in polar_questions:
    expanded_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'intermediate', exp))

# De Moivre's theorem basics (10 questions)
demoivre_questions = [
    ("(cos 30° + i sin 30°)² = ?", "cos 60° + i sin 60°", ["cos 30° + i sin 30°", "cos 90° + i sin 90°", "2(cos 30° + i sin 30°)"], "De Moivre's theorem: multiply the angle by 2."),
    ("(cos 45° + i sin 45°)² = ?", "cos 90° + i sin 90°", ["cos 45° + i sin 45°", "cos 135° + i sin 135°", "i"], "Angle doubles: 45° × 2 = 90°. This equals i."),
    ("(cos 60° + i sin 60°)³ = ?", "cos 180° + i sin 180°", ["cos 60° + i sin 60°", "cos 240° + i sin 240°", "-1"], "Angle triples: 60° × 3 = 180°. This equals -1."),
    ("What does De Moivre's theorem state?", "(cos θ + i sin θ)ⁿ = cos(nθ) + i sin(nθ)", ["(cos θ)ⁿ + i(sin θ)ⁿ", "n(cos θ + i sin θ)", "cos(θⁿ) + i sin(θⁿ)"], "De Moivre's theorem: raise to power n, multiply angle by n."),
    ("(cos 90° + i sin 90°)² = ?", "cos 180° + i sin 180°", ["i²", "-1", "cos 90° + i sin 90°"], "Angle doubles: 90° × 2 = 180°, which equals -1."),
    ("(cos 0° + i sin 0°)⁵ = ?", "1", ["0", "5", "cos 0° + i sin 0°"], "Any power of 1 is 1. Also 0° × 5 = 0°."),
    ("i² using De Moivre?", "-1", ["i", "1", "2i"], "i = cos 90° + i sin 90°, so i² = cos 180° + i sin 180° = -1."),
    ("i⁴ using De Moivre?", "1", ["-1", "i", "4i"], "i⁴ = (cos 90°)⁴ = cos 360° + i sin 360° = 1."),
    ("(cos 120° + i sin 120°)² = ?", "cos 240° + i sin 240°", ["cos 120°", "cos 60°", "-1"], "Angle doubles: 120° × 2 = 240°."),
    ("To find zⁿ in polar form, what happens to the angle?", "Multiply by n", ["Divide by n", "Add n", "No change"], "De Moivre: the argument is multiplied by n."),
]

for q, a, w, exp in demoivre_questions:
    expanded_intermediate.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'intermediate', exp))

print(f"✓ Complex Numbers Expanded - Intermediate: {len(expanded_intermediate)} questions")


# ------------------------------------------------------------------------------
# ADVANCED: Mixed Revision (40 questions sampled from all sections)
# ------------------------------------------------------------------------------
print("\n📝 Creating revision questions by sampling from all 5 sections...")

# Collect all original questions (before they were converted to standard format)
all_original_questions = []

# From Section 1
all_original_questions.extend([
    (q, a, w, exp, 'basics') for q, a, w, exp in powers_of_i + parts_questions + definition_questions
])

# From Section 2 - we need to extract from the dicts we already created
# Actually, let's create a simpler mixed set by directly defining some review questions

expanded_advanced = []

# Mixed review questions covering all topics (40 questions)
mixed_review = [
    # Basics
    ("What is i²?", "-1", ["1", "i", "-i"], "i² = -1 by definition."),
    ("What is the real part of 5 - 3i?", "5", ["-3", "5i", "3"], "The real part is 5."),
    ("What is the conjugate of 4 + 7i?", "4 - 7i", ["4 + 7i", "-4 - 7i", "-4 + 7i"], "Change the sign of the imaginary part."),
    
    # Operations
    ("(3 + 2i) + (1 + 4i) = ?", "4 + 6i", ["4 + 2i", "3 + 6i", "4 + 4i"], "Add real parts: 3+1=4. Add imaginary: 2+4=6."),
    ("(5 + 3i) - (2 + i) = ?", "3 + 2i", ["7 + 4i", "3 + 4i", "3 + i"], "Subtract: 5-2=3, 3-1=2."),
    ("(2 + i)(3 + 2i) = ?", "4 + 7i", ["6 + 2i", "6 + 7i", "5 + 7i"], "Expand: 6 + 4i + 3i + 2i² = 6 + 7i - 2 = 4 + 7i."),
    ("i × (3 + 4i) = ?", "-4 + 3i", ["3i + 4i²", "3 + 4i", "4 + 3i"], "Distribute: 3i + 4i² = 3i - 4 = -4 + 3i."),
    
    # Division & Quadratics
    ("(6 + 3i) ÷ 3 = ?", "2 + i", ["3 + i", "2 + 3i", "6 + i"], "Divide both parts by 3."),
    ("Solve: x² + 9 = 0", "±3i", ["±9i", "±3", "No solution"], "x² = -9, so x = ±3i."),
    ("What is (1 + i)²?", "2i", ["1 + 2i", "2", "1 + i²"], "Expand: 1 + 2i + i² = 1 + 2i - 1 = 2i."),
    ("Solve: x² - 2x + 5 = 0", "1 ± 2i", ["1 ± i", "-1 ± 2i", "2 ± i"], "Use quadratic formula: (2±√(-16))/2 = 1±2i."),
    
    # Argand & Modulus
    ("On Argand diagram, where is 4 + 3i?", "(4, 3)", ["(3, 4)", "(4, -3)", "(-4, 3)"], "Real part on x-axis, imaginary on y-axis."),
    ("What complex number is at (0, 5)?", "5i", ["5", "0", "0 + 5"], "On imaginary axis: 5i."),
    ("Which quadrant contains -2 + 3i?", "Second", ["First", "Third", "Fourth"], "Real negative, imaginary positive: second quadrant."),
    ("What is |3 + 4i|?", "5", ["7", "12", "√7"], "|z| = √(3² + 4²) = 5."),
    ("What is |5 - 12i|?", "13", ["17", "7", "√13"], "|z| = √(5² + 12²) = 13."),
    ("What is |i|?", "1", ["0", "i", "-1"], "|i| = √(0² + 1²) = 1."),
    ("What is |2 + 2i|?", "2√2", ["4", "2", "8"], "|z| = √(2² + 2²) = √8 = 2√2."),
    
    # Transformations
    ("What is the argument of 1 + i?", "45°", ["90°", "135°", "0°"], "arg(1+i) = 45° in first quadrant."),
    ("What is the argument of -1 + i?", "135°", ["45°", "90°", "225°"], "arg(-1+i) = 135° in second quadrant."),
    ("What is the argument of i?", "90°", ["0°", "180°", "270°"], "arg(i) = 90° on positive imaginary axis."),
    ("Multiplying by i rotates by?", "90°", ["45°", "180°", "270°"], "Multiplication by i rotates 90° counterclockwise."),
    ("What is i⁴?", "1", ["-1", "i", "-i"], "i⁴ = (i²)² = (-1)² = 1."),
    ("What is the polar form of |z|=1, arg=90°?", "i", ["1", "-i", "1+i"], "1(cos 90° + i sin 90°) = i."),
    ("(cos 45° + i sin 45°)² = ?", "cos 90° + i sin 90°", ["cos 45°", "i", "2(cos 45°)"], "De Moivre: angle doubles to 90°."),
    
    # Mixed advanced
    ("What is i³?", "-i", ["i", "1", "-1"], "i³ = i² × i = -1 × i = -i."),
    ("What is √(-25)?", "5i", ["5", "-5", "25i"], "√(-25) = 5i."),
    ("What is the imaginary part of 10i?", "10", ["0", "10i", "i"], "10i = 0 + 10i, coefficient is 10."),
    ("Is 7 a complex number?", "Yes", ["No", "Sometimes", "Only if negative"], "Yes, 7 = 7 + 0i."),
    ("What is (1 - i)(1 + i)?", "2", ["0", "2i", "1-i²"], "(1-i)(1+i) = 1 - i² = 1 + 1 = 2."),
    ("(4 + 2i) - (4 - 2i) = ?", "4i", ["0", "8", "2i"], "4-4 + 2i-(-2i) = 4i."),
    ("What is i⁸?", "1", ["-1", "i", "8i"], "i⁸ = (i⁴)² = 1² = 1."),
    ("Solve: x² + 4 = 0", "±2i", ["±4i", "±2", "No solution"], "x² = -4, x = ±2i."),
    ("What axis do conjugates reflect across?", "x-axis", ["y-axis", "Both", "Neither"], "Conjugates reflect across the real (x) axis."),
    ("What is |5|?", "5", ["-5", "0", "25"], "|5| = 5 for any real number."),
    ("What is the argument of -1?", "180°", ["0°", "90°", "270°"], "arg(-1) = 180° on negative real axis."),
    ("In z = a + bi, what is b?", "Imaginary coefficient", ["Real part", "Modulus", "Argument"], "b is the coefficient of i."),
    ("What is i × i × i?", "-i", ["i", "1", "-1"], "i³ = -i."),
    ("(6 - 8i) has modulus?", "10", ["14", "2", "√14"], "|6-8i| = √(36+64) = 10."),
    ("What is (2i)²?", "-4", ["4i", "4", "2i²"], "(2i)² = 4i² = -4."),
]

for q, a, w, exp in mixed_review:
    expanded_advanced.append(create_question_dict(q, a, w, 'complex_numbers_expanded', 'advanced', exp))

print(f"✓ Complex Numbers Expanded - Advanced (Revision): {len(expanded_advanced)} questions")


# ==============================================================================
# DATABASE INSERTION
# ==============================================================================

all_questions = (
    intro_beginner +         # 40 questions
    intro_intermediate +     # 40 questions
    intro_advanced +         # 40 questions
    expanded_beginner +      # 40 questions
    expanded_intermediate +  # 40 questions
    expanded_advanced        # 40 questions
)

print("\n" + "="*70)
print("QUESTION SUMMARY")
print("="*70)
print(f"\nTOPIC 1: Complex Numbers Intro")
print(f"  Beginner:     {len(intro_beginner)} questions")
print(f"  Intermediate: {len(intro_intermediate)} questions")
print(f"  Advanced:     {len(intro_advanced)} questions")
print(f"  Subtotal:     {len(intro_beginner) + len(intro_intermediate) + len(intro_advanced)} questions")

print(f"\nTOPIC 2: Complex Numbers - Expanded")
print(f"  Beginner:     {len(expanded_beginner)} questions")
print(f"  Intermediate: {len(expanded_intermediate)} questions")
print(f"  Advanced:     {len(expanded_advanced)} questions (mixed revision)")
print(f"  Subtotal:     {len(expanded_beginner) + len(expanded_intermediate) + len(expanded_advanced)} questions")

print(f"\nTOTAL:          {len(all_questions)} questions")
print("="*70)

# Add to database
with app.app_context():
    # Remove existing complex numbers questions
    existing_intro = Question.query.filter_by(topic='complex_numbers_intro').count()
    existing_expanded = Question.query.filter_by(topic='complex_numbers_expanded').count()
    existing_old = Question.query.filter_by(topic='complex_numbers').count()
    
    if existing_intro > 0:
        Question.query.filter_by(topic='complex_numbers_intro').delete()
        print(f"\n🗑️  Removed {existing_intro} existing 'complex_numbers_intro' questions")
    
    if existing_expanded > 0:
        Question.query.filter_by(topic='complex_numbers_expanded').delete()
        print(f"🗑️  Removed {existing_expanded} existing 'complex_numbers_expanded' questions")
    
    if existing_old > 0:
        Question.query.filter_by(topic='complex_numbers').delete()
        print(f"🗑️  Removed {existing_old} existing 'complex_numbers' questions (old format)")
    
    db.session.commit()
    
    # Add new questions
    print("\n📝 Adding new questions to database...")
    for q_data in all_questions:
        question = Question(
            topic=q_data['topic'],
            difficulty=q_data['difficulty'],
            question_text=q_data['question_text'],
            option_a=q_data['option_a'],
            option_b=q_data['option_b'],
            option_c=q_data['option_c'],
            option_d=q_data['option_d'],
            correct_answer=q_data['correct_answer'],
            explanation=q_data['explanation']
        )
        db.session.add(question)
    
    db.session.commit()
    print(f"✅ Successfully added {len(all_questions)} questions!")
    
    # Verify
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    intro_count = Question.query.filter_by(topic='complex_numbers_intro').count()
    expanded_count = Question.query.filter_by(topic='complex_numbers_expanded').count()
    
    print(f"\nComplex Numbers Intro: {intro_count} questions")
    for diff in ['beginner', 'intermediate', 'advanced']:
        count = Question.query.filter_by(topic='complex_numbers_intro', difficulty=diff).count()
        print(f"  {diff.capitalize()}: {count}")
    
    print(f"\nComplex Numbers - Expanded: {expanded_count} questions")
    for diff in ['beginner', 'intermediate', 'advanced']:
        count = Question.query.filter_by(topic='complex_numbers_expanded', difficulty=diff).count()
        print(f"  {diff.capitalize()}: {count}")
    
    print(f"\nTotal Complex Numbers questions: {intro_count + expanded_count}")
    print("="*70)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*70)
