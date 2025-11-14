"""
Script to generate Surds questions for the math app
Based on Corbett Maths surds worksheet
"""
import random
import math

def simplify_surd(n):
    """Simplify √n into a√b form where b has no perfect square factors"""
    if n <= 0:
        return (0, 0)
    
    coefficient = 1
    remaining = n
    
    # Find perfect square factors
    for i in range(int(math.sqrt(n)), 1, -1):
        square = i * i
        while remaining % square == 0:
            coefficient *= i
            remaining //= square
    
    return (coefficient, remaining)

def format_surd(coeff, radical):
    """Format a surd for display"""
    if radical == 1:
        return str(coeff)
    elif coeff == 1:
        return f"√{radical}"
    else:
        return f"{coeff}√{radical}"

def generate_beginner_questions():
    """Generate beginner level surds questions (basic multiplication, division, simplification)"""
    questions = []
    
    # Type 1: Basic multiplication √a × √b
    for _ in range(15):
        a = random.choice([2, 3, 5, 6, 7, 10, 11])
        b = random.choice([2, 3, 5, 6, 7, 10, 11])
        product = a * b
        coeff, rad = simplify_surd(product)
        correct_answer = format_surd(coeff, rad)
        
        # Generate wrong options
        wrong_options = []
        wrong_options.append(f"√{a + b}")  # Common mistake: add under sqrt
        wrong_options.append(f"√{a}√{b}")  # Don't simplify
        if coeff > 1:
            wrong_options.append(f"{coeff + 1}√{rad}")  # Off by one
        else:
            wrong_options.append(f"√{product + 1}")
        
        options = [correct_answer] + wrong_options[:3]
        random.shuffle(options)
        
        explanation = f"√{a} × √{b} = √({a} × {b}) = √{product}"
        if rad != 1:
            explanation += f" = {correct_answer}"
        
        questions.append({
            "topic": "surds",
            "difficulty": "beginner",
            "question": f"Simplify: √{a} × √{b}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": explanation
        })
    
    # Type 2: Basic division √a ÷ √b
    for _ in range(10):
        pairs = [(10, 5), (21, 7), (30, 6), (8, 2), (80, 5), (56, 7), (15, 3), (72, 8)]
        a, b = random.choice(pairs)
        quotient = a // b
        coeff, rad = simplify_surd(quotient)
        correct_answer = format_surd(coeff, rad)
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"√{a - b}")
        options.append(f"√{a}÷√{b}")
        options.append(str(a // b) if quotient != int(correct_answer.replace('√', '').replace('1', '')) else f"√{quotient + 1}")
        
        random.shuffle(options)
        
        explanation = f"√{a} ÷ √{b} = √({a} ÷ {b}) = √{quotient}"
        if rad != 1:
            explanation += f" = {correct_answer}"
        
        questions.append({
            "topic": "surds",
            "difficulty": "beginner",
            "question": f"Simplify: √{a} ÷ √{b}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": explanation
        })
    
    # Type 3: Simplify √n
    for _ in range(15):
        values = [8, 12, 18, 20, 24, 27, 32, 45, 48, 50, 63, 72, 75, 80, 98]
        n = random.choice(values)
        coeff, rad = simplify_surd(n)
        correct_answer = format_surd(coeff, rad)
        
        # Generate wrong options
        options = [correct_answer]
        if coeff > 1:
            options.append(f"{coeff - 1}√{rad}")
            options.append(f"{coeff}√{rad + 1}")
            options.append(f"{coeff + 1}√{rad}")
        else:
            options.append(f"√{n}")
            options.append(f"2√{n//2}")
            options.append(str(int(math.sqrt(n))))
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "beginner",
            "question": f"Simplify: √{n}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"√{n} = √({coeff}² × {rad}) = {coeff}√{rad}" if rad != 1 else f"√{n} = {coeff}"
        })
    
    return questions

def generate_intermediate_questions():
    """Generate intermediate level surds questions (operations, addition/subtraction)"""
    questions = []
    
    # Type 1: Multiplication with coefficients: a√b × c√d
    for _ in range(15):
        a = random.randint(2, 5)
        b = random.choice([2, 3, 5, 6])
        c = random.randint(2, 4)
        d = random.choice([2, 3, 5, 6])
        
        prod_coeff = a * c
        prod_rad = b * d
        final_coeff, final_rad = simplify_surd(prod_rad)
        final_coeff *= prod_coeff
        correct_answer = format_surd(final_coeff, final_rad)
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"{prod_coeff}√{prod_rad}")  # Don't simplify
        options.append(f"{a * c - 1}√{b * d}")  # Off by one on coefficient
        options.append(f"{a + c}√{b * d}")  # Add instead of multiply coefficients
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "intermediate",
            "question": f"Simplify: {a}√{b} × {c}√{d}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"{a}√{b} × {c}√{d} = {prod_coeff}√{prod_rad} = {correct_answer}"
        })
    
    # Type 2: Addition/Subtraction of like surds
    for _ in range(12):
        # Ensure we're adding/subtracting like surds
        rad = random.choice([2, 3, 5, 6, 7])
        a = random.randint(2, 6)
        b = random.randint(1, 5)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            result_coeff = a + b
            op_word = "add"
        else:
            result_coeff = a - b
            op_word = "subtract"
        
        # Need to present these as simplified forms like √8 + √18
        inner_a = a * a * rad  # This will simplify to a√rad
        inner_b = b * b * rad  # This will simplify to b√rad
        
        correct_answer = format_surd(result_coeff, rad)
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"√{inner_a} {operation} √{inner_b}")  # Don't simplify
        options.append(format_surd(result_coeff + 1, rad))
        options.append(format_surd(a * b if operation == '+' else abs(a - b - 1), rad))
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "intermediate",
            "question": f"Simplify: √{inner_a} {operation} √{inner_b}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"√{inner_a} = {a}√{rad} and √{inner_b} = {b}√{rad}, so √{inner_a} {operation} √{inner_b} = {correct_answer}"
        })
    
    # Type 3: Expanding √a(√b + c)
    for _ in range(13):
        a = random.choice([2, 3, 5, 6])
        b = random.choice([2, 3, 5, 6, 8])
        c = random.randint(2, 7)
        
        # √a × √b
        prod1 = a * b
        coeff1, rad1 = simplify_surd(prod1)
        term1 = format_surd(coeff1, rad1)
        
        # √a × c = c√a
        term2 = f"{c}√{a}"
        
        correct_answer = f"{term1} + {term2}"
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"√{a}√{b} + {c}")  # Don't multiply first term
        options.append(f"{coeff1}√{rad1} + {c}")  # Forget the √a in second term
        options.append(f"√{a * b} + {c}√{a}")  # Don't simplify first term
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "intermediate",
            "question": f"Expand: √{a}(√{b} + {c})",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"√{a}(√{b} + {c}) = √{a} × √{b} + √{a} × {c} = {term1} + {term2}"
        })
    
    return questions

def generate_advanced_questions():
    """Generate advanced level surds questions (expansion, rationalization)"""
    questions = []
    
    # Type 1: Expanding (a + √b)(c + √d)
    for _ in range(12):
        a = random.randint(1, 5)
        b = random.choice([2, 3, 5, 7])
        c = random.randint(1, 5)
        d = random.choice([2, 3, 5, 7])
        
        # (a + √b)(c + √d) = ac + a√d + c√b + √(bd)
        term1 = a * c  # constant term
        term2_coeff = a
        term2_rad = d
        term3_coeff = c
        term3_rad = b
        bd = b * d
        term4_coeff, term4_rad = simplify_surd(bd)
        
        # Format answer
        terms = [str(term1)]
        if term2_coeff > 1:
            terms.append(f"{term2_coeff}√{term2_rad}")
        else:
            terms.append(f"√{term2_rad}")
        if term3_coeff > 1:
            terms.append(f"{term3_coeff}√{term3_rad}")
        else:
            terms.append(f"√{term3_rad}")
        
        if term4_rad == 1:
            terms.append(str(term4_coeff))
        elif term4_coeff > 1:
            terms.append(f"{term4_coeff}√{term4_rad}")
        else:
            terms.append(f"√{term4_rad}")
        
        correct_answer = " + ".join(terms)
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"{term1 + 1} + {term2_coeff}√{term2_rad} + {term3_coeff}√{term3_rad} + {format_surd(term4_coeff, term4_rad)}")
        options.append(f"{term1} + √{term2_rad + term3_rad} + {format_surd(term4_coeff, term4_rad)}")
        options.append(f"{a + c} + {format_surd(term2_coeff + term3_coeff, b)}")
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "advanced",
            "question": f"Expand: ({a} + √{b})({c} + √{d})",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"Use FOIL: ({a})({c}) + ({a})(√{d}) + (√{b})({c}) + (√{b})(√{d}) = {correct_answer}"
        })
    
    # Type 2: Difference of squares (a + √b)(a - √b) = a² - b
    for _ in range(10):
        a = random.randint(2, 8)
        b = random.choice([2, 3, 5, 6, 7])
        
        result = a * a - b
        correct_answer = str(result)
        
        # Generate wrong options
        options = [correct_answer]
        options.append(str(result + 1))
        options.append(str(result - 1))
        options.append(str(a * a + b))  # Wrong sign
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "advanced",
            "question": f"Expand: ({a} + √{b})({a} - √{b})",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"This is a difference of squares: ({a})² - (√{b})² = {a * a} - {b} = {result}"
        })
    
    # Type 3: Rationalizing denominators 1/√a
    for _ in range(10):
        a = random.choice([2, 3, 5, 6, 7, 10])
        
        correct_answer = f"√{a}/{a}"
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"1/√{a}")  # Don't rationalize
        options.append(f"√{a}")  # Missing denominator
        options.append(f"1/{a}")  # Wrong
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "advanced",
            "question": f"Rationalize the denominator: 1/√{a}",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"Multiply by √{a}/√{a}: (1 × √{a})/(√{a} × √{a}) = √{a}/{a}"
        })
    
    # Type 4: Rationalizing a/(b + √c) using conjugate
    for _ in range(8):
        a = random.randint(2, 6)
        b = random.randint(1, 4)
        c = random.choice([2, 3, 5])
        
        # Multiply by conjugate (b - √c)/(b - √c)
        # Result: a(b - √c)/(b² - c)
        denominator = b * b - c
        
        if denominator == 1:
            if a == 1:
                correct_answer = f"{b} - √{c}"
            else:
                correct_answer = f"{a * b} - {a}√{c}"
        else:
            if a == 1:
                correct_answer = f"({b} - √{c})/{denominator}"
            else:
                correct_answer = f"({a * b} - {a}√{c})/{denominator}"
        
        # Generate wrong options
        options = [correct_answer]
        options.append(f"{a}/({b} + √{c})")  # Don't rationalize
        options.append(f"{a * b}/{denominator}")  # Forget surd term
        options.append(f"({a * b} + {a}√{c})/{denominator}")  # Wrong sign
        
        random.shuffle(options)
        
        questions.append({
            "topic": "surds",
            "difficulty": "advanced",
            "question": f"Rationalize the denominator: {a}/({b} + √{c})",
            "options": options,
            "correct": options.index(correct_answer),
            "explanation": f"Multiply by conjugate ({b} - √{c})/({b} - √{c}): " +
                          f"{a}({b} - √{c})/(({b})² - (√{c})²) = {correct_answer}"
        })
    
    return questions

def generate_all_questions():
    """Generate all surds questions"""
    all_questions = []
    
    print("Generating beginner questions...")
    beginner = generate_beginner_questions()
    all_questions.extend(beginner)
    print(f"Generated {len(beginner)} beginner questions")
    
    print("Generating intermediate questions...")
    intermediate = generate_intermediate_questions()
    all_questions.extend(intermediate)
    print(f"Generated {len(intermediate)} intermediate questions")
    
    print("Generating advanced questions...")
    advanced = generate_advanced_questions()
    all_questions.extend(advanced)
    print(f"Generated {len(advanced)} advanced questions")
    
    print(f"\nTotal questions generated: {len(all_questions)}")
    return all_questions

if __name__ == "__main__":
    questions = generate_all_questions()
    
    # Print sample questions
    print("\n" + "="*80)
    print("SAMPLE QUESTIONS")
    print("="*80)
    
    for difficulty in ['beginner', 'intermediate', 'advanced']:
        print(f"\n{difficulty.upper()} LEVEL:")
        samples = [q for q in questions if q['difficulty'] == difficulty][:3]
        for i, q in enumerate(samples, 1):
            print(f"\n{i}. {q['question']}")
            for j, opt in enumerate(q['options']):
                marker = "✓" if j == q['correct'] else " "
                print(f"   {marker} {chr(65+j)}) {opt}")
            print(f"   Explanation: {q['explanation']}")
