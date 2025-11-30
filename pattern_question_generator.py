#!/usr/bin/env python3
"""
Pattern Question Generator for AgentMath.app

Generates pattern/sequence questions with auto-generated visual images:
- Dot patterns (triangular, square, rectangular numbers)
- Shape sequences (growing patterns)
- Block/staircase patterns
- Tile patterns (repeating)
- Number sequence visualizations

Each pattern comes with multiple question types testing different skills.
Aligned with Irish Junior Cycle Mathematics curriculum.
"""

import os
import random
import math
from datetime import datetime

# Pattern generation with matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Circle, Rectangle, RegularPolygon
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
            offset = random.randint(2, 8) * random.choice([-1, 1])
        else:
            offset = random.randint(3, 15) * random.choice([-1, 1])
        
        candidate = correct + offset
        
        if decimal:
            candidate = round(candidate, 1)
        else:
            candidate = int(candidate)
        
        if candidate >= min_val and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Fallback: add simple offsets
    fallback_offsets = [1, 2, 3, -1, -2, 4, 5, -3, 6, 7, 8, 10]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = correct + offset
        if candidate >= min_val and candidate != correct:
            if max_val is None or candidate <= max_val:
                wrong.add(candidate)
    
    # Last resort
    if len(wrong) < 3:
        for i in range(min_val, min_val + 20):
            if len(wrong) >= 3:
                break
            if i != correct and i not in wrong:
                wrong.add(i)
    
    return list(wrong)


def ensure_four_options(correct, wrong_list, as_string=True, suffix=''):
    """Ensure we have exactly 4 options"""
    options = [correct]
    
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options:
            options.append(w)
    
    # Pad if needed
    placeholders = [correct + 10, correct + 5, correct - 2, correct * 2]
    for p in placeholders:
        if len(options) >= 4:
            break
        if p not in options and p > 0:
            options.append(p)
    
    if as_string:
        options = [f"{o}{suffix}" for o in options]
    
    random.shuffle(options)
    correct_str = f"{correct}{suffix}" if as_string else correct
    return options, options.index(correct_str)


# ============================================================================
# DOT PATTERN GENERATORS
# ============================================================================

def generate_triangular_pattern_data(difficulty='beginner'):
    """Generate triangular number pattern (1, 3, 6, 10, 15...)"""
    # Triangular numbers: n(n+1)/2
    if difficulty == 'beginner':
        show_terms = 4
        ask_term = 5
    elif difficulty == 'intermediate':
        show_terms = 4
        ask_term = random.choice([6, 7, 8])
    else:
        show_terms = 5
        ask_term = random.choice([8, 9, 10])
    
    def triangular(n):
        return n * (n + 1) // 2
    
    sequence = [triangular(i) for i in range(1, show_terms + 1)]
    answer = triangular(ask_term)
    
    return {
        'type': 'triangular',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer,
        'formula': 'n(n+1)/2',
        'name': 'Triangular Numbers',
    }


def generate_square_pattern_data(difficulty='beginner'):
    """Generate square number pattern (1, 4, 9, 16, 25...)"""
    if difficulty == 'beginner':
        show_terms = 4
        ask_term = 5
    elif difficulty == 'intermediate':
        show_terms = 4
        ask_term = random.choice([6, 7, 8])
    else:
        show_terms = 5
        ask_term = random.choice([9, 10, 11])
    
    sequence = [i * i for i in range(1, show_terms + 1)]
    answer = ask_term * ask_term
    
    return {
        'type': 'square',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer,
        'formula': 'n²',
        'name': 'Square Numbers',
    }


def generate_rectangular_pattern_data(difficulty='beginner'):
    """Generate rectangular/oblong pattern (2, 6, 12, 20, 30...)"""
    # Rectangular numbers: n(n+1)
    if difficulty == 'beginner':
        show_terms = 4
        ask_term = 5
    elif difficulty == 'intermediate':
        show_terms = 4
        ask_term = random.choice([6, 7])
    else:
        show_terms = 5
        ask_term = random.choice([8, 9, 10])
    
    def rectangular(n):
        return n * (n + 1)
    
    sequence = [rectangular(i) for i in range(1, show_terms + 1)]
    answer = rectangular(ask_term)
    
    return {
        'type': 'rectangular',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer,
        'formula': 'n(n+1)',
        'name': 'Rectangular Numbers',
    }


# ============================================================================
# LINEAR PATTERN GENERATORS
# ============================================================================

def generate_linear_pattern_data(difficulty='beginner'):
    """Generate linear pattern (arithmetic sequence)"""
    if difficulty == 'beginner':
        # Simple patterns like 2, 4, 6, 8 or 5, 10, 15, 20
        start = random.choice([1, 2, 3, 5])
        step = random.choice([2, 3, 5, 10])
        show_terms = 4
        ask_term = 5
    elif difficulty == 'intermediate':
        start = random.randint(1, 10)
        step = random.choice([3, 4, 5, 6, 7])
        show_terms = 4
        ask_term = random.choice([6, 7, 8, 10])
    else:
        start = random.randint(1, 20)
        step = random.choice([4, 5, 6, 7, 8, 9, 11, 12])
        show_terms = 5
        ask_term = random.choice([10, 12, 15, 20])
    
    sequence = [start + step * i for i in range(show_terms)]
    answer = start + step * (ask_term - 1)
    
    return {
        'type': 'linear',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer,
        'start': start,
        'step': step,
        'formula': f'{step}n + {start - step}' if start != step else f'{step}n',
        'name': 'Linear Pattern',
    }


def generate_staircase_pattern_data(difficulty='beginner'):
    """Generate staircase/block pattern (cumulative: 1, 3, 6, 10...)"""
    if difficulty == 'beginner':
        step = random.choice([1, 2])
        show_terms = 4
        ask_term = 5
    elif difficulty == 'intermediate':
        step = random.choice([2, 3])
        show_terms = 4
        ask_term = random.choice([6, 7])
    else:
        step = random.choice([3, 4, 5])
        show_terms = 5
        ask_term = random.choice([8, 9, 10])
    
    # Each term adds (step * term_number) blocks
    sequence = []
    total = 0
    for i in range(1, show_terms + 1):
        total += step * i
        sequence.append(total)
    
    # Calculate answer
    answer_total = 0
    for i in range(1, ask_term + 1):
        answer_total += step * i
    
    return {
        'type': 'staircase',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer_total,
        'step': step,
        'name': 'Staircase Pattern',
    }


# ============================================================================
# SHAPE SEQUENCE GENERATORS
# ============================================================================

def generate_growing_shape_data(difficulty='beginner'):
    """Generate growing shape pattern (matchsticks)"""
    # Common patterns: squares and triangles joined (sharing sides)
    # Pentagon and hexagon removed due to image rendering complexity
    patterns = [
        {'name': 'Squares in a Row', 'first': 4, 'add': 3, 'shape': 'square'},  # 4, 7, 10, 13...
        {'name': 'Triangles in a Row', 'first': 3, 'add': 2, 'shape': 'triangle'},  # 3, 5, 7, 9...
    ]
    
    pattern = random.choice(patterns)
    
    if difficulty == 'beginner':
        show_terms = 3
        ask_term = 4
    elif difficulty == 'intermediate':
        show_terms = 4
        ask_term = random.choice([5, 6, 7])
    else:
        show_terms = 4
        ask_term = random.choice([8, 10, 12])
    
    sequence = [pattern['first'] + pattern['add'] * i for i in range(show_terms)]
    answer = pattern['first'] + pattern['add'] * (ask_term - 1)
    
    return {
        'type': 'growing_shape',
        'sequence': sequence,
        'show_terms': show_terms,
        'ask_term': ask_term,
        'answer': answer,
        'first': pattern['first'],
        'add': pattern['add'],
        'shape': pattern['shape'],
        'name': pattern['name'],
        'formula': f"{pattern['add']}n + {pattern['first'] - pattern['add']}",
    }


def generate_tile_pattern_data(difficulty='beginner'):
    """Generate repeating tile pattern"""
    if difficulty == 'beginner':
        # Simple 2-color repeat
        colors = ['🔵', '🔴']
        repeat_length = 2
        total_shown = 6
        ask_position = random.choice([7, 8, 9, 10])
    elif difficulty == 'intermediate':
        colors = random.choice([
            ['🔵', '🔴', '🟢'],
            ['🟡', '🟣', '🔵'],
            ['⬛', '⬜', '🟫'],
        ])
        repeat_length = 3
        total_shown = 6
        ask_position = random.choice([10, 11, 12, 13, 15])
    else:
        colors = random.choice([
            ['🔵', '🔴', '🟢', '🟡'],
            ['⬛', '⬜', '🟫', '🟧'],
        ])
        repeat_length = 4
        total_shown = 8
        ask_position = random.choice([15, 17, 20, 23, 25])
    
    # Generate the shown pattern
    pattern = [colors[i % repeat_length] for i in range(total_shown)]
    
    # Find the answer
    answer_idx = (ask_position - 1) % repeat_length
    answer = colors[answer_idx]
    
    return {
        'type': 'tile',
        'pattern': pattern,
        'colors': colors,
        'repeat_length': repeat_length,
        'ask_position': ask_position,
        'answer': answer,
        'name': 'Repeating Tile Pattern',
    }


# ============================================================================
# IMAGE GENERATORS
# ============================================================================

def create_triangular_pattern_image(data, filepath):
    """Create triangular number pattern image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    show_terms = min(data['show_terms'], 5)  # Max 5 for visual clarity
    
    x_offset = 0
    spacing = 3
    
    for term in range(1, show_terms + 1):
        # Draw triangular arrangement
        dot_count = term * (term + 1) // 2
        
        row = 1
        col = 0
        for dot in range(dot_count):
            x = x_offset + col * 0.4
            y = (term - row) * 0.35
            circle = Circle((x, y), 0.15, color='#3b82f6', ec='#1e40af', linewidth=1)
            ax.add_patch(circle)
            
            col += 1
            if col >= row:
                row += 1
                col = 0
        
        # Label below
        ax.text(x_offset + (term - 1) * 0.2, -0.8, f'Shape {term}\n({data["sequence"][term-1]} dots)', 
                ha='center', va='top', fontsize=10, fontweight='bold')
        
        x_offset += spacing
    
    # Question mark for next term
    ax.text(x_offset + 0.5, 0.5, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 0.5, -0.8, f'Shape {data["ask_term"]}', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-1, x_offset + 2)
    ax.set_ylim(-1.5, show_terms + 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Triangular Number Pattern', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_square_pattern_image(data, filepath):
    """Create square number pattern image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    show_terms = min(data['show_terms'], 5)
    
    x_offset = 0
    spacing = 0.5
    
    colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
    
    for term in range(1, show_terms + 1):
        # Draw square grid
        size = term
        for row in range(size):
            for col in range(size):
                rect = Rectangle((x_offset + col * 0.5, row * 0.5), 0.45, 0.45,
                                  color=colors[(term-1) % len(colors)], ec='white', linewidth=1)
                ax.add_patch(rect)
        
        # Label below
        center_x = x_offset + (size - 1) * 0.25
        ax.text(center_x, -0.6, f'Shape {term}\n({data["sequence"][term-1]})', 
                ha='center', va='top', fontsize=10, fontweight='bold')
        
        x_offset += size * 0.5 + spacing + 1
    
    # Question mark for next term
    ax.text(x_offset + 1, 1, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 1, -0.6, f'Shape {data["ask_term"]}', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-0.5, x_offset + 3)
    ax.set_ylim(-1.5, show_terms * 0.5 + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Square Number Pattern', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_linear_pattern_image(data, filepath):
    """Create linear pattern image with dots"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 4))
    
    show_terms = min(data['show_terms'], 5)
    sequence = data['sequence'][:show_terms]
    
    x_offset = 0
    max_dots = max(sequence)
    
    for term_idx, dot_count in enumerate(sequence):
        term = term_idx + 1
        
        # Draw dots in rows of 5
        for i in range(dot_count):
            row = i // 5
            col = i % 5
            x = x_offset + col * 0.4
            y = row * 0.4
            circle = Circle((x, y), 0.15, color='#8b5cf6', ec='#6d28d9', linewidth=1)
            ax.add_patch(circle)
        
        # Label
        rows_needed = (dot_count + 4) // 5
        ax.text(x_offset + 0.8, -0.6, f'Term {term}\n({dot_count})', 
                ha='center', va='top', fontsize=10, fontweight='bold')
        
        x_offset += 3
    
    # Question mark
    ax.text(x_offset + 0.8, 0.5, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 0.8, -0.6, f'Term {data["ask_term"]}', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-0.5, x_offset + 2.5)
    ax.set_ylim(-1.5, max((max_dots + 4) // 5, 2) * 0.4 + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title(f'Linear Pattern: {sequence[0]}, {sequence[1]}, {sequence[2]}...', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_staircase_pattern_image(data, filepath):
    """Create staircase/block pattern image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    show_terms = min(data['show_terms'], 4)
    step = data['step']
    
    x_offset = 0
    
    colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
    
    for term in range(1, show_terms + 1):
        # Draw staircase - each level has (step * level) blocks
        y = 0
        for level in range(1, term + 1):
            blocks_in_level = step * level
            for b in range(blocks_in_level):
                rect = Rectangle((x_offset + b * 0.35, y), 0.3, 0.3,
                                  color=colors[(level-1) % len(colors)], ec='white', linewidth=1)
                ax.add_patch(rect)
            y += 0.35
        
        # Label
        total_blocks = sum(step * i for i in range(1, term + 1))
        max_width = step * term * 0.35
        ax.text(x_offset + max_width / 2, -0.5, f'Shape {term}\n({total_blocks} blocks)', 
                ha='center', va='top', fontsize=10, fontweight='bold')
        
        x_offset += step * term * 0.35 + 1.5
    
    # Question mark
    ax.text(x_offset + 1, 1, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 1, -0.5, f'Shape {data["ask_term"]}', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-0.5, x_offset + 3)
    ax.set_ylim(-1.2, show_terms * 0.4 + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Staircase Pattern', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_growing_shape_image(data, filepath):
    """Create growing shape pattern image (matchstick-style with shared sides)"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 4))
    
    show_terms = min(data['show_terms'], 4)
    shape = data['shape']
    
    # Colors for each shape type
    colors = {
        'square': '#3b82f6',
        'triangle': '#10b981'
    }
    color = colors.get(shape, '#3b82f6')
    lw = 3  # Line width for matchsticks
    
    x_offset = 0
    
    for term in range(1, show_terms + 1):
        # Draw connected shapes sharing sides
        if shape == 'square':
            # Squares in a row sharing vertical sides
            size = 0.8
            for s in range(term):
                x = x_offset + s * size
                # First square: draw all 4 sides
                # Subsequent squares: skip left side (shared)
                if s == 0:
                    # Left side
                    ax.plot([x, x], [0, size], color=color, linewidth=lw)
                # Bottom
                ax.plot([x, x + size], [0, 0], color=color, linewidth=lw)
                # Top
                ax.plot([x, x + size], [size, size], color=color, linewidth=lw)
                # Right
                ax.plot([x + size, x + size], [0, size], color=color, linewidth=lw)
            
            label_x = x_offset + (term * size) / 2
            x_offset += term * size + 1.2
                
        elif shape == 'triangle':
            # Triangles in a row sharing a side (alternating up/down)
            base = 0.7
            height = 0.6
            for s in range(term):
                x = x_offset + s * (base / 2)
                if s % 2 == 0:  # Pointing up
                    if s == 0:
                        # Left side
                        ax.plot([x, x + base/2], [0, height], color=color, linewidth=lw)
                    # Right side
                    ax.plot([x + base/2, x + base], [height, 0], color=color, linewidth=lw)
                    # Bottom
                    ax.plot([x, x + base], [0, 0], color=color, linewidth=lw)
                else:  # Pointing down (inverted) - shares left side with previous
                    # Right side going up
                    ax.plot([x + base/2, x + base], [0, height], color=color, linewidth=lw)
                    # Top connects the peaks
                    ax.plot([x, x + base], [height, height], color=color, linewidth=lw)
            
            label_x = x_offset + (term * base / 2) / 2 + base / 4
            x_offset += term * (base / 2) + base / 2 + 1.0
            
        # Label with matchstick count
        ax.text(label_x, -0.4, 
                f'{term} shape{"s" if term > 1 else ""}\n({data["sequence"][term-1]} sticks)', 
                ha='center', va='top', fontsize=9, fontweight='bold')
    
    # Question mark
    ax.text(x_offset + 0.5, 0.4, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 0.5, -0.4, f'{data["ask_term"]} shapes', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-0.3, x_offset + 1.5)
    ax.set_ylim(-1.0, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title(f'{data["name"]} - How many matchsticks?', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_tile_pattern_image(data, filepath):
    """Create repeating tile pattern image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 3))
    
    pattern = data['pattern']
    ask_position = data['ask_position']
    
    # Color mapping for emojis to actual colors
    color_map = {
        '🔵': '#3b82f6', '🔴': '#ef4444', '🟢': '#22c55e', '🟡': '#eab308',
        '🟣': '#a855f7', '⬛': '#1f2937', '⬜': '#f3f4f6', '🟫': '#92400e',
        '🟧': '#f97316',
    }
    
    # Draw the shown pattern
    for i, tile in enumerate(pattern):
        color = color_map.get(tile, '#gray')
        rect = Rectangle((i * 0.8, 0), 0.7, 0.7, color=color, ec='white', linewidth=2)
        ax.add_patch(rect)
        ax.text(i * 0.8 + 0.35, -0.3, str(i + 1), ha='center', va='top', fontsize=9)
    
    # Draw dots to show continuation
    x = len(pattern) * 0.8
    for i in range(3):
        ax.plot(x + i * 0.3, 0.35, 'ko', markersize=6)
    
    # Draw question mark tile
    x = len(pattern) * 0.8 + 1.5
    rect = Rectangle((x, 0), 0.7, 0.7, color='#e5e7eb', ec='#dc2626', linewidth=3)
    ax.add_patch(rect)
    ax.text(x + 0.35, 0.35, '?', ha='center', va='center', fontsize=20, 
            color='#dc2626', fontweight='bold')
    ax.text(x + 0.35, -0.3, str(ask_position), ha='center', va='top', fontsize=9,
            color='#dc2626', fontweight='bold')
    
    ax.set_xlim(-0.3, x + 1.5)
    ax.set_ylim(-0.8, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title(f'Repeating Pattern - What colour is tile {ask_position}?', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def create_rectangular_pattern_image(data, filepath):
    """Create rectangular number pattern image"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    show_terms = min(data['show_terms'], 4)
    
    x_offset = 0
    
    colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b']
    
    for term in range(1, show_terms + 1):
        # Draw rectangular grid (n rows × (n+1) columns)
        rows = term
        cols = term + 1
        
        for r in range(rows):
            for c in range(cols):
                rect = Rectangle((x_offset + c * 0.4, r * 0.4), 0.35, 0.35,
                                  color=colors[(term-1) % len(colors)], ec='white', linewidth=1)
                ax.add_patch(rect)
        
        # Label
        total = term * (term + 1)
        ax.text(x_offset + cols * 0.2, -0.5, f'Shape {term}\n({total} squares)', 
                ha='center', va='top', fontsize=9, fontweight='bold')
        
        x_offset += cols * 0.4 + 1
    
    # Question mark
    ax.text(x_offset + 1, 0.8, '?', fontsize=40, ha='center', va='center', 
            color='#dc2626', fontweight='bold')
    ax.text(x_offset + 1, -0.5, f'Shape {data["ask_term"]}', 
            ha='center', va='top', fontsize=10, fontweight='bold', color='#dc2626')
    
    ax.set_xlim(-0.3, x_offset + 3)
    ax.set_ylim(-1.2, show_terms * 0.4 + 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Rectangular Number Pattern', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_dot_pattern_questions(data, difficulty='beginner'):
    """Generate questions about dot/number patterns"""
    questions = []
    
    pattern_type = data['type']
    sequence = data['sequence']
    ask_term = data['ask_term']
    answer = data['answer']
    name = data['name']
    
    # Q1: Find the next term
    wrong = generate_wrong_answers(answer, difficulty)
    options, correct_idx = ensure_four_options(answer, wrong)
    
    questions.append({
        'question_text': f"Look at the {name.lower()} pattern. How many dots will be in Shape {ask_term}?",
        'options': options,
        'correct': correct_idx,
        'explanation': f"The sequence is {', '.join(map(str, sequence))}... Shape {ask_term} has {answer} dots.",
        'difficulty': difficulty,
    })
    
    # Q2: Identify the pattern rule
    if pattern_type == 'triangular':
        questions.append({
            'question_text': f"What type of number pattern is this: {', '.join(map(str, sequence))}...?",
            'options': ['Triangular numbers', 'Square numbers', 'Cube numbers', 'Prime numbers'],
            'correct': 0,
            'explanation': f"These are triangular numbers. Each shape adds one more row of dots.",
            'difficulty': difficulty,
        })
    elif pattern_type == 'square':
        questions.append({
            'question_text': f"What type of number pattern is this: {', '.join(map(str, sequence))}...?",
            'options': ['Square numbers', 'Triangular numbers', 'Even numbers', 'Odd numbers'],
            'correct': 0,
            'explanation': f"These are square numbers (n²). Each shape is a perfect square.",
            'difficulty': difficulty,
        })
    elif pattern_type == 'rectangular':
        questions.append({
            'question_text': f"The pattern shows {sequence[0]}, {sequence[1]}, {sequence[2]}... What's the rule?",
            'options': ['n × (n+1)', 'n × n', 'n + (n+1)', '2n'],
            'correct': 0,
            'explanation': f"These are rectangular numbers. Each shape is n rows by (n+1) columns.",
            'difficulty': difficulty,
        })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q3: Find a specific term
        specific_term = ask_term + random.randint(2, 5)
        if pattern_type == 'triangular':
            specific_answer = specific_term * (specific_term + 1) // 2
        elif pattern_type == 'square':
            specific_answer = specific_term * specific_term
        else:  # rectangular
            specific_answer = specific_term * (specific_term + 1)
        
        wrong = generate_wrong_answers(specific_answer, difficulty)
        options, correct_idx = ensure_four_options(specific_answer, wrong)
        
        questions.append({
            'question_text': f"In the {name.lower()} pattern, how many dots are in Shape {specific_term}?",
            'options': options,
            'correct': correct_idx,
            'explanation': f"Using the formula for {name.lower()}, Shape {specific_term} has {specific_answer} dots.",
            'difficulty': difficulty,
        })
    
    if difficulty == 'advanced':
        # Q4: Formula question
        if pattern_type == 'triangular':
            questions.append({
                'question_text': "What is the formula for the nth triangular number?",
                'options': ['n(n+1)/2', 'n²', 'n(n+1)', '2n'],
                'correct': 0,
                'explanation': "Triangular numbers follow the formula n(n+1)/2.",
                'difficulty': difficulty,
            })
        elif pattern_type == 'square':
            questions.append({
                'question_text': "What is the formula for the nth square number?",
                'options': ['n²', 'n(n+1)/2', '2n', 'n+1'],
                'correct': 0,
                'explanation': "Square numbers follow the formula n² (n squared).",
                'difficulty': difficulty,
            })
    
    return questions


def generate_linear_pattern_questions(data, difficulty='beginner'):
    """Generate questions about linear patterns using Irish curriculum formula Tₙ = a + (n-1)d"""
    questions = []
    
    sequence = data['sequence']
    ask_term = data['ask_term']
    answer = data['answer']
    step = data['step']  # This is 'd' (common difference)
    start = data['start']  # This is 'a' (first term)
    
    # Q1: Find the next term - always include formula reference
    wrong = generate_wrong_answers(answer, difficulty)
    options, correct_idx = ensure_four_options(answer, wrong)
    
    questions.append({
        'question_text': f"Continue the pattern: {', '.join(map(str, sequence))}... What is term {ask_term}?\n\n(Hint: Use Tₙ = a + (n-1)d where a = first term, d = common difference)",
        'options': options,
        'correct': correct_idx,
        'explanation': f"Using Tₙ = a + (n-1)d where a = {start} (first term) and d = {step} (common difference):\nT{ask_term} = {start} + ({ask_term}-1) × {step} = {start} + {ask_term - 1} × {step} = {start} + {(ask_term - 1) * step} = {answer}",
        'difficulty': difficulty,
    })
    
    # Q2: Find the common difference
    wrong = generate_wrong_answers(step, difficulty, min_val=1)
    options, correct_idx = ensure_four_options(step, wrong)
    
    questions.append({
        'question_text': f"What is the common difference (d) in the pattern: {', '.join(map(str, sequence))}...?",
        'options': options,
        'correct': correct_idx,
        'explanation': f"The common difference d = {sequence[1]} - {sequence[0]} = {step}. In the formula Tₙ = a + (n-1)d, d represents how much is added between consecutive terms.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q3: nth term formula using Tₙ = a + (n-1)d format
        # Generate the formula in expanded form for options
        a = start  # first term
        d = step   # common difference
        
        # Correct formula: Tₙ = a + (n-1)d
        correct_formula = f"Tₙ = {a} + (n-1) × {d}"
        
        # Generate wrong formulas - ensure uniqueness
        wrong_formulas = set()
        wrong_formulas.add(f"Tₙ = {a} + n × {d}")  # Common mistake: using n instead of (n-1)
        if a != d:  # Only add if different from correct
            wrong_formulas.add(f"Tₙ = {d} + (n-1) × {a}")  # Swapped a and d
        wrong_formulas.add(f"Tₙ = {a + d} + (n-1) × {d}")  # Wrong first term (T₂ value)
        wrong_formulas.add(f"Tₙ = {a} + (n+1) × {d}")  # Wrong: n+1 instead of n-1
        wrong_formulas.add(f"Tₙ = {a - d} + (n-1) × {d}")  # Wrong first term (before T₁)
        wrong_formulas.add(f"Tₙ = {a} + (n-1) × {d + 1}")  # Wrong common difference
        
        # Remove correct formula if accidentally added and convert to list
        wrong_formulas.discard(correct_formula)
        wrong_list = list(wrong_formulas)[:3]
        
        options = [correct_formula] + wrong_list
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the nth term formula for: {', '.join(map(str, sequence))}...?\n\n(Use the formula Tₙ = a + (n-1)d)",
            'options': options,
            'correct': options.index(correct_formula),
            'explanation': f"Using Tₙ = a + (n-1)d where a = {a} (first term) and d = {d} (common difference):\nTₙ = {a} + (n-1) × {d}\n\nCheck: T₁ = {a} + (1-1) × {d} = {a} + 0 = {a} ✓\nT₂ = {a} + (2-1) × {d} = {a} + {d} = {a + d} ✓",
            'difficulty': difficulty,
        })
        
        # Q4: Apply formula to find specific term (advanced only)
        if difficulty == 'advanced':
            # Ask for a larger term
            find_term = random.choice([15, 20, 25, 50])
            term_answer = a + (find_term - 1) * d
            
            wrong = generate_wrong_answers(term_answer, difficulty)
            options, correct_idx = ensure_four_options(term_answer, wrong)
            
            questions.append({
                'question_text': f"For the pattern {', '.join(map(str, sequence[:3]))}..., find T{find_term} using Tₙ = a + (n-1)d",
                'options': options,
                'correct': correct_idx,
                'explanation': f"Tₙ = a + (n-1)d where a = {a}, d = {d}\nT{find_term} = {a} + ({find_term}-1) × {d}\nT{find_term} = {a} + {find_term - 1} × {d}\nT{find_term} = {a} + {(find_term - 1) * d}\nT{find_term} = {term_answer}",
                'difficulty': difficulty,
            })
    
    return questions


def generate_staircase_questions(data, difficulty='beginner'):
    """Generate questions about staircase patterns"""
    questions = []
    
    sequence = data['sequence']
    ask_term = data['ask_term']
    answer = data['answer']
    
    # Q1: Find total blocks in next shape
    wrong = generate_wrong_answers(answer, difficulty)
    options, correct_idx = ensure_four_options(answer, wrong)
    
    questions.append({
        'question_text': f"The staircase pattern has {', '.join(map(str, sequence))} blocks. How many blocks in Shape {ask_term}?",
        'options': [f"{o} blocks" for o in options] if not isinstance(options[0], str) else options,
        'correct': correct_idx,
        'explanation': f"Shape {ask_term} has {answer} blocks total.",
        'difficulty': difficulty,
    })
    
    # Q2: Difference between terms
    if len(sequence) >= 2:
        diff = sequence[-1] - sequence[-2]
        wrong = generate_wrong_answers(diff, difficulty, min_val=1)
        options, correct_idx = ensure_four_options(diff, wrong)
        
        questions.append({
            'question_text': f"How many more blocks are added from Shape {len(sequence)-1} to Shape {len(sequence)}?",
            'options': options,
            'correct': correct_idx,
            'explanation': f"Difference = {sequence[-1]} - {sequence[-2]} = {diff} blocks.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_growing_shape_questions(data, difficulty='beginner'):
    """Generate questions about growing shape patterns using Tₙ = a + (n-1)d formula"""
    questions = []
    
    sequence = data['sequence']
    ask_term = data['ask_term']
    answer = data['answer']
    shape = data['shape']
    add = data['add']  # This is 'd' (common difference)
    first = data['first']  # This is 'a' (first term)
    
    # Q1: Find matchsticks in next shape - include formula hint
    wrong = generate_wrong_answers(answer, difficulty)
    options, correct_idx = ensure_four_options(answer, wrong, suffix=' sticks')
    
    questions.append({
        'question_text': f"The {shape} pattern uses {', '.join(map(str, sequence))} matchsticks. How many for {ask_term} {shape}s?\n\n(Use Tₙ = a + (n-1)d where a = first term, d = common difference)",
        'options': options,
        'correct': correct_idx,
        'explanation': f"Using Tₙ = a + (n-1)d where a = {first} (first term) and d = {add} (common difference):\nT{ask_term} = {first} + ({ask_term}-1) × {add} = {first} + {(ask_term-1) * add} = {answer} sticks",
        'difficulty': difficulty,
    })
    
    # Q2: How many added each time (common difference)
    wrong = generate_wrong_answers(add, difficulty, min_val=1)
    options, correct_idx = ensure_four_options(add, wrong)
    
    questions.append({
        'question_text': f"What is the common difference (d) - how many matchsticks are added for each new {shape}?",
        'options': options,
        'correct': correct_idx,
        'explanation': f"The common difference d = {add}. Each new {shape} shares one side with the previous one, so we add {add} new matchsticks. In Tₙ = a + (n-1)d, this is the value of d.",
        'difficulty': difficulty,
    })
    
    if difficulty in ['intermediate', 'advanced']:
        # Q3: Formula using Tₙ = a + (n-1)d format
        a = first  # first term
        d = add    # common difference
        
        correct_formula = f"Tₙ = {a} + (n-1) × {d}"
        
        # Generate wrong formulas - ensure uniqueness
        wrong_formulas = set()
        wrong_formulas.add(f"Tₙ = {a} + n × {d}")  # Common mistake
        if a != d:  # Only add if different from correct
            wrong_formulas.add(f"Tₙ = {d} + (n-1) × {a}")  # Swapped
        wrong_formulas.add(f"Tₙ = {a + d} + (n-1) × {d}")  # Wrong first term (T₂ value)
        wrong_formulas.add(f"Tₙ = {a} + (n+1) × {d}")  # Wrong: n+1 instead of n-1
        wrong_formulas.add(f"Tₙ = {a} + (n-1) × {d + 1}")  # Wrong common difference
        
        # Remove correct formula if accidentally added
        wrong_formulas.discard(correct_formula)
        wrong_list = list(wrong_formulas)[:3]
        
        options = [correct_formula] + wrong_list
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is the formula for the number of matchsticks with n {shape}s?\n\n(Use Tₙ = a + (n-1)d)",
            'options': options,
            'correct': options.index(correct_formula),
            'explanation': f"Using Tₙ = a + (n-1)d where a = {a} (first {shape} uses {a} sticks) and d = {d} (each new {shape} adds {d} sticks):\nTₙ = {a} + (n-1) × {d}\n\nCheck: T₁ = {a} + 0 = {a} ✓, T₂ = {a} + {d} = {a + d} ✓",
            'difficulty': difficulty,
        })
    
    return questions


def generate_tile_pattern_questions(data, difficulty='beginner'):
    """Generate questions about repeating tile patterns"""
    questions = []
    
    colors = data['colors']
    repeat_length = data['repeat_length']
    ask_position = data['ask_position']
    answer = data['answer']
    
    # Q1: What colour is tile X?
    wrong_colors = [c for c in colors if c != answer]
    if len(wrong_colors) < 3:
        wrong_colors = wrong_colors + ['🟤', '⬜', '🟠']
    options = [answer] + wrong_colors[:3]
    random.shuffle(options)
    
    questions.append({
        'question_text': f"The pattern repeats: {' '.join(colors)}. What colour is tile {ask_position}?",
        'options': options,
        'correct': options.index(answer),
        'explanation': f"Pattern repeats every {repeat_length} tiles. Tile {ask_position}: {ask_position} ÷ {repeat_length} has remainder {(ask_position - 1) % repeat_length + 1}, so it's {answer}.",
        'difficulty': difficulty,
    })
    
    # Q2: Pattern length
    wrong = generate_wrong_answers(repeat_length, difficulty, min_val=2, max_val=6)
    options, correct_idx = ensure_four_options(repeat_length, wrong)
    
    questions.append({
        'question_text': f"How many tiles are in one complete repeat of the pattern?",
        'options': options,
        'correct': correct_idx,
        'explanation': f"The pattern {' '.join(colors)} has {repeat_length} tiles before it repeats.",
        'difficulty': difficulty,
    })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_pattern_questions(pattern_type, difficulty, count=3, output_dir='static/question_images'):
    """
    Generate pattern questions with images.
    
    Args:
        pattern_type: 'dot', 'linear', 'staircase', 'shape', 'tile'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of different patterns to generate
        output_dir: Directory to save pattern images
    
    Returns:
        List of question dictionaries with image paths
    """
    if not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not installed. Run: pip install matplotlib --user'}
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_questions = []
    
    for i in range(count):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if pattern_type == 'dot':
            # Randomly choose dot pattern type
            dot_type = random.choice(['triangular', 'square', 'rectangular'])
            
            if dot_type == 'triangular':
                data = generate_triangular_pattern_data(difficulty)
                filename = f"pattern_triangular_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_triangular_pattern_image(data, filepath)
            elif dot_type == 'square':
                data = generate_square_pattern_data(difficulty)
                filename = f"pattern_square_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_square_pattern_image(data, filepath)
            else:
                data = generate_rectangular_pattern_data(difficulty)
                filename = f"pattern_rectangular_{difficulty}_{timestamp}_{i}.png"
                filepath = os.path.join(output_dir, filename)
                create_rectangular_pattern_image(data, filepath)
            
            questions = generate_dot_pattern_questions(data, difficulty)
            caption = data['name']
        
        elif pattern_type == 'linear':
            data = generate_linear_pattern_data(difficulty)
            filename = f"pattern_linear_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_linear_pattern_image(data, filepath)
            questions = generate_linear_pattern_questions(data, difficulty)
            caption = "Linear Number Pattern"
        
        elif pattern_type == 'staircase':
            data = generate_staircase_pattern_data(difficulty)
            filename = f"pattern_staircase_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_staircase_pattern_image(data, filepath)
            questions = generate_staircase_questions(data, difficulty)
            caption = "Staircase Block Pattern"
        
        elif pattern_type == 'shape':
            data = generate_growing_shape_data(difficulty)
            filename = f"pattern_shape_{data['shape']}_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_growing_shape_image(data, filepath)
            questions = generate_growing_shape_questions(data, difficulty)
            caption = data['name']
        
        elif pattern_type == 'tile':
            data = generate_tile_pattern_data(difficulty)
            filename = f"pattern_tile_{difficulty}_{timestamp}_{i}.png"
            filepath = os.path.join(output_dir, filename)
            create_tile_pattern_image(data, filepath)
            questions = generate_tile_pattern_questions(data, difficulty)
            caption = "Repeating Tile Pattern"
        
        else:
            continue
        
        # Add image URL to each question
        image_url = f"/static/question_images/{filename}"
        for q in questions:
            q['image_url'] = image_url
            q['image_caption'] = caption
            q['topic'] = 'patterns'
            all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_pattern_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for pattern question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-pattern-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_pattern_questions():
        """Generate pattern questions with images"""
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({
                'error': 'matplotlib not installed. Run: pip install matplotlib --user'
            }), 400
        
        data = request.json or {}
        
        pattern_types = data.get('pattern_types', ['dot', 'linear', 'staircase', 'shape', 'tile'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        patterns_per_type = data.get('patterns_per_type', 3)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for pattern_type in pattern_types:
            for difficulty in difficulties:
                questions = generate_pattern_questions(
                    pattern_type=pattern_type,
                    difficulty=difficulty,
                    count=patterns_per_type,
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
                        'topic': 'patterns',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='patterns',
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
                        'type': pattern_type,
                        'difficulty': difficulty,
                        'question': q['question_text'][:50] + '...'
                    })
        
        db.session.commit()
        
        # Get updated counts
        counts = {}
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            count = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = 'patterns' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/pattern-generator-status', methods=['GET'])
    @admin_required_api
    def pattern_generator_status():
        """Check if pattern generator is available"""
        from flask import jsonify
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'pattern_types': ['dot', 'linear', 'staircase', 'shape', 'tile'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


if __name__ == '__main__':
    # Test the generators
    print("Testing Pattern Question Generator...")
    print("="*50)
    
    if not MATPLOTLIB_AVAILABLE:
        print("ERROR: matplotlib not installed!")
        print("Run: pip install matplotlib")
    else:
        # Test each pattern type
        for pattern_type in ['dot', 'linear', 'staircase', 'shape', 'tile']:
            print(f"\n{pattern_type.upper()} PATTERNS:")
            questions = generate_pattern_questions(pattern_type, 'intermediate', count=1, output_dir='/tmp/test_patterns')
            
            if isinstance(questions, dict) and 'error' in questions:
                print(f"  Error: {questions['error']}")
            else:
                print(f"  Generated {len(questions)} questions")
                for q in questions[:2]:
                    print(f"  - {q['question_text'][:60]}...")
                    print(f"    Options: {q['options']}")
