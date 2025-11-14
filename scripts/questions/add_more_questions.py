"""
ADD MORE QUESTIONS FOR BODMAS, SETS, AND FUNCTIONS

This script adds 20 additional questions to each topic/difficulty combination
to bring the total from 20 to 40 questions per topic/difficulty.

Run this ONCE in PythonAnywhere Bash console:
    cd ~/your-project-directory
    python add_more_questions_FIXED.py

This will add:
- BODMAS: 60 new questions (20 per difficulty)
- Sets: 60 new questions (20 per difficulty)
- Functions: 60 new questions (20 per difficulty)
Total: 180 new questions

After running, students will get 25 random questions from the pool of 40.
"""

from app import app, db, Question
import random

def generate_bodmas_questions():
    """Generate additional BODMAS questions (20 per difficulty)"""
    questions = []
    
    # ========== BEGINNER (20 more questions) ==========
    print("Generating BODMAS Beginner questions...")
    
    # 10 questions with brackets
    for _ in range(10):
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 5)
        
        # (a + b) × c
        answer = (a + b) * c
        question_text = "({0} + {1}) × {2} = ?".format(a, b, c)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-5, -3, -2, 2, 3, 5])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Brackets first: {0} + {1} = {2}, then multiply: {2} × {3} = {4}.".format(a, b, a+b, c, answer)
        })
    
    # 10 questions with multiplication before addition
    for _ in range(10):
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 5)
        
        # a + b × c
        answer = a + (b * c)
        question_text = "{0} + {1} × {2} = ?".format(a, b, c)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-5, -3, -2, 2, 3, 5])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'beginner',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Multiplication first: {0} × {1} = {2}, then add: {3} + {2} = {4}.".format(b, c, b*c, a, answer)
        })
    
    print("✓ Generated 20 BODMAS Beginner questions")
    
    # ========== INTERMEDIATE (20 more questions) ==========
    print("Generating BODMAS Intermediate questions...")
    
    # 10 questions with division and multiplication
    for _ in range(10):
        a = random.randint(10, 50)
        b = random.randint(2, 9)
        c = random.randint(2, 9)
        
        # a ÷ b × c
        answer = (a // b) * c
        question_text = "{0} ÷ {1} × {2} = ?".format(a, b, c)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-10, -5, -3, 3, 5, 10])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Left to right: {0} ÷ {1} = {2}, then {2} × {3} = {4}.".format(a, b, a//b, c, answer)
        })
    
    # 10 questions with brackets and multiple operations
    for _ in range(10):
        a = random.randint(5, 15)
        b = random.randint(2, 9)
        c = random.randint(2, 9)
        d = random.randint(1, 5)
        
        # (a + b) × c - d
        answer = (a + b) * c - d
        question_text = "({0} + {1}) × {2} - {3} = ?".format(a, b, c, d)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-10, -5, -3, 3, 5, 10])
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Brackets: {0} + {1} = {2}, multiply: {2} × {3} = {4}, subtract: {4} - {5} = {6}.".format(a, b, a+b, c, (a+b)*c, d, answer)
        })
    
    print("✓ Generated 20 BODMAS Intermediate questions")
    
    # ========== ADVANCED (20 more questions) ==========
    print("Generating BODMAS Advanced questions...")
    
    # 10 questions with nested brackets
    for _ in range(10):
        a = random.randint(5, 15)
        b = random.randint(2, 9)
        c = random.randint(2, 9)
        d = random.randint(1, 5)
        
        # [(a + b) × c] - d
        answer = (a + b) * c - d
        question_text = "[({0} + {1}) × {2}] - {3} = ?".format(a, b, c, d)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-15, -10, -5, 5, 10, 15])
            if wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Innermost brackets: {0} + {1} = {2}, multiply: {2} × {3} = {4}, subtract: {4} - {5} = {6}.".format(a, b, a+b, c, (a+b)*c, d, answer)
        })
    
    # 10 questions with all operations
    for _ in range(10):
        a = random.randint(10, 30)
        b = random.randint(2, 5)
        c = random.randint(2, 5)
        d = random.randint(1, 5)
        e = random.randint(1, 5)
        
        # a + b × c - d ÷ e (assuming d is divisible by e)
        d = d * e  # Make it divisible
        answer = a + (b * c) - (d // e)
        question_text = "{0} + {1} × {2} - {3} ÷ {4} = ?".format(a, b, c, d, e)
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-15, -10, -5, 5, 10, 15])
            if wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'bodmas',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Multiply and divide first: {0}×{1}={2}, {3}÷{4}={5}. Then: {6}+{2}-{5} = {7}.".format(b, c, b*c, d, e, d//e, a, answer)
        })
    
    print("✓ Generated 20 BODMAS Advanced questions")
    
    return questions


def generate_sets_questions():
    """Generate additional Sets questions (20 per difficulty)"""
    questions = []
    
    # ========== BEGINNER (20 more questions) ==========
    print("Generating Sets Beginner questions...")
    
    for _ in range(20):
        set_type = random.choice(['union', 'intersection', 'difference', 'element'])
        
        if set_type == 'union':
            a_elements = random.sample(range(1, 15), k=random.randint(3, 5))
            b_elements = random.sample(range(1, 15), k=random.randint(3, 5))
            union = sorted(list(set(a_elements) | set(b_elements)))
            
            a_str = ', '.join(map(str, sorted(a_elements)))
            b_str = ', '.join(map(str, sorted(b_elements)))
            question_text = "A = {" + a_str + "} and B = {" + b_str + "}. Find A ∪ B."
            answer_str = '{' + ', '.join(map(str, union)) + '}'
            
            options = [answer_str]
            while len(options) < 4:
                wrong_set = random.sample(range(1, 20), k=len(union))
                wrong_str = '{' + ', '.join(map(str, sorted(wrong_set))) + '}'
                if wrong_str not in options:
                    options.append(wrong_str)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'sets',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer_str),
                'explanation': "Union (∪) combines all elements: " + answer_str
            })
        
        elif set_type == 'intersection':
            common = random.sample(range(1, 10), k=random.randint(2, 3))
            a_only = random.sample(range(10, 20), k=random.randint(2, 3))
            b_only = random.sample(range(20, 30), k=random.randint(2, 3))
            
            a_elements = sorted(common + a_only)
            b_elements = sorted(common + b_only)
            intersection = sorted(common)
            
            a_str = ', '.join(map(str, a_elements))
            b_str = ', '.join(map(str, b_elements))
            question_text = "A = {" + a_str + "} and B = {" + b_str + "}. Find A ∩ B."
            answer_str = '{' + ', '.join(map(str, intersection)) + '}'
            
            options = [answer_str]
            while len(options) < 4:
                wrong_set = random.sample(range(1, 30), k=len(intersection) + random.randint(0, 2))
                wrong_str = '{' + ', '.join(map(str, sorted(wrong_set))) + '}'
                if wrong_str not in options:
                    options.append(wrong_str)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'sets',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer_str),
                'explanation': "Intersection (∩) finds common elements: " + answer_str
            })
        
        elif set_type == 'difference':
            common = random.sample(range(1, 10), k=random.randint(2, 3))
            a_only = random.sample(range(10, 20), k=random.randint(2, 4))
            b_only = random.sample(range(20, 30), k=random.randint(2, 3))
            
            a_elements = sorted(common + a_only)
            b_elements = sorted(common + b_only)
            difference = sorted(a_only)
            
            a_str = ', '.join(map(str, a_elements))
            b_str = ', '.join(map(str, b_elements))
            question_text = "A = {" + a_str + "} and B = {" + b_str + "}. Find A - B."
            answer_str = '{' + ', '.join(map(str, difference)) + '}'
            
            options = [answer_str]
            while len(options) < 4:
                wrong_set = random.sample(range(1, 30), k=max(1, len(difference) + random.randint(-1, 2)))
                wrong_str = '{' + ', '.join(map(str, sorted(wrong_set))) + '}'
                if wrong_str not in options and len(wrong_set) > 0:
                    options.append(wrong_str)
            
            while len(options) < 4:
                options.append('{}')
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'sets',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer_str),
                'explanation': "Difference (A - B) finds elements in A but not in B: " + answer_str
            })
        
        else:  # element check
            set_elements = sorted(random.sample(range(1, 20), k=random.randint(4, 6)))
            check_element = random.choice([random.choice(set_elements), random.randint(20, 30)])
            is_member = check_element in set_elements
            
            set_str = ', '.join(map(str, set_elements))
            question_text = "Is {0} ∈ ".format(check_element) + "{" + set_str + "}?"
            answer = "Yes" if is_member else "No"
            
            options = ["Yes", "No", "Cannot determine", "Insufficient data"]
            random.shuffle(options)
            
            questions.append({
                'topic': 'sets',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer),
                'explanation': "{0}, {1} {2} in the set.".format(answer, check_element, 'is' if is_member else 'is not')
            })
    
    print("✓ Generated 20 Sets Beginner questions")
    
    # ========== INTERMEDIATE (20 more questions) ==========
    print("Generating Sets Intermediate questions...")
    
    for _ in range(20):
        a_elements = random.sample(range(1, 20), k=random.randint(4, 6))
        b_elements = random.sample(range(1, 20), k=random.randint(4, 6))
        c_elements = random.sample(range(1, 20), k=random.randint(4, 6))
        
        operation = random.choice(['(A ∪ B) ∩ C', 'A ∪ (B ∩ C)', '(A ∩ B) ∪ C', 'A - (B ∪ C)'])
        
        a_set = set(a_elements)
        b_set = set(b_elements)
        c_set = set(c_elements)
        
        if operation == '(A ∪ B) ∩ C':
            result = (a_set | b_set) & c_set
        elif operation == 'A ∪ (B ∩ C)':
            result = a_set | (b_set & c_set)
        elif operation == '(A ∩ B) ∪ C':
            result = (a_set & b_set) | c_set
        else:  # 'A - (B ∪ C)'
            result = a_set - (b_set | c_set)
        
        answer_str = '{' + ', '.join(map(str, sorted(result))) + '}' if result else '{}'
        
        a_str = ', '.join(map(str, sorted(a_elements)))
        b_str = ', '.join(map(str, sorted(b_elements)))
        c_str = ', '.join(map(str, sorted(c_elements)))
        question_text = "A = {" + a_str + "}, B = {" + b_str + "}, C = {" + c_str + "}. Find " + operation + "."
        
        options = [answer_str]
        while len(options) < 4:
            if result:
                wrong_set = random.sample(range(1, 25), k=random.randint(max(1, len(result)-1), len(result)+3))
            else:
                wrong_set = random.sample(range(1, 25), k=random.randint(1, 3))
            wrong_str = '{' + ', '.join(map(str, sorted(wrong_set))) + '}' if wrong_set else '{}'
            if wrong_str not in options:
                options.append(wrong_str)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'sets',
            'difficulty': 'intermediate',
            'question_text': question_text,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_answer': options.index(answer_str),
            'explanation': "Following BODMAS for sets, " + operation + " = " + answer_str
        })
    
    print("✓ Generated 20 Sets Intermediate questions")
    
    # ========== ADVANCED (20 more questions) ==========
    print("Generating Sets Advanced questions...")
    
    for _ in range(20):
        total = random.randint(50, 100)
        only_a = random.randint(10, 20)
        only_b = random.randint(10, 20)
        both = random.randint(5, 15)
        neither = total - (only_a + only_b + both)
        
        if neither < 0:
            neither = random.randint(5, 15)
            total = only_a + only_b + both + neither
        
        question_types = [
            ('both', both),
            ('only A', only_a),
            ('only B', only_b),
            ('neither', neither),
            ('at least one', only_a + only_b + both)
        ]
        
        q_type, answer = random.choice(question_types)
        
        question_text = "In a class of {0} students, {1} study Math, {2} study Science, and {3} study both. How many students study {4}?".format(
            total, only_a + both, only_b + both, both, q_type
        )
        
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.choice([-10, -5, -3, 3, 5, 10])
            if 0 <= wrong <= total and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        
        questions.append({
            'topic': 'sets',
            'difficulty': 'advanced',
            'question_text': question_text,
            'option_a': str(options[0]),
            'option_b': str(options[1]),
            'option_c': str(options[2]),
            'option_d': str(options[3]),
            'correct_answer': options.index(answer),
            'explanation': "Using Venn diagram logic: {0} students study {1}.".format(answer, q_type)
        })
    
    print("✓ Generated 20 Sets Advanced questions")
    
    return questions


def generate_functions_questions():
    """Generate additional Functions questions (20 per difficulty)"""
    questions = []
    
    # ========== BEGINNER (20 more questions) ==========
    print("Generating Functions Beginner questions...")
    
    for _ in range(20):
        func_type = random.choice(['linear', 'evaluate', 'inverse_simple'])
        
        if func_type == 'linear':
            a = random.randint(2, 9)
            b = random.randint(1, 9)
            x = random.randint(1, 9)
            
            answer = a * x + b
            question_text = "If f(x) = {0}x + {1}, what is f({2})?".format(a, b, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-5, -3, -2, 2, 3, 5])
                if wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "f({0}) = {1}×{0} + {2} = {3} + {2} = {4}".format(x, a, b, a*x, answer)
            })
        
        elif func_type == 'evaluate':
            a = random.randint(2, 9)
            b = random.randint(1, 9)
            x = random.randint(1, 9)
            
            answer = a * x - b
            question_text = "If g(x) = {0}x - {1}, find g({2}).".format(a, b, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-5, -3, -2, 2, 3, 5])
                if wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "g({0}) = {1}×{0} - {2} = {3} - {2} = {4}".format(x, a, b, a*x, answer)
            })
        
        else:  # inverse_simple
            a = random.randint(2, 9)
            x = random.randint(10, 50)
            
            answer = x // a
            question_text = "If f(x) = {0}x, and f(n) = {1}, what is n?".format(a, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-3, -2, -1, 1, 2, 3])
                if wrong > 0 and wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'beginner',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "If f(n) = {0}, then {1}n = {0}, so n = {0}/{1} = {2}".format(x, a, answer)
            })
    
    print("✓ Generated 20 Functions Beginner questions")
    
    # ========== INTERMEDIATE (20 more questions) ==========
    print("Generating Functions Intermediate questions...")
    
    for _ in range(20):
        func_type = random.choice(['quadratic', 'composite', 'find_function'])
        
        if func_type == 'quadratic':
            a = random.randint(1, 5)
            b = random.randint(1, 9)
            x = random.randint(1, 5)
            
            answer = a * x * x + b
            question_text = "If f(x) = {0}x² + {1}, calculate f({2}).".format(a, b, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-10, -5, -3, 3, 5, 10])
                if wrong > 0 and wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'intermediate',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "f({0}) = {1}×{0}² + {2} = {1}×{3} + {2} = {4} + {2} = {5}".format(x, a, b, x*x, a*x*x, answer)
            })
        
        elif func_type == 'composite':
            a = random.randint(2, 5)
            b = random.randint(2, 5)
            x = random.randint(1, 5)
            
            inner = x + b
            answer = a * inner
            
            question_text = "If f(x) = {0}x and g(x) = x + {1}, find f(g({2})).".format(a, b, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-10, -5, -3, 3, 5, 10])
                if wrong > 0 and wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'intermediate',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "g({0}) = {0} + {1} = {2}, then f({2}) = {3}×{2} = {4}".format(x, b, inner, a, answer)
            })
        
        else:  # find_function
            x1, y1 = random.randint(1, 5), random.randint(10, 30)
            x2, y2 = random.randint(6, 10), random.randint(40, 70)
            
            m = (y2 - y1) // (x2 - x1)
            c = y1 - m * x1
            
            answer_str = "f(x) = {0}x + {1}".format(m, c)
            
            question_text = "A function passes through ({0}, {1}) and ({2}, {3}). Which function is it?".format(x1, y1, x2, y2)
            
            options = [answer_str]
            while len(options) < 4:
                wrong_m = m + random.choice([-2, -1, 1, 2])
                wrong_c = c + random.choice([-5, -3, 3, 5])
                wrong_str = "f(x) = {0}x + {1}".format(wrong_m, wrong_c)
                if wrong_str not in options:
                    options.append(wrong_str)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'intermediate',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer_str),
                'explanation': "Using two points to find the linear function: " + answer_str
            })
    
    print("✓ Generated 20 Functions Intermediate questions")
    
    # ========== ADVANCED (20 more questions) ==========
    print("Generating Functions Advanced questions...")
    
    for _ in range(20):
        func_type = random.choice(['inverse', 'composite_complex', 'piecewise'])
        
        if func_type == 'inverse':
            a = random.randint(2, 9)
            b = random.randint(1, 9)
            
            answer_str = "f⁻¹(x) = (x - {0})/{1}".format(b, a)
            
            question_text = "If f(x) = {0}x + {1}, what is f⁻¹(x)?".format(a, b)
            
            options = [answer_str]
            while len(options) < 4:
                wrong_a = a + random.choice([-2, -1, 1, 2])
                wrong_b = b + random.choice([-3, -2, 2, 3])
                wrong_str = "f⁻¹(x) = (x - {0})/{1}".format(wrong_b, wrong_a)
                if wrong_str not in options and wrong_a != 0:
                    options.append(wrong_str)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'advanced',
                'question_text': question_text,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_answer': options.index(answer_str),
                'explanation': "Inverse: swap x and y, solve for y: " + answer_str
            })
        
        elif func_type == 'composite_complex':
            a = random.randint(2, 5)
            b = random.randint(1, 5)
            c = random.randint(2, 5)
            x = random.randint(1, 3)
            
            inner = a * x + b
            answer = c * inner
            
            question_text = "If f(x) = {0}x + {1} and g(x) = {2}x, find g(f({3})).".format(a, b, c, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-15, -10, -5, 5, 10, 15])
                if wrong > 0 and wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'advanced',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "f({0}) = {1}×{0} + {2} = {3}, then g({3}) = {4}×{3} = {5}".format(x, a, b, inner, c, answer)
            })
        
        else:  # piecewise
            a = random.randint(2, 5)
            b = random.randint(2, 5)
            threshold = random.randint(5, 10)
            x = random.choice([threshold - 2, threshold + 2])
            
            if x < threshold:
                answer = a * x
                question_text = "f(x) = {0}x if x < {1}, and f(x) = {2}x if x ≥ {1}. Find f({3}).".format(a, threshold, b, x)
            else:
                answer = b * x
                question_text = "f(x) = {0}x if x < {1}, and f(x) = {2}x if x ≥ {1}. Find f({3}).".format(a, threshold, b, x)
            
            options = [answer]
            while len(options) < 4:
                wrong = answer + random.choice([-10, -5, 5, 10])
                if wrong > 0 and wrong not in options:
                    options.append(wrong)
            
            random.shuffle(options)
            
            questions.append({
                'topic': 'functions',
                'difficulty': 'advanced',
                'question_text': question_text,
                'option_a': str(options[0]),
                'option_b': str(options[1]),
                'option_c': str(options[2]),
                'option_d': str(options[3]),
                'correct_answer': options.index(answer),
                'explanation': "Since {0} {1} {2}, use {3} part: f({0}) = {4}".format(
                    x, '<' if x < threshold else '≥', threshold, 
                    'first' if x < threshold else 'second', answer
                )
            })
    
    print("✓ Generated 20 Functions Advanced questions")
    
    return questions


def add_questions_to_database():
    """Add all new questions to the database"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("ADDING MORE QUESTIONS TO DATABASE")
        print("="*70 + "\n")
        
        bodmas_count = Question.query.filter_by(topic='bodmas').count()
        sets_count = Question.query.filter_by(topic='sets').count()
        functions_count = Question.query.filter_by(topic='functions').count()
        
        print("Current question counts:")
        print("  BODMAS: {0}".format(bodmas_count))
        print("  Sets: {0}".format(sets_count))
        print("  Functions: {0}".format(functions_count))
        print()
        
        print("Generating new questions...\n")
        
        bodmas_questions = generate_bodmas_questions()
        sets_questions = generate_sets_questions()
        functions_questions = generate_functions_questions()
        
        all_questions = bodmas_questions + sets_questions + functions_questions
        
        print("\nTotal new questions generated: {0}".format(len(all_questions)))
        print("  BODMAS: {0}".format(len(bodmas_questions)))
        print("  Sets: {0}".format(len(sets_questions)))
        print("  Functions: {0}".format(len(functions_questions)))
        print()
        
        print("Adding questions to database...")
        for q_data in all_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        
        bodmas_new = Question.query.filter_by(topic='bodmas').count()
        sets_new = Question.query.filter_by(topic='sets').count()
        functions_new = Question.query.filter_by(topic='functions').count()
        
        print("\n" + "="*70)
        print("✅ QUESTIONS ADDED SUCCESSFULLY!")
        print("="*70)
        print("\nNew question counts:")
        print("  BODMAS: {0} (was {1}, added {2})".format(bodmas_new, bodmas_count, bodmas_new - bodmas_count))
        print("  Sets: {0} (was {1}, added {2})".format(sets_new, sets_count, sets_new - sets_count))
        print("  Functions: {0} (was {1}, added {2})".format(functions_new, functions_count, functions_new - functions_count))
        print()
        
        for topic in ['bodmas', 'sets', 'functions']:
            print("\n{0} breakdown:".format(topic.upper()))
            for diff in ['beginner', 'intermediate', 'advanced']:
                count = Question.query.filter_by(topic=topic, difficulty=diff).count()
                print("  {0}: {1} questions".format(diff.capitalize(), count))
        
        print("\n✅ Students will now get 25 random questions from 40 available!")
        print("="*70 + "\n")


if __name__ == "__main__":
    add_questions_to_database()
