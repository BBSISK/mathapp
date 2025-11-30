#!/usr/bin/env python3
"""
Chart Question Generator for Math Master

Generates descriptive statistics questions with auto-generated charts:
- Bar Charts
- Histograms  
- Pie Charts
- Line Graphs

Each chart comes with multiple question types testing different skills.
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
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# ============================================================================
# CHART DATA GENERATORS
# ============================================================================

# Real-world contexts for charts (age-appropriate for 14-year-olds)
CONTEXTS = {
    'sports': {
        'bar': [
            {'title': 'Goals Scored by Players', 'categories': ['Emma', 'Liam', 'Sophie', 'Jack', 'Aoife'], 'unit': 'goals'},
            {'title': 'Points per Match', 'categories': ['Match 1', 'Match 2', 'Match 3', 'Match 4', 'Match 5'], 'unit': 'points'},
            {'title': 'Training Hours per Week', 'categories': ['Running', 'Weights', 'Skills', 'Recovery', 'Matches'], 'unit': 'hours'},
        ],
        'pie': [
            {'title': 'Time Spent in Training', 'categories': ['Cardio', 'Strength', 'Skills', 'Rest'], 'unit': '%'},
            {'title': 'Team Budget Allocation', 'categories': ['Equipment', 'Travel', 'Coaching', 'Facilities'], 'unit': '%'},
        ],
        'line': [
            {'title': 'Team Points Over Season', 'x_label': 'Week', 'y_label': 'Total Points', 'periods': 8},
            {'title': 'Player Fitness Score', 'x_label': 'Month', 'y_label': 'Fitness Score', 'periods': 6},
        ],
    },
    'school': {
        'bar': [
            {'title': 'Students per Subject', 'categories': ['Maths', 'English', 'Science', 'History', 'Art'], 'unit': 'students'},
            {'title': 'Library Books Borrowed', 'categories': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'unit': 'books'},
            {'title': 'Test Scores by Class', 'categories': ['1st Year', '2nd Year', '3rd Year', 'TY', '5th Year'], 'unit': 'average %'},
        ],
        'pie': [
            {'title': 'Favourite School Subjects', 'categories': ['Maths', 'PE', 'Art', 'Science', 'Music'], 'unit': '%'},
            {'title': 'How Students Travel to School', 'categories': ['Walk', 'Bus', 'Car', 'Cycle'], 'unit': '%'},
        ],
        'line': [
            {'title': 'Homework Completion Rate', 'x_label': 'Week', 'y_label': 'Completion %', 'periods': 6},
            {'title': 'Library Visitors per Month', 'x_label': 'Month', 'y_label': 'Visitors', 'periods': 5},
        ],
    },
    'food': {
        'bar': [
            {'title': 'Favourite Ice Cream Flavours', 'categories': ['Vanilla', 'Chocolate', 'Strawberry', 'Mint', 'Cookie'], 'unit': 'votes'},
            {'title': 'Fruit Sold at Market', 'categories': ['Apples', 'Bananas', 'Oranges', 'Grapes', 'Berries'], 'unit': 'kg'},
            {'title': 'Café Drinks Sold', 'categories': ['Tea', 'Coffee', 'Hot Choc', 'Juice', 'Water'], 'unit': 'cups'},
        ],
        'pie': [
            {'title': 'Pizza Toppings Ordered', 'categories': ['Pepperoni', 'Cheese', 'Veggie', 'Hawaiian'], 'unit': '%'},
            {'title': 'Lunch Choices', 'categories': ['Sandwich', 'Pasta', 'Salad', 'Soup', 'Other'], 'unit': '%'},
        ],
        'line': [
            {'title': 'Ice Cream Sales by Month', 'x_label': 'Month', 'y_label': 'Sales (€)', 'periods': 6},
            {'title': 'Daily Café Customers', 'x_label': 'Day', 'y_label': 'Customers', 'periods': 7},
        ],
    },
    'environment': {
        'bar': [
            {'title': 'Recycling by Material', 'categories': ['Paper', 'Plastic', 'Glass', 'Metal', 'Compost'], 'unit': 'kg'},
            {'title': 'Trees Planted by Class', 'categories': ['1A', '1B', '2A', '2B', '3A'], 'unit': 'trees'},
            {'title': 'Water Usage per Day', 'categories': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'unit': 'litres'},
        ],
        'pie': [
            {'title': 'School Energy Sources', 'categories': ['Solar', 'Wind', 'Grid', 'Other'], 'unit': '%'},
            {'title': 'Waste Composition', 'categories': ['Recyclable', 'Compost', 'Landfill'], 'unit': '%'},
        ],
        'line': [
            {'title': 'Monthly Rainfall', 'x_label': 'Month', 'y_label': 'Rainfall (mm)', 'periods': 6},
            {'title': 'Average Temperature', 'x_label': 'Month', 'y_label': 'Temp (°C)', 'periods': 12},
        ],
    },
    'technology': {
        'bar': [
            {'title': 'App Downloads by Platform', 'categories': ['iOS', 'Android', 'Windows', 'Mac', 'Web'], 'unit': 'downloads'},
            {'title': 'Screen Time by Activity', 'categories': ['Social', 'Games', 'Videos', 'Study', 'Other'], 'unit': 'hours'},
            {'title': 'Device Ownership in Class', 'categories': ['Phone', 'Tablet', 'Laptop', 'Console', 'PC'], 'unit': 'students'},
        ],
        'pie': [
            {'title': 'Social Media Usage', 'categories': ['TikTok', 'Instagram', 'YouTube', 'Snapchat', 'Other'], 'unit': '%'},
            {'title': 'How Teens Use Phones', 'categories': ['Messaging', 'Social', 'Games', 'Music', 'Study'], 'unit': '%'},
        ],
        'line': [
            {'title': 'Website Visitors per Week', 'x_label': 'Week', 'y_label': 'Visitors', 'periods': 8},
            {'title': 'Game Players Online', 'x_label': 'Hour', 'y_label': 'Players', 'periods': 6},
        ],
    },
}

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Color schemes for charts
COLORS = {
    'bar': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'],
    'pie': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#ffecd2', '#fcb69f', '#a1c4fd', '#c2e9fb'],
    'line': '#667eea',
    'histogram': '#667eea',
}


def generate_bar_data(difficulty='beginner'):
    """Generate data for a bar chart"""
    context = random.choice(list(CONTEXTS.keys()))
    template = random.choice(CONTEXTS[context]['bar'])
    
    categories = template['categories']
    
    # Generate values based on difficulty
    if difficulty == 'beginner':
        # Simple round numbers
        values = [random.randint(2, 10) * 5 for _ in categories]
    elif difficulty == 'intermediate':
        # Mix of values
        values = [random.randint(10, 100) for _ in categories]
    else:  # advanced
        # Larger, more complex numbers
        values = [random.randint(50, 500) for _ in categories]
    
    return {
        'type': 'bar',
        'title': template['title'],
        'categories': categories,
        'values': values,
        'unit': template['unit'],
        'context': context,
    }


def generate_pie_data(difficulty='beginner'):
    """Generate data for a pie chart (percentages that sum to 100)"""
    context = random.choice(list(CONTEXTS.keys()))
    template = random.choice(CONTEXTS[context]['pie'])
    
    categories = template['categories']
    n = len(categories)
    
    # Generate percentages that sum to 100
    if difficulty == 'beginner':
        # Simple percentages divisible by 5 or 10
        base_values = [random.choice([10, 15, 20, 25, 30]) for _ in range(n-1)]
        remaining = 100 - sum(base_values)
        if remaining < 5:
            base_values[-1] -= (5 - remaining)
            remaining = 5
        values = base_values + [remaining]
    elif difficulty == 'intermediate':
        # Any whole percentages
        base_values = [random.randint(10, 40) for _ in range(n-1)]
        total = sum(base_values)
        if total >= 95:
            factor = 80 / total
            base_values = [int(v * factor) for v in base_values]
        remaining = 100 - sum(base_values)
        values = base_values + [remaining]
    else:  # advanced
        # Can include decimal percentages
        base_values = [random.randint(10, 35) for _ in range(n-1)]
        total = sum(base_values)
        if total >= 90:
            factor = 75 / total
            base_values = [int(v * factor) for v in base_values]
        remaining = 100 - sum(base_values)
        values = base_values + [remaining]
    
    # Shuffle so the "remaining" isn't always last
    combined = list(zip(categories, values))
    random.shuffle(combined)
    categories, values = zip(*combined)
    
    return {
        'type': 'pie',
        'title': template['title'],
        'categories': list(categories),
        'values': list(values),
        'unit': '%',
        'context': context,
    }


def generate_line_data(difficulty='beginner'):
    """Generate data for a line graph"""
    context = random.choice(list(CONTEXTS.keys()))
    template = random.choice(CONTEXTS[context]['line'])
    
    periods = template['periods']
    
    # Generate x-axis labels
    if 'Month' in template['x_label']:
        x_labels = MONTHS[:periods]
    elif 'Week' in template['x_label']:
        x_labels = [f'W{i+1}' for i in range(periods)]
    elif 'Day' in template['x_label']:
        x_labels = DAYS[:periods]
    else:
        x_labels = [f'{template["x_label"]} {i+1}' for i in range(periods)]
    
    # Generate values with a trend
    if difficulty == 'beginner':
        # Simple increasing or decreasing trend
        trend = random.choice(['up', 'down', 'stable'])
        if trend == 'up':
            base = random.randint(20, 40)
            values = [base + i * random.randint(5, 10) for i in range(periods)]
        elif trend == 'down':
            base = random.randint(60, 80)
            values = [base - i * random.randint(5, 10) for i in range(periods)]
        else:
            base = random.randint(40, 60)
            values = [base + random.randint(-5, 5) for _ in range(periods)]
    elif difficulty == 'intermediate':
        # More variation
        base = random.randint(30, 70)
        values = [base]
        for _ in range(periods - 1):
            change = random.randint(-15, 20)
            values.append(max(10, values[-1] + change))
    else:  # advanced
        # Complex patterns
        base = random.randint(100, 200)
        values = [base]
        for _ in range(periods - 1):
            change = random.randint(-30, 40)
            values.append(max(20, values[-1] + change))
    
    return {
        'type': 'line',
        'title': template['title'],
        'x_labels': x_labels,
        'values': values,
        'x_label': template['x_label'],
        'y_label': template['y_label'],
        'context': context,
    }


def generate_histogram_data(difficulty='beginner'):
    """Generate data for a histogram (frequency distribution)"""
    # Contexts for histograms
    histogram_contexts = [
        {'title': 'Test Scores Distribution', 'x_label': 'Score Range', 'y_label': 'Number of Students'},
        {'title': 'Heights of Students', 'x_label': 'Height (cm)', 'y_label': 'Frequency'},
        {'title': 'Time to Complete Homework', 'x_label': 'Time (minutes)', 'y_label': 'Number of Students'},
        {'title': 'Daily Steps Walked', 'x_label': 'Steps (thousands)', 'y_label': 'Number of Days'},
        {'title': 'Ages at Concert', 'x_label': 'Age Group', 'y_label': 'Number of People'},
    ]
    
    template = random.choice(histogram_contexts)
    
    if difficulty == 'beginner':
        # 4-5 bins with simple frequencies
        bins = ['0-20', '21-40', '41-60', '61-80', '81-100']
        frequencies = [random.randint(2, 8) for _ in bins]
    elif difficulty == 'intermediate':
        # 5-6 bins
        bins = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90']
        frequencies = [random.randint(3, 15) for _ in bins]
    else:  # advanced
        # More bins with varied frequencies
        bins = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80']
        frequencies = [random.randint(1, 20) for _ in bins]
    
    return {
        'type': 'histogram',
        'title': template['title'],
        'bins': bins,
        'frequencies': frequencies,
        'x_label': template['x_label'],
        'y_label': template['y_label'],
    }


# ============================================================================
# CHART IMAGE GENERATORS
# ============================================================================

def create_bar_chart(data, filepath):
    """Create and save a bar chart image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = COLORS['bar'][:len(data['categories'])]
    bars = ax.bar(data['categories'], data['values'], color=colors, edgecolor='white', linewidth=1.5)
    
    ax.set_title(data['title'], fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(data['unit'].capitalize(), fontsize=12)
    
    # Add value labels on bars
    for bar, val in zip(bars, data['values']):
        height = bar.get_height()
        ax.annotate(f'{val}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_pie_chart(data, filepath):
    """Create and save a pie chart image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = COLORS['pie'][:len(data['categories'])]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        data['values'],
        labels=data['categories'],
        colors=colors,
        autopct='%1.0f%%',
        startangle=90,
        pctdistance=0.75,
        explode=[0.02] * len(data['categories'])
    )
    
    # Style the labels
    for text in texts:
        text.set_fontsize(12)
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.set_title(data['title'], fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_line_chart(data, filepath):
    """Create and save a line graph image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(data['x_labels'], data['values'], 
            color=COLORS['line'], linewidth=3, marker='o', 
            markersize=10, markerfacecolor='white', markeredgewidth=2)
    
    # Add value labels at each point
    for i, (x, y) in enumerate(zip(data['x_labels'], data['values'])):
        ax.annotate(f'{y}',
                    xy=(i, y),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title(data['title'], fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(data['x_label'], fontsize=12)
    ax.set_ylabel(data['y_label'], fontsize=12)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    
    # Add some padding to y-axis
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - (ymax - ymin) * 0.1, ymax + (ymax - ymin) * 0.15)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_histogram(data, filepath):
    """Create and save a histogram image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_positions = range(len(data['bins']))
    bars = ax.bar(x_positions, data['frequencies'], 
                  color=COLORS['histogram'], edgecolor='white', linewidth=1.5, width=0.8)
    
    ax.set_xticks(x_positions)
    ax.set_xticklabels(data['bins'], rotation=0)
    
    # Add frequency labels on bars
    for bar, freq in zip(bars, data['frequencies']):
        height = bar.get_height()
        ax.annotate(f'{freq}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_title(data['title'], fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(data['x_label'], fontsize=12)
    ax.set_ylabel(data['y_label'], fontsize=12)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_bar_questions(data, difficulty='beginner'):
    """Generate questions about a bar chart"""
    questions = []
    categories = data['categories']
    values = data['values']
    unit = data['unit']
    
    max_val = max(values)
    min_val = min(values)
    max_cat = categories[values.index(max_val)]
    min_cat = categories[values.index(min_val)]
    total = sum(values)
    mean = round(total / len(values), 1)
    
    # Question 1: Read a specific value
    cat_idx = random.randint(0, len(categories) - 1)
    correct_val = values[cat_idx]
    wrong_answers = generate_wrong_answers(correct_val, difficulty)
    options = [correct_val] + wrong_answers[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"According to the chart, how many {unit} does '{categories[cat_idx]}' have?",
        'options': [str(o) for o in options],
        'correct': options.index(correct_val),
        'explanation': f"Looking at the bar for '{categories[cat_idx]}', we can read the value as {correct_val} {unit}.",
        'difficulty': difficulty,
    })
    
    # Question 2: Find the maximum
    wrong_cats = [c for c in categories if c != max_cat]
    random.shuffle(wrong_cats)
    options = [max_cat] + wrong_cats[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"Which category has the highest number of {unit}?",
        'options': options,
        'correct': options.index(max_cat),
        'explanation': f"'{max_cat}' has the highest value with {max_val} {unit}.",
        'difficulty': difficulty,
    })
    
    # Question 3: Find the minimum
    wrong_cats = [c for c in categories if c != min_cat]
    random.shuffle(wrong_cats)
    options = [min_cat] + wrong_cats[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"Which category has the lowest number of {unit}?",
        'options': options,
        'correct': options.index(min_cat),
        'explanation': f"'{min_cat}' has the lowest value with {min_val} {unit}.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Calculate difference
        cat1_idx, cat2_idx = random.sample(range(len(categories)), 2)
        diff = abs(values[cat1_idx] - values[cat2_idx])
        wrong_answers = generate_wrong_answers(diff, difficulty)
        options = [diff] + wrong_answers[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the difference in {unit} between '{categories[cat1_idx]}' and '{categories[cat2_idx]}'?",
            'options': [str(o) for o in options],
            'correct': options.index(diff),
            'explanation': f"The difference is |{values[cat1_idx]} - {values[cat2_idx]}| = {diff} {unit}.",
            'difficulty': difficulty,
        })
        
        # Question 5: Calculate total
        wrong_answers = generate_wrong_answers(total, difficulty)
        options = [total] + wrong_answers[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the total of all {unit} shown in the chart?",
            'options': [str(o) for o in options],
            'correct': options.index(total),
            'explanation': f"Adding all values: {' + '.join(map(str, values))} = {total} {unit}.",
            'difficulty': difficulty,
        })
    
    if difficulty == 'advanced':
        # Question 6: Calculate mean
        wrong_answers = generate_wrong_answers(mean, difficulty, decimal=True)
        options = [mean] + wrong_answers[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the mean (average) number of {unit}?",
            'options': [str(o) for o in options],
            'correct': options.index(mean),
            'explanation': f"Mean = Total ÷ Number of categories = {total} ÷ {len(values)} = {mean} {unit}.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_pie_questions(data, difficulty='beginner'):
    """Generate questions about a pie chart"""
    questions = []
    categories = data['categories']
    values = data['values']  # These are percentages
    
    max_val = max(values)
    min_val = min(values)
    max_cat = categories[values.index(max_val)]
    min_cat = categories[values.index(min_val)]
    
    # Question 1: Read a percentage
    cat_idx = random.randint(0, len(categories) - 1)
    correct_val = values[cat_idx]
    wrong_answers = generate_wrong_answers(correct_val, difficulty, max_val=100)
    options = [f"{correct_val}%"] + [f"{w}%" for w in wrong_answers[:3]]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"What percentage does '{categories[cat_idx]}' represent?",
        'options': options,
        'correct': options.index(f"{correct_val}%"),
        'explanation': f"The pie chart shows '{categories[cat_idx]}' at {correct_val}%.",
        'difficulty': difficulty,
    })
    
    # Question 2: Find the largest category
    wrong_cats = [c for c in categories if c != max_cat]
    random.shuffle(wrong_cats)
    options = [max_cat] + wrong_cats[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "Which category has the largest share?",
        'options': options,
        'correct': options.index(max_cat),
        'explanation': f"'{max_cat}' has the largest share at {max_val}%.",
        'difficulty': difficulty,
    })
    
    # Question 3: Find the smallest category
    wrong_cats = [c for c in categories if c != min_cat]
    random.shuffle(wrong_cats)
    options = [min_cat] + wrong_cats[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "Which category has the smallest share?",
        'options': options,
        'correct': options.index(min_cat),
        'explanation': f"'{min_cat}' has the smallest share at {min_val}%.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Combined percentage
        idx1, idx2 = random.sample(range(len(categories)), 2)
        combined = values[idx1] + values[idx2]
        wrong_answers = generate_wrong_answers(combined, difficulty, max_val=100)
        options = [f"{combined}%"] + [f"{w}%" for w in wrong_answers[:3]]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the combined percentage of '{categories[idx1]}' and '{categories[idx2]}'?",
            'options': options,
            'correct': options.index(f"{combined}%"),
            'explanation': f"Combined: {values[idx1]}% + {values[idx2]}% = {combined}%.",
            'difficulty': difficulty,
        })
        
        # Question 5: Fraction equivalent
        cat_idx = random.randint(0, len(categories) - 1)
        percentage = values[cat_idx]
        
        # Find a nice fraction equivalent
        fraction_map = {25: '1/4', 50: '1/2', 75: '3/4', 20: '1/5', 10: '1/10', 30: '3/10', 40: '2/5'}
        if percentage in fraction_map:
            correct_fraction = fraction_map[percentage]
            wrong_fractions = [f for f in ['1/4', '1/2', '3/4', '1/5', '1/3', '2/5', '1/10'] if f != correct_fraction]
            random.shuffle(wrong_fractions)
            options = [correct_fraction] + wrong_fractions[:3]
            random.shuffle(options)
            
            questions.append({
                'question_text': f"What fraction of the total does '{categories[cat_idx]}' ({percentage}%) represent?",
                'options': options,
                'correct': options.index(correct_fraction),
                'explanation': f"{percentage}% = {correct_fraction} of the whole.",
                'difficulty': difficulty,
            })
    
    return questions


def generate_line_questions(data, difficulty='beginner'):
    """Generate questions about a line graph"""
    questions = []
    x_labels = data['x_labels']
    values = data['values']
    
    max_val = max(values)
    min_val = min(values)
    max_period = x_labels[values.index(max_val)]
    min_period = x_labels[values.index(min_val)]
    
    # Determine trend
    if values[-1] > values[0] + 10:
        trend = "increasing"
    elif values[-1] < values[0] - 10:
        trend = "decreasing"
    else:
        trend = "relatively stable"
    
    # Question 1: Read a value
    idx = random.randint(0, len(x_labels) - 1)
    correct_val = values[idx]
    wrong_answers = generate_wrong_answers(correct_val, difficulty)
    options = [correct_val] + wrong_answers[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"What was the value at {x_labels[idx]}?",
        'options': [str(o) for o in options],
        'correct': options.index(correct_val),
        'explanation': f"At {x_labels[idx]}, the graph shows a value of {correct_val}.",
        'difficulty': difficulty,
    })
    
    # Question 2: Find the peak
    wrong_periods = [p for p in x_labels if p != max_period]
    random.shuffle(wrong_periods)
    options = [max_period] + wrong_periods[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "At which point was the value highest?",
        'options': options,
        'correct': options.index(max_period),
        'explanation': f"The highest value of {max_val} was at {max_period}.",
        'difficulty': difficulty,
    })
    
    # Question 3: Identify trend
    trend_options = ['increasing', 'decreasing', 'relatively stable', 'fluctuating wildly']
    random.shuffle(trend_options)
    
    questions.append({
        'question_text': "What is the overall trend shown in this graph?",
        'options': [t.capitalize() for t in trend_options],
        'correct': trend_options.index(trend),
        'explanation': f"The graph shows an overall {trend} trend from {values[0]} to {values[-1]}.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Calculate change between two points
        idx1, idx2 = 0, len(values) - 1  # First to last
        change = values[idx2] - values[idx1]
        change_text = f"increase of {change}" if change > 0 else f"decrease of {abs(change)}"
        
        wrong_changes = [change + random.randint(-20, 20) for _ in range(3)]
        wrong_changes = [c for c in wrong_changes if c != change][:3]
        
        options = [change] + wrong_changes
        options = [f"{'Increase' if o >= 0 else 'Decrease'} of {abs(o)}" for o in options]
        correct_option = f"{'Increase' if change >= 0 else 'Decrease'} of {abs(change)}"
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What was the change from {x_labels[idx1]} to {x_labels[idx2]}?",
            'options': options,
            'correct': options.index(correct_option),
            'explanation': f"Change = {values[idx2]} - {values[idx1]} = {change} (an {change_text}).",
            'difficulty': difficulty,
        })
    
    return questions


def generate_histogram_questions(data, difficulty='beginner'):
    """Generate questions about a histogram"""
    questions = []
    bins = data['bins']
    frequencies = data['frequencies']
    
    max_freq = max(frequencies)
    min_freq = min(frequencies)
    max_bin = bins[frequencies.index(max_freq)]
    min_bin = bins[frequencies.index(min_freq)]
    total = sum(frequencies)
    
    # Question 1: Read a frequency
    idx = random.randint(0, len(bins) - 1)
    correct_freq = frequencies[idx]
    wrong_answers = generate_wrong_answers(correct_freq, difficulty, max_val=30)
    options = [correct_freq] + wrong_answers[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"How many items are in the '{bins[idx]}' range?",
        'options': [str(o) for o in options],
        'correct': options.index(correct_freq),
        'explanation': f"The histogram shows {correct_freq} items in the '{bins[idx]}' range.",
        'difficulty': difficulty,
    })
    
    # Question 2: Find modal class (highest frequency)
    wrong_bins = [b for b in bins if b != max_bin]
    random.shuffle(wrong_bins)
    options = [max_bin] + wrong_bins[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "Which range has the highest frequency (modal class)?",
        'options': options,
        'correct': options.index(max_bin),
        'explanation': f"The modal class is '{max_bin}' with a frequency of {max_freq}.",
        'difficulty': difficulty,
    })
    
    # Question 3: Total frequency
    wrong_answers = generate_wrong_answers(total, difficulty)
    options = [total] + wrong_answers[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "What is the total number of items shown in the histogram?",
        'options': [str(o) for o in options],
        'correct': options.index(total),
        'explanation': f"Total = {' + '.join(map(str, frequencies))} = {total}.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Question 4: Compare frequencies
        idx1, idx2 = random.sample(range(len(bins)), 2)
        diff = abs(frequencies[idx1] - frequencies[idx2])
        wrong_answers = generate_wrong_answers(diff, difficulty, max_val=20)
        options = [diff] + wrong_answers[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the difference in frequency between '{bins[idx1]}' and '{bins[idx2]}'?",
            'options': [str(o) for o in options],
            'correct': options.index(diff),
            'explanation': f"Difference = |{frequencies[idx1]} - {frequencies[idx2]}| = {diff}.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_wrong_answers(correct, difficulty, max_val=None, decimal=False):
    """Generate plausible wrong answers - ALWAYS returns at least 3"""
    wrong = set()
    
    # First pass: try to generate natural-looking wrong answers
    attempts = 0
    while len(wrong) < 4 and attempts < 30:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.randint(1, 3) * 5 * random.choice([-1, 1])
        elif difficulty == 'intermediate':
            offset = random.randint(5, 20) * random.choice([-1, 1])
        else:
            offset = random.randint(10, 50) * random.choice([-1, 1])
        
        candidate = correct + offset
        
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        
        if candidate > 0 and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Fallback: if we still don't have enough, add simple offsets
    fallback_offsets = [1, 2, 3, 5, 10, -1, -2, 4, 6, 7, 8, 9]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = correct + offset
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        if candidate > 0 and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Last resort: just add some numbers
    if len(wrong) < 3:
        for i in range(1, 20):
            if len(wrong) >= 3:
                break
            candidate = i if not decimal else float(i)
            if candidate != correct and candidate not in wrong:
                if max_val is None or candidate <= max_val:
                    wrong.add(candidate)
    
    return list(wrong)


def ensure_four_options(correct, wrong_list, is_string=False):
    """Ensure we have exactly 4 options (1 correct + 3 wrong)"""
    options = [correct]
    
    # Add wrong answers
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options:
            options.append(w)
    
    # If still not enough, add placeholders
    placeholders = ['N/A', 'None', 'Cannot determine', 'Not enough info'] if is_string else [0, -1, 999, 100]
    for p in placeholders:
        if len(options) >= 4:
            break
        if p not in options and p != correct:
            options.append(p)
    
    random.shuffle(options)
    return options, options.index(correct)


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_chart_questions(chart_type, difficulty, count=5, output_dir='static/question_images'):
    """
    Generate chart questions with images.
    
    Args:
        chart_type: 'bar', 'pie', 'line', or 'histogram'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of question sets to generate
        output_dir: Directory to save chart images
    
    Returns:
        List of question dictionaries with image paths
    """
    if not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not installed. Run: pip install matplotlib --user'}
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_questions = []
    
    for i in range(count):
        # Generate chart data
        if chart_type == 'bar':
            data = generate_bar_data(difficulty)
            questions = generate_bar_questions(data, difficulty)
            create_func = create_bar_chart
        elif chart_type == 'pie':
            data = generate_pie_data(difficulty)
            questions = generate_pie_questions(data, difficulty)
            create_func = create_pie_chart
        elif chart_type == 'line':
            data = generate_line_data(difficulty)
            questions = generate_line_questions(data, difficulty)
            create_func = create_line_chart
        elif chart_type == 'histogram':
            data = generate_histogram_data(difficulty)
            questions = generate_histogram_questions(data, difficulty)
            create_func = create_histogram
        else:
            continue
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"chart_{chart_type}_{difficulty}_{timestamp}_{i}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Create the chart image
        if create_func(data, filepath):
            image_url = f"/static/question_images/{filename}"
            
            # Add image URL and caption to each question
            for q in questions:
                q['image_url'] = image_url
                q['image_caption'] = data['title']
                q['topic'] = 'descriptive_statistics'
                all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_chart_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for chart question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-chart-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_chart_questions():
        """Generate chart-based questions"""
        from flask import request, jsonify, session
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({
                'error': 'matplotlib not installed. Run: pip install matplotlib --user'
            }), 400
        
        data = request.json or {}
        
        chart_types = data.get('chart_types', ['bar', 'pie', 'line', 'histogram'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        charts_per_type = data.get('charts_per_type', 3)  # Number of different charts per type/difficulty
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for chart_type in chart_types:
            for difficulty in difficulties:
                questions = generate_chart_questions(
                    chart_type=chart_type,
                    difficulty=difficulty,
                    count=charts_per_type,
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
                        'topic': 'descriptive_statistics',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='descriptive_statistics',
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
                        'type': chart_type,
                        'difficulty': difficulty,
                        'question': q['question_text'][:50] + '...'
                    })
        
        db.session.commit()
        
        # Get updated counts
        counts = {}
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = 'descriptive_statistics' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/chart-generator-status', methods=['GET'])
    @admin_required_api
    def chart_generator_status():
        """Check if chart generator is available"""
        from flask import jsonify
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'chart_types': ['bar', 'pie', 'line', 'histogram'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


if __name__ == '__main__':
    # Test the generators
    print("Testing Chart Question Generator...")
    print("="*50)
    
    if not MATPLOTLIB_AVAILABLE:
        print("ERROR: matplotlib not installed!")
        print("Run: pip install matplotlib")
    else:
        # Test each chart type
        for chart_type in ['bar', 'pie', 'line', 'histogram']:
            print(f"\n{chart_type.upper()} CHART:")
            questions = generate_chart_questions(chart_type, 'intermediate', count=1, output_dir='/tmp/test_charts')
            
            if isinstance(questions, dict) and 'error' in questions:
                print(f"  Error: {questions['error']}")
            else:
                print(f"  Generated {len(questions)} questions")
                for q in questions[:2]:
                    print(f"  - {q['question_text'][:60]}...")
