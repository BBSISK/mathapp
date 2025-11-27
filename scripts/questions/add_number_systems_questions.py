"""
Script to add Number Systems questions to the AgentMath.app app.

Beginner: Natural numbers, Integers, Prime numbers
Intermediate: More complex versions + Rounding and Significant figures
Advanced: Temperature conversions + More complex versions

All calculations are simple and don't require a calculator.
"""

from app import app, db, Question
import random

def add_number_systems_questions():
    with app.app_context():
        # Clear existing number_systems questions
        Question.query.filter_by(topic='number_systems').delete()
        
        questions = []
        
        # ==================== BEGINNER LEVEL ====================
        # Natural Numbers (1, 2, 3, 4, ...)
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which of the following is a natural number?',
                'options': ['0', '-5', '3', '1.5'],
                'correct': 2,
                'explanation': 'Natural numbers are positive counting numbers: 1, 2, 3, 4, ... They do not include zero, negative numbers, or fractions.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is the smallest natural number?',
                'options': ['0', '1', '-1', '2'],
                'correct': 1,
                'explanation': 'The smallest natural number is 1. Natural numbers start from 1 and go upward (1, 2, 3, 4, ...).'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which set does the number 5 belong to?',
                'options': ['Negative integers', 'Natural numbers', 'Fractions', 'None of these'],
                'correct': 1,
                'explanation': '5 is a natural number because it is a positive counting number.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 100 a natural number?',
                'options': ['Yes', 'No', 'Only if it is positive', 'Only if it is even'],
                'correct': 0,
                'explanation': 'Yes, 100 is a natural number. All positive whole numbers are natural numbers.'
            },
            
            # Integers (..., -2, -1, 0, 1, 2, ...)
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which of the following is an integer?',
                'options': ['2.5', '-7', '1/2', 'π'],
                'correct': 1,
                'explanation': 'Integers are whole numbers that can be positive, negative, or zero. -7 is an integer.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 0 an integer?',
                'options': ['Yes', 'No', 'Only when positive', 'Only when negative'],
                'correct': 0,
                'explanation': 'Yes, 0 is an integer. Integers include all positive numbers, negative numbers, and zero.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which number is NOT an integer?',
                'options': ['-5', '0', '3.2', '8'],
                'correct': 2,
                'explanation': '3.2 is not an integer because it has a decimal part. Integers must be whole numbers.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is -3 + 5?',
                'options': ['-8', '-2', '2', '8'],
                'correct': 2,
                'explanation': 'When adding integers with different signs, subtract the smaller from the larger: 5 - 3 = 2, and take the sign of the larger number (positive).'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is -2 - 3?',
                'options': ['-5', '-1', '1', '5'],
                'correct': 0,
                'explanation': 'Subtracting 3 from -2 means moving 3 more units to the left on the number line: -2 - 3 = -5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is 4 × (-2)?',
                'options': ['-8', '-6', '6', '8'],
                'correct': 0,
                'explanation': 'When multiplying a positive number by a negative number, the result is negative: 4 × (-2) = -8.'
            },
            
            # Prime Numbers
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which of the following is a prime number?',
                'options': ['4', '6', '7', '9'],
                'correct': 2,
                'explanation': '7 is a prime number because it can only be divided by 1 and itself. The others have more divisors.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 2 a prime number?',
                'options': ['Yes', 'No', 'Only when doubled', 'Only when squared'],
                'correct': 0,
                'explanation': 'Yes, 2 is the only even prime number. It can only be divided by 1 and 2.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which is NOT a prime number?',
                'options': ['2', '3', '4', '5'],
                'correct': 2,
                'explanation': '4 is not prime because it can be divided by 1, 2, and 4. Prime numbers have exactly two factors.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is the smallest prime number?',
                'options': ['0', '1', '2', '3'],
                'correct': 2,
                'explanation': '2 is the smallest prime number. 1 is not considered prime, and 0 is not prime.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 1 a prime number?',
                'options': ['Yes', 'No', 'Sometimes', 'It depends'],
                'correct': 1,
                'explanation': 'No, 1 is not considered a prime number. Prime numbers must have exactly two distinct factors: 1 and itself. The number 1 only has one factor.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'How many prime numbers are there between 1 and 10?',
                'options': ['3', '4', '5', '6'],
                'correct': 1,
                'explanation': 'There are 4 prime numbers between 1 and 10: 2, 3, 5, and 7.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which number below is a prime number?',
                'options': ['15', '17', '18', '20'],
                'correct': 1,
                'explanation': '17 is prime. It can only be divided evenly by 1 and 17. The others have multiple factors.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 9 a prime number?',
                'options': ['Yes', 'No', 'Only when odd', 'Only when positive'],
                'correct': 1,
                'explanation': 'No, 9 is not prime. It can be divided by 1, 3, and 9, so it has more than two factors.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'All prime numbers greater than 2 are:',
                'options': ['Even', 'Odd', 'Negative', 'Fractions'],
                'correct': 1,
                'explanation': 'All prime numbers greater than 2 are odd. If they were even, they would be divisible by 2.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which is the next prime number after 5?',
                'options': ['6', '7', '8', '9'],
                'correct': 1,
                'explanation': '7 is the next prime number after 5. The numbers 6, 8, and 9 are composite.'
            },
        ])
        
        # Additional beginner questions for variety
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is the opposite of 8?',
                'options': ['-8', '8', '0', '1/8'],
                'correct': 0,
                'explanation': 'The opposite (or additive inverse) of 8 is -8. When added together, they equal 0.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is 6 + (-6)?',
                'options': ['12', '0', '-12', '6'],
                'correct': 1,
                'explanation': 'A number plus its opposite equals 0. So 6 + (-6) = 0.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which is larger: -10 or -3?',
                'options': ['-10', '-3', 'They are equal', 'Cannot compare'],
                'correct': 1,
                'explanation': '-3 is larger than -10. On a number line, -3 is to the right of -10.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 11 a prime number?',
                'options': ['Yes', 'No', 'Only when multiplied', 'Only when divided'],
                'correct': 0,
                'explanation': 'Yes, 11 is a prime number. It can only be divided by 1 and 11.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is -5 × 2?',
                'options': ['-10', '-7', '7', '10'],
                'correct': 0,
                'explanation': 'When multiplying a negative by a positive, the result is negative: -5 × 2 = -10.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which of these is a natural number?',
                'options': ['-3', '0', '12', '2.5'],
                'correct': 2,
                'explanation': '12 is a natural number. Natural numbers are positive whole numbers starting from 1.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What type of number is 0?',
                'options': ['Natural', 'Integer', 'Prime', 'None'],
                'correct': 1,
                'explanation': '0 is an integer, but not a natural number or prime number.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Is 13 a prime number?',
                'options': ['Yes', 'No', 'Sometimes', 'Never'],
                'correct': 0,
                'explanation': 'Yes, 13 is prime. It can only be divided by 1 and 13.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'What is -7 + 7?',
                'options': ['-14', '0', '14', '7'],
                'correct': 1,
                'explanation': 'Adding a number to its opposite always equals 0: -7 + 7 = 0.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'beginner',
                'question': 'Which number is both an integer and a natural number?',
                'options': ['-4', '0', '5', '2.1'],
                'correct': 2,
                'explanation': '5 is both an integer (whole number) and a natural number (positive counting number).'
            },
        ])
        
        # ==================== INTERMEDIATE LEVEL ====================
        # More complex natural numbers, integers, primes
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is -8 + (-5)?',
                'options': ['-13', '-3', '3', '13'],
                'correct': 0,
                'explanation': 'When adding two negative numbers, add their absolute values and keep the negative sign: -8 + (-5) = -13.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is -12 ÷ 3?',
                'options': ['-4', '-9', '4', '9'],
                'correct': 0,
                'explanation': 'Dividing a negative by a positive gives a negative result: -12 ÷ 3 = -4.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is (-3) × (-4)?',
                'options': ['-12', '-7', '7', '12'],
                'correct': 3,
                'explanation': 'When multiplying two negative numbers, the result is positive: (-3) × (-4) = 12.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'How many prime numbers are between 10 and 20?',
                'options': ['3', '4', '5', '6'],
                'correct': 1,
                'explanation': 'There are 4 prime numbers between 10 and 20: 11, 13, 17, and 19.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Is 21 a prime number?',
                'options': ['Yes', 'No', 'Only if divided by 3', 'Only if multiplied by 7'],
                'correct': 1,
                'explanation': 'No, 21 is not prime because it can be divided by 1, 3, 7, and 21. It is a composite number.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is the absolute value of -15?',
                'options': ['-15', '0', '15', '30'],
                'correct': 2,
                'explanation': 'The absolute value of a number is its distance from zero, always positive: |-15| = 15.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is 10 - 18?',
                'options': ['-8', '-28', '8', '28'],
                'correct': 0,
                'explanation': 'When subtracting a larger number from a smaller one, the result is negative: 10 - 18 = -8.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Which is the largest prime number less than 30?',
                'options': ['27', '28', '29', '31'],
                'correct': 2,
                'explanation': '29 is the largest prime number less than 30. 27 and 28 are composite.'
            },
            
            # Rounding
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 47 to the nearest 10.',
                'options': ['40', '45', '50', '60'],
                'correct': 2,
                'explanation': '47 is closer to 50 than to 40. When the ones digit is 5 or more, round up.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 123 to the nearest 10.',
                'options': ['100', '120', '125', '130'],
                'correct': 1,
                'explanation': '123 rounds down to 120 because the ones digit (3) is less than 5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 385 to the nearest 100.',
                'options': ['300', '350', '380', '400'],
                'correct': 3,
                'explanation': '385 rounds up to 400 because the tens digit (8) is 5 or more.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 2,450 to the nearest 1,000.',
                'options': ['2,000', '2,400', '2,500', '3,000'],
                'correct': 0,
                'explanation': '2,450 rounds down to 2,000 because the hundreds digit (4) is less than 5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 74.3 to the nearest whole number.',
                'options': ['70', '74', '75', '80'],
                'correct': 1,
                'explanation': '74.3 rounds down to 74 because the decimal part (0.3) is less than 0.5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 18.7 to the nearest whole number.',
                'options': ['18', '18.5', '19', '20'],
                'correct': 2,
                'explanation': '18.7 rounds up to 19 because the decimal part (0.7) is 0.5 or more.'
            },
            
            # Significant Figures
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'How many significant figures are in 205?',
                'options': ['1', '2', '3', '4'],
                'correct': 2,
                'explanation': '205 has 3 significant figures. All non-zero digits and zeros between them count.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'How many significant figures are in 3,400?',
                'options': ['1', '2', '3', '4'],
                'correct': 1,
                'explanation': '3,400 has 2 significant figures (3 and 4). Trailing zeros without a decimal point don\'t count.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 3.47 to 2 significant figures.',
                'options': ['3.4', '3.5', '4.0', '3'],
                'correct': 1,
                'explanation': '3.47 rounded to 2 significant figures is 3.5 (the third digit 7 causes us to round up).'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'How many significant figures are in 0.0053?',
                'options': ['1', '2', '4', '6'],
                'correct': 1,
                'explanation': '0.0053 has 2 significant figures (5 and 3). Leading zeros don\'t count.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 1,276 to 2 significant figures.',
                'options': ['1,200', '1,270', '1,280', '1,300'],
                'correct': 3,
                'explanation': '1,276 rounded to 2 significant figures is 1,300. The third digit (7) causes us to round up.'
            },
        ])
        
        # Additional intermediate questions
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is -20 ÷ (-4)?',
                'options': ['-5', '-16', '5', '16'],
                'correct': 2,
                'explanation': 'Dividing two negative numbers gives a positive result: -20 ÷ (-4) = 5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is the product of -6 and -7?',
                'options': ['-42', '-13', '13', '42'],
                'correct': 3,
                'explanation': 'Multiplying two negative numbers gives a positive: (-6) × (-7) = 42.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Is 27 a prime number?',
                'options': ['Yes', 'No', 'Only when cubed', 'Only when squared'],
                'correct': 1,
                'explanation': 'No, 27 is not prime. It equals 3 × 3 × 3, so it has factors other than 1 and itself.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 549 to the nearest 100.',
                'options': ['500', '540', '550', '600'],
                'correct': 0,
                'explanation': '549 rounds down to 500 because the tens digit (4) is less than 5.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is the absolute value of -23?',
                'options': ['-23', '0', '23', '46'],
                'correct': 2,
                'explanation': 'The absolute value is the distance from zero: |-23| = 23.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'How many significant figures are in 5.00?',
                'options': ['1', '2', '3', '4'],
                'correct': 2,
                'explanation': '5.00 has 3 significant figures. Trailing zeros after a decimal point count as significant.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is -15 + 23?',
                'options': ['-38', '-8', '8', '38'],
                'correct': 2,
                'explanation': 'When adding numbers with different signs, subtract: 23 - 15 = 8. Take the sign of the larger number (positive).'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Which is the smallest prime number greater than 40?',
                'options': ['41', '42', '43', '44'],
                'correct': 0,
                'explanation': '41 is prime and is the smallest prime number greater than 40.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'Round 8.25 to 1 decimal place.',
                'options': ['8.0', '8.2', '8.3', '9.0'],
                'correct': 2,
                'explanation': '8.25 rounds to 8.3 because the second decimal digit (5) means we round up.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'intermediate',
                'question': 'What is -9 - (-4)?',
                'options': ['-13', '-5', '5', '13'],
                'correct': 1,
                'explanation': 'Subtracting a negative is the same as adding: -9 - (-4) = -9 + 4 = -5.'
            },
        ])
        
        # ==================== ADVANCED LEVEL ====================
        # Practical temperature calculations
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 3 degrees colder than -5°C?',
                'options': ['-8°C', '-2°C', '2°C', '8°C'],
                'correct': 0,
                'explanation': '3 degrees colder means subtract 3: -5 - 3 = -8°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'If the temperature is -7°C and it rises by 10 degrees, what is the new temperature?',
                'options': ['-17°C', '-3°C', '3°C', '17°C'],
                'correct': 2,
                'explanation': 'Rising by 10 degrees means add 10: -7 + 10 = 3°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'The temperature at night was -4°C. During the day it was 8°C. What was the temperature increase?',
                'options': ['4°C', '8°C', '12°C', '16°C'],
                'correct': 2,
                'explanation': 'Temperature increase = 8 - (-4) = 8 + 4 = 12°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 5 degrees warmer than -2°C?',
                'options': ['-7°C', '-3°C', '3°C', '7°C'],
                'correct': 2,
                'explanation': '5 degrees warmer means add 5: -2 + 5 = 3°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'The temperature dropped from 2°C to -6°C. By how many degrees did it drop?',
                'options': ['4°C', '8°C', '12°C', '16°C'],
                'correct': 1,
                'explanation': 'Temperature drop = 2 - (-6) = 2 + 6 = 8°C.'
            },
            
            # More complex integer operations
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is (-8) × 3 + 10?',
                'options': ['-38', '-14', '14', '34'],
                'correct': 1,
                'explanation': 'Follow order of operations: (-8) × 3 = -24, then -24 + 10 = -14.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 15 ÷ (-3) - 7?',
                'options': ['-12', '-5', '5', '12'],
                'correct': 0,
                'explanation': 'Follow order of operations: 15 ÷ (-3) = -5, then -5 - 7 = -12.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is (-4)²?',
                'options': ['-16', '-8', '8', '16'],
                'correct': 3,
                'explanation': '(-4)² means (-4) × (-4) = 16. Squaring a negative number gives a positive result.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is -3 × 4 ÷ 2?',
                'options': ['-6', '-1', '1', '6'],
                'correct': 0,
                'explanation': 'Work left to right: -3 × 4 = -12, then -12 ÷ 2 = -6.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is |−8 + 3|?',
                'options': ['-11', '-5', '5', '11'],
                'correct': 2,
                'explanation': 'First calculate inside: -8 + 3 = -5. Then take absolute value: |-5| = 5.'
            },
            
            # Complex prime number questions
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'How many prime numbers are there between 20 and 40?',
                'options': ['4', '5', '6', '7'],
                'correct': 0,
                'explanation': 'The primes between 20 and 40 are: 23, 29, 31, and 37. That\'s 4 primes.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is the sum of the first three prime numbers?',
                'options': ['6', '8', '10', '12'],
                'correct': 2,
                'explanation': 'The first three primes are 2, 3, and 5. Their sum is 2 + 3 + 5 = 10.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Is 51 a prime number?',
                'options': ['Yes', 'No', 'Only when odd', 'Only when positive'],
                'correct': 1,
                'explanation': 'No, 51 is not prime. It equals 3 × 17, so it has factors other than 1 and itself.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is the largest prime number less than 50?',
                'options': ['43', '45', '47', '49'],
                'correct': 2,
                'explanation': '47 is the largest prime less than 50. 49 = 7 × 7, and 45 is divisible by many numbers.'
            },
            
            # Complex rounding and significant figures
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Round 4,782 to 1 significant figure.',
                'options': ['4,000', '4,700', '4,800', '5,000'],
                'correct': 3,
                'explanation': 'The first significant figure is 4. The next digit (7) is ≥5, so round up to 5,000.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'How many significant figures are in 0.00470?',
                'options': ['2', '3', '5', '6'],
                'correct': 1,
                'explanation': '0.00470 has 3 significant figures: 4, 7, and 0. Leading zeros don\'t count, but trailing zeros after decimal do.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Round 0.08659 to 2 significant figures.',
                'options': ['0.086', '0.087', '0.09', '0.1'],
                'correct': 1,
                'explanation': 'The first two significant figures are 8 and 6. The next digit (5) means round up: 0.087.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Express 3,200 with 3 significant figures.',
                'options': ['3,200', '3,200.', '3,210', '3,000'],
                'correct': 1,
                'explanation': 'To show 3 sig figs, use a decimal point: 3,200. (the point indicates the trailing zeros are significant).'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Round 15.449 to 3 significant figures.',
                'options': ['15.4', '15.44', '15.45', '15.5'],
                'correct': 0,
                'explanation': 'Three significant figures are 1, 5, and 4. The next digit (4) is less than 5, so it\'s 15.4.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 8 degrees colder than 3°C?',
                'options': ['-11°C', '-5°C', '5°C', '11°C'],
                'correct': 1,
                'explanation': '8 degrees colder means subtract 8: 3 - 8 = -5°C.'
            },
        ])
        
        # Additional advanced questions
        questions.extend([
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is (-5)² - 3²?',
                'options': ['-34', '-16', '16', '34'],
                'correct': 2,
                'explanation': '(-5)² = 25 and 3² = 9. So 25 - 9 = 16.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is |5 - 12|?',
                'options': ['-7', '-17', '7', '17'],
                'correct': 2,
                'explanation': 'First calculate: 5 - 12 = -7. Then absolute value: |-7| = 7.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'If the temperature starts at -10°C and rises 15 degrees, what is the final temperature?',
                'options': ['-25°C', '-5°C', '5°C', '25°C'],
                'correct': 2,
                'explanation': 'Rising 15 degrees means add 15: -10 + 15 = 5°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is -6 × (-2) + (-8)?',
                'options': ['-20', '-4', '4', '20'],
                'correct': 2,
                'explanation': 'First: -6 × (-2) = 12. Then: 12 + (-8) = 4.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'How many prime numbers are there from 1 to 20?',
                'options': ['6', '7', '8', '9'],
                'correct': 2,
                'explanation': 'The primes from 1-20 are: 2, 3, 5, 7, 11, 13, 17, 19. That\'s 8 primes.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Round 0.7856 to 2 decimal places.',
                'options': ['0.78', '0.79', '0.8', '0.80'],
                'correct': 1,
                'explanation': 'The third decimal (5) means round up: 0.79.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 20 - (-15)?',
                'options': ['-35', '-5', '5', '35'],
                'correct': 3,
                'explanation': 'Subtracting a negative is adding: 20 - (-15) = 20 + 15 = 35.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'Is 91 a prime number?',
                'options': ['Yes', 'No', 'Only when multiplied', 'Only when divided'],
                'correct': 1,
                'explanation': 'No, 91 = 7 × 13, so it\'s not prime.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'How many significant figures are in 120.00?',
                'options': ['2', '3', '4', '5'],
                'correct': 3,
                'explanation': '120.00 has 5 significant figures. The decimal point shows all zeros are significant.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is (-10) ÷ 2 + 15?',
                'options': ['-20', '-5', '10', '20'],
                'correct': 2,
                'explanation': 'First: (-10) ÷ 2 = -5. Then: -5 + 15 = 10.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'The temperature was 4°C at noon. It dropped 12 degrees by midnight. What was the temperature at midnight?',
                'options': ['-16°C', '-8°C', '8°C', '16°C'],
                'correct': 1,
                'explanation': 'Dropped 12 degrees means subtract 12: 4 - 12 = -8°C.'
            },
            {
                'topic': 'number_systems',
                'difficulty': 'advanced',
                'question': 'What is 6 degrees warmer than -9°C?',
                'options': ['-15°C', '-3°C', '3°C', '15°C'],
                'correct': 1,
                'explanation': '6 degrees warmer means add 6: -9 + 6 = -3°C.'
            },
        ])
        
        # Add all questions to database
        for q_data in questions:
            question = Question(
                topic=q_data['topic'],
                difficulty=q_data['difficulty'],
                question_text=q_data['question'],
                option_a=q_data['options'][0],
                option_b=q_data['options'][1],
                option_c=q_data['options'][2],
                option_d=q_data['options'][3],
                correct_answer=q_data['correct'],
                explanation=q_data['explanation']
            )
            db.session.add(question)
        
        db.session.commit()
        
        # Count questions by difficulty
        beginner_count = Question.query.filter_by(topic='number_systems', difficulty='beginner').count()
        intermediate_count = Question.query.filter_by(topic='number_systems', difficulty='intermediate').count()
        advanced_count = Question.query.filter_by(topic='number_systems', difficulty='advanced').count()
        
        print(f"✓ Successfully added Number Systems questions!")
        print(f"  - Beginner: {beginner_count} questions")
        print(f"  - Intermediate: {intermediate_count} questions")
        print(f"  - Advanced: {advanced_count} questions")
        print(f"  - Total: {beginner_count + intermediate_count + advanced_count} questions")

if __name__ == '__main__':
    add_number_systems_questions()
