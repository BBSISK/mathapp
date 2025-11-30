#!/usr/bin/env python3
"""
Currency Question Generator for AgentMath.app

Generates graphical currency questions with:
- Euro/cent conversions
- Coin counting with images
- Making change calculations
- Shopping totals
- Exchange rates
- Best value / discounts

Integrated with Flask admin dashboard via register_currency_generator_routes()
"""

import os
import random
import math
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None

TOPIC_NAME = 'currency'

EURO_COINS = {
    '1c': {'value': 0.01, 'color': '#cd7f32', 'size': 0.16},
    '2c': {'value': 0.02, 'color': '#cd7f32', 'size': 0.19},
    '5c': {'value': 0.05, 'color': '#cd7f32', 'size': 0.21},
    '10c': {'value': 0.10, 'color': '#ffd700', 'size': 0.20},
    '20c': {'value': 0.20, 'color': '#ffd700', 'size': 0.22},
    '50c': {'value': 0.50, 'color': '#ffd700', 'size': 0.24},
    '€1': {'value': 1.00, 'color': '#c0c0c0', 'size': 0.23, 'ring': '#ffd700'},
    '€2': {'value': 2.00, 'color': '#ffd700', 'size': 0.26, 'ring': '#c0c0c0'},
}

EXCHANGE_RATES = {
    'USD': {'rate': 1.08, 'symbol': '$', 'name': 'US Dollar', 'flag': '🇺🇸'},
    'GBP': {'rate': 0.86, 'symbol': '£', 'name': 'British Pound', 'flag': '🇬🇧'},
    'JPY': {'rate': 162.0, 'symbol': '¥', 'name': 'Japanese Yen', 'flag': '🇯🇵'},
}

SHOP_ITEMS = {
    'beginner': [
        {'name': 'Apple', 'price': 0.50, 'icon': '🍎'},
        {'name': 'Banana', 'price': 0.30, 'icon': '🍌'},
        {'name': 'Milk', 'price': 1.50, 'icon': '🥛'},
        {'name': 'Bread', 'price': 1.80, 'icon': '🍞'},
        {'name': 'Chocolate', 'price': 1.00, 'icon': '🍫'},
    ],
    'intermediate': [
        {'name': 'Sandwich', 'price': 4.50, 'icon': '🥪'},
        {'name': 'Coffee', 'price': 3.50, 'icon': '☕'},
        {'name': 'Pizza slice', 'price': 3.00, 'icon': '🍕'},
        {'name': 'Magazine', 'price': 4.95, 'icon': '📖'},
    ],
    'advanced': [
        {'name': 'Cinema ticket', 'price': 12.50, 'icon': '🎬'},
        {'name': 'Book', 'price': 14.99, 'icon': '📚'},
        {'name': 'T-shirt', 'price': 19.99, 'icon': '👕'},
        {'name': 'Game', 'price': 29.99, 'icon': '🎮'},
    ]
}


def format_euro(amount):
    return f"€{amount:.2f}" if amount != int(amount) else f"€{int(amount)}"


def generate_wrong_answers(correct, difficulty, min_val=0, is_cents=False):
    wrong = set()
    offsets = [0.5, 1, -0.5, -1, 2, -2, 0.2, -0.2] if not is_cents else [10, -10, 5, -5, 20, -20, 1, -1]
    
    for offset in offsets:
        if len(wrong) >= 3:
            break
        candidate = round(correct + offset, 2) if not is_cents else int(correct + offset)
        if candidate > min_val and candidate != correct:
            wrong.add(candidate)
    
    return list(wrong)[:3]


def ensure_four_options(correct, wrong_list, formatter=format_euro):
    options = [correct]
    for w in wrong_list:
        if len(options) >= 4:
            break
        if w not in options and w > 0:
            options.append(w)
    
    while len(options) < 4:
        options.append(round(correct + len(options) * 0.5, 2))
    
    formatted = [formatter(o) for o in options]
    random.shuffle(formatted)
    return formatted, formatted.index(formatter(correct))


# ============================================================================
# IMAGE GENERATORS
# ============================================================================

def create_coins_image(coins_list, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    ax.add_patch(FancyBboxPatch((0.1, 0.1), 9.8, 2.8, boxstyle="round,pad=0.05",
                                 facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=2))
    
    x_pos = 1
    for coin_name in coins_list:
        if coin_name in EURO_COINS:
            coin = EURO_COINS[coin_name]
            if 'ring' in coin:
                ax.add_patch(Circle((x_pos, 1.5), coin['size'] + 0.05, 
                                   facecolor=coin['ring'], edgecolor='#333', linewidth=1))
            ax.add_patch(Circle((x_pos, 1.5), coin['size'], 
                               facecolor=coin['color'], edgecolor='#333', linewidth=2))
            ax.text(x_pos, 1.5, coin_name, ha='center', va='center',
                   fontsize=9, fontweight='bold', color='#333')
            x_pos += coin['size'] * 2 + 0.4
    
    ax.text(9, 2.5, 'Total = ?', ha='right', va='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef3c7', edgecolor='#f59e0b'))
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath
    plt.close()
    return None


def create_shopping_basket(items, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    ax.add_patch(FancyBboxPatch((0.1, 0.1), 9.8, 4.8, boxstyle="round,pad=0.05",
                                 facecolor='#f0fdf4', edgecolor='#22c55e', linewidth=2))
    ax.text(5, 4.5, '🛒 Shopping Basket', ha='center', va='center',
           fontsize=14, fontweight='bold', color='#1e3a5f')
    
    for i, item in enumerate(items):
        col = i % 4
        row = i // 4
        x = 1.5 + col * 2.2
        y = 3.5 - row * 1.5
        
        ax.add_patch(FancyBboxPatch((x - 0.8, y - 0.5), 1.6, 1.2, boxstyle="round,pad=0.05",
                                    facecolor='white', edgecolor='#cbd5e1', linewidth=1))
        ax.text(x, y + 0.2, item['icon'], ha='center', va='center', fontsize=20)
        ax.text(x, y - 0.2, format_euro(item['price']), ha='center', va='center',
               fontsize=10, fontweight='bold', color='#1e3a5f')
    
    total = sum(item['price'] for item in items)
    ax.add_patch(FancyBboxPatch((6.5, 0.3), 3, 0.8, boxstyle="round,pad=0.05",
                                facecolor='#fef3c7', edgecolor='#f59e0b', linewidth=2))
    ax.text(8, 0.7, f'Total: ?', ha='center', va='center',
           fontsize=12, fontweight='bold', color='#92400e')
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath
    plt.close()
    return None


def create_exchange_display(to_currency, rate, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 3))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    ax.add_patch(FancyBboxPatch((0.1, 0.1), 5.8, 2.8, boxstyle="round,pad=0.05",
                                 facecolor='#1e3a5f', edgecolor='#3b82f6', linewidth=3))
    
    ax.text(3, 2.6, '💱 Exchange Rate', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    ax.text(1.5, 1.5, '🇪🇺', ha='center', va='center', fontsize=30)
    ax.text(1.5, 0.9, '€1 EUR', ha='center', va='center', fontsize=11, color='white', fontweight='bold')
    
    ax.text(3, 1.5, '=', ha='center', va='center', fontsize=20, color='#ffd700', fontweight='bold')
    
    info = EXCHANGE_RATES[to_currency]
    ax.text(4.5, 1.5, info['flag'], ha='center', va='center', fontsize=30)
    ax.text(4.5, 0.9, f"{info['symbol']}{rate:.2f}", ha='center', va='center',
           fontsize=11, color='white', fontweight='bold')
    
    plt.tight_layout()
    
    if filename and output_dir:
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='#0f172a')
        plt.close()
        return filepath
    plt.close()
    return None


def create_change_calc(paid, cost, output_dir=None, filename=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 3))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    ax.add_patch(FancyBboxPatch((0.1, 0.1), 5.8, 2.8, boxstyle="round,pad=0.05",
                                 facecolor='#fef3c7', edgecolor='#f59e0b', linewidth=2))
    
    ax.text(3, 2.6, '🧾 Change Calculator', ha='center', va='center', fontsize=12, fontweight='bold', color='#92400e')
    
    ax.add_patch(FancyBboxPatch((0.3, 1.3), 2.2, 1, boxstyle="round,pad=0.05",
                                facecolor='#dcfce7', edgecolor='#22c55e', linewidth=2))
    ax.text(1.4, 2, 'You Pay:', ha='center', va='center', fontsize=10, color='#166534')
    ax.text(1.4, 1.6, format_euro(paid), ha='center', va='center', fontsize=16, fontweight='bold', color='#166534')
    
    ax.add_patch(FancyBboxPatch((2.7, 1.3), 2.2, 1, boxstyle="round,pad=0.05",
                                facecolor='#fee2e2', edgecolor='#ef4444', linewidth=2))
    ax.text(3.8, 2, 'Cost:', ha='center', va='center', fontsize=10, color='#dc2626')
    ax.text(3.8, 1.6, format_euro(cost), ha='center', va='center', fontsize=16, fontweight='bold', color='#dc2626')
    
    ax.text(3, 0.7, f'Change = ?', ha='center', va='center', fontsize=11, fontweight='bold', color='#1e3a5f')
    
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

def generate_cents_euro_question(difficulty='beginner'):
    if difficulty == 'beginner':
        cents = random.choice([100, 200, 300, 500])
        question = f"How many euros is {cents} cent?"
        correct = cents / 100
    elif difficulty == 'intermediate':
        cents = random.choice([150, 225, 350, 475])
        question = f"Convert {cents} cent to euros."
        correct = cents / 100
    else:
        cents = random.choice([1275, 1850, 2350])
        question = f"Express {cents} cent in euros."
        correct = cents / 100
    
    wrong = generate_wrong_answers(correct, difficulty)
    options, correct_idx = ensure_four_options(correct, wrong)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': '100 cent = €1',
        'image_data': None
    }


def generate_count_coins_question(difficulty='beginner'):
    if difficulty == 'beginner':
        coin_opts = ['€1', '€2', '50c', '20c']
        num_coins = 3
    elif difficulty == 'intermediate':
        coin_opts = ['€2', '€1', '50c', '20c', '10c']
        num_coins = 4
    else:
        coin_opts = ['€2', '€1', '50c', '20c', '10c', '5c']
        num_coins = 5
    
    coins = [random.choice(coin_opts) for _ in range(num_coins)]
    total = sum(EURO_COINS[c]['value'] for c in coins)
    total = round(total, 2)
    
    question = "What is the total value of these coins?"
    
    wrong = generate_wrong_answers(total, difficulty)
    options, correct_idx = ensure_four_options(total, wrong)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': 'Add up all coin values',
        'image_data': {'type': 'coins', 'coins': coins}
    }


def generate_making_change_question(difficulty='beginner'):
    if difficulty == 'beginner':
        cost = random.choice([1.50, 2.00, 2.50, 3.00])
        paid = 5.00
    elif difficulty == 'intermediate':
        cost = round(random.uniform(4.00, 8.00) * 2) / 2
        paid = 10.00
    else:
        cost = round(random.uniform(12.00, 18.00), 2)
        paid = 20.00
    
    change = round(paid - cost, 2)
    
    question = f"You buy something for {format_euro(cost)} and pay with {format_euro(paid)}. How much change do you get?"
    
    wrong = generate_wrong_answers(change, difficulty, min_val=0)
    options, correct_idx = ensure_four_options(change, wrong)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f'Change = {format_euro(paid)} - {format_euro(cost)}',
        'image_data': {'type': 'change_calc', 'paid': paid, 'cost': cost}
    }


def generate_shopping_total_question(difficulty='beginner'):
    items_pool = SHOP_ITEMS[difficulty]
    num_items = 2 if difficulty == 'beginner' else 3 if difficulty == 'intermediate' else 4
    
    selected = random.sample(items_pool, min(num_items, len(items_pool)))
    total = round(sum(item['price'] for item in selected), 2)
    
    items_text = ', '.join([f"{item['icon']} {item['name']} ({format_euro(item['price'])})" for item in selected])
    question = f"What is the total cost: {items_text}?"
    
    wrong = generate_wrong_answers(total, difficulty)
    options, correct_idx = ensure_four_options(total, wrong)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': 'Add all prices together',
        'image_data': {'type': 'shopping_basket', 'items': selected}
    }


def generate_exchange_rate_question(difficulty='beginner'):
    currency = random.choice(['USD', 'GBP'])
    rate = EXCHANGE_RATES[currency]['rate']
    euros = random.choice([10, 20, 50]) if difficulty == 'beginner' else random.choice([25, 75, 100])
    
    converted = round(euros * rate, 2)
    symbol = EXCHANGE_RATES[currency]['symbol']
    
    question = f"If €1 = {symbol}{rate:.2f}, how much is €{euros} in {EXCHANGE_RATES[currency]['name']}s?"
    
    wrong = generate_wrong_answers(converted, difficulty)
    formatter = lambda x: f"{symbol}{x:.2f}"
    options, correct_idx = ensure_four_options(converted, wrong, formatter=formatter)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f'€{euros} × {rate} = {symbol}{converted:.2f}',
        'image_data': {'type': 'exchange', 'currency': currency, 'rate': rate}
    }


def generate_discount_question(difficulty='beginner'):
    item = random.choice(SHOP_ITEMS['advanced'])
    original = item['price']
    discount_pct = random.choice([10, 20, 25, 50]) if difficulty == 'beginner' else random.choice([15, 25, 30])
    
    sale = round(original * (100 - discount_pct) / 100, 2)
    
    question = f"A {item['name']} {item['icon']} costs {format_euro(original)}. With {discount_pct}% off, what is the sale price?"
    
    wrong = generate_wrong_answers(sale, difficulty)
    options, correct_idx = ensure_four_options(sale, wrong)
    
    return {
        'question_text': question, 'options': options, 'correct': correct_idx,
        'difficulty': difficulty, 'explanation': f'Sale = {format_euro(original)} × {100-discount_pct}%',
        'image_data': None
    }


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_currency_questions(question_types=None, difficulties=None, count=3, output_dir=None):
    if question_types is None:
        question_types = ['cents_euro', 'count_coins', 'making_change', 'shopping_total', 'exchange_rate', 'discount']
    if difficulties is None:
        difficulties = ['beginner', 'intermediate', 'advanced']
    
    generators = {
        'cents_euro': generate_cents_euro_question,
        'count_coins': generate_count_coins_question,
        'making_change': generate_making_change_question,
        'shopping_total': generate_shopping_total_question,
        'exchange_rate': generate_exchange_rate_question,
        'discount': generate_discount_question,
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
                        filename = f"currency_{q_type}_{difficulty}_{timestamp}_{i}.png"
                        
                        if img['type'] == 'coins':
                            create_coins_image(img['coins'], output_dir, filename)
                        elif img['type'] == 'shopping_basket':
                            create_shopping_basket(img['items'], output_dir, filename)
                        elif img['type'] == 'change_calc':
                            create_change_calc(img['paid'], img['cost'], output_dir, filename)
                        elif img['type'] == 'exchange':
                            create_exchange_display(img['currency'], img['rate'], output_dir, filename)
                        
                        q['image_url'] = f"/static/question_images/{filename}"
                    
                    all_questions.append(q)
                except Exception as e:
                    print(f"Error: {e}")
    
    return all_questions


# ============================================================================
# FLASK ROUTE REGISTRATION
# ============================================================================

def register_currency_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for Currency question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-currency-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_currency_questions():
        from flask import request, jsonify
        
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({'error': 'matplotlib not installed'}), 400
        
        data = request.json or {}
        question_types = data.get('question_types', ['cents_euro', 'count_coins', 'making_change', 'shopping_total', 'exchange_rate', 'discount'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        questions_per_type = data.get('questions_per_type', 3)
        
        output_dir = os.path.join(app.static_folder, 'question_images')
        os.makedirs(output_dir, exist_ok=True)
        
        questions = generate_currency_questions(question_types, difficulties, questions_per_type, output_dir)
        
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
    
    @app.route('/api/admin/currency-generator-status', methods=['GET'])
    @admin_required_api
    def currency_generator_status():
        from flask import jsonify
        
        counts = {}
        for d in ['beginner', 'intermediate', 'advanced']:
            counts[d] = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = :t AND difficulty = :d"
            ), {'t': TOPIC_NAME, 'd': d}).fetchone()[0]
        
        return jsonify({
            'matplotlib_available': MATPLOTLIB_AVAILABLE,
            'question_types': ['cents_euro', 'count_coins', 'making_change', 'shopping_total', 'exchange_rate', 'discount'],
            'counts': counts, 'total': sum(counts.values())
        })


if __name__ == '__main__':
    print("💶 Currency Generator Test")
    questions = generate_currency_questions(count=1, output_dir='/tmp/currency_test')
    for q in questions[:3]:
        print(f"\n[{q['difficulty']}] {q['question_text'][:60]}...")
