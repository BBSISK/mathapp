"""
TUTORIAL MIGRATION SCRIPT
=========================
Run this script on PythonAnywhere to import all tutorials from student_app.html
into the database so they appear in the Admin module.

Usage:
    cd ~/mathapp
    source venv/bin/activate
    python migrate_tutorials.py
"""

import json
import sqlite3
import os

# Database path
DB_PATH = '/home/bbsisk/mathapp/instance/mathquiz.db'

# All tutorials data extracted from student_app.html
TUTORIALS = {
    'introductory_algebra': {
        'beginner': {
            'title': 'Collecting Like Terms',
            'introduction': 'In this level, you\'ll learn to <strong>collect like terms</strong> - combining terms that have the same letter.',
            'principles': [
                {'title': 'Like Terms', 'content': '<strong>Like terms</strong> have exactly the same letter part.<br>• 3x and 5x are like terms (both have \'x\')<br>• 4y and 2y are like terms (both have \'y\')<br>• 3x and 5y are NOT like terms (different letters)'},
                {'title': 'How to Collect', 'content': 'Think of it like fruit: 3 apples + 5 apples = 8 apples<br>Just add the numbers, keep the letter!'}
            ],
            'examples': [
                {'question': 'Simplify: 4x + 3x', 'steps': ['Both terms have \'x\' - they are like terms ✓', 'Add the numbers: 4 + 3 = 7', 'Keep the letter: x'], 'answer': '7x'},
                {'question': 'Simplify: 5y + 2y', 'steps': ['Both terms have \'y\' - they are like terms ✓', 'Add the numbers: 5 + 2 = 7', 'Keep the letter: y'], 'answer': '7y'}
            ],
            'tips': ['✅ Always keep the letter - it doesn\'t change!', '✅ Just add the numbers - ignore the letters when adding', '⚠️ Don\'t forget the letter: 4x + 3x = 7x (not 7)', '⚠️ Don\'t multiply: 2y + 3y = 5y (not 6y)']
        },
        'intermediate': {
            'title': 'Substitution (One Variable)',
            'introduction': 'In this level, you\'ll learn <strong>substitution</strong> - finding the value of expressions when you know what x equals.',
            'principles': [
                {'title': 'What is Substitution?', 'content': '<strong>Substitution</strong> means replacing a letter with its number value.<br>Example: If x = 5, then x + 3 means 5 + 3 = 8'},
                {'title': 'Use Brackets!', 'content': 'Always use brackets when substituting.<br>If x = 4, write 3(4) not 34'}
            ],
            'examples': [
                {'question': 'If x = 4, find the value of x + 7', 'steps': ['Write the expression: x + 7', 'Replace x with 4: (4) + 7', 'Calculate: 4 + 7'], 'answer': '11'},
                {'question': 'If x = 5, find the value of 2x', 'steps': ['Write the expression: 2x (means 2 times x)', 'Replace x with 5 (use brackets!): 2(5)', 'Calculate: 2 × 5'], 'answer': '10'}
            ],
            'tips': ['✅ Always use brackets when substituting', '✅ Remember 2x means 2 × x (multiply!)', '✅ Follow BOMDAS - multiply before adding', '⚠️ Don\'t just stick numbers together: 3x when x=4 is 12, not 34']
        },
        'advanced': {
            'title': 'Substitution (Two Variables)',
            'introduction': 'In this level, you\'ll substitute <strong>two different variables</strong> (like x and y) in the same expression.',
            'principles': [
                {'title': 'Multiple Variables', 'content': 'Each letter can represent a different number!<br>Example: If x = 3 and y = 5, then x + y means 3 + 5 = 8'},
                {'title': 'Multiply First', 'content': 'When you see 2x or 3y, multiply BEFORE adding/subtracting (BOMDAS!)'}
            ],
            'examples': [
                {'question': 'If x = 4 and y = 3, find x + y', 'steps': ['Write: x + y', 'Replace both letters: (4) + (3)', 'Calculate: 4 + 3'], 'answer': '7'},
                {'question': 'If x = 5 and y = 4, find 2x + y', 'steps': ['Write: 2x + y', 'Replace: 2(5) + (4)', 'Multiply first: 10 + 4', 'Then add: 14'], 'answer': '14'}
            ],
            'tips': ['✅ Keep track of which value goes with which letter', '✅ Use brackets for both variables', '✅ Multiply before you add/subtract (BOMDAS!)', '⚠️ Don\'t mix up the values: x=4, y=3 means x+y = 4+3, not 3+4... well, same answer, but you get the idea!']
        }
    },
    'solving_equations': {
        'beginner': {
            'title': 'One-Step Equations',
            'introduction': 'Learn to solve <strong>one-step equations</strong> like x + 5 = 12. You\'ll discover how to "undo" addition to find the value of x.',
            'principles': [
                {'title': 'What is an Equation?', 'content': 'An <strong>equation</strong> is like a balance scale - both sides must be equal.<br>Example: x + 3 = 10 means "something plus 3 equals 10"<br>Our job is to find what that "something" (x) is!'},
                {'title': 'The Golden Rule', 'content': '<strong>Whatever you do to one side, do to the other!</strong><br>Think of it like a seesaw - if you take weight off one side, you must take the same weight off the other side to keep it balanced.'},
                {'title': 'Undoing Addition', 'content': 'To solve x + 3 = 10, we need to <strong>undo</strong> the +3<br>• Addition is undone by subtraction<br>• Subtract 3 from BOTH sides<br>• x + 3 - 3 = 10 - 3<br>• x = 7'}
            ],
            'examples': [
                {'question': 'Solve: x + 3 = 10', 'steps': ['We need to get x by itself (isolate x)', 'The +3 is attached to x, so we undo it', 'Subtract 3 from BOTH sides: x + 3 - 3 = 10 - 3', 'Left side: x + 3 - 3 = x (the 3s cancel out!)', 'Right side: 10 - 3 = 7', 'Therefore: x = 7'], 'answer': 'x = 7'},
                {'question': 'Solve: x + 9 = 29', 'steps': ['We need to remove the +9 to isolate x', 'Subtract 9 from BOTH sides: x + 9 - 9 = 29 - 9', 'Left side: x + 9 - 9 = x', 'Right side: 29 - 9 = 20', 'Therefore: x = 20'], 'answer': 'x = 20'}
            ],
            'tips': ['✅ Always do the same thing to both sides', '✅ To undo addition, subtract', '✅ Check your answer by substituting back']
        },
        'intermediate': {
            'title': 'Two-Step Equations',
            'introduction': 'Solve equations with two operations like 2x + 3 = 11',
            'principles': [
                {'title': 'Reverse BOMDAS', 'content': 'Undo addition/subtraction first, then multiplication/division'},
                {'title': 'Two Steps', 'content': 'First remove the number, then divide by the coefficient'}
            ],
            'examples': [
                {'question': 'Solve: 2x + 3 = 11', 'steps': ['Subtract 3 from both sides: 2x = 8', 'Divide both sides by 2: x = 4'], 'answer': 'x = 4'}
            ],
            'tips': ['✅ Undo addition first, then multiplication']
        },
        'advanced': {
            'title': 'Equations with Variables on Both Sides',
            'introduction': 'Solve equations like 3x + 2 = x + 10',
            'principles': [
                {'title': 'Collect Variables', 'content': 'Get all x terms on one side first'}
            ],
            'examples': [
                {'question': 'Solve: 3x + 2 = x + 10', 'steps': ['Subtract x from both sides: 2x + 2 = 10', 'Subtract 2: 2x = 8', 'Divide by 2: x = 4'], 'answer': 'x = 4'}
            ],
            'tips': ['✅ Move variables to one side first']
        }
    },
    'simplifying_expressions': {
        'beginner': {
            'title': 'Basic Simplification',
            'introduction': 'Simplify algebraic expressions by collecting like terms',
            'principles': [
                {'title': 'Like Terms', 'content': 'Combine terms with the same variable'}
            ],
            'examples': [
                {'question': '3x + 2x', 'steps': ['Both have x', 'Add coefficients'], 'answer': '5x'}
            ],
            'tips': ['✅ Only combine like terms']
        },
        'intermediate': {
            'title': 'Multiple Terms',
            'introduction': 'Simplify expressions with multiple different variables',
            'principles': [
                {'title': 'Group Like Terms', 'content': 'Group x terms, y terms, and numbers separately'}
            ],
            'examples': [
                {'question': '3x + 2y + x + 4y', 'steps': ['Group: (3x + x) + (2y + 4y)', 'Simplify: 4x + 6y'], 'answer': '4x + 6y'}
            ],
            'tips': ['✅ Organize terms first']
        },
        'advanced': {
            'title': 'Complex Expressions',
            'introduction': 'Simplify expressions with brackets and multiple operations',
            'principles': [
                {'title': 'Expand First', 'content': 'Remove brackets before simplifying'}
            ],
            'examples': [
                {'question': '2(x + 3) + 3x', 'steps': ['Expand: 2x + 6 + 3x', 'Combine: 5x + 6'], 'answer': '5x + 6'}
            ],
            'tips': ['✅ Expand brackets first']
        }
    },
    'expanding_factorising': {
        'beginner': {
            'title': 'Expanding Single Brackets',
            'introduction': 'Multiply out expressions like 3(x + 2)',
            'principles': [
                {'title': 'Distributive Law', 'content': 'Multiply each term inside by the number outside'}
            ],
            'examples': [
                {'question': '3(x + 2)', 'steps': ['3 × x = 3x', '3 × 2 = 6'], 'answer': '3x + 6'}
            ],
            'tips': ['✅ Multiply EVERY term inside']
        },
        'intermediate': {
            'title': 'Expanding Double Brackets',
            'introduction': 'Use FOIL to expand (x + 2)(x + 3)',
            'principles': [
                {'title': 'FOIL', 'content': 'First, Outer, Inner, Last'}
            ],
            'examples': [
                {'question': '(x + 2)(x + 3)', 'steps': ['First: x²', 'Outer: 3x', 'Inner: 2x', 'Last: 6', 'Combine: x² + 5x + 6'], 'answer': 'x² + 5x + 6'}
            ],
            'tips': ['✅ Remember FOIL']
        },
        'advanced': {
            'title': 'Factorising Quadratics',
            'introduction': 'Reverse of expanding: x² + 5x + 6 → (x + 2)(x + 3)',
            'principles': [
                {'title': 'Find Factors', 'content': 'Find two numbers that multiply to c and add to b'}
            ],
            'examples': [
                {'question': 'Factorise x² + 5x + 6', 'steps': ['Need: ? × ? = 6 and ? + ? = 5', 'Answer: 2 and 3'], 'answer': '(x + 2)(x + 3)'}
            ],
            'tips': ['✅ Check by expanding']
        }
    },
    'functions': {
        'beginner': {
            'title': 'Function Notation',
            'introduction': 'Understand f(x) notation',
            'principles': [
                {'title': 'f(x)', 'content': 'f(x) means "the function f applied to x"'}
            ],
            'examples': [
                {'question': 'If f(x) = x + 3, find f(2)', 'steps': ['Replace x with 2', 'f(2) = 2 + 3 = 5'], 'answer': '5'}
            ],
            'tips': ['✅ Substitute the number for x']
        },
        'intermediate': {
            'title': 'Composite Functions',
            'introduction': 'Apply one function then another',
            'principles': [
                {'title': 'Composition', 'content': 'f(g(x)) means apply g first, then f'}
            ],
            'examples': [
                {'question': 'f(x) = 2x, g(x) = x + 1. Find f(g(3))', 'steps': ['g(3) = 3 + 1 = 4', 'f(4) = 2(4) = 8'], 'answer': '8'}
            ],
            'tips': ['✅ Work from inside out']
        },
        'advanced': {
            'title': 'Inverse Functions',
            'introduction': 'Find the function that reverses another',
            'principles': [
                {'title': 'Inverse', 'content': 'f⁻¹ undoes what f does'}
            ],
            'examples': [
                {'question': 'f(x) = 2x + 1. Find f⁻¹(x)', 'steps': ['Let y = 2x + 1', 'Swap x and y: x = 2y + 1', 'Solve for y: y = (x-1)/2'], 'answer': 'f⁻¹(x) = (x-1)/2'}
            ],
            'tips': ['✅ Swap x and y, then solve']
        }
    },
    'patterns': {
        'beginner': {
            'title': 'Recognising Patterns',
            'introduction': 'Find the next term in simple sequences',
            'principles': [
                {'title': 'Look for the Rule', 'content': 'Find what changes between terms'}
            ],
            'examples': [
                {'question': '2, 4, 6, 8, ?', 'steps': ['Pattern: +2 each time', 'Next: 8 + 2'], 'answer': '10'}
            ],
            'tips': ['✅ Find the difference between terms']
        },
        'intermediate': {
            'title': 'Linear Sequences',
            'introduction': 'Find the nth term of arithmetic sequences',
            'principles': [
                {'title': 'nth Term Formula', 'content': 'nth term = first term + (n-1) × common difference'}
            ],
            'examples': [
                {'question': 'Find nth term of 3, 7, 11, 15...', 'steps': ['Common difference: 4', 'First term: 3', 'nth term = 3 + (n-1)×4 = 4n - 1'], 'answer': '4n - 1'}
            ],
            'tips': ['✅ Find the common difference first']
        },
        'advanced': {
            'title': 'Quadratic Sequences',
            'introduction': 'Sequences where second difference is constant',
            'principles': [
                {'title': 'Second Difference', 'content': 'If first differences change, look at second differences'}
            ],
            'examples': [
                {'question': '1, 4, 9, 16, ?', 'steps': ['These are square numbers', 'n² formula', 'Next: 5² = 25'], 'answer': '25'}
            ],
            'tips': ['✅ Check if it\'s a known sequence (squares, cubes)']
        }
    },
    'arithmetic': {
        'beginner': {
            'title': 'Basic Operations',
            'introduction': 'Addition, subtraction, multiplication, division',
            'principles': [
                {'title': 'Operations', 'content': 'The four basic operations form the foundation of maths'}
            ],
            'examples': [
                {'question': '24 + 17', 'steps': ['Add units: 4 + 7 = 11', 'Add tens: 20 + 10 = 30', 'Total: 41'], 'answer': '41'}
            ],
            'tips': ['✅ Line up place values']
        },
        'intermediate': {
            'title': 'Order of Operations',
            'introduction': 'BOMDAS - the correct order',
            'principles': [
                {'title': 'BOMDAS', 'content': 'Brackets, Orders, Multiplication/Division, Addition/Subtraction'}
            ],
            'examples': [
                {'question': '3 + 4 × 2', 'steps': ['Multiplication first: 4 × 2 = 8', 'Then add: 3 + 8'], 'answer': '11'}
            ],
            'tips': ['✅ Multiply before you add']
        },
        'advanced': {
            'title': 'Complex Calculations',
            'introduction': 'Multi-step problems with all operations',
            'principles': [
                {'title': 'Step by Step', 'content': 'Break complex problems into smaller steps'}
            ],
            'examples': [
                {'question': '(3 + 5) × 2 - 4', 'steps': ['Brackets: 8', 'Multiply: 16', 'Subtract: 12'], 'answer': '12'}
            ],
            'tips': ['✅ Do brackets first']
        }
    },
    'bodmas': {
        'beginner': {
            'title': 'BOMDAS Basics',
            'introduction': 'Learn the order of operations',
            'principles': [
                {'title': 'The Order', 'content': 'B-Brackets, O-Orders, M-Multiply, D-Divide, A-Add, S-Subtract'}
            ],
            'examples': [
                {'question': '2 + 3 × 4', 'steps': ['Multiply first: 3 × 4 = 12', 'Then add: 2 + 12'], 'answer': '14'}
            ],
            'tips': ['✅ Multiplication before addition']
        },
        'intermediate': {
            'title': 'Brackets and Powers',
            'introduction': 'Brackets come first, then powers',
            'principles': [
                {'title': 'Powers', 'content': 'Orders (powers) come after brackets'}
            ],
            'examples': [
                {'question': '(2 + 3)²', 'steps': ['Brackets: 5', 'Square: 25'], 'answer': '25'}
            ],
            'tips': ['✅ Brackets first, then square']
        },
        'advanced': {
            'title': 'Complex BOMDAS',
            'introduction': 'Multiple operations in one expression',
            'principles': [
                {'title': 'Left to Right', 'content': 'For same-level operations, go left to right'}
            ],
            'examples': [
                {'question': '20 ÷ 4 × 2', 'steps': ['Left to right: 20 ÷ 4 = 5', 'Then: 5 × 2 = 10'], 'answer': '10'}
            ],
            'tips': ['✅ Same level = left to right']
        }
    },
    'fractions': {
        'beginner': {
            'title': 'Equivalent Fractions',
            'introduction': 'Different fractions that mean the same thing',
            'principles': [
                {'title': 'Equivalent', 'content': 'Multiply top and bottom by the same number'}
            ],
            'examples': [
                {'question': 'Find equivalent to 1/2 with denominator 6', 'steps': ['Multiply both by 3', '1×3/2×3 = 3/6'], 'answer': '3/6'}
            ],
            'tips': ['✅ Whatever you do to top, do to bottom']
        },
        'intermediate': {
            'title': 'Adding Fractions',
            'introduction': 'Add fractions with different denominators',
            'principles': [
                {'title': 'Common Denominator', 'content': 'Find a common denominator first'}
            ],
            'examples': [
                {'question': '1/3 + 1/4', 'steps': ['LCD = 12', '4/12 + 3/12 = 7/12'], 'answer': '7/12'}
            ],
            'tips': ['✅ Find LCD first']
        },
        'advanced': {
            'title': 'Multiplying and Dividing Fractions',
            'introduction': 'Multiply straight across, invert to divide',
            'principles': [
                {'title': 'Division', 'content': 'To divide, multiply by the reciprocal'}
            ],
            'examples': [
                {'question': '2/3 ÷ 1/2', 'steps': ['Flip second fraction: 2/3 × 2/1', 'Multiply: 4/3'], 'answer': '4/3 or 1⅓'}
            ],
            'tips': ['✅ Keep, Change, Flip for division']
        }
    },
    'decimals': {
        'beginner': {
            'title': 'Decimal Place Value',
            'introduction': 'Understand tenths, hundredths, thousandths',
            'principles': [
                {'title': 'Places', 'content': 'Each place is 10 times smaller going right'}
            ],
            'examples': [
                {'question': 'What is the value of 7 in 3.27?', 'steps': ['7 is in hundredths place', '7/100 = 0.07'], 'answer': '0.07'}
            ],
            'tips': ['✅ Count places after decimal']
        },
        'intermediate': {
            'title': 'Decimal Operations',
            'introduction': 'Add, subtract, multiply decimals',
            'principles': [
                {'title': 'Line Up', 'content': 'Keep decimal points aligned'}
            ],
            'examples': [
                {'question': '3.5 + 2.75', 'steps': ['Line up decimals', '3.50 + 2.75 = 6.25'], 'answer': '6.25'}
            ],
            'tips': ['✅ Add zeros to help align']
        },
        'advanced': {
            'title': 'Converting Decimals',
            'introduction': 'Convert between decimals, fractions, percentages',
            'principles': [
                {'title': 'Conversions', 'content': 'Decimal × 100 = percentage, decimal = fraction/denominator'}
            ],
            'examples': [
                {'question': 'Convert 0.75 to fraction', 'steps': ['0.75 = 75/100', 'Simplify: 3/4'], 'answer': '3/4'}
            ],
            'tips': ['✅ Use place value to convert']
        }
    },
    'multiplication_division': {
        'beginner': {
            'title': 'Times Tables',
            'introduction': 'Master multiplication facts',
            'principles': [
                {'title': 'Multiplication', 'content': 'Repeated addition: 3 × 4 = 4 + 4 + 4'}
            ],
            'examples': [
                {'question': '7 × 8', 'steps': ['Use times table knowledge'], 'answer': '56'}
            ],
            'tips': ['✅ Practice times tables regularly']
        },
        'intermediate': {
            'title': 'Long Multiplication',
            'introduction': 'Multiply larger numbers',
            'principles': [
                {'title': 'Partitioning', 'content': 'Break numbers into parts, multiply each, add results'}
            ],
            'examples': [
                {'question': '23 × 15', 'steps': ['23 × 10 = 230', '23 × 5 = 115', '230 + 115 = 345'], 'answer': '345'}
            ],
            'tips': ['✅ Break into easier parts']
        },
        'advanced': {
            'title': 'Long Division',
            'introduction': 'Divide larger numbers',
            'principles': [
                {'title': 'Division Steps', 'content': 'Divide, Multiply, Subtract, Bring down, Repeat'}
            ],
            'examples': [
                {'question': '156 ÷ 12', 'steps': ['12 goes into 15 once (12)', '15-12=3, bring down 6 = 36', '12 goes into 36 three times'], 'answer': '13'}
            ],
            'tips': ['✅ Work step by step']
        }
    },
    'number_systems': {
        'beginner': {
            'title': 'Types of Numbers',
            'introduction': 'Natural, whole, integers, rational numbers',
            'principles': [
                {'title': 'Number Sets', 'content': 'ℕ = natural (1,2,3...), ℤ = integers (...-2,-1,0,1,2...), ℚ = rational (fractions)'}
            ],
            'examples': [
                {'question': 'Is -3 a natural number?', 'steps': ['Natural numbers start at 1', 'Negatives not included'], 'answer': 'No'}
            ],
            'tips': ['✅ Know which numbers belong where']
        },
        'intermediate': {
            'title': 'Rational vs Irrational',
            'introduction': 'Numbers that can or cannot be written as fractions',
            'principles': [
                {'title': 'Irrational', 'content': 'Cannot be written as a fraction (π, √2)'}
            ],
            'examples': [
                {'question': 'Is √4 rational?', 'steps': ['√4 = 2', '2 = 2/1 (a fraction)'], 'answer': 'Yes, rational'}
            ],
            'tips': ['✅ If it simplifies to a fraction, it\'s rational']
        },
        'advanced': {
            'title': 'Real and Complex',
            'introduction': 'All numbers including imaginary',
            'principles': [
                {'title': 'Complex', 'content': 'Real numbers + imaginary numbers (i = √-1)'}
            ],
            'examples': [
                {'question': 'What type is 3 + 2i?', 'steps': ['Has real part (3) and imaginary part (2i)'], 'answer': 'Complex number'}
            ],
            'tips': ['✅ Complex = real + imaginary']
        }
    },
    'surds': {
        'beginner': {
            'title': 'Understanding Surds',
            'introduction': 'Surds are roots that don\'t simplify to whole numbers',
            'principles': [
                {'title': 'What is a Surd?', 'content': '√2, √3, √5 are surds because they are irrational'}
            ],
            'examples': [
                {'question': 'Is √9 a surd?', 'steps': ['√9 = 3', '3 is rational'], 'answer': 'No, √9 = 3'}
            ],
            'tips': ['✅ Perfect squares are not surds']
        },
        'intermediate': {
            'title': 'Simplifying Surds',
            'introduction': 'Write surds in simplest form',
            'principles': [
                {'title': 'Factor Method', 'content': 'Find the largest perfect square factor'}
            ],
            'examples': [
                {'question': 'Simplify √12', 'steps': ['√12 = √(4 × 3)', '= √4 × √3', '= 2√3'], 'answer': '2√3'}
            ],
            'tips': ['✅ Look for perfect square factors']
        },
        'advanced': {
            'title': 'Operations with Surds',
            'introduction': 'Add, multiply, rationalise surds',
            'principles': [
                {'title': 'Like Surds', 'content': 'Can only add/subtract like surds (same root)'}
            ],
            'examples': [
                {'question': '2√3 + 5√3', 'steps': ['Same root, add coefficients', '(2+5)√3'], 'answer': '7√3'}
            ],
            'tips': ['✅ Treat √3 like a variable']
        }
    },
    'complex_numbers_intro': {
        'beginner': {
            'title': 'What is i?',
            'introduction': 'The imaginary unit i = √-1',
            'principles': [
                {'title': 'Imaginary Unit', 'content': 'i² = -1, this allows us to work with √ of negative numbers'}
            ],
            'examples': [
                {'question': 'What is i²?', 'steps': ['By definition'], 'answer': '-1'}
            ],
            'tips': ['✅ Remember: i² = -1']
        },
        'intermediate': {
            'title': 'Adding Complex Numbers',
            'introduction': 'Add real parts and imaginary parts separately',
            'principles': [
                {'title': 'Addition', 'content': '(a + bi) + (c + di) = (a+c) + (b+d)i'}
            ],
            'examples': [
                {'question': '(3 + 2i) + (1 + 4i)', 'steps': ['Real: 3 + 1 = 4', 'Imaginary: 2i + 4i = 6i'], 'answer': '4 + 6i'}
            ],
            'tips': ['✅ Keep real and imaginary separate']
        },
        'advanced': {
            'title': 'Dividing Complex Numbers',
            'introduction': 'Divide complex numbers',
            'principles': [
                {'title': 'Simplification', 'content': 'Divide real and imaginary parts'}
            ],
            'examples': [
                {'question': '(6 + 3i) ÷ 3', 'steps': ['6/3 = 2', '3i/3 = i'], 'answer': '2 + i'}
            ],
            'tips': ['✅ Divide each part']
        }
    },
    'complex_numbers_expanded': {
        'beginner': {
            'title': 'Argand Diagram',
            'introduction': 'Plot complex numbers on Argand diagram',
            'principles': [
                {'title': 'Axes', 'content': 'Horizontal = real, Vertical = imaginary'}
            ],
            'examples': [
                {'question': 'Which axis is real?', 'steps': ['Real = horizontal (x-axis)'], 'answer': 'x-axis'}
            ],
            'tips': ['✅ x = real, y = imaginary']
        },
        'intermediate': {
            'title': 'Multiplication by i',
            'introduction': 'Understand i × (complex number)',
            'principles': [
                {'title': 'Rotation', 'content': 'Multiplying by i rotates 90° counterclockwise'}
            ],
            'examples': [
                {'question': 'i × (1 + 0i)', 'steps': ['i × 1 = i'], 'answer': 'i'}
            ],
            'tips': ['✅ i rotates 90°']
        },
        'advanced': {
            'title': 'Conjugates',
            'introduction': 'Find conjugate of complex numbers',
            'principles': [
                {'title': 'Conjugate', 'content': 'Change sign of imaginary part'}
            ],
            'examples': [
                {'question': 'Conjugate of 4 + 7i?', 'steps': ['Change imaginary sign', '4 - 7i'], 'answer': '4 - 7i'}
            ],
            'tips': ['✅ Flip imaginary sign only']
        }
    },
    'descriptive_statistics': {
        'beginner': {
            'title': 'Finding the Mean (Simple)',
            'introduction': 'Calculate the mean (average) of small datasets',
            'principles': [
                {'title': 'Mean Formula', 'content': 'Add all numbers, divide by how many there are'}
            ],
            'examples': [
                {'question': 'Mean of: 2, 2, 5, 12, 17', 'steps': ['Sum: 2+2+5+12+17 = 38', 'Count: 5 numbers', 'Mean: 38 ÷ 5 = 7.6'], 'answer': '7.6'}
            ],
            'tips': ['✅ Add all, then divide by count']
        },
        'intermediate': {
            'title': 'Mean of Larger Datasets',
            'introduction': 'Calculate mean with more numbers',
            'principles': [
                {'title': 'Same Process', 'content': 'Still add and divide, just more numbers'}
            ],
            'examples': [
                {'question': 'Mean of: 20, 27, 30, 34, 36, 39, 58', 'steps': ['Sum = 244', 'Count = 7', 'Mean = 244 ÷ 7 = 34.9'], 'answer': '34.9'}
            ],
            'tips': ['✅ Be careful adding larger numbers']
        },
        'advanced': {
            'title': 'Mean with Decimals',
            'introduction': 'Calculate mean of decimal numbers',
            'principles': [
                {'title': 'Decimal Data', 'content': 'Same method, careful with decimal arithmetic'}
            ],
            'examples': [
                {'question': 'Mean of: 12.1, 15.8, 20.0, 21.8, 41.8', 'steps': ['Sum = 111.5', 'Count = 5', 'Mean = 22.3'], 'answer': '22.3'}
            ],
            'tips': ['✅ Use calculator for decimal sums']
        }
    },
    'probability': {
        'beginner': {
            'title': 'Simple Probability',
            'introduction': 'Calculate basic probabilities: coin flips, dice',
            'principles': [
                {'title': 'Probability', 'content': 'P = favorable outcomes / total outcomes'}
            ],
            'examples': [
                {'question': 'P(heads on coin flip)?', 'steps': ['Favorable: 1 (heads)', 'Total: 2 (heads or tails)', 'P = 1/2'], 'answer': '1/2'}
            ],
            'tips': ['✅ Count carefully']
        },
        'intermediate': {
            'title': 'Compound Probability',
            'introduction': 'Two or more events: multiply probabilities',
            'principles': [
                {'title': 'AND Rule', 'content': 'P(A and B) = P(A) × P(B)'}
            ],
            'examples': [
                {'question': 'Two heads in a row?', 'steps': ['P(H) = 1/2', 'P(H and H) = 1/2 × 1/2 = 1/4'], 'answer': '1/4'}
            ],
            'tips': ['✅ Multiply for "and"']
        },
        'advanced': {
            'title': 'Conditional Probability',
            'introduction': 'Probability that depends on previous events',
            'principles': [
                {'title': 'Without Replacement', 'content': 'Probability changes after first draw'}
            ],
            'examples': [
                {'question': 'Two aces without replacement', 'steps': ['P(1st ace) = 4/52', 'P(2nd ace) = 3/51', 'P(both) = 4/52 × 3/51 = 1/221'], 'answer': '1/221'}
            ],
            'tips': ['✅ Update probabilities after each event']
        }
    },
    'sets': {
        'beginner': {
            'title': 'Union and Intersection',
            'introduction': 'Combine sets or find common elements',
            'principles': [
                {'title': 'Union (∪)', 'content': 'All elements from both sets'},
                {'title': 'Intersection (∩)', 'content': 'Only common elements'}
            ],
            'examples': [
                {'question': '{1,2,3} ∪ {3,4,5}?', 'steps': ['Combine all', 'Remove duplicates'], 'answer': '{1,2,3,4,5}'},
                {'question': '{1,2,3} ∩ {3,4,5}?', 'steps': ['Only common'], 'answer': '{3}'}
            ],
            'tips': ['✅ Union = all, Intersection = common']
        },
        'intermediate': {
            'title': 'Set Difference',
            'introduction': 'Elements in A but not in B: A - B',
            'principles': [
                {'title': 'Difference', 'content': 'In first set but not second'}
            ],
            'examples': [
                {'question': 'A={1,2,3,4}, B={3,4,5,6}, A-B?', 'steps': ['In A: 1,2,3,4', 'Remove what is in B: remove 3,4'], 'answer': '{1,2}'}
            ],
            'tips': ['✅ Start with first set, remove second']
        },
        'advanced': {
            'title': 'Cardinality Formulas',
            'introduction': 'Count elements using formulas',
            'principles': [
                {'title': 'Formula', 'content': '|A ∪ B| = |A| + |B| - |A ∩ B|'}
            ],
            'examples': [
                {'question': '|A|=5, |B|=7, |A∩B|=3, |A∪B|?', 'steps': ['5 + 7 - 3 = 9'], 'answer': '9'}
            ],
            'tips': ['✅ Subtract intersection to avoid double counting']
        }
    }
}


def migrate_tutorials():
    """Migrate all tutorials to the database"""
    
    print("=" * 60)
    print("TUTORIAL MIGRATION SCRIPT")
    print("=" * 60)
    
    # Connect to database
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all topics from database
    cursor.execute("SELECT id, topic_id FROM topics")
    db_topics = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"\nFound {len(db_topics)} topics in database")
    
    # Check if tutorials table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tutorials'")
    if not cursor.fetchone():
        print("Creating tutorials table...")
        cursor.execute('''
            CREATE TABLE tutorials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                title TEXT NOT NULL,
                introduction TEXT,
                principles TEXT,
                examples TEXT,
                tips TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        ''')
        conn.commit()
    
    # Migration stats
    migrated = 0
    skipped = 0
    not_found = []
    
    for topic_key, difficulties in TUTORIALS.items():
        if topic_key not in db_topics:
            not_found.append(topic_key)
            print(f"  ⚠ Topic '{topic_key}' not found in database - skipping")
            continue
        
        topic_db_id = db_topics[topic_key]
        
        for difficulty, content in difficulties.items():
            # Check if tutorial already exists
            cursor.execute(
                "SELECT id FROM tutorials WHERE topic_id = ? AND difficulty = ?",
                (topic_db_id, difficulty)
            )
            existing = cursor.fetchone()
            
            if existing:
                print(f"  ⏭ {topic_key}/{difficulty} already exists - skipping")
                skipped += 1
                continue
            
            # Insert tutorial
            cursor.execute('''
                INSERT INTO tutorials (topic_id, difficulty, title, introduction, principles, examples, tips)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                topic_db_id,
                difficulty,
                content.get('title', ''),
                content.get('introduction', ''),
                json.dumps(content.get('principles', [])),
                json.dumps(content.get('examples', [])),
                json.dumps(content.get('tips', []))
            ))
            migrated += 1
            print(f"  ✓ Migrated {topic_key}/{difficulty}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print(f"✓ Migrated: {migrated}")
    print(f"⏭ Skipped (already exist): {skipped}")
    if not_found:
        print(f"⚠ Topics not in database: {', '.join(not_found)}")
    print("\nRefresh your Admin dashboard to see the tutorials!")


if __name__ == "__main__":
    migrate_tutorials()
