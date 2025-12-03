#!/usr/bin/env python3
"""
Sets Question Generator for AgentMath.app

Generates Sets and Venn Diagram questions aligned with Irish Junior Cycle Mathematics:
- Set notation (element of, not element of, subset, proper subset, empty set, universal set)
- Venn diagrams (2-set and 3-set)
- Union, Intersection, Complement
- Set difference
- Cardinal number (#)
- Real-world contexts for 14-year-olds

Each Venn diagram comes with multiple question types testing different skills.
"""

import os
import random
import json
from datetime import datetime

# Chart generation with matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Circle, Rectangle
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# ============================================================================
# SET DATA GENERATORS
# ============================================================================

# Real-world contexts for sets (age-appropriate for 14-year-olds in Ireland)
CONTEXTS = {
    'sports': {
        'universal': 'students in a PE class',
        'sets': [
            {'name': 'F', 'label': 'plays Football', 'description': 'Students who play football'},
            {'name': 'H', 'label': 'plays Hurling', 'description': 'Students who play hurling'},
            {'name': 'R', 'label': 'plays Rugby', 'description': 'Students who play rugby'},
            {'name': 'B', 'label': 'plays Basketball', 'description': 'Students who play basketball'},
        ]
    },
    'music': {
        'universal': 'students in a year group',
        'sets': [
            {'name': 'P', 'label': 'plays Piano', 'description': 'Students who play piano'},
            {'name': 'G', 'label': 'plays Guitar', 'description': 'Students who play guitar'},
            {'name': 'D', 'label': 'plays Drums', 'description': 'Students who play drums'},
            {'name': 'V', 'label': 'sings in choir', 'description': 'Students who sing in choir'},
        ]
    },
    'subjects': {
        'universal': 'students choosing optional subjects',
        'sets': [
            {'name': 'A', 'label': 'studies Art', 'description': 'Students studying Art'},
            {'name': 'M', 'label': 'studies Music', 'description': 'Students studying Music'},
            {'name': 'G', 'label': 'studies German', 'description': 'Students studying German'},
            {'name': 'H', 'label': 'studies Home Ec', 'description': 'Students studying Home Economics'},
        ]
    },
    'technology': {
        'universal': 'teenagers surveyed about devices',
        'sets': [
            {'name': 'P', 'label': 'owns a Phone', 'description': 'Teens who own a smartphone'},
            {'name': 'T', 'label': 'owns a Tablet', 'description': 'Teens who own a tablet'},
            {'name': 'L', 'label': 'owns a Laptop', 'description': 'Teens who own a laptop'},
            {'name': 'C', 'label': 'owns a Console', 'description': 'Teens who own a gaming console'},
        ]
    },
    'food': {
        'universal': 'students in a canteen survey',
        'sets': [
            {'name': 'P', 'label': 'likes Pizza', 'description': 'Students who like pizza'},
            {'name': 'B', 'label': 'likes Burgers', 'description': 'Students who like burgers'},
            {'name': 'S', 'label': 'likes Salad', 'description': 'Students who like salad'},
            {'name': 'C', 'label': 'likes Chips', 'description': 'Students who like chips'},
        ]
    },
    'numbers': {
        'universal': 'numbers from 1 to 20',
        'sets': [
            {'name': 'E', 'label': 'Even numbers', 'description': 'Even numbers'},
            {'name': 'P', 'label': 'Prime numbers', 'description': 'Prime numbers'},
            {'name': 'M', 'label': 'Multiples of 3', 'description': 'Multiples of 3'},
            {'name': 'F', 'label': 'Factors of 20', 'description': 'Factors of 20'},
        ]
    },
}

# Color schemes for Venn diagrams
COLORS = {
    'set_a': '#667eea',      # Blue
    'set_b': '#f093fb',      # Pink
    'set_c': '#43e97b',      # Green
    'intersection': '#764ba2', # Purple
    'universal': '#f5f5f5',  # Light grey
    'outside': '#ffffff',    # White
}

ALPHA = 0.4  # Transparency for overlapping regions


def generate_number_sets(difficulty='beginner'):
    """Generate number-based sets for pure mathematical questions"""
    if difficulty == 'beginner':
        universal = list(range(1, 13))  # 1-12
    elif difficulty == 'intermediate':
        universal = list(range(1, 21))  # 1-20
    else:
        universal = list(range(1, 31))  # 1-30
    
    # Define possible set types
    set_definitions = [
        ('E', 'Even', lambda x: x % 2 == 0),
        ('O', 'Odd', lambda x: x % 2 == 1),
        ('P', 'Prime', lambda x: x > 1 and all(x % i != 0 for i in range(2, int(x**0.5) + 1))),
        ('M3', 'Multiples of 3', lambda x: x % 3 == 0),
        ('M4', 'Multiples of 4', lambda x: x % 4 == 0),
        ('M5', 'Multiples of 5', lambda x: x % 5 == 0),
        ('S', 'Square numbers', lambda x: int(x**0.5)**2 == x),
        ('F12', 'Factors of 12', lambda x: 12 % x == 0),
        ('F20', 'Factors of 20', lambda x: 20 % x == 0),
        ('L10', 'Less than 10', lambda x: x < 10),
        ('G5', 'Greater than 5', lambda x: x > 5),
    ]
    
    # Pick 2 set definitions
    chosen = random.sample(set_definitions, 2)
    
    set_a = {x for x in universal if chosen[0][2](x)}
    set_b = {x for x in universal if chosen[1][2](x)}
    
    return {
        'type': 'number',
        'universal': set(universal),
        'set_a': {'name': chosen[0][0], 'label': chosen[0][1], 'elements': set_a},
        'set_b': {'name': chosen[1][0], 'label': chosen[1][1], 'elements': set_b},
        'context': f"Let ξ = {{{', '.join(map(str, sorted(universal)))}}}"
    }


def generate_survey_sets(difficulty='beginner'):
    """Generate survey-based sets for real-world context questions"""
    context_key = random.choice(list(CONTEXTS.keys()))
    if context_key == 'numbers':
        context_key = 'sports'  # Avoid numbers context for survey
    
    context = CONTEXTS[context_key]
    chosen_sets = random.sample(context['sets'], 2)
    
    # Generate realistic numbers based on difficulty
    if difficulty == 'beginner':
        total = random.randint(20, 30)
        # Simple, non-overlapping friendly numbers
        only_a = random.randint(5, 10)
        only_b = random.randint(5, 10)
        both = random.randint(2, 5)
        neither = total - only_a - only_b - both
        if neither < 0:
            neither = random.randint(2, 5)
            total = only_a + only_b + both + neither
    elif difficulty == 'intermediate':
        total = random.randint(30, 50)
        only_a = random.randint(8, 15)
        only_b = random.randint(8, 15)
        both = random.randint(3, 8)
        neither = total - only_a - only_b - both
        if neither < 0:
            neither = random.randint(3, 8)
            total = only_a + only_b + both + neither
    else:
        total = random.randint(50, 100)
        only_a = random.randint(15, 30)
        only_b = random.randint(15, 30)
        both = random.randint(5, 15)
        neither = total - only_a - only_b - both
        if neither < 0:
            neither = random.randint(5, 12)
            total = only_a + only_b + both + neither
    
    return {
        'type': 'survey',
        'context_name': context_key,
        'universal_desc': context['universal'],
        'total': total,
        'set_a': {
            'name': chosen_sets[0]['name'],
            'label': chosen_sets[0]['label'],
            'description': chosen_sets[0]['description'],
            'only': only_a,
            'total': only_a + both,
        },
        'set_b': {
            'name': chosen_sets[1]['name'],
            'label': chosen_sets[1]['label'],
            'description': chosen_sets[1]['description'],
            'only': only_b,
            'total': only_b + both,
        },
        'both': both,
        'neither': neither,
        'context': f"A survey of {total} {context['universal']}"
    }


# ============================================================================
# VENN DIAGRAM CREATION
# ============================================================================

def create_two_set_venn(data, filepath, show_numbers=True):
    """Create and save a 2-set Venn diagram image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Draw universal set rectangle
    universal_rect = Rectangle((-3.5, -2.5), 7, 5, linewidth=2, 
                                edgecolor='black', facecolor=COLORS['universal'])
    ax.add_patch(universal_rect)
    
    # Draw circles for sets
    circle_a = Circle((-0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_a'], facecolor=COLORS['set_a'], alpha=ALPHA)
    circle_b = Circle((0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_b'], facecolor=COLORS['set_b'], alpha=ALPHA)
    
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)
    
    if data['type'] == 'survey' and show_numbers:
        # Add numbers to regions
        # Only A
        ax.text(-1.6, 0, str(data['set_a']['only']), fontsize=20, fontweight='bold',
                ha='center', va='center', color='#333')
        # Only B
        ax.text(1.6, 0, str(data['set_b']['only']), fontsize=20, fontweight='bold',
                ha='center', va='center', color='#333')
        # Both (intersection)
        ax.text(0, 0, str(data['both']), fontsize=20, fontweight='bold',
                ha='center', va='center', color='#333')
        # Neither
        ax.text(2.8, -1.8, str(data['neither']), fontsize=16, fontweight='bold',
                ha='center', va='center', color='#666')
    
    elif data['type'] == 'number' and show_numbers:
        set_a = data['set_a']['elements']
        set_b = data['set_b']['elements']
        only_a = set_a - set_b
        only_b = set_b - set_a
        both = set_a & set_b
        neither = data['universal'] - set_a - set_b
        
        # Format elements nicely
        def format_elements(s):
            if len(s) == 0:
                return '∅'
            elif len(s) <= 6:
                return '\n'.join([str(x) for x in sorted(s)])
            else:
                return f"{len(s)}\nelements"
        
        ax.text(-1.6, 0, format_elements(only_a), fontsize=12, fontweight='bold',
                ha='center', va='center', color='#333')
        ax.text(1.6, 0, format_elements(only_b), fontsize=12, fontweight='bold',
                ha='center', va='center', color='#333')
        ax.text(0, 0, format_elements(both), fontsize=12, fontweight='bold',
                ha='center', va='center', color='#333')
        ax.text(2.8, -1.8, format_elements(neither), fontsize=10,
                ha='center', va='center', color='#666')
    
    # Labels
    ax.text(-2.2, 2, data['set_a']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_a'], ha='center')
    ax.text(2.2, 2, data['set_b']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_b'], ha='center')
    ax.text(-3.2, 2.2, 'ξ', fontsize=16, fontweight='bold', color='#333')
    
    # Title
    if data['type'] == 'survey':
        title = f"{data['set_a']['name']} = {data['set_a']['label']}, {data['set_b']['name']} = {data['set_b']['label']}"
    else:
        title = f"{data['set_a']['name']} = {data['set_a']['label']}, {data['set_b']['name']} = {data['set_b']['label']}"
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_two_set_venn_blank(data, filepath):
    """Create a Venn diagram with question marks instead of numbers"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Draw universal set rectangle
    universal_rect = Rectangle((-3.5, -2.5), 7, 5, linewidth=2, 
                                edgecolor='black', facecolor=COLORS['universal'])
    ax.add_patch(universal_rect)
    
    # Draw circles for sets
    circle_a = Circle((-0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_a'], facecolor=COLORS['set_a'], alpha=ALPHA)
    circle_b = Circle((0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_b'], facecolor=COLORS['set_b'], alpha=ALPHA)
    
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)
    
    # Add question marks
    ax.text(-1.6, 0, '?', fontsize=28, fontweight='bold',
            ha='center', va='center', color='#e74c3c')
    ax.text(1.6, 0, '?', fontsize=28, fontweight='bold',
            ha='center', va='center', color='#e74c3c')
    ax.text(0, 0, '?', fontsize=28, fontweight='bold',
            ha='center', va='center', color='#e74c3c')
    ax.text(2.8, -1.8, '?', fontsize=22, fontweight='bold',
            ha='center', va='center', color='#e74c3c')
    
    # Labels
    ax.text(-2.2, 2, data['set_a']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_a'], ha='center')
    ax.text(2.2, 2, data['set_b']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_b'], ha='center')
    ax.text(-3.2, 2.2, 'ξ', fontsize=16, fontweight='bold', color='#333')
    
    # Title
    if data['type'] == 'survey':
        title = f"{data['set_a']['name']} = {data['set_a']['label']}, {data['set_b']['name']} = {data['set_b']['label']}"
    else:
        title = f"{data['set_a']['name']} = {data['set_a']['label']}, {data['set_b']['name']} = {data['set_b']['label']}"
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_shaded_venn(data, filepath, region):
    """Create a Venn diagram with a specific region shaded for identification questions"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Draw universal set rectangle
    universal_rect = Rectangle((-3.5, -2.5), 7, 5, linewidth=2, 
                                edgecolor='black', facecolor=COLORS['universal'])
    ax.add_patch(universal_rect)
    
    # Create the shaded region based on the region type
    # We'll use a different approach - draw circles and then highlight the region
    
    # Base circles (lighter)
    circle_a = Circle((-0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_a'], facecolor='white', alpha=0.3)
    circle_b = Circle((0.8, 0), 1.8, linewidth=2, 
                      edgecolor=COLORS['set_b'], facecolor='white', alpha=0.3)
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)
    
    # Shade the appropriate region
    highlight_color = '#ffd93d'  # Yellow for highlighting
    
    if region == 'intersection':  # A ∩ B
        # Draw the intersection region
        from matplotlib.patches import Wedge
        theta1 = -60
        theta2 = 60
        wedge1 = Wedge((-0.8, 0), 1.8, theta1, theta2, facecolor=highlight_color, edgecolor='none')
        wedge2 = Wedge((0.8, 0), 1.8, 180-theta2, 180-theta1, facecolor=highlight_color, edgecolor='none')
        ax.add_patch(wedge1)
        ax.add_patch(wedge2)
        # Highlight text
        ax.text(0, -2.8, 'Shaded region = ?', fontsize=14, fontweight='bold',
                ha='center', color='#333')
    
    elif region == 'only_a':  # A only (A - B or A ∩ B')
        circle_a_filled = Circle((-0.8, 0), 1.8, linewidth=0, 
                                  facecolor=highlight_color, alpha=0.8)
        circle_b_cover = Circle((0.8, 0), 1.8, linewidth=0, 
                                 facecolor='white')
        ax.add_patch(circle_a_filled)
        ax.add_patch(circle_b_cover)
        # Redraw borders
        circle_a_border = Circle((-0.8, 0), 1.8, linewidth=2, 
                                  edgecolor=COLORS['set_a'], facecolor='none')
        circle_b_border = Circle((0.8, 0), 1.8, linewidth=2, 
                                  edgecolor=COLORS['set_b'], facecolor='none')
        ax.add_patch(circle_a_border)
        ax.add_patch(circle_b_border)
        ax.text(0, -2.8, 'Shaded region = ?', fontsize=14, fontweight='bold',
                ha='center', color='#333')
    
    elif region == 'union':  # A ∪ B
        circle_a_filled = Circle((-0.8, 0), 1.8, linewidth=2, 
                                  edgecolor=COLORS['set_a'], facecolor=highlight_color, alpha=0.7)
        circle_b_filled = Circle((0.8, 0), 1.8, linewidth=2, 
                                  edgecolor=COLORS['set_b'], facecolor=highlight_color, alpha=0.7)
        ax.add_patch(circle_a_filled)
        ax.add_patch(circle_b_filled)
        ax.text(0, -2.8, 'Shaded region = ?', fontsize=14, fontweight='bold',
                ha='center', color='#333')
    
    # Labels
    ax.text(-2.2, 2, data['set_a']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_a'], ha='center')
    ax.text(2.2, 2, data['set_b']['name'], fontsize=18, fontweight='bold',
            color=COLORS['set_b'], ha='center')
    ax.text(-3.2, 2.2, 'ξ', fontsize=16, fontweight='bold', color='#333')
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3.5, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_wrong_answers(correct, difficulty, max_val=None):
    """Generate plausible wrong answers - ALWAYS returns at least 3"""
    wrong = set()
    
    # First pass: try to generate natural-looking wrong answers
    attempts = 0
    while len(wrong) < 4 and attempts < 30:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.randint(1, 5) * random.choice([-1, 1])
        elif difficulty == 'intermediate':
            offset = random.randint(2, 10) * random.choice([-1, 1])
        else:
            offset = random.randint(5, 20) * random.choice([-1, 1])
        
        candidate = int(correct + offset)
        
        if candidate >= 0 and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Fallback: if we still don't have enough, add simple offsets
    fallback_offsets = [1, 2, 3, 5, 10, -1, -2, 4, 6]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = int(correct + offset)
        if candidate >= 0 and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    return list(wrong)


def generate_survey_venn_questions(data, difficulty='beginner'):
    """Generate questions about a survey-based Venn diagram"""
    questions = []
    
    name_a = data['set_a']['name']
    name_b = data['set_b']['name']
    label_a = data['set_a']['label']
    label_b = data['set_b']['label']
    only_a = data['set_a']['only']
    only_b = data['set_b']['only']
    both = data['both']
    neither = data['neither']
    total = data['total']
    
    total_a = only_a + both
    total_b = only_b + both
    union = only_a + only_b + both
    
    # Question 1: Read intersection (∩)
    correct = both
    wrong = generate_wrong_answers(correct, difficulty, max_val=total)
    options = [correct] + wrong[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"How many students are in {name_a} ∩ {name_b} (both {label_a} AND {label_b})?",
        'options': [str(o) for o in options],
        'correct': options.index(correct),
        'explanation': f"The intersection {name_a} ∩ {name_b} contains students who {label_a} AND {label_b}. Reading from the overlapping region: {both} students.",
        'difficulty': difficulty,
    })
    
    # Question 2: Read only one set
    correct = only_a
    wrong = generate_wrong_answers(correct, difficulty, max_val=total)
    options = [correct] + wrong[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"How many students ONLY {label_a} (not {label_b})?",
        'options': [str(o) for o in options],
        'correct': options.index(correct),
        'explanation': f"Looking at the region in {name_a} but NOT in {name_b}: {only_a} students.",
        'difficulty': difficulty,
    })
    
    # Question 3: Total in a set (using notation)
    correct = total_a
    wrong = generate_wrong_answers(correct, difficulty, max_val=total)
    options = [correct] + wrong[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"What is #{name_a} (the total number who {label_a})?",
        'options': [str(o) for o in options],
        'correct': options.index(correct),
        'explanation': f"#{name_a} = only {name_a} + both = {only_a} + {both} = {total_a}",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Union (∪)
        correct = union
        wrong = generate_wrong_answers(correct, difficulty, max_val=total)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"How many students are in {name_a} ∪ {name_b} (at least one of the activities)?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{name_a} ∪ {name_b} = only {name_a} + both + only {name_b} = {only_a} + {both} + {only_b} = {union}. Or use: #{name_a} + #{name_b} - #{name_a} ∩ {name_b} = {total_a} + {total_b} - {both} = {union}",
            'difficulty': difficulty,
        })
        
        # Question 5: Complement
        correct = total - total_a
        wrong = generate_wrong_answers(correct, difficulty, max_val=total)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"How many students are in {name_a}' (do NOT {label_a})?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{name_a}' = total - #{name_a} = {total} - {total_a} = {total - total_a}",
            'difficulty': difficulty,
        })
    
    if difficulty == 'advanced':
        # Question 6: Set difference
        correct = only_a
        wrong = generate_wrong_answers(correct, difficulty, max_val=total)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is #{name_a} \\ {name_b} (in {name_a} but not in {name_b})?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{name_a} \\ {name_b} represents elements in {name_a} but NOT in {name_b}. This equals {only_a}.",
            'difficulty': difficulty,
        })
        
        # Question 7: Complex expression
        # (A ∪ B)'
        correct = neither
        wrong = generate_wrong_answers(correct, difficulty, max_val=total)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"How many students are in ({name_a} ∪ {name_b})' (neither activity)?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"({name_a} ∪ {name_b})' = students not in the union = {neither}. Or: total - union = {total} - {union} = {neither}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_number_set_questions(data, difficulty='beginner'):
    """Generate questions about number-based sets"""
    questions = []
    
    name_a = data['set_a']['name']
    name_b = data['set_b']['name']
    label_a = data['set_a']['label']
    label_b = data['set_b']['label']
    set_a = data['set_a']['elements']
    set_b = data['set_b']['elements']
    universal = data['universal']
    
    intersection = set_a & set_b
    union = set_a | set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    complement_a = universal - set_a
    neither = universal - union
    
    # Question 1: Intersection count
    correct = len(intersection)
    wrong = generate_wrong_answers(correct, difficulty, max_val=len(universal))
    options = [correct] + wrong[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"What is #{name_a} ∩ {name_b}?",
        'options': [str(o) for o in options],
        'correct': options.index(correct),
        'explanation': f"{name_a} ∩ {name_b} = {{{', '.join(map(str, sorted(intersection)))}}} so #{name_a} ∩ {name_b} = {len(intersection)}",
        'difficulty': difficulty,
    })
    
    # Question 2: Membership question
    test_element = random.choice(list(universal))
    in_a = test_element in set_a
    in_b = test_element in set_b
    
    if in_a and in_b:
        correct = f"{name_a} ∩ {name_b}"
        wrong_options = [f"{name_a} only", f"{name_b} only", "Neither"]
    elif in_a:
        correct = f"{name_a} only"
        wrong_options = [f"{name_a} ∩ {name_b}", f"{name_b} only", "Neither"]
    elif in_b:
        correct = f"{name_b} only"
        wrong_options = [f"{name_a} only", f"{name_a} ∩ {name_b}", "Neither"]
    else:
        correct = "Neither"
        wrong_options = [f"{name_a} only", f"{name_b} only", f"{name_a} ∩ {name_b}"]
    
    options = [correct] + wrong_options
    random.shuffle(options)
    
    questions.append({
        'question_text': f"In which region of the Venn diagram does {test_element} belong?",
        'options': options,
        'correct': options.index(correct),
        'explanation': f"{test_element} is {'in' if in_a else 'not in'} {name_a} ({label_a}) and {'in' if in_b else 'not in'} {name_b} ({label_b}).",
        'difficulty': difficulty,
    })
    
    # Question 3: Union count
    correct = len(union)
    wrong = generate_wrong_answers(correct, difficulty, max_val=len(universal))
    options = [correct] + wrong[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"What is #{name_a} ∪ {name_b}?",
        'options': [str(o) for o in options],
        'correct': options.index(correct),
        'explanation': f"{name_a} ∪ {name_b} = {{{', '.join(map(str, sorted(union)))}}} so #{name_a} ∪ {name_b} = {len(union)}",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Complement
        correct = len(complement_a)
        wrong = generate_wrong_answers(correct, difficulty, max_val=len(universal))
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is #{name_a}'?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{name_a}' = elements NOT in {name_a} = {{{', '.join(map(str, sorted(complement_a)))}}} so #{name_a}' = {len(complement_a)}",
            'difficulty': difficulty,
        })
        
        # Question 5: List elements in intersection
        if len(intersection) > 0 and len(intersection) <= 5:
            correct_str = ', '.join(map(str, sorted(intersection)))
            # Generate wrong answers by slightly modifying
            wrong_sets = []
            for _ in range(3):
                modified = set(intersection)
                if len(modified) > 0 and random.random() > 0.5:
                    modified.discard(random.choice(list(modified)))
                extra = random.choice(list(universal - intersection))
                modified.add(extra)
                wrong_sets.append(', '.join(map(str, sorted(modified))))
            
            options = [correct_str] + wrong_sets
            random.shuffle(options)
            
            questions.append({
                'question_text': f"List all elements in {name_a} ∩ {name_b}:",
                'options': options,
                'correct': options.index(correct_str),
                'explanation': f"{name_a} = {{{', '.join(map(str, sorted(set_a)))}}}, {name_b} = {{{', '.join(map(str, sorted(set_b)))}}}. The intersection is {{{correct_str}}}.",
                'difficulty': difficulty,
            })
    
    if difficulty == 'advanced':
        # Question 6: Set difference
        correct = len(only_a)
        wrong = generate_wrong_answers(correct, difficulty, max_val=len(universal))
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is #{name_a} \\ {name_b}?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{name_a} \\ {name_b} = elements in {name_a} but NOT in {name_b} = {{{', '.join(map(str, sorted(only_a)))}}} so the answer is {len(only_a)}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_notation_questions(difficulty='beginner'):
    """Generate pure set notation questions without Venn diagram"""
    questions = []
    
    if difficulty == 'beginner':
        # Basic notation recognition
        notation_qs = [
            {
                'question_text': "What does the symbol ∩ mean in set notation?",
                'correct': "Intersection (AND)",
                'wrong': ["Union (OR)", "Complement (NOT)", "Subset of"],
            },
            {
                'question_text': "What does the symbol ∪ mean in set notation?",
                'correct': "Union (OR)",
                'wrong': ["Intersection (AND)", "Complement (NOT)", "Element of"],
            },
            {
                'question_text': "What does A' mean in set notation?",
                'correct': "The complement of A (NOT in A)",
                'wrong': ["A squared", "A intersection B", "A union B"],
            },
            {
                'question_text': "What does the symbol ∈ mean?",
                'correct': "Is an element of",
                'wrong': ["Is not an element of", "Is a subset of", "Is equal to"],
            },
            {
                'question_text': "What does ∅ represent?",
                'correct': "The empty set (no elements)",
                'wrong': ["The universal set", "Zero", "Infinity"],
            },
            {
                'question_text': "What does #A mean?",
                'correct': "The number of elements in set A",
                'wrong': ["A is empty", "The complement of A", "A squared"],
            },
        ]
    elif difficulty == 'intermediate':
        notation_qs = [
            {
                'question_text': "If A = {1, 2, 3} and B = {2, 3, 4}, what is A ∩ B?",
                'correct': "{2, 3}",
                'wrong': ["{1, 2, 3, 4}", "{1, 4}", "{1}"],
            },
            {
                'question_text': "If A = {1, 2, 3} and B = {2, 3, 4}, what is A ∪ B?",
                'correct': "{1, 2, 3, 4}",
                'wrong': ["{2, 3}", "{1, 4}", "{2}"],
            },
            {
                'question_text': "If ξ = {1, 2, 3, 4, 5} and A = {1, 3, 5}, what is A'?",
                'correct': "{2, 4}",
                'wrong': ["{1, 3, 5}", "{1, 2, 3, 4, 5}", "∅"],
            },
            {
                'question_text': "What does A ⊂ B mean?",
                'correct': "A is a proper subset of B",
                'wrong': ["A equals B", "A contains B", "A intersects B"],
            },
            {
                'question_text': "If A = {2, 4, 6} and B = {1, 2, 3, 4, 5, 6}, which is true?",
                'correct': "A ⊂ B",
                'wrong': ["B ⊂ A", "A = B", "A ∩ B = ∅"],
            },
        ]
    else:  # advanced
        notation_qs = [
            {
                'question_text': "If #A = 10, #B = 8, and #(A ∩ B) = 3, what is #(A ∪ B)?",
                'correct': "15",
                'wrong': ["18", "21", "5"],
            },
            {
                'question_text': "If #ξ = 50, #A = 20, and #A' = 30, is this consistent?",
                'correct': "Yes, because #A + #A' = #ξ",
                'wrong': ["No, the numbers don't add up", "Yes, but only if A = B", "Cannot determine"],
            },
            {
                'question_text': "What is (A ∩ B)' equivalent to?",
                'correct': "A' ∪ B' (De Morgan's Law)",
                'wrong': ["A' ∩ B'", "(A ∪ B)", "A \\ B"],
            },
            {
                'question_text': "If A and B are disjoint sets, what is A ∩ B?",
                'correct': "∅ (empty set)",
                'wrong': ["A ∪ B", "A", "B"],
            },
            {
                'question_text': "What is A \\ B also written as?",
                'correct': "A ∩ B'",
                'wrong': ["A ∪ B'", "A' ∩ B", "(A ∩ B)'"],
            },
        ]
    
    # Pick some questions
    selected = random.sample(notation_qs, min(3, len(notation_qs)))
    
    for q in selected:
        options = [q['correct']] + q['wrong']
        random.shuffle(options)
        questions.append({
            'question_text': q['question_text'],
            'options': options,
            'correct': options.index(q['correct']),
            'explanation': f"The correct answer is: {q['correct']}",
            'difficulty': difficulty,
        })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_set_questions(question_type, difficulty, count=5, output_dir='static/question_images'):
    """
    Generate sets questions with Venn diagram images.
    
    Args:
        question_type: 'survey', 'number', 'notation', or 'mixed'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of question sets to generate
        output_dir: Directory to save Venn diagram images
    
    Returns:
        List of question dictionaries with image paths
    """
    if question_type != 'notation' and not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not installed. Run: pip install matplotlib --user'}
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_questions = []
    
    for i in range(count):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if question_type == 'survey' or (question_type == 'mixed' and random.random() > 0.5):
            # Survey-based Venn diagram
            data = generate_survey_sets(difficulty)
            questions = generate_survey_venn_questions(data, difficulty)
            
            filename = f"venn_survey_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            
            if create_two_set_venn(data, filepath):
                image_url = f"/static/question_images/{filename}"
                caption = f"Venn diagram: {data['context']}"
                
                for q in questions:
                    q['image_url'] = image_url
                    q['image_caption'] = caption
                    q['topic'] = 'sets'
                    all_questions.append(q)
        
        elif question_type == 'number' or question_type == 'mixed':
            # Number-based Venn diagram
            data = generate_number_sets(difficulty)
            questions = generate_number_set_questions(data, difficulty)
            
            filename = f"venn_number_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            
            if create_two_set_venn(data, filepath):
                image_url = f"/static/question_images/{filename}"
                caption = f"Venn diagram: {data['context']}"
                
                for q in questions:
                    q['image_url'] = image_url
                    q['image_caption'] = caption
                    q['topic'] = 'sets'
                    all_questions.append(q)
        
        elif question_type == 'notation':
            # Pure notation questions (no image)
            questions = generate_notation_questions(difficulty)
            for q in questions:
                q['image_url'] = None
                q['image_caption'] = None
                q['topic'] = 'sets'
                all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_sets_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for sets question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-sets-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_sets_questions():
        """Generate sets-based questions with Venn diagrams"""
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({
                'error': 'matplotlib not installed. Run: pip install matplotlib --user'
            }), 400
        
        data = request.json or {}
        
        question_types = data.get('question_types', ['survey', 'number', 'notation'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        sets_per_type = data.get('sets_per_type', 3)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for q_type in question_types:
            for difficulty in difficulties:
                questions = generate_set_questions(
                    question_type=q_type,
                    difficulty=difficulty,
                    count=sets_per_type,
                    output_dir=output_dir
                )
                
                if isinstance(questions, dict) and 'error' in questions:
                    continue
                
                for q in questions:
                    # Validate question has exactly 4 options
                    if 'options' not in q or len(q['options']) != 4:
                        skipped_count += 1
                        continue
                    
                    # Check for duplicate
                    existing = db.session.execute(text("""
                        SELECT id FROM questions 
                        WHERE topic = :topic AND difficulty = :difficulty AND question_text = :question_text
                    """), {
                        'topic': 'sets',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='sets',
                        difficulty=q['difficulty'],
                        question_text=q['question_text'],
                        option_a=str(q['options'][0]),
                        option_b=str(q['options'][1]),
                        option_c=str(q['options'][2]),
                        option_d=str(q['options'][3]),
                        correct_answer=q['correct'],
                        explanation=q['explanation'],
                        image_url=q.get('image_url'),
                        image_caption=q.get('image_caption'),
                    )
                    db.session.add(new_question)
                    saved_count += 1
                    all_generated.append({
                        'type': q_type,
                        'difficulty': difficulty,
                        'question': q['question_text'][:50] + '...'
                    })
        
        db.session.commit()
        
        # Get updated counts
        counts = {}
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = 'sets' AND difficulty = :difficulty"
            ), {'difficulty': difficulty}).fetchone()[0]
            counts[difficulty] = count
        
        return jsonify({
            'success': True,
            'message': f'Generated {saved_count} questions. {skipped_count} duplicates skipped.',
            'saved': saved_count,
            'skipped': skipped_count,
            'counts': counts,
            'total': sum(counts.values()),
            'sample_questions': all_generated[:10]
        })
    
    @app.route('/api/admin/sets-generator-status', methods=['GET'])
    @admin_required_api
    def sets_generator_status():
        """Check if sets generator is available"""
        from flask import jsonify
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'question_types': ['survey', 'number', 'notation', 'mixed'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("Testing Sets Question Generator...")
    print("=" * 50)
    
    if not MATPLOTLIB_AVAILABLE:
        print("WARNING: matplotlib not installed - Venn diagrams won't be generated")
        print("Run: pip install matplotlib")
    
    # Test each question type
    for q_type in ['survey', 'number', 'notation']:
        print(f"\n{q_type.upper()} QUESTIONS:")
        questions = generate_set_questions(q_type, 'intermediate', count=1, output_dir='/tmp/test_sets')
        
        if isinstance(questions, dict) and 'error' in questions:
            print(f"  Error: {questions['error']}")
        else:
            print(f"  Generated {len(questions)} questions")
            for q in questions[:3]:
                print(f"  - {q['question_text'][:60]}...")
                print(f"    Options: {q['options']}")
                print(f"    Correct: {q['correct']}")
