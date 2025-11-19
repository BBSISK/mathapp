/**
 * TUTORIAL DATA STRUCTURE
 * 
 * This file contains all tutorial content for topics.
 * To add a new topic tutorial, simply add a new entry to the TUTORIALS object.
 * 
 * Structure:
 * TUTORIALS = {
 *   'topic_name': {
 *     'beginner': { title, introduction, principles, examples, tips },
 *     'intermediate': { ... },
 *     'advanced': { ... }
 *   }
 * }
 */

const TUTORIALS = {
    // Introductory Algebra Tutorial Content
    'introductory_algebra': {
        'beginner': {
            title: 'Collecting Like Terms',
            introduction: 'In this level, you\'ll learn to <strong>collect like terms</strong> - combining terms that have the same letter.',
            
            principles: [
                {
                    title: 'Like Terms',
                    content: '<strong>Like terms</strong> have exactly the same letter part.<br>• 3x and 5x are like terms (both have \'x\')<br>• 4y and 2y are like terms (both have \'y\')<br>• 3x and 5y are NOT like terms (different letters)'
                },
                {
                    title: 'How to Collect',
                    content: 'Think of it like fruit: 3 apples + 5 apples = 8 apples<br>Just add the numbers, keep the letter!'
                }
            ],
            
            examples: [
                {
                    question: 'Simplify: 4x + 3x',
                    steps: [
                        'Both terms have \'x\' - they are like terms ✓',
                        'Add the numbers: 4 + 3 = 7',
                        'Keep the letter: x'
                    ],
                    answer: '7x'
                },
                {
                    question: 'Simplify: 5y + 2y',
                    steps: [
                        'Both terms have \'y\' - they are like terms ✓',
                        'Add the numbers: 5 + 2 = 7',
                        'Keep the letter: y'
                    ],
                    answer: '7y'
                }
            ],
            
            tips: [
                '✅ Always keep the letter - it doesn\'t change!',
                '✅ Just add the numbers - ignore the letters when adding',
                '⚠️ Don\'t forget the letter: 4x + 3x = 7x (not 7)',
                '⚠️ Don\'t multiply: 2y + 3y = 5y (not 6y)'
            ]
        },
        
        'intermediate': {
            title: 'Substitution (One Variable)',
            introduction: 'In this level, you\'ll learn <strong>substitution</strong> - finding the value of expressions when you know what x equals.',
            
            principles: [
                {
                    title: 'What is Substitution?',
                    content: '<strong>Substitution</strong> means replacing a letter with its number value.<br>Example: If x = 5, then x + 3 means 5 + 3 = 8'
                },
                {
                    title: 'Use Brackets!',
                    content: 'Always use brackets when substituting.<br>If x = 4, write 3(4) not 34'
                }
            ],
            
            examples: [
                {
                    question: 'If x = 4, find the value of x + 7',
                    steps: [
                        'Write the expression: x + 7',
                        'Replace x with 4: (4) + 7',
                        'Calculate: 4 + 7'
                    ],
                    answer: '11'
                },
                {
                    question: 'If x = 5, find the value of 2x',
                    steps: [
                        'Write the expression: 2x (means 2 times x)',
                        'Replace x with 5 (use brackets!): 2(5)',
                        'Calculate: 2 × 5'
                    ],
                    answer: '10'
                }
            ],
            
            tips: [
                '✅ Always use brackets when substituting',
                '✅ Remember 2x means 2 × x (multiply!)',
                '✅ Follow BOMDAS - multiply before adding',
                '⚠️ Don\'t just stick numbers together: 3x when x=4 is 12, not 34'
            ]
        },
        
        'advanced': {
            title: 'Substitution (Two Variables)',
            introduction: 'In this level, you\'ll substitute <strong>two different variables</strong> (like x and y) in the same expression.',
            
            principles: [
                {
                    title: 'Multiple Variables',
                    content: 'Each letter can represent a different number!<br>Example: If x = 3 and y = 5, then x + y means 3 + 5 = 8'
                },
                {
                    title: 'Multiply First',
                    content: 'When you see 2x or 3y, multiply BEFORE adding/subtracting (BOMDAS!)'
                }
            ],
            
            examples: [
                {
                    question: 'If x = 4 and y = 3, find x + y',
                    steps: [
                        'Write: x + y',
                        'Replace both letters: (4) + (3)',
                        'Calculate: 4 + 3'
                    ],
                    answer: '7'
                },
                {
                    question: 'If x = 5 and y = 4, find 2x + y',
                    steps: [
                        'Write: 2x + y',
                        'Replace: 2(5) + (4)',
                        'Multiply first: 10 + 4',
                        'Then add: 14'
                    ],
                    answer: '14'
                }
            ],
            
            tips: [
                '✅ Keep track of which value goes with which letter',
                '✅ Use brackets for both variables',
                '✅ Multiply before you add/subtract (BOMDAS!)',
                '⚠️ Don\'t mix up the values: x=4, y=3 means x+y = 4+3, not 3+4... well, same answer, but you get the idea!'
            ]
        }
    }
    
    // FUTURE TOPICS - Just add them here following the same structure:
    /*
    'patterns': {
        'beginner': { ... },
        'intermediate': { ... },
        'advanced': { ... }
    },
    'functions': {
        'beginner': { ... },
        'intermediate': { ... },
        'advanced': { ... }
    }
    */
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TUTORIALS;
}
