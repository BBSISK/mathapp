#!/usr/bin/env python3
"""
Speed, Distance, Time Question Generator for AgentMath.app

Generates graphical SDT questions with:
- Journey map visualizations (Irish locations)
- Distance-Time graphs for interpretation
- Speedometer/dashboard displays
- Race track scenarios

Integrated with Flask admin dashboard via register_sdt_generator_routes()
"""

import os
import random
import math
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None

TOPIC_NAME = 'speed_distance_time'

IRISH_ROUTES = [
    ('Dublin', 'Cork', 256), ('Dublin', 'Galway', 208), ('Dublin', 'Limerick', 195),
    ('Dublin', 'Belfast', 167), ('Dublin', 'Waterford', 154), ('Dublin', 'Wexford', 145),
    ('Cork', 'Limerick', 105), ('Galway', 'Limerick', 100), ('Cork', 'Waterford', 120),
]

TRANSPORT = {
    'car': {'icon': '🚗', 'name': 'car'},
    'bus': {'icon': '🚌', 'name': 'bus'},
    'train': {'icon': '🚂', 'name': 'train'},
    'cyclist': {'icon': '🚴', 'name': 'cyclist'},
}


def generate_wrong_answers(correct, difficulty, min_val=1):
    wrong = set()
    for offset in [1, 2, 5, 10, -1, -2, 15, 20, -5, -10, 3, 7]:
        if len(wrong) >= 3:
            break
        candidate = correct + offset
        candidate = int(round(candidate)) if isinstance(correct, int) else round(candidate, 1)
        if candidate > min_val and candidate != correct:
            wrong.add(candidate)
    return list(wrong)[:3]


def ensure_four_options(correct, wrong_list, suffix=''):
    options = [correct]
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options:
            options.append(w)
    while len(options) < 4:
        options.append(correct + len(options) * 5)
    options = [f"{o}{suffix}" for o in options]
    random.shuffle(options)
    correct_str = f"{correct}{suffix}"
    return options, options.index(correct_str)


def format_time(hours):
    if hours == int(hours):
        return f"{int(hours)} hour{'s' if hours != 1 else ''}"
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{m} minutes" if h == 0 else f"{h}h {m}m"


# ============================================================================
# IMAGE GENERATORS
# ============================================================================

def create_journey_map(start, end, distance, transport_icon, highlight_value=None, 
                       highlight_type=None, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    ax.add_patch(Rectangle((0, 0), 10, 4, facecolor='#e8f4ea', edgecolor='none'))
    ax.add_patch(Circle((1.5, 2), 0.4, facecolor='#3b82f6', edgecolor='white', linewidth=3))
    ax.text(1.5, 2, '📍', ha='center', va='center', fontsize=20)
    ax.text(1.5, 1.2, start, ha='center', va='center', fontsize=12, fontweight='bold', color='#1e3a5f')
    
    ax.add_patch(Circle((8.5, 2), 0.4, facecolor='#10b981', edgecolor='white', linewidth=3))
    ax.text(8.5, 2, '🏁', ha='center', va='center', fontsize=20)
    ax.text(8.5, 1.2, end, ha='center', va='center', fontsize=12, fontweight='bold', color='#1e3a5f')
    
    ax.plot([2, 8], [2, 2], color='#64748b', linewidth=15, solid_capstyle='round', zorder=1)
    ax.plot([2, 8], [2, 2], color='#94a3b8', linewidth=10, solid_capstyle='round', zorder=2)
    ax.plot([2.2, 7.8], [2, 2], color='white', linewidth=2, linestyle='--', zorder=3)
    ax.text(5, 2, transport_icon, ha='center', va='center', fontsize=35, zorder=4)
    
    ax.add_patch(FancyBboxPatch((3.5, 2.8), 3, 0.8, boxstyle="round,pad=0.1", 
                                 facecolor='white', edgecolor='#1e3a5f', linewidth=2))
    ax.text(5, 3.2, f'Distance: {distance} km', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#1e3a5f')
    
    if highlight_type and highlight_value:
        ax.add_patch(FancyBboxPatch((3, 0.3), 4, 0.7, boxstyle="round,pad=0.1",
                                     facecolor='#fef3c7', edgecolor='#f59e0b', linewidth=2))
        ax.text(5, 0.65, f'{highlight_type}: {highlight_value}', ha='center', va='center',
                fontsize=11, fontweight='bold', color='#92400e')
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath
    plt.close()
    return None


def create_distance_time_graph(segments, title='Journey Graph', output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    
    times = [0]
    distances = [0]
    current_time = 0
    current_distance = 0
    
    for duration, dist_change, label in segments:
        current_time += duration
        current_distance += dist_change
        times.append(current_time)
        distances.append(current_distance)
    
    ax.plot(times, distances, 'b-', linewidth=3, marker='o', markersize=8, 
            color='#3b82f6', markerfacecolor='#3b82f6', markeredgecolor='white', markeredgewidth=2)
    ax.fill_between(times, distances, alpha=0.2, color='#3b82f6')
    
    ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1e3a5f')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(0, max(times) * 1.1)
    ax.set_ylim(0, max(distances) * 1.1)
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath
    plt.close()
    return None


def create_speedometer(speed, max_speed=160, label='Current Speed', output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.add_patch(FancyBboxPatch((-1.4, -0.4), 2.8, 1.8, boxstyle="round,pad=0.05",
                                 facecolor='#1e293b', edgecolor='#334155', linewidth=3))
    
    theta = np.linspace(np.pi, 0, 100)
    x_outer = 1.0 * np.cos(theta)
    y_outer = 1.0 * np.sin(theta) + 0.3
    ax.fill_between(x_outer, y_outer * 0, y_outer, color='#374151', alpha=0.8)
    
    for start, end, color in [(0, 0.4, '#22c55e'), (0.4, 0.7, '#f59e0b'), (0.7, 1.0, '#ef4444')]:
        theta_zone = np.linspace(np.pi - start * np.pi, np.pi - end * np.pi, 50)
        ax.plot(0.85 * np.cos(theta_zone), 0.85 * np.sin(theta_zone) + 0.3, 
                color=color, linewidth=8, solid_capstyle='round')
    
    for i in range(0, max_speed + 1, 20):
        angle = np.pi - (i / max_speed) * np.pi
        ax.plot([0.7 * np.cos(angle), 0.9 * np.cos(angle)], 
                [0.7 * np.sin(angle) + 0.3, 0.9 * np.sin(angle) + 0.3], color='white', linewidth=2)
        ax.text(0.6 * np.cos(angle), 0.6 * np.sin(angle) + 0.3, str(i), 
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    speed_ratio = min(speed / max_speed, 1.0)
    needle_angle = np.pi - speed_ratio * np.pi
    ax.annotate('', xy=(0.75 * np.cos(needle_angle), 0.75 * np.sin(needle_angle) + 0.3), 
                xytext=(0, 0.3), arrowprops=dict(arrowstyle='->', color='#ef4444', lw=3))
    ax.add_patch(Circle((0, 0.3), 0.08, facecolor='#ef4444', edgecolor='white', linewidth=2))
    
    ax.add_patch(FancyBboxPatch((-0.4, -0.25), 0.8, 0.35, boxstyle="round,pad=0.02",
                                 facecolor='#111827', edgecolor='#4ade80', linewidth=2))
    ax.text(0, -0.08, f'{speed}', ha='center', va='center', fontsize=24, 
            fontweight='bold', color='#4ade80', fontfamily='monospace')
    ax.text(0, 0.4, 'km/h', ha='center', va='center', fontsize=10, color='#9ca3af')
    ax.text(0, 1.25, label, ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='#0f172a')
        plt.close()
        return filepath
    plt.close()
    return None


def create_race_track(positions, labels, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    ax.add_patch(Rectangle((0, 0), 10, 5, facecolor='#f0fdf4', edgecolor='none'))
    
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    icons = ['🚗', '🚌', '🚴', '🏃']
    
    for i, (pos, label) in enumerate(zip(positions, labels)):
        y = 4 - i * 1.0
        ax.add_patch(Rectangle((0.5, y - 0.3), 9, 0.6, facecolor=colors[i % 4], alpha=0.2))
        ax.plot([0.5, 9.5], [y, y], color=colors[i % 4], linewidth=3, alpha=0.5)
        ax.plot([0.5, 0.5], [y - 0.3, y + 0.3], color='black', linewidth=2)
        ax.plot([9.5, 9.5], [y - 0.3, y + 0.3], color='black', linewidth=4)
        ax.text(0.5 + pos * 9, y, icons[i % 4], ha='center', va='center', fontsize=25)
        ax.text(0.2, y, label, ha='right', va='center', fontsize=10, fontweight='bold')
    
    ax.text(0.5, 4.5, 'START', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(9.5, 4.5, 'FINISH', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(9.5, 0.3, '🏁', ha='center', va='center', fontsize=30)
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath
    plt.close()
    return None


# ============================================================================
# QUESTION GENERATORS
# ============================================================================

def generate_find_speed_question(difficulty='beginner'):
    if difficulty == 'beginner':
        distance = random.choice([20, 30, 40, 50, 60, 80, 100])
        time = random.choice([1, 2, 4, 5])
        transport = random.choice(['car', 'bus', 'cyclist'])
        start, end = 'Town A', 'Town B'
    elif difficulty == 'intermediate':
        route = random.choice(IRISH_ROUTES)
        start, end, distance = route
        time = random.choice([2, 2.5, 3, 4])
        transport = random.choice(['car', 'bus', 'train'])
    else:
        route = random.choice(IRISH_ROUTES)
        start, end, distance = route
        time = round(random.uniform(1.5, 4), 1)
        transport = random.choice(['car', 'train'])
    
    speed = distance / time
    speed = int(speed) if speed == int(speed) else round(speed, 1)
    t_info = TRANSPORT[transport]
    
    question = f"A {t_info['name']} {t_info['icon']} travels from {start} to {end} ({distance} km) in {format_time(time)}. What is the average speed?"
    
    wrong = generate_wrong_answers(speed, difficulty, min_val=5)
    options, correct_idx = ensure_four_options(speed, wrong, suffix=' km/h')
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f"Speed = Distance ÷ Time = {distance} ÷ {time} = {speed} km/h",
        'image_data': {'type': 'journey_map', 'start': start, 'end': end, 'distance': distance,
                      'transport_icon': t_info['icon'], 'highlight_type': 'Time', 'highlight_value': format_time(time)}
    }


def generate_find_distance_question(difficulty='beginner'):
    if difficulty == 'beginner':
        speed = random.choice([30, 40, 50, 60])
        time = random.choice([1, 2, 3])
    elif difficulty == 'intermediate':
        speed = random.choice([60, 80, 100, 120])
        time = random.choice([1.5, 2, 2.5, 3])
    else:
        speed = random.choice([80, 100, 110, 120])
        time = round(random.uniform(1.5, 4), 1)
    
    transport = random.choice(['car', 'train'])
    distance = speed * time
    distance = int(distance) if distance == int(distance) else round(distance, 1)
    t_info = TRANSPORT[transport]
    
    question = f"A {t_info['name']} {t_info['icon']} travels at {speed} km/h for {format_time(time)}. How far does it travel?"
    
    wrong = generate_wrong_answers(distance, difficulty, min_val=10)
    options, correct_idx = ensure_four_options(distance, wrong, suffix=' km')
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f"Distance = Speed × Time = {speed} × {time} = {distance} km",
        'image_data': {'type': 'speedometer', 'speed': speed, 'label': f'Time: {format_time(time)}'}
    }


def generate_find_time_question(difficulty='beginner'):
    if difficulty == 'beginner':
        distance = random.choice([60, 80, 100, 120])
        speed = random.choice([30, 40, 60])
        start, end = 'Town A', 'Town B'
    elif difficulty == 'intermediate':
        route = random.choice(IRISH_ROUTES)
        start, end, distance = route
        speed = random.choice([60, 80, 100])
    else:
        route = random.choice(IRISH_ROUTES)
        start, end, distance = route
        speed = random.choice([80, 100, 120])
    
    transport = random.choice(['car', 'train'])
    time = distance / speed
    time = int(time) if time == int(time) else round(time, 2)
    time_str = f"{int(time)} hours" if time == int(time) else f"{int((time % 1) * 60)} minutes" if int(time) == 0 else f"{int(time)}h {int((time % 1) * 60)}m"
    
    t_info = TRANSPORT[transport]
    question = f"A {t_info['name']} {t_info['icon']} travels from {start} to {end} ({distance} km) at {speed} km/h. How long is the journey?"
    
    wrong_times = [f"{int(time)+i} hours" if i > 0 else f"{int(abs(time-0.5)*60)} minutes" for i in [1, 2, -1]]
    options = [time_str] + wrong_times[:3]
    random.shuffle(options)
    correct_idx = options.index(time_str)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f"Time = Distance ÷ Speed = {distance} ÷ {speed} = {time} hours",
        'image_data': {'type': 'journey_map', 'start': start, 'end': end, 'distance': distance,
                      'transport_icon': t_info['icon'], 'highlight_type': 'Speed', 'highlight_value': f'{speed} km/h'}
    }


def generate_graph_reading_question(difficulty='beginner'):
    speed = random.choice([30, 40, 50, 60])
    total_time = random.choice([2, 3, 4])
    total_distance = speed * total_time
    segments = [(total_time, total_distance, '')]
    
    question = f"Look at the distance-time graph. What was the average speed of the journey?"
    correct = speed
    
    wrong = generate_wrong_answers(correct, difficulty)
    options, correct_idx = ensure_four_options(correct, wrong, suffix=' km/h')
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': "Speed = Distance ÷ Time from graph",
        'image_data': {'type': 'distance_time_graph', 'segments': segments, 'title': 'Journey Progress'}
    }


def generate_comparison_question(difficulty='beginner'):
    distance = random.choice([60, 100, 120])
    speed1 = random.choice([60, 80])
    speed2 = random.choice([30, 40])
    
    time_diff_mins = round(abs(distance/speed2 - distance/speed1) * 60)
    
    question = f"A car 🚗 travels at {speed1} km/h and a bus 🚌 travels at {speed2} km/h. Both travel {distance} km. How much sooner does the car arrive?"
    
    wrong = generate_wrong_answers(time_diff_mins, difficulty, min_val=5)
    options, correct_idx = ensure_four_options(time_diff_mins, wrong, suffix=' minutes')
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f"Time difference = {time_diff_mins} minutes",
        'image_data': {'type': 'race_track', 'positions': [0.7, 0.4], 'labels': [f'🚗 {speed1}km/h', f'🚌 {speed2}km/h']}
    }


def generate_unit_conversion_question(difficulty='beginner'):
    if difficulty == 'beginner':
        km = random.choice([1, 2, 3, 5])
        m = km * 1000
        question = f"A runner completes a {km} km race. How many metres is this?"
        correct, suffix = m, ' m'
    else:
        kmh = random.choice([36, 72, 90])
        ms = int(kmh / 3.6)
        question = f"A car travels at {kmh} km/h. What is this in m/s?"
        correct, suffix = ms, ' m/s'
    
    wrong = generate_wrong_answers(correct, difficulty)
    options, correct_idx = ensure_four_options(correct, wrong, suffix=suffix)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': "1 km = 1000 m, km/h ÷ 3.6 = m/s",
        'image_data': None
    }


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_sdt_questions(question_types=None, difficulties=None, count=3, output_dir=None):
    if question_types is None:
        question_types = ['find_speed', 'find_distance', 'find_time', 'graph_reading', 'comparison', 'unit_conversion']
    if difficulties is None:
        difficulties = ['beginner', 'intermediate', 'advanced']
    
    generators = {
        'find_speed': generate_find_speed_question,
        'find_distance': generate_find_distance_question,
        'find_time': generate_find_time_question,
        'graph_reading': generate_graph_reading_question,
        'comparison': generate_comparison_question,
        'unit_conversion': generate_unit_conversion_question,
    }
    
    all_questions = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for q_type in question_types:
        if q_type not in generators:
            continue
        for difficulty in difficulties:
            for i in range(count):
                try:
                    q = generators[q_type](difficulty)
                    
                    if q.get('image_data') and output_dir:
                        img = q['image_data']
                        filename = f"sdt_{q_type}_{difficulty}_{timestamp}_{i}.png"
                        
                        if img['type'] == 'journey_map':
                            create_journey_map(img['start'], img['end'], img['distance'],
                                             img['transport_icon'], img.get('highlight_value'),
                                             img.get('highlight_type'), output_dir, filename)
                        elif img['type'] == 'speedometer':
                            create_speedometer(img['speed'], label=img.get('label', ''),
                                             output_dir=output_dir, filename=filename)
                        elif img['type'] == 'distance_time_graph':
                            create_distance_time_graph(img['segments'], img.get('title', 'Journey'),
                                                      output_dir, filename)
                        elif img['type'] == 'race_track':
                            create_race_track(img['positions'], img['labels'], output_dir, filename)
                        
                        q['image_url'] = f"/static/question_images/{filename}"
                    
                    all_questions.append(q)
                except Exception as e:
                    print(f"Error: {e}")
    
    return all_questions


# ============================================================================
# FLASK ROUTE REGISTRATION
# ============================================================================

def register_sdt_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for SDT question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-sdt-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_sdt_questions():
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({'error': 'matplotlib not installed'}), 400
        
        data = request.json or {}
        question_types = data.get('question_types', ['find_speed', 'find_distance', 'find_time', 'graph_reading', 'comparison', 'unit_conversion'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        questions_per_type = data.get('questions_per_type', 3)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        questions = generate_sdt_questions(question_types, difficulties, questions_per_type, output_dir)
        
        saved_count = 0
        skipped_count = 0
        
        for q in questions:
            if len(q.get('options', [])) != 4:
                skipped_count += 1
                continue
            
            existing = db.session.execute(text(
                "SELECT id FROM questions WHERE topic = :topic AND question_text = :qt"
            ), {'topic': TOPIC_NAME, 'qt': q['question_text']}).fetchone()
            
            if existing:
                skipped_count += 1
                continue
            
            new_q = Question(
                topic=TOPIC_NAME, difficulty=q['difficulty'], question_text=q['question_text'],
                option_a=q['options'][0], option_b=q['options'][1],
                option_c=q['options'][2], option_d=q['options'][3],
                correct_answer=q['correct'], explanation=q.get('explanation', ''),
                image_url=q.get('image_url')
            )
            db.session.add(new_q)
            saved_count += 1
        
        db.session.commit()
        
        counts = {}
        for d in ['beginner', 'intermediate', 'advanced']:
            counts[d] = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = :t AND difficulty = :d"
            ), {'t': TOPIC_NAME, 'd': d}).fetchone()[0]
        
        return jsonify({
            'success': True, 'saved': saved_count, 'skipped': skipped_count,
            'counts': counts, 'total': sum(counts.values()),
            'message': f'Generated {saved_count} questions. {skipped_count} skipped.'
        })
    
    @app.route('/api/admin/sdt-generator-status', methods=['GET'])
    @admin_required_api
    def sdt_generator_status():
        from flask import jsonify
        
        counts = {}
        for d in ['beginner', 'intermediate', 'advanced']:
            counts[d] = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = :t AND difficulty = :d"
            ), {'t': TOPIC_NAME, 'd': d}).fetchone()[0]
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'question_types': ['find_speed', 'find_distance', 'find_time', 'graph_reading', 'comparison', 'unit_conversion'],
            'counts': counts, 'total': sum(counts.values())
        })


if __name__ == '__main__':
    print("🚗 SDT Generator Test")
    questions = generate_sdt_questions(count=1, output_dir='/tmp/sdt_test')
    for q in questions[:3]:
        print(f"\n[{q['difficulty']}] {q['question_text'][:60]}...")
