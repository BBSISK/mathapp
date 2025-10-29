"""
COMPLEX NUMBERS QUESTIONS - 5 SECTIONS

This script adds questions for the new Complex Numbers topic with 5 sections:
1. The basics of complex numbers (40 questions)
2. Operating with complex numbers (40 questions)
3. Division and quadratic equations (40 questions)
4. The Argand diagram and modulus (40 questions)
5. Transformations (40 questions)

Total: 200 questions

Run this ONCE in PythonAnywhere Bash console:
    cd ~/your-project-directory
    python complex_numbers_questions.py
"""

from app import app, db, Question
import random
import math

def generate_section1_questions():
    """Section 1: The basics of complex numbers (40 questions)"""
    questions = []
    
    print("Generating Section 1: The basics of complex numbers...")
    
    # 10 questions on imaginary unit i
    for _ in range(10):
        q_type = random.choice(['i_squared', 'sqrt_negative', 'i_definition'])
        
        if q_type == 'i_squared':
            question_text = "What does i² equal?"
            options = ["-1", "1", "i", "-i"]
            correct = 0
            explanation = "By definition, i² = -1. This is the fundamental property of the imaginary unit."
        
        elif q_type == 'sqrt_negative':
            n = random.randint(2, 20)
            question_text = "Simplify √(-{0}).".format(n)
            answer_str = "i√{0}".format(n) if n > 1 else "i"
            
            options = [answer_str]
            wrong_options = [
                "-i√{0}".format(n),
                "√{0}".format(n),
                "-√{0}".format(n)
            ]
            options.extend(random.sample(wrong_options, 3))
            random.shuffle(options)
            correct = options.index(answer_str)
            explanation = "√(-{0}) = √(-1) × √{0} = i√{0}".format(n)
        
        else:  # i_definition
            question_text = "What is the value of √(-1)?"
            options = ["i", "-i", "1", "-1"]
            correct = 0
            explanation = "By definition, the imaginary unit i is defined as i = √(-1)."
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section1',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 10 questions on definition and form
    for _ in range(10):
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        if b == 0:
            b = random.choice([1, 2, 3])
        
        question_text = "For the complex number {0} + {1}i, what is the real part?".format(a, b)
        options = [str(a), str(b), str(abs(a)), str(a+b)]
        random.shuffle(options)
        correct = options.index(str(a))
        explanation = "In the form a + bi, the real part is a = {0}.".format(a)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section1',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 20 questions on powers of i
    for _ in range(20):
        power = random.randint(1, 20)
        
        # Calculate i^power
        remainder = power % 4
        if remainder == 1:
            answer = "i"
        elif remainder == 2:
            answer = "-1"
        elif remainder == 3:
            answer = "-i"
        else:  # remainder == 0
            answer = "1"
        
        question_text = "What is i^{0}?".format(power)
        options = ["i", "-1", "-i", "1"]
        random.shuffle(options)
        correct = options.index(answer)
        
        explanation = "Powers of i follow a cycle: i¹=i, i²=-1, i³=-i, i⁴=1. Since {0} ÷ 4 has remainder {1}, i^{0} = {2}.".format(power, remainder, answer)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section1',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    print("✓ Generated 40 Section 1 questions")
    return questions


def generate_section2_questions():
    """Section 2: Operating with complex numbers (40 questions)"""
    questions = []
    
    print("Generating Section 2: Operating with complex numbers...")
    
    # 10 questions on addition
    for _ in range(10):
        a1, b1 = random.randint(-9, 9), random.randint(-9, 9)
        a2, b2 = random.randint(-9, 9), random.randint(-9, 9)
        
        real_sum = a1 + a2
        imag_sum = b1 + b2
        
        if imag_sum >= 0:
            answer_str = "{0} + {1}i".format(real_sum, imag_sum)
        else:
            answer_str = "{0} - {1}i".format(real_sum, abs(imag_sum))
        
        question_text = "Simplify: ({0} + {1}i) + ({2} + {3}i)".format(a1, b1, a2, b2)
        
        options = [answer_str]
        # Generate wrong options
        wrong1 = "{0} + {1}i".format(a1 + a2 + 1, b1 + b2)
        wrong2 = "{0} + {1}i".format(a1 + a2, b1 + b2 + 1)
        wrong3 = "{0} + {1}i".format(a1 + a2 - 1, b1 + b2 - 1)
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Add real parts: {0} + {1} = {2}. Add imaginary parts: {3} + {4} = {5}. Result: {6}".format(
            a1, a2, real_sum, b1, b2, imag_sum, answer_str
        )
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section2',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 10 questions on subtraction
    for _ in range(10):
        a1, b1 = random.randint(-9, 9), random.randint(-9, 9)
        a2, b2 = random.randint(-9, 9), random.randint(-9, 9)
        
        real_diff = a1 - a2
        imag_diff = b1 - b2
        
        if imag_diff >= 0:
            answer_str = "{0} + {1}i".format(real_diff, imag_diff)
        else:
            answer_str = "{0} - {1}i".format(real_diff, abs(imag_diff))
        
        question_text = "Simplify: ({0} + {1}i) - ({2} + {3}i)".format(a1, b1, a2, b2)
        
        options = [answer_str]
        wrong1 = "{0} + {1}i".format(real_diff + 1, imag_diff)
        wrong2 = "{0} + {1}i".format(real_diff, imag_diff + 1)
        wrong3 = "{0} + {1}i".format(a1 + a2, b1 - b2)  # Common error: adding instead
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Subtract real parts: {0} - {1} = {2}. Subtract imaginary parts: {3} - {4} = {5}. Result: {6}".format(
            a1, a2, real_diff, b1, b2, imag_diff, answer_str
        )
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section2',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 10 questions on multiplication
    for _ in range(10):
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
        
        # (a1 + b1i)(a2 + b2i) = a1*a2 + a1*b2*i + b1*a2*i + b1*b2*i²
        # = (a1*a2 - b1*b2) + (a1*b2 + b1*a2)i
        real_prod = a1 * a2 - b1 * b2
        imag_prod = a1 * b2 + b1 * a2
        
        if imag_prod >= 0:
            answer_str = "{0} + {1}i".format(real_prod, imag_prod)
        else:
            answer_str = "{0} - {1}i".format(real_prod, abs(imag_prod))
        
        question_text = "Multiply: ({0} + {1}i)({2} + {3}i)".format(a1, b1, a2, b2)
        
        options = [answer_str]
        wrong1 = "{0} + {1}i".format(a1 * a2, b1 * b2)  # Forgot to FOIL
        wrong2 = "{0} + {1}i".format(real_prod + b1*b2, imag_prod)  # Forgot i²=-1
        wrong3 = "{0} + {1}i".format(a1 * a2 + b1 * b2, a1 * b2 + b1 * a2)  # Wrong sign on i²
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Use FOIL: ({0})({1}) - ({2})({3}) + [({0})({3}) + ({2})({1})]i = {4}".format(
            a1, a2, b1, b2, answer_str
        )
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section2',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 10 questions on complex conjugate
    for _ in range(10):
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        if b == 0:
            b = random.choice([1, 2, 3, -1, -2, -3])
        
        if b >= 0:
            z_str = "{0} + {1}i".format(a, b)
            conj_str = "{0} - {1}i".format(a, b)
        else:
            z_str = "{0} - {1}i".format(a, abs(b))
            conj_str = "{0} + {1}i".format(a, abs(b))
        
        question_text = "What is the complex conjugate of {0}?".format(z_str)
        
        options = [conj_str]
        wrong1 = "{0} + {1}i".format(-a, b if b >= 0 else abs(b))  # Changed real part
        wrong2 = "{0} + {1}i".format(a, b if b >= 0 else abs(b))  # Didn't change sign
        wrong3 = "-{0}".format(z_str)  # Negated everything
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(conj_str)
        explanation = "The conjugate of a + bi is a - bi. Just change the sign of the imaginary part: {0}".format(conj_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section2',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    print("✓ Generated 40 Section 2 questions")
    return questions


def generate_section3_questions():
    """Section 3: Division and quadratic equations (40 questions)"""
    questions = []
    
    print("Generating Section 3: Division and quadratic equations...")
    
    # 20 questions on division
    for _ in range(20):
        # Keep numbers small for division
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(1, 5), random.randint(1, 5)
        
        # (a1 + b1i) / (a2 + b2i)
        # Multiply by conjugate: (a1 + b1i)(a2 - b2i) / (a2 + b2i)(a2 - b2i)
        # Numerator: (a1*a2 + b1*b2) + (b1*a2 - a1*b2)i
        # Denominator: a2² + b2²
        
        num_real = a1 * a2 + b1 * b2
        num_imag = b1 * a2 - a1 * b2
        denom = a2 * a2 + b2 * b2
        
        # Simplify if possible
        from math import gcd
        if num_imag != 0:
            g = gcd(gcd(abs(num_real), abs(num_imag)), denom)
        else:
            g = gcd(abs(num_real), denom) if num_real != 0 else denom
        
        num_real //= g
        num_imag //= g
        denom //= g
        
        if denom == 1:
            if num_imag >= 0:
                answer_str = "{0} + {1}i".format(num_real, num_imag)
            else:
                answer_str = "{0} - {1}i".format(num_real, abs(num_imag))
        else:
            if num_imag >= 0:
                answer_str = "{0}/{2} + {1}/{2}i".format(num_real, num_imag, denom)
            else:
                answer_str = "{0}/{2} - {1}/{2}i".format(num_real, abs(num_imag), denom)
        
        question_text = "Divide: ({0} + {1}i) / ({2} + {3}i)".format(a1, b1, a2, b2)
        
        options = [answer_str]
        # Generate plausible wrong answers
        wrong1 = "{0} + {1}i".format(num_real + 1, num_imag) if denom == 1 else "{0}/{2} + {1}/{2}i".format(num_real + 1, num_imag, denom)
        wrong2 = "{0}".format(num_real) if num_imag == 0 else "{0}i".format(num_imag)
        wrong3 = "{0} + {1}i".format(a1, b1)  # Didn't divide
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Multiply numerator and denominator by conjugate ({0} - {1}i). Simplify to get {2}.".format(a2, b2, answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section3',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 20 questions on quadratic equations with complex roots
    for _ in range(20):
        # x² + bx + c = 0 where discriminant < 0
        b = random.randint(1, 10)
        # Choose c such that discriminant b² - 4c < 0
        min_c = (b * b // 4) + 1
        c = random.randint(min_c, min_c + 10)
        
        # Quadratic formula: x = (-b ± √(b² - 4c)) / 2
        discriminant = b * b - 4 * c
        
        # √(discriminant) = √(-(4c - b²)) = i√(4c - b²)
        under_root = abs(discriminant)
        
        # Try to simplify √(under_root)
        sqrt_val = int(math.sqrt(under_root))
        if sqrt_val * sqrt_val == under_root:
            if b % 2 == 0 and sqrt_val % 2 == 0:
                answer_str = "{0} ± {1}i".format(-b // 2, sqrt_val // 2)
            else:
                answer_str = "(-{0} ± {1}i) / 2".format(b, sqrt_val)
        else:
            answer_str = "(-{0} ± i√{1}) / 2".format(b, under_root)
        
        question_text = "Solve: x² + {0}x + {1} = 0".format(b, c)
        
        options = [answer_str]
        wrong1 = "{0} ± {1}".format(-b // 2, sqrt_val // 2) if sqrt_val * sqrt_val == under_root else "(-{0} ± √{1}) / 2".format(b, under_root)
        wrong2 = "{0}, {1}".format(-b, -c)  # Just negatives
        wrong3 = "No real solutions"  # Technically true but we want complex
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Using quadratic formula with discriminant {0} < 0, we get complex roots: {1}".format(discriminant, answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section3',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    print("✓ Generated 40 Section 3 questions")
    return questions


def generate_section4_questions():
    """Section 4: The Argand diagram and modulus (40 questions)"""
    questions = []
    
    print("Generating Section 4: The Argand diagram and modulus...")
    
    # 10 questions on plotting complex numbers
    for _ in range(10):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        
        if b >= 0:
            z_str = "{0} + {1}i".format(a, b)
        else:
            z_str = "{0} - {1}i".format(a, abs(b))
        
        answer_str = "({0}, {1})".format(a, b)
        
        question_text = "Where is {0} plotted on the Argand diagram?".format(z_str)
        
        options = [answer_str]
        wrong1 = "({0}, {1})".format(b, a)  # Swapped coordinates
        wrong2 = "({0}, {1})".format(-a, b)  # Wrong sign on real
        wrong3 = "({0}, {1})".format(a, -b)  # Wrong sign on imaginary
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Complex number a + bi is plotted at point (a, b). Real part is x-coordinate, imaginary part is y-coordinate: {0}".format(answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section4',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 30 questions on modulus calculation
    for _ in range(30):
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        
        if a == 0 and b == 0:
            a, b = 3, 4  # Make it non-zero
        
        if b >= 0:
            z_str = "{0} + {1}i".format(a, b)
        else:
            z_str = "{0} - {1}i".format(a, abs(b))
        
        # Calculate modulus: √(a² + b²)
        mod_squared = a * a + b * b
        mod = math.sqrt(mod_squared)
        
        # Check if it's a perfect square
        mod_int = int(mod)
        if mod_int * mod_int == mod_squared:
            answer_str = str(mod_int)
        else:
            answer_str = "√{0}".format(mod_squared)
        
        question_text = "Find the modulus of {0}.".format(z_str)
        
        options = [answer_str]
        wrong1 = str(a + b)  # Just added parts
        wrong2 = str(abs(a) + abs(b))  # Manhattan distance
        if mod_int * mod_int == mod_squared:
            wrong3 = str(mod_int + 1)
        else:
            wrong3 = "√{0}".format(mod_squared + 1)
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "|{0}| = √({1}² + {2}²) = √{3} = {4}".format(z_str, a, abs(b), mod_squared, answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section4',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    print("✓ Generated 40 Section 4 questions")
    return questions


def generate_section5_questions():
    """Section 5: Transformations (40 questions)"""
    questions = []
    
    print("Generating Section 5: Transformations...")
    
    # 15 questions on addition/subtraction (translation)
    for _ in range(15):
        a1, b1 = random.randint(-9, 9), random.randint(-9, 9)
        a2, b2 = random.randint(-9, 9), random.randint(-9, 9)
        
        operation = random.choice(['add', 'subtract'])
        
        if operation == 'add':
            new_a = a1 + a2
            new_b = b1 + b2
            if b1 >= 0:
                z_str = "{0} + {1}i".format(a1, b1)
            else:
                z_str = "{0} - {1}i".format(a1, abs(b1))
            if b2 >= 0:
                w_str = "{0} + {1}i".format(a2, b2)
            else:
                w_str = "{0} - {1}i".format(a2, abs(b2))
            question_text = "If z = {0} is translated by adding {1}, where does it move to?".format(z_str, w_str)
            explanation = "Adding {0} translates by ({1}, {2}). New position: ({3}, {4})".format(w_str, a2, b2, new_a, new_b)
        else:
            new_a = a1 - a2
            new_b = b1 - b2
            if b1 >= 0:
                z_str = "{0} + {1}i".format(a1, b1)
            else:
                z_str = "{0} - {1}i".format(a1, abs(b1))
            if b2 >= 0:
                w_str = "{0} + {1}i".format(a2, b2)
            else:
                w_str = "{0} - {1}i".format(a2, abs(b2))
            question_text = "If z = {0} is translated by subtracting {1}, where does it move to?".format(z_str, w_str)
            explanation = "Subtracting {0} translates by ({1}, {2}). New position: ({3}, {4})".format(w_str, -a2, -b2, new_a, new_b)
        
        answer_str = "({0}, {1})".format(new_a, new_b)
        
        options = [answer_str]
        wrong1 = "({0}, {1})".format(new_a + 1, new_b)
        wrong2 = "({0}, {1})".format(new_a, new_b + 1)
        wrong3 = "({0}, {1})".format(a1, b1)  # No change
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section5',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 15 questions on multiplying by i (90° rotation)
    for _ in range(15):
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        
        if b >= 0:
            z_str = "{0} + {1}i".format(a, b)
        else:
            z_str = "{0} - {1}i".format(a, abs(b))
        
        # i(a + bi) = ai + bi² = -b + ai
        new_a = -b
        new_b = a
        
        answer_str = "({0}, {1})".format(new_a, new_b)
        
        question_text = "If z = {0} is multiplied by i, what are the new coordinates?".format(z_str)
        
        options = [answer_str]
        wrong1 = "({0}, {1})".format(-a, -b)  # 180° rotation
        wrong2 = "({0}, {1})".format(b, -a)  # -90° rotation (or 270°)
        wrong3 = "({0}, {1})".format(a, b)  # No change
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Multiplying by i rotates 90° anti-clockwise: (a, b) → (-b, a). Result: {0}".format(answer_str)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section5',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    # 10 questions on multiplying by real number (scaling)
    for _ in range(10):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        k = random.randint(2, 5)
        
        if b >= 0:
            z_str = "{0} + {1}i".format(a, b)
        else:
            z_str = "{0} - {1}i".format(a, abs(b))
        
        new_a = k * a
        new_b = k * b
        
        answer_str = "({0}, {1})".format(new_a, new_b)
        
        question_text = "If z = {0} is multiplied by {1}, what are the new coordinates?".format(z_str, k)
        
        options = [answer_str]
        wrong1 = "({0}, {1})".format(a + k, b + k)  # Added instead
        wrong2 = "({0}, {1})".format(k * a, b)  # Only scaled real
        wrong3 = "({0}, {1})".format(a, k * b)  # Only scaled imaginary
        options.extend([wrong1, wrong2, wrong3])
        random.shuffle(options)
        
        correct = options.index(answer_str)
        explanation = "Multiplying by {0} scales all coordinates by {0}: ({1}, {2}) → ({3}, {4})".format(k, a, b, new_a, new_b)
        
        questions.append({
            'topic': 'complex_numbers',
            'difficulty': 'section5',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': correct,
            'explanation': explanation
        })
    
    print("✓ Generated 40 Section 5 questions")
    return questions


def add_complex_numbers_to_database():
    """Add all Complex Numbers questions to the database"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("ADDING COMPLEX NUMBERS TOPIC TO DATABASE")
        print("="*70 + "\n")
        
        # Check if complex numbers questions already exist
        existing = Question.query.filter_by(topic='complex_numbers').count()
        
        if existing > 0:
            print("⚠️  WARNING: {0} Complex Numbers questions already exist!".format(existing))
            response = input("Do you want to continue and add more? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted. No questions added.")
                return
        
        print("Generating questions for 5 sections...\n")
        
        section1 = generate_section1_questions()
        section2 = generate_section2_questions()
        section3 = generate_section3_questions()
        section4 = generate_section4_questions()
        section5 = generate_section5_questions()
        
        all_questions = section1 + section2 + section3 + section4 + section5
        
        print("\n" + "="*70)
        print("SUMMARY OF QUESTIONS GENERATED")
        print("="*70)
        print("Section 1 (Basics): {0} questions".format(len(section1)))
        print("Section 2 (Operations): {0} questions".format(len(section2)))
        print("Section 3 (Division & Quadratics): {0} questions".format(len(section3)))
        print("Section 4 (Argand & Modulus): {0} questions".format(len(section4)))
        print("Section 5 (Transformations): {0} questions".format(len(section5)))
        print("="*70)
        print("TOTAL: {0} questions\n".format(len(all_questions)))
        
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
            print("  {0}: {1} questions".format(section, count))
        print("\nTotal Complex Numbers questions: {0}".format(total))
        print("\n✅ Students will now get 25 random questions from 40 per section!")
        print("="*70 + "\n")


if __name__ == "__main__":
    add_complex_numbers_to_database()
