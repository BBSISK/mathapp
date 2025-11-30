#!/usr/bin/env python3
"""
Geometry Question Generator for Math Master

Generates geometry questions with auto-generated shape images:
- Triangles (right-angled, isosceles, equilateral, scalene)
- Rectangles and Squares
- Circles
- Compound Shapes
- Angles (complementary, supplementary, vertically opposite)

Each shape comes with multiple question types testing different skills.
"""

import os
import random
import math
from datetime import datetime

# Shape generation with matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Arc, FancyArrowPatch, Circle, Rectangle, Polygon, Wedge
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_wrong_answers(correct, difficulty, max_val=None, decimal=False, min_val=1):
    """Generate plausible wrong answers - ALWAYS returns at least 3"""
    wrong = set()
    
    # First pass: try to generate natural-looking wrong answers
    attempts = 0
    while len(wrong) < 4 and attempts < 30:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.randint(1, 3) * random.choice([-1, 1])
        elif difficulty == 'intermediate':
            offset = random.randint(2, 10) * random.choice([-1, 1])
        else:
            offset = random.randint(5, 20) * random.choice([-1, 1])
        
        candidate = correct + offset
        
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        
        if candidate >= min_val and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Fallback: add simple offsets
    fallback_offsets = [1, 2, 3, 4, 5, -1, -2, 6, 7, 8, 10, 12, 15]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = correct + offset
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        if candidate >= min_val and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Last resort
    if len(wrong) < 3:
        for i in range(min_val, min_val + 20):
            if len(wrong) >= 3:
                break
            candidate = i if not decimal else float(i)
            if candidate != correct and candidate not in wrong:
                if max_val is None or candidate <= max_val:
                    wrong.add(candidate)
    
    return list(wrong)


def ensure_four_options(correct, wrong_list, as_string=True):
    """Ensure we have exactly 4 options"""
    options = [correct]
    
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options:
            options.append(w)
    
    # Pad if needed
    placeholders = [correct + 100, correct + 50, correct - 10, correct * 2]
    for p in placeholders:
        if len(options) >= 4:
            break
        if p not in options and p > 0:
            options.append(p)
    
    if as_string:
        options = [str(o) for o in options]
    
    random.shuffle(options)
    correct_str = str(correct) if as_string else correct
    return options, options.index(correct_str)


# ============================================================================
# TRIANGLE GENERATORS
# ============================================================================

def generate_right_triangle_data(difficulty='beginner'):
    """Generate a right-angled triangle with Pythagorean triples"""
    # Common Pythagorean triples scaled for difficulty
    triples = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (6, 8, 10), (9, 12, 15), (12, 16, 20), (15, 20, 25)
    ]
    
    if difficulty == 'beginner':
        base_triple = random.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
        scale = 1
    elif difficulty == 'intermediate':
        base_triple = random.choice(triples[:6])
        scale = random.choice([1, 2])
    else:
        base_triple = random.choice(triples)
        scale = random.choice([1, 2, 3])
    
    a, b, c = [x * scale for x in base_triple]
    
    return {
        'type': 'right_triangle',
        'base': a,
        'height': b,
        'hypotenuse': c,
        'area': (a * b) / 2,
        'perimeter': a + b + c,
    }


def generate_isosceles_triangle_data(difficulty='beginner'):
    """Generate an isosceles triangle"""
    if difficulty == 'beginner':
        equal_side = random.choice([5, 6, 8, 10])
        base = random.choice([4, 6, 8])
    elif difficulty == 'intermediate':
        equal_side = random.randint(6, 15)
        base = random.randint(4, 12)
    else:
        equal_side = random.randint(8, 20)
        base = random.randint(6, 16)
    
    # Calculate height using Pythagoras
    height = math.sqrt(equal_side**2 - (base/2)**2)
    height = round(height, 1)
    
    return {
        'type': 'isosceles_triangle',
        'equal_side': equal_side,
        'base': base,
        'height': height,
        'area': round((base * height) / 2, 1),
        'perimeter': equal_side * 2 + base,
    }


def generate_scalene_triangle_data(difficulty='beginner'):
    """Generate a scalene triangle with valid sides"""
    if difficulty == 'beginner':
        sides = sorted([random.randint(5, 10) for _ in range(3)])
    elif difficulty == 'intermediate':
        sides = sorted([random.randint(6, 15) for _ in range(3)])
    else:
        sides = sorted([random.randint(8, 20) for _ in range(3)])
    
    # Ensure triangle inequality (sum of two sides > third side)
    while sides[0] + sides[1] <= sides[2]:
        sides[2] -= 1
    
    a, b, c = sides
    
    # Calculate area using Heron's formula
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    
    return {
        'type': 'scalene_triangle',
        'side_a': a,
        'side_b': b,
        'side_c': c,
        'area': round(area, 1),
        'perimeter': a + b + c,
    }


def create_right_triangle_image(data, filepath, show_labels=True):
    """Create and save a right-angled triangle image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    base = data['base']
    height = data['height']
    hyp = data['hypotenuse']
    
    # Scale for display
    scale = 1
    if max(base, height) > 15:
        scale = 10 / max(base, height)
    
    b = base * scale
    h = height * scale
    
    # Draw triangle
    triangle = plt.Polygon([(0, 0), (b, 0), (0, h)], 
                           fill=True, facecolor='#e6f3ff', 
                           edgecolor='#2563eb', linewidth=3)
    ax.add_patch(triangle)
    
    # Right angle marker
    marker_size = min(b, h) * 0.15
    right_angle = plt.Polygon([(0, 0), (marker_size, 0), (marker_size, marker_size), (0, marker_size)],
                              fill=False, edgecolor='#2563eb', linewidth=2)
    ax.add_patch(right_angle)
    
    if show_labels:
        # Label sides
        ax.text(b/2, -0.5, f'{base} cm', ha='center', va='top', fontsize=14, fontweight='bold', color='#1e40af')
        ax.text(-0.5, h/2, f'{height} cm', ha='right', va='center', fontsize=14, fontweight='bold', color='#1e40af')
        ax.text(b/2 + 0.3, h/2 + 0.3, f'{hyp} cm', ha='left', va='bottom', fontsize=14, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-1.5, b + 1.5)
    ax.set_ylim(-1.5, h + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Right-Angled Triangle', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_isosceles_triangle_image(data, filepath, show_labels=True):
    """Create and save an isosceles triangle image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    base = data['base']
    equal_side = data['equal_side']
    height = data['height']
    
    # Scale for display
    scale = 1
    if max(base, height) > 15:
        scale = 10 / max(base, height)
    
    b = base * scale
    h = height * scale
    
    # Draw triangle (centered at origin)
    triangle = plt.Polygon([(-b/2, 0), (b/2, 0), (0, h)],
                           fill=True, facecolor='#fef3c7',
                           edgecolor='#d97706', linewidth=3)
    ax.add_patch(triangle)
    
    if show_labels:
        # Label sides
        ax.text(0, -0.5, f'{base} cm', ha='center', va='top', fontsize=14, fontweight='bold', color='#92400e')
        ax.text(-b/4 - 0.5, h/2, f'{equal_side} cm', ha='right', va='center', fontsize=14, fontweight='bold', color='#92400e')
        ax.text(b/4 + 0.5, h/2, f'{equal_side} cm', ha='left', va='center', fontsize=14, fontweight='bold', color='#92400e')
        
        # Show equal side markers
        ax.plot([-b/4 - 0.2, -b/4 + 0.2], [h/2 - 0.1, h/2 + 0.1], 'k-', linewidth=2)
        ax.plot([b/4 - 0.2, b/4 + 0.2], [h/2 - 0.1, h/2 + 0.1], 'k-', linewidth=2)
    
    ax.set_xlim(-b/2 - 2, b/2 + 2)
    ax.set_ylim(-1.5, h + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Isosceles Triangle', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_scalene_triangle_image(data, filepath, show_labels=True):
    """Create and save a scalene triangle image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    a = data['side_a']
    b = data['side_b']
    c = data['side_c']
    
    # Calculate vertices using law of cosines
    # Place side c along x-axis
    scale = 10 / max(a, b, c)
    c_scaled = c * scale
    
    # Calculate angle at origin using law of cosines
    cos_angle = (c**2 + a**2 - b**2) / (2 * c * a)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
    angle = math.acos(cos_angle)
    
    # Third vertex
    x2 = a * scale * math.cos(angle)
    y2 = a * scale * math.sin(angle)
    
    # Draw triangle
    triangle = plt.Polygon([(0, 0), (c_scaled, 0), (x2, y2)],
                           fill=True, facecolor='#dcfce7',
                           edgecolor='#16a34a', linewidth=3)
    ax.add_patch(triangle)
    
    if show_labels:
        # Label sides
        ax.text(c_scaled/2, -0.5, f'{c} cm', ha='center', va='top', fontsize=14, fontweight='bold', color='#166534')
        ax.text(x2/2 - 0.5, y2/2 + 0.3, f'{a} cm', ha='right', va='bottom', fontsize=14, fontweight='bold', color='#166534')
        ax.text((c_scaled + x2)/2 + 0.5, y2/2 + 0.3, f'{b} cm', ha='left', va='bottom', fontsize=14, fontweight='bold', color='#166534')
    
    ax.set_xlim(-1.5, c_scaled + 1.5)
    ax.set_ylim(-1.5, y2 + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Scalene Triangle', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# RECTANGLE AND SQUARE GENERATORS
# ============================================================================

def generate_rectangle_data(difficulty='beginner'):
    """Generate a rectangle"""
    if difficulty == 'beginner':
        length = random.choice([6, 8, 10, 12])
        width = random.choice([3, 4, 5, 6])
    elif difficulty == 'intermediate':
        length = random.randint(8, 20)
        width = random.randint(4, 12)
    else:
        length = random.randint(10, 30)
        width = random.randint(5, 20)
    
    # Ensure length > width
    if width > length:
        length, width = width, length
    
    diagonal = round(math.sqrt(length**2 + width**2), 1)
    
    return {
        'type': 'rectangle',
        'length': length,
        'width': width,
        'area': length * width,
        'perimeter': 2 * (length + width),
        'diagonal': diagonal,
    }


def generate_square_data(difficulty='beginner'):
    """Generate a square"""
    if difficulty == 'beginner':
        side = random.choice([4, 5, 6, 8, 10])
    elif difficulty == 'intermediate':
        side = random.randint(5, 15)
    else:
        side = random.randint(8, 25)
    
    diagonal = round(side * math.sqrt(2), 1)
    
    return {
        'type': 'square',
        'side': side,
        'area': side * side,
        'perimeter': 4 * side,
        'diagonal': diagonal,
    }


def create_rectangle_image(data, filepath, show_labels=True):
    """Create and save a rectangle image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    length = data['length']
    width = data['width']
    
    # Scale for display
    scale = 8 / max(length, width)
    l = length * scale
    w = width * scale
    
    # Draw rectangle
    rect = plt.Rectangle((0, 0), l, w,
                          fill=True, facecolor='#fce7f3',
                          edgecolor='#db2777', linewidth=3)
    ax.add_patch(rect)
    
    # Right angle markers at corners
    marker_size = min(l, w) * 0.1
    for corner in [(0, 0), (l, 0), (l, w), (0, w)]:
        x, y = corner
        dx = marker_size if x == 0 else -marker_size
        dy = marker_size if y == 0 else -marker_size
        ax.plot([x, x + dx], [y, y], 'k-', linewidth=1.5)
        ax.plot([x, x], [y, y + dy], 'k-', linewidth=1.5)
    
    if show_labels:
        # Label sides
        ax.text(l/2, -0.5, f'{length} cm', ha='center', va='top', fontsize=14, fontweight='bold', color='#9d174d')
        ax.text(-0.5, w/2, f'{width} cm', ha='right', va='center', fontsize=14, fontweight='bold', color='#9d174d')
    
    ax.set_xlim(-1.5, l + 1.5)
    ax.set_ylim(-1.5, w + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Rectangle', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_square_image(data, filepath, show_labels=True):
    """Create and save a square image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    side = data['side']
    
    # Scale for display
    scale = 8 / side
    s = side * scale
    
    # Draw square
    square = plt.Rectangle((0, 0), s, s,
                            fill=True, facecolor='#e0e7ff',
                            edgecolor='#4f46e5', linewidth=3)
    ax.add_patch(square)
    
    # Equal side markers
    marker_pos = s * 0.5
    marker_len = s * 0.08
    ax.plot([marker_pos - marker_len, marker_pos + marker_len], [-0.2, -0.2], 'k-', linewidth=2)
    ax.plot([marker_pos - marker_len, marker_pos + marker_len], [s + 0.2, s + 0.2], 'k-', linewidth=2)
    ax.plot([-0.2, -0.2], [marker_pos - marker_len, marker_pos + marker_len], 'k-', linewidth=2)
    ax.plot([s + 0.2, s + 0.2], [marker_pos - marker_len, marker_pos + marker_len], 'k-', linewidth=2)
    
    if show_labels:
        ax.text(s/2, -0.6, f'{side} cm', ha='center', va='top', fontsize=14, fontweight='bold', color='#3730a3')
    
    ax.set_xlim(-1.5, s + 1.5)
    ax.set_ylim(-1.5, s + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Square', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# CIRCLE GENERATORS
# ============================================================================

def generate_circle_data(difficulty='beginner'):
    """Generate a circle"""
    if difficulty == 'beginner':
        radius = random.choice([3, 4, 5, 7, 10])
    elif difficulty == 'intermediate':
        radius = random.randint(4, 14)
    else:
        radius = random.randint(6, 20)
    
    return {
        'type': 'circle',
        'radius': radius,
        'diameter': 2 * radius,
        'circumference': round(2 * math.pi * radius, 1),
        'area': round(math.pi * radius * radius, 1),
    }


def create_circle_image(data, filepath, show_labels=True):
    """Create and save a circle image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    radius = data['radius']
    
    # Draw circle
    circle = plt.Circle((0, 0), 4, fill=True, facecolor='#fef9c3', 
                         edgecolor='#ca8a04', linewidth=3)
    ax.add_patch(circle)
    
    # Draw radius line
    ax.plot([0, 4], [0, 0], 'r-', linewidth=2.5)
    ax.plot(0, 0, 'ko', markersize=6)  # Center point
    
    if show_labels:
        # Label radius
        ax.text(2, 0.4, f'r = {radius} cm', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', color='#dc2626')
        
        # Mark center
        ax.text(0.2, -0.5, 'O', ha='left', va='top', fontsize=12, fontweight='bold')
    
    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-5.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Circle', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# ANGLE GENERATORS
# ============================================================================

def generate_angle_data(difficulty='beginner'):
    """Generate angle problems"""
    angle_types = ['complementary', 'supplementary', 'angles_on_line', 'vertically_opposite', 'triangle_angles']
    
    if difficulty == 'beginner':
        angle_type = random.choice(['complementary', 'supplementary', 'triangle_angles'])
    else:
        angle_type = random.choice(angle_types)
    
    if angle_type == 'complementary':
        # Two angles that sum to 90°
        angle1 = random.randint(20, 70)
        angle2 = 90 - angle1
        return {
            'type': 'complementary',
            'angle1': angle1,
            'angle2': angle2,
            'total': 90,
            'question_angle': random.choice([1, 2]),
        }
    
    elif angle_type == 'supplementary':
        # Two angles that sum to 180°
        angle1 = random.randint(30, 150)
        angle2 = 180 - angle1
        return {
            'type': 'supplementary',
            'angle1': angle1,
            'angle2': angle2,
            'total': 180,
            'question_angle': random.choice([1, 2]),
        }
    
    elif angle_type == 'angles_on_line':
        # Three angles on a straight line summing to 180°
        angle1 = random.randint(30, 70)
        angle2 = random.randint(30, 70)
        angle3 = 180 - angle1 - angle2
        return {
            'type': 'angles_on_line',
            'angle1': angle1,
            'angle2': angle2,
            'angle3': angle3,
            'total': 180,
        }
    
    elif angle_type == 'vertically_opposite':
        angle1 = random.randint(30, 150)
        angle2 = 180 - angle1
        return {
            'type': 'vertically_opposite',
            'angle1': angle1,
            'angle2': angle2,
        }
    
    else:  # triangle_angles
        # Three angles in a triangle summing to 180°
        angle1 = random.randint(30, 80)
        angle2 = random.randint(30, 80)
        angle3 = 180 - angle1 - angle2
        return {
            'type': 'triangle_angles',
            'angle1': angle1,
            'angle2': angle2,
            'angle3': angle3,
            'total': 180,
        }


def create_angle_image(data, filepath):
    """Create and save an angle diagram"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if data['type'] == 'complementary':
        # Draw right angle with two parts
        ax.plot([0, 5], [0, 0], 'b-', linewidth=2.5)  # Horizontal
        ax.plot([0, 0], [0, 5], 'b-', linewidth=2.5)  # Vertical
        
        # Dividing line
        angle_rad = math.radians(data['angle1'])
        x = 4 * math.cos(angle_rad)
        y = 4 * math.sin(angle_rad)
        ax.plot([0, x], [0, y], 'r-', linewidth=2.5)
        
        # Right angle marker
        ax.plot([0.5, 0.5, 0], [0, 0.5, 0.5], 'b-', linewidth=1.5)
        
        # Arc for angle1
        arc1 = Arc((0, 0), 2, 2, angle=0, theta1=0, theta2=data['angle1'], color='green', linewidth=2)
        ax.add_patch(arc1)
        
        # Labels
        if data['question_angle'] == 1:
            ax.text(1.5, 0.5, '?', fontsize=18, fontweight='bold', color='green')
            ax.text(0.5, 2, f"{data['angle2']}°", fontsize=14, fontweight='bold', color='blue')
        else:
            ax.text(1.5, 0.5, f"{data['angle1']}°", fontsize=14, fontweight='bold', color='green')
            ax.text(0.5, 2, '?', fontsize=18, fontweight='bold', color='blue')
        
        ax.set_title('Complementary Angles (sum to 90°)', fontsize=14, fontweight='bold')
    
    elif data['type'] == 'supplementary':
        # Draw straight line with angle
        ax.plot([-5, 5], [0, 0], 'b-', linewidth=2.5)
        
        # Dividing line
        angle_rad = math.radians(data['angle1'])
        x = 4 * math.cos(angle_rad)
        y = 4 * math.sin(angle_rad)
        ax.plot([0, x], [0, y], 'r-', linewidth=2.5)
        
        # Arcs
        arc1 = Arc((0, 0), 2.5, 2.5, angle=0, theta1=0, theta2=data['angle1'], color='green', linewidth=2)
        ax.add_patch(arc1)
        
        # Labels
        if data['question_angle'] == 1:
            ax.text(1.5, 0.8, '?', fontsize=18, fontweight='bold', color='green')
            ax.text(-2, 0.5, f"{data['angle2']}°", fontsize=14, fontweight='bold', color='blue')
        else:
            ax.text(1.5, 0.8, f"{data['angle1']}°", fontsize=14, fontweight='bold', color='green')
            ax.text(-2, 0.5, '?', fontsize=18, fontweight='bold', color='blue')
        
        ax.set_title('Supplementary Angles (sum to 180°)', fontsize=14, fontweight='bold')
    
    elif data['type'] == 'triangle_angles':
        # Draw a triangle with labeled angles
        points = [(0, 0), (6, 0), (3, 4)]
        triangle = plt.Polygon(points, fill=True, facecolor='#e0f2fe', 
                               edgecolor='#0284c7', linewidth=3)
        ax.add_patch(triangle)
        
        # Label angles
        ax.text(-0.3, -0.3, f"{data['angle1']}°", fontsize=12, fontweight='bold', color='#0369a1')
        ax.text(6.3, -0.3, f"{data['angle2']}°", fontsize=12, fontweight='bold', color='#0369a1')
        ax.text(3, 4.3, '?', fontsize=16, fontweight='bold', color='red')
        
        ax.set_title('Angles in a Triangle (sum to 180°)', fontsize=14, fontweight='bold')
    
    elif data['type'] == 'vertically_opposite':
        # Draw two intersecting lines
        ax.plot([-4, 4], [-2, 2], 'b-', linewidth=2.5)
        ax.plot([-4, 4], [2, -2], 'b-', linewidth=2.5)
        
        # Labels
        ax.text(1.5, 0.8, f"{data['angle1']}°", fontsize=14, fontweight='bold', color='green')
        ax.text(-2.5, 0.8, '?', fontsize=18, fontweight='bold', color='red')
        ax.text(1.5, -1.2, '?', fontsize=14, fontweight='bold', color='orange')
        ax.text(-2.5, -1.2, f"{data['angle1']}°", fontsize=12, fontweight='bold', color='green')
        
        ax.set_title('Vertically Opposite Angles', fontsize=14, fontweight='bold')
    
    else:  # angles_on_line
        # Draw straight line with two dividing lines
        ax.plot([-5, 5], [0, 0], 'b-', linewidth=2.5)
        
        angle1_rad = math.radians(data['angle1'])
        ax.plot([0, 3*math.cos(angle1_rad)], [0, 3*math.sin(angle1_rad)], 'r-', linewidth=2.5)
        
        angle2_rad = math.radians(data['angle1'] + data['angle2'])
        ax.plot([0, 3*math.cos(angle2_rad)], [0, 3*math.sin(angle2_rad)], 'g-', linewidth=2.5)
        
        ax.text(1.5, 0.3, f"{data['angle1']}°", fontsize=12, fontweight='bold', color='red')
        ax.text(-0.5, 1.5, f"{data['angle2']}°", fontsize=12, fontweight='bold', color='green')
        ax.text(-2, 0.3, '?', fontsize=16, fontweight='bold', color='blue')
        
        ax.set_title('Angles on a Straight Line (sum to 180°)', fontsize=14, fontweight='bold')
    
    ax.set_xlim(-6, 7)
    ax.set_ylim(-3, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_triangle_questions(data, difficulty='beginner'):
    """Generate questions about a triangle"""
    questions = []
    
    if data['type'] == 'right_triangle':
        base = data['base']
        height = data['height']
        hyp = data['hypotenuse']
        area = data['area']
        perimeter = data['perimeter']
        
        # Q1: Find the area
        wrong = generate_wrong_answers(area, difficulty, decimal=isinstance(area, float))
        options, correct_idx = ensure_four_options(area, wrong)
        questions.append({
            'question_text': f"What is the area of this right-angled triangle?",
            'options': [f"{o} cm²" for o in options],
            'correct': correct_idx,
            'explanation': f"Area = ½ × base × height = ½ × {base} × {height} = {area} cm²",
            'difficulty': difficulty,
        })
        
        # Q2: Find the perimeter
        wrong = generate_wrong_answers(perimeter, difficulty)
        options, correct_idx = ensure_four_options(perimeter, wrong)
        questions.append({
            'question_text': f"What is the perimeter of this right-angled triangle?",
            'options': [f"{o} cm" for o in options],
            'correct': correct_idx,
            'explanation': f"Perimeter = {base} + {height} + {hyp} = {perimeter} cm",
            'difficulty': difficulty,
        })
        
        if difficulty in ['intermediate', 'advanced']:
            # Q3: Pythagoras - find hypotenuse
            questions.append({
                'question_text': f"If a right-angled triangle has sides {base} cm and {height} cm, what is the hypotenuse?",
                'options': [f"{hyp} cm", f"{base + height} cm", f"{int((base + height)/2)} cm", f"{hyp + 2} cm"],
                'correct': 0,
                'explanation': f"Using Pythagoras: c² = a² + b² = {base}² + {height}² = {base**2} + {height**2} = {hyp**2}, so c = {hyp} cm",
                'difficulty': difficulty,
            })
    
    elif data['type'] == 'isosceles_triangle':
        equal_side = data['equal_side']
        base = data['base']
        perimeter = data['perimeter']
        
        # Q1: Find the perimeter
        wrong = generate_wrong_answers(perimeter, difficulty)
        options, correct_idx = ensure_four_options(perimeter, wrong)
        questions.append({
            'question_text': f"What is the perimeter of this isosceles triangle?",
            'options': [f"{o} cm" for o in options],
            'correct': correct_idx,
            'explanation': f"Perimeter = {equal_side} + {equal_side} + {base} = {perimeter} cm",
            'difficulty': difficulty,
        })
        
        # Q2: Property question
        questions.append({
            'question_text': "How many equal sides does an isosceles triangle have?",
            'options': ['2', '3', '1', '0'],
            'correct': 0,
            'explanation': "An isosceles triangle has exactly 2 equal sides.",
            'difficulty': difficulty,
        })
    
    elif data['type'] == 'scalene_triangle':
        perimeter = data['perimeter']
        
        wrong = generate_wrong_answers(perimeter, difficulty)
        options, correct_idx = ensure_four_options(perimeter, wrong)
        questions.append({
            'question_text': f"What is the perimeter of this scalene triangle?",
            'options': [f"{o} cm" for o in options],
            'correct': correct_idx,
            'explanation': f"Perimeter = {data['side_a']} + {data['side_b']} + {data['side_c']} = {perimeter} cm",
            'difficulty': difficulty,
        })
        
        # Property question
        questions.append({
            'question_text': "What is special about a scalene triangle?",
            'options': ['All sides are different lengths', 'All sides are equal', 'Two sides are equal', 'It has a right angle'],
            'correct': 0,
            'explanation': "A scalene triangle has all sides of different lengths.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_rectangle_questions(data, difficulty='beginner'):
    """Generate questions about a rectangle or square"""
    questions = []
    
    if data['type'] == 'rectangle':
        length = data['length']
        width = data['width']
        area = data['area']
        perimeter = data['perimeter']
        
        # Q1: Find the area
        wrong = generate_wrong_answers(area, difficulty)
        options, correct_idx = ensure_four_options(area, wrong)
        questions.append({
            'question_text': f"What is the area of this rectangle?",
            'options': [f"{o} cm²" for o in options],
            'correct': correct_idx,
            'explanation': f"Area = length × width = {length} × {width} = {area} cm²",
            'difficulty': difficulty,
        })
        
        # Q2: Find the perimeter
        wrong = generate_wrong_answers(perimeter, difficulty)
        options, correct_idx = ensure_four_options(perimeter, wrong)
        questions.append({
            'question_text': f"What is the perimeter of this rectangle?",
            'options': [f"{o} cm" for o in options],
            'correct': correct_idx,
            'explanation': f"Perimeter = 2 × (length + width) = 2 × ({length} + {width}) = {perimeter} cm",
            'difficulty': difficulty,
        })
        
        if difficulty in ['intermediate', 'advanced']:
            # Q3: Find missing dimension
            questions.append({
                'question_text': f"A rectangle has area {area} cm² and length {length} cm. What is the width?",
                'options': [f"{width} cm", f"{width + 2} cm", f"{width - 1} cm", f"{length} cm"],
                'correct': 0,
                'explanation': f"Width = Area ÷ Length = {area} ÷ {length} = {width} cm",
                'difficulty': difficulty,
            })
    
    else:  # square
        side = data['side']
        area = data['area']
        perimeter = data['perimeter']
        
        # Q1: Find the area
        wrong = generate_wrong_answers(area, difficulty)
        options, correct_idx = ensure_four_options(area, wrong)
        questions.append({
            'question_text': f"What is the area of this square?",
            'options': [f"{o} cm²" for o in options],
            'correct': correct_idx,
            'explanation': f"Area = side × side = {side} × {side} = {area} cm²",
            'difficulty': difficulty,
        })
        
        # Q2: Find the perimeter
        wrong = generate_wrong_answers(perimeter, difficulty)
        options, correct_idx = ensure_four_options(perimeter, wrong)
        questions.append({
            'question_text': f"What is the perimeter of this square?",
            'options': [f"{o} cm" for o in options],
            'correct': correct_idx,
            'explanation': f"Perimeter = 4 × side = 4 × {side} = {perimeter} cm",
            'difficulty': difficulty,
        })
        
        if difficulty in ['intermediate', 'advanced']:
            # Q3: Find side from area
            questions.append({
                'question_text': f"A square has an area of {area} cm². What is the length of one side?",
                'options': [f"{side} cm", f"{side + 2} cm", f"{side * 2} cm", f"{int(area/4)} cm"],
                'correct': 0,
                'explanation': f"Side = √Area = √{area} = {side} cm",
                'difficulty': difficulty,
            })
    
    return questions


def generate_circle_questions(data, difficulty='beginner'):
    """Generate questions about a circle"""
    questions = []
    
    radius = data['radius']
    diameter = data['diameter']
    circumference = data['circumference']
    area = data['area']
    
    # Q1: Find the diameter
    wrong = generate_wrong_answers(diameter, difficulty)
    options, correct_idx = ensure_four_options(diameter, wrong)
    questions.append({
        'question_text': f"What is the diameter of this circle?",
        'options': [f"{o} cm" for o in options],
        'correct': correct_idx,
        'explanation': f"Diameter = 2 × radius = 2 × {radius} = {diameter} cm",
        'difficulty': difficulty,
    })
    
    # Q2: Find the circumference (using π ≈ 3.14)
    wrong = generate_wrong_answers(circumference, difficulty, decimal=True)
    options, correct_idx = ensure_four_options(circumference, wrong)
    questions.append({
        'question_text': f"What is the circumference of this circle? (Use π ≈ 3.14)",
        'options': [f"{o} cm" for o in options],
        'correct': correct_idx,
        'explanation': f"Circumference = 2πr = 2 × 3.14 × {radius} = {circumference} cm",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q3: Find the area
        wrong = generate_wrong_answers(area, difficulty, decimal=True)
        options, correct_idx = ensure_four_options(area, wrong)
        questions.append({
            'question_text': f"What is the area of this circle? (Use π ≈ 3.14)",
            'options': [f"{o} cm²" for o in options],
            'correct': correct_idx,
            'explanation': f"Area = πr² = 3.14 × {radius}² = 3.14 × {radius**2} = {area} cm²",
            'difficulty': difficulty,
        })
        
        # Q4: Relationship question
        questions.append({
            'question_text': "What is the relationship between the radius and diameter of a circle?",
            'options': ['Diameter = 2 × Radius', 'Diameter = Radius ÷ 2', 'Diameter = Radius + 2', 'Diameter = Radius²'],
            'correct': 0,
            'explanation': "The diameter of a circle is always twice the radius: d = 2r",
            'difficulty': difficulty,
        })
    
    return questions


def generate_angle_questions(data, difficulty='beginner'):
    """Generate questions about angles"""
    questions = []
    
    if data['type'] == 'complementary':
        known_angle = data['angle1'] if data['question_angle'] == 2 else data['angle2']
        missing_angle = data['angle2'] if data['question_angle'] == 2 else data['angle1']
        
        wrong = generate_wrong_answers(missing_angle, difficulty, max_val=90)
        options, correct_idx = ensure_four_options(missing_angle, wrong)
        questions.append({
            'question_text': f"Two angles are complementary. One angle is {known_angle}°. What is the other angle?",
            'options': [f"{o}°" for o in options],
            'correct': correct_idx,
            'explanation': f"Complementary angles sum to 90°. Missing angle = 90° - {known_angle}° = {missing_angle}°",
            'difficulty': difficulty,
        })
    
    elif data['type'] == 'supplementary':
        known_angle = data['angle1'] if data['question_angle'] == 2 else data['angle2']
        missing_angle = data['angle2'] if data['question_angle'] == 2 else data['angle1']
        
        wrong = generate_wrong_answers(missing_angle, difficulty, max_val=180)
        options, correct_idx = ensure_four_options(missing_angle, wrong)
        questions.append({
            'question_text': f"Two angles are supplementary. One angle is {known_angle}°. What is the other angle?",
            'options': [f"{o}°" for o in options],
            'correct': correct_idx,
            'explanation': f"Supplementary angles sum to 180°. Missing angle = 180° - {known_angle}° = {missing_angle}°",
            'difficulty': difficulty,
        })
    
    elif data['type'] == 'triangle_angles':
        missing = data['angle3']
        wrong = generate_wrong_answers(missing, difficulty, max_val=180)
        options, correct_idx = ensure_four_options(missing, wrong)
        questions.append({
            'question_text': f"A triangle has angles of {data['angle1']}° and {data['angle2']}°. What is the third angle?",
            'options': [f"{o}°" for o in options],
            'correct': correct_idx,
            'explanation': f"Angles in a triangle sum to 180°. Third angle = 180° - {data['angle1']}° - {data['angle2']}° = {missing}°",
            'difficulty': difficulty,
        })
    
    elif data['type'] == 'vertically_opposite':
        questions.append({
            'question_text': f"Two lines intersect. One angle is {data['angle1']}°. What is the vertically opposite angle?",
            'options': [f"{data['angle1']}°", f"{data['angle2']}°", f"{180 - data['angle1']}°", f"{90}°"],
            'correct': 0,
            'explanation': f"Vertically opposite angles are equal. The answer is {data['angle1']}°",
            'difficulty': difficulty,
        })
    
    elif data['type'] == 'angles_on_line':
        missing = data['angle3']
        wrong = generate_wrong_answers(missing, difficulty, max_val=180)
        options, correct_idx = ensure_four_options(missing, wrong)
        questions.append({
            'question_text': f"Three angles on a straight line measure {data['angle1']}°, {data['angle2']}°, and x°. Find x.",
            'options': [f"{o}°" for o in options],
            'correct': correct_idx,
            'explanation': f"Angles on a line sum to 180°. x = 180° - {data['angle1']}° - {data['angle2']}° = {missing}°",
            'difficulty': difficulty,
        })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_geometry_questions(shape_type, difficulty, count=3, output_dir='static/question_images'):
    """
    Generate geometry questions with images.
    
    Args:
        shape_type: 'triangle', 'rectangle', 'circle', or 'angle'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of different shapes to generate
        output_dir: Directory to save shape images
    
    Returns:
        List of question dictionaries with image paths
    """
    if not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not installed. Run: pip install matplotlib --user'}
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_questions = []
    
    for i in range(count):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if shape_type == 'triangle':
            # Randomly choose triangle type
            triangle_type = random.choice(['right', 'isosceles', 'scalene'])
            
            if triangle_type == 'right':
                data = generate_right_triangle_data(difficulty)
                filename = f"geom_right_triangle_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_right_triangle_image(data, filepath)
                questions = generate_triangle_questions(data, difficulty)
            elif triangle_type == 'isosceles':
                data = generate_isosceles_triangle_data(difficulty)
                filename = f"geom_isosceles_triangle_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_isosceles_triangle_image(data, filepath)
                questions = generate_triangle_questions(data, difficulty)
            else:
                data = generate_scalene_triangle_data(difficulty)
                filename = f"geom_scalene_triangle_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_scalene_triangle_image(data, filepath)
                questions = generate_triangle_questions(data, difficulty)
            
            caption = f"{triangle_type.capitalize()} Triangle"
        
        elif shape_type == 'rectangle':
            # Randomly choose rectangle or square
            rect_type = random.choice(['rectangle', 'square'])
            
            if rect_type == 'rectangle':
                data = generate_rectangle_data(difficulty)
                filename = f"geom_rectangle_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_rectangle_image(data, filepath)
                caption = "Rectangle"
            else:
                data = generate_square_data(difficulty)
                filename = f"geom_square_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_square_image(data, filepath)
                caption = "Square"
            
            questions = generate_rectangle_questions(data, difficulty)
        
        elif shape_type == 'circle':
            data = generate_circle_data(difficulty)
            filename = f"geom_circle_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_circle_image(data, filepath)
            questions = generate_circle_questions(data, difficulty)
            caption = "Circle"
        
        elif shape_type == 'angle':
            data = generate_angle_data(difficulty)
            filename = f"geom_angle_{data['type']}_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_angle_image(data, filepath)
            questions = generate_angle_questions(data, difficulty)
            caption = f"Angle Problem - {data['type'].replace('_', ' ').title()}"
        
        else:
            continue
        
        # Add image URL to each question
        image_url = f"/static/question_images/{filename}"
        for q in questions:
            q['image_url'] = image_url
            q['image_caption'] = caption
            q['topic'] = 'geometry'
            all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_geometry_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for geometry question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-geometry-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_geometry_questions():
        """Generate geometry questions with shapes"""
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({
                'error': 'matplotlib not installed. Run: pip install matplotlib --user'
            }), 400
        
        data = request.json or {}
        
        shape_types = data.get('shape_types', ['triangle', 'rectangle', 'circle', 'angle'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        shapes_per_type = data.get('shapes_per_type', 3)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for shape_type in shape_types:
            for difficulty in difficulties:
                questions = generate_geometry_questions(
                    shape_type=shape_type,
                    difficulty=difficulty,
                    count=shapes_per_type,
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
                        'topic': 'geometry',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='geometry',
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
                        'type': shape_type,
                        'difficulty': difficulty,
                        'question': q['question_text'][:50] + '...'
                    })
        
        db.session.commit()
        
        # Get updated counts
        counts = {}
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = 'geometry' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/geometry-generator-status', methods=['GET'])
    @admin_required_api
    def geometry_generator_status():
        """Check if geometry generator is available"""
        from flask import jsonify
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'shape_types': ['triangle', 'rectangle', 'circle', 'angle'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


if __name__ == '__main__':
    # Test the generators
    print("Testing Geometry Question Generator...")
    print("="*50)
    
    if not MATPLOTLIB_AVAILABLE:
        print("ERROR: matplotlib not installed!")
        print("Run: pip install matplotlib")
    else:
        # Test each shape type
        for shape_type in ['triangle', 'rectangle', 'circle', 'angle']:
            print(f"\n{shape_type.upper()}:")
            questions = generate_geometry_questions(shape_type, 'intermediate', count=1, output_dir='/tmp/test_geometry')
            
            if isinstance(questions, dict) and 'error' in questions:
                print(f"  Error: {questions['error']}")
            else:
                print(f"  Generated {len(questions)} questions")
                for q in questions[:2]:
                    print(f"  - {q['question_text'][:60]}...")
                    print(f"    Options: {q['options']}")
