#!/usr/bin/env python3
"""
Coordinate Geometry Question Generator for AgentMath.app

Generates coordinate geometry questions with auto-generated Cartesian plane images:
- Plotting and reading points
- Distance between two points
- Midpoint of a line segment
- Slope/gradient of a line
- Equation of a line (y = mx + c)
- Parallel and perpendicular lines

Aligned with Irish Junior Cycle Mathematics curriculum.
"""

import os
import random
import math
from datetime import datetime

# Coordinate plane generation with matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyArrowPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_wrong_answers(correct, difficulty, max_val=None, decimal=False, min_val=None, avoid=None):
    """Generate plausible wrong answers - ALWAYS returns at least 3"""
    wrong = set()
    avoid = avoid or []
    
    # First pass: try to generate natural-looking wrong answers
    attempts = 0
    while len(wrong) < 4 and attempts < 40:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.randint(1, 3) * random.choice([-1, 1])
        elif difficulty == 'intermediate':
            offset = random.randint(1, 5) * random.choice([-1, 1])
        else:
            offset = random.randint(2, 8) * random.choice([-1, 1])
        
        candidate = correct + offset
        
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        
        valid = True
        if min_val is not None and candidate < min_val:
            valid = False
        if max_val is not None and candidate > max_val:
            valid = False
        if candidate == correct or candidate in avoid:
            valid = False
        
        if valid:
            wrong.add(candidate)
    
    # Fallback: add simple offsets
    fallback_offsets = [1, -1, 2, -2, 3, -3, 4, 5, -4, -5, 6, 7]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = correct + offset
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        if candidate != correct and candidate not in avoid:
            if min_val is None or candidate >= min_val:
                if max_val is None or candidate <= max_val:
                    wrong.add(candidate)
    
    return list(wrong)


def ensure_four_options(correct, wrong_list, as_string=True, prefix='', suffix=''):
    """Ensure we have exactly 4 options"""
    options = [correct]
    
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options:
            options.append(w)
    
    # Pad if needed
    pad_val = correct + 10 if isinstance(correct, (int, float)) else 0
    placeholders = [pad_val, pad_val + 5, pad_val - 3, pad_val + 7]
    for p in placeholders:
        if len(options) >= 4:
            break
        if p not in options:
            options.append(p)
    
    if as_string:
        options = [f"{prefix}{o}{suffix}" for o in options]
    
    random.shuffle(options)
    correct_str = f"{prefix}{correct}{suffix}" if as_string else correct
    return options, options.index(correct_str)


def gcd(a, b):
    """Greatest common divisor"""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def simplify_fraction(num, den):
    """Simplify a fraction"""
    if den == 0:
        return (num, den)
    g = gcd(num, den)
    return (num // g, den // g)


# ============================================================================
# COORDINATE PLANE IMAGE GENERATOR
# ============================================================================

def create_coordinate_plane(ax, x_range=(-10, 10), y_range=(-10, 10), grid=True):
    """Set up a coordinate plane with axes and grid"""
    ax.set_xlim(x_range[0] - 0.5, x_range[1] + 0.5)
    ax.set_ylim(y_range[0] - 0.5, y_range[1] + 0.5)
    
    # Draw grid
    if grid:
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
    
    # Draw axes
    ax.axhline(y=0, color='black', linewidth=1.5)
    ax.axvline(x=0, color='black', linewidth=1.5)
    
    # Add axis labels
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('y', fontsize=12, fontweight='bold')
    
    # Set ticks
    x_ticks = range(x_range[0], x_range[1] + 1)
    y_ticks = range(y_range[0], y_range[1] + 1)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    
    ax.set_aspect('equal')
    
    return ax


def plot_point(ax, x, y, label=None, color='#3b82f6', size=100):
    """Plot a point on the coordinate plane"""
    ax.scatter([x], [y], c=color, s=size, zorder=5, edgecolors='white', linewidths=2)
    
    if label:
        offset_x = 0.3 if x >= 0 else -0.3
        offset_y = 0.4
        ax.annotate(label, (x, y), xytext=(x + offset_x, y + offset_y),
                    fontsize=11, fontweight='bold', color=color)


def plot_line_segment(ax, x1, y1, x2, y2, color='#3b82f6', linewidth=2):
    """Plot a line segment between two points"""
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, zorder=3)


def plot_line(ax, slope, intercept, x_range=(-10, 10), color='#3b82f6', linewidth=2, label=None):
    """Plot a line given slope and y-intercept"""
    x_vals = np.linspace(x_range[0], x_range[1], 100)
    y_vals = slope * x_vals + intercept
    ax.plot(x_vals, y_vals, color=color, linewidth=linewidth, zorder=3, label=label)


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_plot_point_data(difficulty='beginner'):
    """Generate data for plotting/reading points"""
    if difficulty == 'beginner':
        # First quadrant only, small positive integers
        x = random.randint(1, 6)
        y = random.randint(1, 6)
    elif difficulty == 'intermediate':
        # All four quadrants
        x = random.randint(-6, 6)
        y = random.randint(-6, 6)
        # Avoid origin
        if x == 0 and y == 0:
            x = random.choice([-3, 3])
    else:
        # Include larger values
        x = random.randint(-8, 8)
        y = random.randint(-8, 8)
        if x == 0 and y == 0:
            x = random.choice([-5, 5])
    
    # Determine quadrant
    if x > 0 and y > 0:
        quadrant = 1
    elif x < 0 and y > 0:
        quadrant = 2
    elif x < 0 and y < 0:
        quadrant = 3
    elif x > 0 and y < 0:
        quadrant = 4
    else:
        quadrant = 0  # On an axis
    
    return {
        'type': 'plot_point',
        'x': x,
        'y': y,
        'quadrant': quadrant,
    }


def generate_distance_data(difficulty='beginner'):
    """Generate data for distance between two points"""
    if difficulty == 'beginner':
        # Horizontal or vertical lines (easy calculation)
        if random.choice([True, False]):
            # Horizontal line
            x1 = random.randint(1, 4)
            y1 = random.randint(1, 5)
            x2 = x1 + random.randint(2, 5)
            y2 = y1
        else:
            # Vertical line
            x1 = random.randint(1, 5)
            y1 = random.randint(1, 4)
            x2 = x1
            y2 = y1 + random.randint(2, 5)
    elif difficulty == 'intermediate':
        # Pythagorean triples for nice answers
        triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)]
        dx, dy, dist = random.choice(triples[:2])
        x1 = random.randint(-3, 3)
        y1 = random.randint(-3, 3)
        x2 = x1 + dx * random.choice([-1, 1])
        y2 = y1 + dy * random.choice([-1, 1])
    else:
        # Any points, may have decimal answers
        triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (9, 12, 15)]
        dx, dy, dist = random.choice(triples)
        x1 = random.randint(-5, 3)
        y1 = random.randint(-5, 3)
        x2 = x1 + dx * random.choice([-1, 1])
        y2 = y1 + dy * random.choice([-1, 1])
    
    # Calculate distance
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    distance = round(distance, 1) if distance != int(distance) else int(distance)
    
    return {
        'type': 'distance',
        'x1': x1, 'y1': y1,
        'x2': x2, 'y2': y2,
        'distance': distance,
    }


def generate_midpoint_data(difficulty='beginner'):
    """Generate data for midpoint problems"""
    if difficulty == 'beginner':
        # Even differences for whole number midpoints
        x1 = random.randint(0, 4) * 2
        y1 = random.randint(0, 4) * 2
        x2 = random.randint(0, 4) * 2
        y2 = random.randint(0, 4) * 2
        # Ensure different points
        while x1 == x2 and y1 == y2:
            x2 = random.randint(0, 4) * 2
    elif difficulty == 'intermediate':
        x1 = random.randint(-4, 4)
        y1 = random.randint(-4, 4)
        # Make midpoint whole number
        x2 = x1 + random.choice([-4, -2, 2, 4])
        y2 = y1 + random.choice([-4, -2, 2, 4])
    else:
        x1 = random.randint(-6, 6)
        y1 = random.randint(-6, 6)
        x2 = random.randint(-6, 6)
        y2 = random.randint(-6, 6)
        while x1 == x2 and y1 == y2:
            x2 = random.randint(-6, 6)
    
    # Calculate midpoint
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # Clean up decimals
    if mid_x == int(mid_x):
        mid_x = int(mid_x)
    if mid_y == int(mid_y):
        mid_y = int(mid_y)
    
    return {
        'type': 'midpoint',
        'x1': x1, 'y1': y1,
        'x2': x2, 'y2': y2,
        'mid_x': mid_x,
        'mid_y': mid_y,
    }


def generate_slope_data(difficulty='beginner'):
    """Generate data for slope/gradient problems"""
    if difficulty == 'beginner':
        # Integer slopes
        slope = random.choice([1, 2, -1, -2, 0])
        x1 = random.randint(0, 3)
        y1 = random.randint(0, 3)
        x2 = x1 + random.randint(2, 4)
        y2 = y1 + slope * (x2 - x1)
    elif difficulty == 'intermediate':
        # Simple fraction slopes
        slopes = [(1, 2), (1, 3), (2, 3), (3, 2), (-1, 2), (-2, 1), (1, 1), (2, 1)]
        rise, run = random.choice(slopes)
        x1 = random.randint(-3, 3)
        y1 = random.randint(-3, 3)
        x2 = x1 + run * random.choice([1, 2])
        y2 = y1 + rise * random.choice([1, 2])
        slope = rise / run
    else:
        # More complex slopes
        rise = random.randint(-4, 4)
        run = random.randint(1, 4)
        if rise == 0:
            rise = random.choice([-2, 2])
        x1 = random.randint(-4, 2)
        y1 = random.randint(-4, 2)
        x2 = x1 + run
        y2 = y1 + rise
        slope = rise / run
    
    # Determine if line is rising or falling
    if isinstance(slope, (int, float)):
        if slope > 0:
            direction = 'rising'
        elif slope < 0:
            direction = 'falling'
        else:
            direction = 'horizontal'
    else:
        direction = 'unknown'
    
    slope_simplified = simplify_fraction(y2 - y1, x2 - x1) if x2 != x1 else (1, 0)
    
    return {
        'type': 'slope',
        'x1': x1, 'y1': y1,
        'x2': x2, 'y2': y2,
        'slope': round(slope, 2) if isinstance(slope, float) else slope,
        'slope_fraction': slope_simplified,
        'direction': direction,
    }


def generate_equation_data(difficulty='beginner'):
    """Generate data for equation of a line problems"""
    if difficulty == 'beginner':
        # y = mx + c with simple m and c
        slope = random.choice([1, 2, -1, -2])
        intercept = random.randint(-3, 3)
    elif difficulty == 'intermediate':
        slope = random.choice([1, 2, 3, -1, -2, -3, 0.5, -0.5])
        intercept = random.randint(-5, 5)
    else:
        slope = random.choice([0.5, 1.5, 2, -0.5, -1.5, -2, 3, -3])
        intercept = random.randint(-6, 6)
    
    # Generate two points on the line
    x1 = 0
    y1 = intercept
    x2 = 2
    y2 = slope * x2 + intercept
    
    return {
        'type': 'equation',
        'slope': slope,
        'intercept': intercept,
        'x1': x1, 'y1': y1,
        'x2': x2, 'y2': int(y2) if y2 == int(y2) else y2,
    }


def generate_parallel_perpendicular_data(difficulty='intermediate'):
    """Generate data for parallel/perpendicular line problems"""
    # Generate a reference line
    slope1 = random.choice([1, 2, -1, -2, 0.5, -0.5])
    intercept1 = random.randint(-3, 3)
    
    # Decide relationship
    relationship = random.choice(['parallel', 'perpendicular', 'neither'])
    
    if relationship == 'parallel':
        slope2 = slope1
        intercept2 = intercept1 + random.choice([-3, -2, 2, 3])
    elif relationship == 'perpendicular':
        if slope1 != 0:
            slope2 = -1 / slope1
        else:
            slope2 = 999  # Vertical line (undefined)
        intercept2 = random.randint(-3, 3)
    else:
        # Neither - different slope, not perpendicular
        slope2 = slope1 + random.choice([0.5, 1, -0.5, -1])
        # Make sure it's not accidentally perpendicular
        if abs(slope1 * slope2 + 1) < 0.01:
            slope2 += 0.5
        intercept2 = random.randint(-3, 3)
    
    return {
        'type': 'parallel_perpendicular',
        'slope1': slope1,
        'intercept1': intercept1,
        'slope2': slope2,
        'intercept2': intercept2,
        'relationship': relationship,
    }


# ============================================================================
# IMAGE GENERATORS
# ============================================================================

def create_point_image(data, filepath):
    """Create image showing a point on coordinate plane"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    x, y = data['x'], data['y']
    
    # Determine range
    max_val = max(abs(x), abs(y), 6) + 1
    x_range = (-max_val, max_val) if x < 0 or y < 0 else (0, max_val + 2)
    y_range = (-max_val, max_val) if x < 0 or y < 0 else (0, max_val + 2)
    
    # For beginner, show first quadrant only
    if data.get('difficulty') == 'beginner' or (x >= 0 and y >= 0):
        x_range = (-1, max(8, x + 2))
        y_range = (-1, max(8, y + 2))
    
    create_coordinate_plane(ax, x_range, y_range)
    plot_point(ax, x, y, label='P', color='#dc2626', size=150)
    
    plt.title('What are the coordinates of point P?', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_distance_image(data, filepath):
    """Create image showing two points for distance calculation"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    
    max_val = max(abs(x1), abs(y1), abs(x2), abs(y2), 5) + 2
    
    if min(x1, x2, y1, y2) >= 0:
        x_range = (-1, max_val + 1)
        y_range = (-1, max_val + 1)
    else:
        x_range = (-max_val, max_val)
        y_range = (-max_val, max_val)
    
    create_coordinate_plane(ax, x_range, y_range)
    
    # Plot line segment
    plot_line_segment(ax, x1, y1, x2, y2, color='#3b82f6', linewidth=2)
    
    # Plot points
    plot_point(ax, x1, y1, label=f'A({x1},{y1})', color='#dc2626', size=120)
    plot_point(ax, x2, y2, label=f'B({x2},{y2})', color='#16a34a', size=120)
    
    plt.title('Find the distance between A and B', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_midpoint_image(data, filepath):
    """Create image showing two points for midpoint calculation"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    mid_x, mid_y = data['mid_x'], data['mid_y']
    
    max_val = max(abs(x1), abs(y1), abs(x2), abs(y2), 5) + 2
    
    if min(x1, x2, y1, y2) >= 0:
        x_range = (-1, max_val + 1)
        y_range = (-1, max_val + 1)
    else:
        x_range = (-max_val, max_val)
        y_range = (-max_val, max_val)
    
    create_coordinate_plane(ax, x_range, y_range)
    
    # Plot line segment
    plot_line_segment(ax, x1, y1, x2, y2, color='#3b82f6', linewidth=2)
    
    # Plot endpoints
    plot_point(ax, x1, y1, label=f'A({x1},{y1})', color='#dc2626', size=120)
    plot_point(ax, x2, y2, label=f'B({x2},{y2})', color='#16a34a', size=120)
    
    # Plot midpoint with question mark
    ax.scatter([mid_x], [mid_y], c='#f59e0b', s=100, zorder=5, marker='s', edgecolors='white', linewidths=2)
    ax.annotate('M = ?', (mid_x, mid_y), xytext=(mid_x + 0.5, mid_y + 0.5),
                fontsize=11, fontweight='bold', color='#f59e0b')
    
    plt.title('Find the midpoint M of line segment AB', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_slope_image(data, filepath):
    """Create image showing a line for slope calculation"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    
    max_val = max(abs(x1), abs(y1), abs(x2), abs(y2), 5) + 2
    x_range = (-max_val, max_val)
    y_range = (-max_val, max_val)
    
    create_coordinate_plane(ax, x_range, y_range)
    
    # Extend line beyond points
    if x2 != x1:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        plot_line(ax, slope, intercept, x_range, color='#3b82f6', linewidth=2)
    
    # Plot the two points
    plot_point(ax, x1, y1, label=f'({x1},{y1})', color='#dc2626', size=120)
    plot_point(ax, x2, y2, label=f'({x2},{y2})', color='#16a34a', size=120)
    
    # Show rise and run
    ax.plot([x1, x2], [y1, y1], 'k--', linewidth=1.5, alpha=0.5)
    ax.plot([x2, x2], [y1, y2], 'k--', linewidth=1.5, alpha=0.5)
    
    # Label rise and run
    ax.text((x1 + x2) / 2, y1 - 0.5, f'run = {x2 - x1}', ha='center', fontsize=10, color='#666')
    ax.text(x2 + 0.3, (y1 + y2) / 2, f'rise = {y2 - y1}', ha='left', fontsize=10, color='#666')
    
    plt.title('Find the slope (gradient) of this line', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_equation_image(data, filepath):
    """Create image showing a line for equation identification"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    slope = data['slope']
    intercept = data['intercept']
    
    max_val = max(abs(intercept) + 3, 6)
    x_range = (-max_val, max_val)
    y_range = (-max_val, max_val)
    
    create_coordinate_plane(ax, x_range, y_range)
    
    # Plot the line
    plot_line(ax, slope, intercept, x_range, color='#3b82f6', linewidth=3)
    
    # Mark y-intercept
    plot_point(ax, 0, intercept, label=f'(0, {intercept})', color='#dc2626', size=120)
    
    # Mark another point
    x2 = 2
    y2 = slope * x2 + intercept
    plot_point(ax, x2, y2, label=f'({x2}, {int(y2) if y2 == int(y2) else y2})', color='#16a34a', size=120)
    
    plt.title('What is the equation of this line?', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_parallel_perpendicular_image(data, filepath):
    """Create image showing two lines for parallel/perpendicular identification"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    slope1 = data['slope1']
    intercept1 = data['intercept1']
    slope2 = data['slope2']
    intercept2 = data['intercept2']
    
    x_range = (-8, 8)
    y_range = (-8, 8)
    
    create_coordinate_plane(ax, x_range, y_range)
    
    # Plot first line
    plot_line(ax, slope1, intercept1, x_range, color='#3b82f6', linewidth=3, label='Line 1')
    
    # Plot second line (handle vertical line case)
    if abs(slope2) < 100:
        plot_line(ax, slope2, intercept2, x_range, color='#dc2626', linewidth=3, label='Line 2')
    else:
        ax.axvline(x=2, color='#dc2626', linewidth=3, label='Line 2')
    
    ax.legend(loc='upper right', fontsize=10)
    
    plt.title('Are these lines parallel, perpendicular, or neither?', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_point_questions(data, difficulty='beginner'):
    """Generate questions about plotting/reading points"""
    questions = []
    
    x, y = data['x'], data['y']
    
    # Q1: What are the coordinates?
    correct = f"({x}, {y})"
    wrong_options = [
        f"({y}, {x})",  # Swapped
        f"({x + random.choice([-1, 1])}, {y})",
        f"({x}, {y + random.choice([-1, 1])})",
        f"({-x}, {y})",
    ]
    options = [correct] + wrong_options[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "What are the coordinates of point P shown on the graph?",
        'options': options,
        'correct': options.index(correct),
        'explanation': f"Point P is located at x = {x} and y = {y}, so the coordinates are ({x}, {y}).",
        'difficulty': difficulty,
    })
    
    # Q2: Which quadrant?
    if data['quadrant'] > 0:
        quadrant_names = {1: 'First', 2: 'Second', 3: 'Third', 4: 'Fourth'}
        correct_q = quadrant_names[data['quadrant']]
        wrong_qs = [q for q in quadrant_names.values() if q != correct_q]
        options = [correct_q] + wrong_qs
        random.shuffle(options)
        
        questions.append({
            'question_text': f"In which quadrant is the point ({x}, {y}) located?",
            'options': options,
            'correct': options.index(correct_q),
            'explanation': f"({x}, {y}) is in the {correct_q} quadrant because x is {'positive' if x > 0 else 'negative'} and y is {'positive' if y > 0 else 'negative'}.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_distance_questions(data, difficulty='beginner'):
    """Generate questions about distance between points"""
    questions = []
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    distance = data['distance']
    
    # Q1: Find the distance
    wrong = generate_wrong_answers(distance, difficulty, min_val=1)
    options, correct_idx = ensure_four_options(distance, wrong, suffix=' units')
    
    questions.append({
        'question_text': f"Find the distance between A({x1}, {y1}) and B({x2}, {y2}).",
        'options': options,
        'correct': correct_idx,
        'explanation': f"Using the distance formula: √[(x₂-x₁)² + (y₂-y₁)²] = √[({x2}-{x1})² + ({y2}-{y1})²] = √[{(x2-x1)**2} + {(y2-y1)**2}] = √{(x2-x1)**2 + (y2-y1)**2} = {distance}",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q2: Distance formula
        questions.append({
            'question_text': "Which formula is used to find the distance between two points?",
            'options': [
                '√[(x₂-x₁)² + (y₂-y₁)²]',
                '(x₂-x₁) + (y₂-y₁)',
                '(x₂+x₁)/2, (y₂+y₁)/2',
                '(y₂-y₁)/(x₂-x₁)',
            ],
            'correct': 0,
            'explanation': "The distance formula is √[(x₂-x₁)² + (y₂-y₁)²], derived from Pythagoras' theorem.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_midpoint_questions(data, difficulty='beginner'):
    """Generate questions about midpoints"""
    questions = []
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    mid_x, mid_y = data['mid_x'], data['mid_y']
    
    # Q1: Find the midpoint
    correct = f"({mid_x}, {mid_y})"
    wrong_options = [
        f"({mid_x + 1}, {mid_y})",
        f"({mid_x}, {mid_y + 1})",
        f"({mid_x - 1}, {mid_y - 1})",
        f"({(x1 + x2)}, {(y1 + y2)})",  # Sum instead of average
    ]
    options = [correct] + wrong_options[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"Find the midpoint of the line segment from A({x1}, {y1}) to B({x2}, {y2}).",
        'options': options,
        'correct': options.index(correct),
        'explanation': f"Midpoint = ((x₁+x₂)/2, (y₁+y₂)/2) = (({x1}+{x2})/2, ({y1}+{y2})/2) = ({mid_x}, {mid_y})",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q2: Midpoint formula
        questions.append({
            'question_text': "What is the formula for finding the midpoint of a line segment?",
            'options': [
                '((x₁+x₂)/2, (y₁+y₂)/2)',
                '(x₂-x₁, y₂-y₁)',
                '√[(x₂-x₁)² + (y₂-y₁)²]',
                '(x₁×x₂, y₁×y₂)',
            ],
            'correct': 0,
            'explanation': "The midpoint formula averages the x-coordinates and y-coordinates: ((x₁+x₂)/2, (y₁+y₂)/2).",
            'difficulty': difficulty,
        })
    
    return questions


def generate_slope_questions(data, difficulty='beginner'):
    """Generate questions about slope/gradient"""
    questions = []
    
    x1, y1 = data['x1'], data['y1']
    x2, y2 = data['x2'], data['y2']
    slope = data['slope']
    rise, run = y2 - y1, x2 - x1
    
    # Q1: Find the slope
    if isinstance(slope, int) or (isinstance(slope, float) and slope == int(slope)):
        slope_display = int(slope)
        wrong = generate_wrong_answers(slope_display, difficulty)
        options, correct_idx = ensure_four_options(slope_display, wrong)
    else:
        slope_display = slope
        # For fractions, show as fraction
        num, den = simplify_fraction(rise, run)
        if den == 1:
            correct = str(num)
        else:
            correct = f"{num}/{den}"
        wrong_fracs = [f"{num+1}/{den}", f"{num}/{den+1}", f"{den}/{num}", f"{num-1}/{den}"]
        options = [correct] + wrong_fracs[:3]
        random.shuffle(options)
        correct_idx = options.index(correct)
    
    questions.append({
        'question_text': f"Find the slope (gradient) of the line passing through ({x1}, {y1}) and ({x2}, {y2}).",
        'options': options,
        'correct': correct_idx,
        'explanation': f"Slope = rise/run = (y₂-y₁)/(x₂-x₁) = ({y2}-{y1})/({x2}-{x1}) = {rise}/{run} = {slope}",
        'difficulty': difficulty,
    })
    
    # Q2: Positive or negative slope
    if slope != 0:
        correct_dir = 'Positive (line rises left to right)' if slope > 0 else 'Negative (line falls left to right)'
        options = [
            'Positive (line rises left to right)',
            'Negative (line falls left to right)',
            'Zero (horizontal line)',
            'Undefined (vertical line)',
        ]
        correct_idx = 0 if slope > 0 else 1
        
        questions.append({
            'question_text': "Looking at the graph, is the slope positive or negative?",
            'options': options,
            'correct': correct_idx,
            'explanation': f"The line {'rises' if slope > 0 else 'falls'} from left to right, so the slope is {'positive' if slope > 0 else 'negative'}.",
            'difficulty': difficulty,
        })
    
    if difficulty == 'advanced':
        # Q3: Slope formula
        questions.append({
            'question_text': "What is the formula for calculating slope?",
            'options': [
                '(y₂ - y₁) / (x₂ - x₁)',
                '(x₂ - x₁) / (y₂ - y₁)',
                '(x₂ + x₁) / (y₂ + y₁)',
                '√[(x₂-x₁)² + (y₂-y₁)²]',
            ],
            'correct': 0,
            'explanation': "Slope = rise/run = (y₂ - y₁) / (x₂ - x₁).",
            'difficulty': difficulty,
        })
    
    return questions


def generate_equation_questions(data, difficulty='beginner'):
    """Generate questions about equation of a line"""
    questions = []
    
    slope = data['slope']
    intercept = data['intercept']
    
    # Format equation
    if intercept == 0:
        correct_eq = f"y = {slope}x" if slope != 1 else "y = x"
    elif intercept > 0:
        correct_eq = f"y = {slope}x + {intercept}" if slope != 1 else f"y = x + {intercept}"
    else:
        correct_eq = f"y = {slope}x - {abs(intercept)}" if slope != 1 else f"y = x - {abs(intercept)}"
    
    # Clean up "1x" to "x"
    correct_eq = correct_eq.replace("1x", "x").replace("-1x", "-x")
    
    # Generate wrong equations
    wrong_eqs = [
        f"y = {slope + 1}x + {intercept}",
        f"y = {slope}x + {intercept + 2}",
        f"y = {-slope}x + {intercept}",
        f"y = {slope}x - {intercept}" if intercept > 0 else f"y = {slope}x + {abs(intercept)}",
    ]
    wrong_eqs = [eq.replace("1x", "x").replace("-1x", "-x") for eq in wrong_eqs]
    
    options = [correct_eq] + wrong_eqs[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': "What is the equation of the line shown on the graph?",
        'options': options,
        'correct': options.index(correct_eq),
        'explanation': f"The line has slope {slope} and y-intercept {intercept}, so the equation is {correct_eq}.",
        'difficulty': difficulty,
    })
    
    # Q2: Identify slope from equation
    questions.append({
        'question_text': f"What is the slope of the line {correct_eq}?",
        'options': [str(slope), str(intercept), str(slope + 1), str(-slope)],
        'correct': 0,
        'explanation': f"In y = mx + c, the slope m is the coefficient of x. Here m = {slope}.",
        'difficulty': difficulty,
    })
    
    # Q3: Identify y-intercept
    questions.append({
        'question_text': f"What is the y-intercept of the line {correct_eq}?",
        'options': [str(intercept), str(slope), str(intercept + 1), str(-intercept)],
        'correct': 0,
        'explanation': f"In y = mx + c, the y-intercept c is {intercept}. This is where the line crosses the y-axis.",
        'difficulty': difficulty,
    })
    
    return questions


def generate_parallel_perpendicular_questions(data, difficulty='intermediate'):
    """Generate questions about parallel and perpendicular lines"""
    questions = []
    
    relationship = data['relationship']
    slope1 = data['slope1']
    slope2 = data['slope2']
    
    # Q1: Identify relationship
    options = ['Parallel', 'Perpendicular', 'Neither']
    random.shuffle(options)
    correct = relationship.capitalize()
    
    questions.append({
        'question_text': "Looking at the two lines, are they parallel, perpendicular, or neither?",
        'options': options + ['Cannot determine'],
        'correct': options.index(correct),
        'explanation': f"The lines are {relationship}. Parallel lines have equal slopes. Perpendicular lines have slopes that multiply to -1.",
        'difficulty': difficulty,
    })
    
    if difficulty == 'advanced':
        # Q2: Condition for parallel
        questions.append({
            'question_text': "Two lines are parallel when their slopes are:",
            'options': ['Equal', 'Negative reciprocals', 'Opposite signs', 'Both zero'],
            'correct': 0,
            'explanation': "Parallel lines have equal slopes (m₁ = m₂).",
            'difficulty': difficulty,
        })
        
        # Q3: Condition for perpendicular
        questions.append({
            'question_text': "Two lines are perpendicular when their slopes multiply to:",
            'options': ['-1', '0', '1', '2'],
            'correct': 0,
            'explanation': "Perpendicular lines have slopes that multiply to -1 (m₁ × m₂ = -1).",
            'difficulty': difficulty,
        })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_coordinate_questions(topic_type, difficulty, count=3, output_dir='static/question_images'):
    """
    Generate coordinate geometry questions with images.
    
    Args:
        topic_type: 'point', 'distance', 'midpoint', 'slope', 'equation', 'parallel'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of different problems to generate
        output_dir: Directory to save images
    
    Returns:
        List of question dictionaries with image paths
    """
    if not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not installed. Run: pip install matplotlib --user'}
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_questions = []
    
    for i in range(count):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if topic_type == 'point':
            data = generate_plot_point_data(difficulty)
            data['difficulty'] = difficulty
            filename = f"coord_point_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_point_image(data, filepath)
            questions = generate_point_questions(data, difficulty)
            caption = "Reading Coordinates"
        
        elif topic_type == 'distance':
            data = generate_distance_data(difficulty)
            filename = f"coord_distance_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_distance_image(data, filepath)
            questions = generate_distance_questions(data, difficulty)
            caption = "Distance Between Points"
        
        elif topic_type == 'midpoint':
            data = generate_midpoint_data(difficulty)
            filename = f"coord_midpoint_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_midpoint_image(data, filepath)
            questions = generate_midpoint_questions(data, difficulty)
            caption = "Midpoint of Line Segment"
        
        elif topic_type == 'slope':
            data = generate_slope_data(difficulty)
            filename = f"coord_slope_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_slope_image(data, filepath)
            questions = generate_slope_questions(data, difficulty)
            caption = "Slope/Gradient of a Line"
        
        elif topic_type == 'equation':
            data = generate_equation_data(difficulty)
            filename = f"coord_equation_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_equation_image(data, filepath)
            questions = generate_equation_questions(data, difficulty)
            caption = "Equation of a Line"
        
        elif topic_type == 'parallel':
            data = generate_parallel_perpendicular_data(difficulty)
            filename = f"coord_parallel_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_parallel_perpendicular_image(data, filepath)
            questions = generate_parallel_perpendicular_questions(data, difficulty)
            caption = "Parallel and Perpendicular Lines"
        
        else:
            continue
        
        # Add image URL to each question
        image_url = f"/static/question_images/{filename}"
        for q in questions:
            q['image_url'] = image_url
            q['image_caption'] = caption
            q['topic'] = 'coordinate_geometry'
            all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_coordinate_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for coordinate geometry question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-coordinate-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_coordinate_questions():
        """Generate coordinate geometry questions with graphs"""
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({
                'error': 'matplotlib not installed. Run: pip install matplotlib --user'
            }), 400
        
        data = request.json or {}
        
        topic_types = data.get('topic_types', ['point', 'distance', 'midpoint', 'slope', 'equation', 'parallel'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        problems_per_type = data.get('problems_per_type', 2)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for topic_type in topic_types:
            for difficulty in difficulties:
                # Skip parallel for beginner
                if topic_type == 'parallel' and difficulty == 'beginner':
                    continue
                
                questions = generate_coordinate_questions(
                    topic_type=topic_type,
                    difficulty=difficulty,
                    count=problems_per_type,
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
                        'topic': 'coordinate_geometry',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='coordinate_geometry',
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
                        'type': topic_type,
                        'difficulty': difficulty,
                        'question': q['question_text'][:50] + '...'
                    })
        
        db.session.commit()
        
        # Get updated counts
        counts = {}
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = 'coordinate_geometry' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/coordinate-generator-status', methods=['GET'])
    @admin_required_api
    def coordinate_generator_status():
        """Check if coordinate generator is available"""
        from flask import jsonify
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'topic_types': ['point', 'distance', 'midpoint', 'slope', 'equation', 'parallel'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


if __name__ == '__main__':
    # Test the generators
    print("Testing Coordinate Geometry Question Generator...")
    print("="*50)
    
    if not MATPLOTLIB_AVAILABLE:
        print("ERROR: matplotlib not installed!")
        print("Run: pip install matplotlib")
    else:
        # Test each topic type
        for topic_type in ['point', 'distance', 'midpoint', 'slope', 'equation', 'parallel']:
            print(f"\n{topic_type.upper()}:")
            diff = 'intermediate' if topic_type == 'parallel' else 'beginner'
            questions = generate_coordinate_questions(topic_type, diff, count=1, output_dir='/tmp/test_coord')
            
            if isinstance(questions, dict) and 'error' in questions:
                print(f"  Error: {questions['error']}")
            else:
                print(f"  Generated {len(questions)} questions")
                for q in questions[:2]:
                    print(f"  - {q['question_text'][:55]}...")
                    print(f"    Options: {q['options']}")
