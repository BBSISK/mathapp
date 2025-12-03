#!/usr/bin/env python3
"""
Percentages Question Generator for AgentMath.app

Generates percentage and financial maths questions aligned with Irish Junior Cycle Mathematics:
- Basic percentage calculations
- Percentage increase/decrease
- Profit/loss and % profit/loss (on cost price)
- VAT calculations (Irish rates)
- Cost price, selling price
- Mark-up (profit as % of cost price)
- Margin (profit as % of selling price)
- Value for money comparisons
- Compound interest (up to 3 years)

Real-world contexts appropriate for 14-year-olds in Ireland.
"""

import os
import random
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# Optional: matplotlib for visual questions (price comparison charts)
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# ============================================================================
# IRISH CONTEXT DATA
# ============================================================================

# Irish VAT rates (as of 2024)
VAT_RATES = {
    'standard': 23,      # Most goods and services
    'reduced': 13.5,     # Fuel, electricity, building services
    'second_reduced': 9, # Newspapers, e-books, hospitality
    'livestock': 4.8,    # Agricultural
    'zero': 0,           # Food, children's clothes, books
}

# Real-world contexts for percentage questions (Irish-focused)
CONTEXTS = {
    'shopping': {
        'items': [
            {'name': 'smartphone', 'base_price': (200, 800), 'vat': 'standard'},
            {'name': 'laptop', 'base_price': (400, 1200), 'vat': 'standard'},
            {'name': 'headphones', 'base_price': (30, 150), 'vat': 'standard'},
            {'name': 'trainers', 'base_price': (50, 180), 'vat': 'standard'},
            {'name': 'jacket', 'base_price': (40, 120), 'vat': 'standard'},
            {'name': 'schoolbag', 'base_price': (25, 80), 'vat': 'standard'},
            {'name': 'watch', 'base_price': (30, 200), 'vat': 'standard'},
            {'name': 'bicycle', 'base_price': (150, 500), 'vat': 'standard'},
        ]
    },
    'food': {
        'items': [
            {'name': 'meal deal', 'base_price': (5, 12), 'vat': 'second_reduced'},
            {'name': 'coffee', 'base_price': (3, 6), 'vat': 'second_reduced'},
            {'name': 'cinema popcorn', 'base_price': (4, 8), 'vat': 'second_reduced'},
            {'name': 'pizza', 'base_price': (10, 20), 'vat': 'second_reduced'},
            {'name': 'sandwich', 'base_price': (4, 8), 'vat': 'second_reduced'},
        ]
    },
    'services': {
        'items': [
            {'name': 'phone repair', 'base_price': (40, 120), 'vat': 'standard'},
            {'name': 'haircut', 'base_price': (15, 40), 'vat': 'standard'},
            {'name': 'car wash', 'base_price': (8, 25), 'vat': 'standard'},
            {'name': 'guitar lesson', 'base_price': (25, 50), 'vat': 'zero'},
            {'name': 'gym membership (monthly)', 'base_price': (30, 60), 'vat': 'standard'},
        ]
    },
    'school': {
        'items': [
            {'name': 'school trip', 'base_price': (30, 100), 'vat': 'zero'},
            {'name': 'art supplies', 'base_price': (15, 50), 'vat': 'standard'},
            {'name': 'calculator', 'base_price': (10, 30), 'vat': 'standard'},
            {'name': 'textbook', 'base_price': (20, 45), 'vat': 'zero'},
            {'name': 'locker rental', 'base_price': (20, 40), 'vat': 'standard'},
        ]
    },
}

# Irish shop names for realism
SHOP_NAMES = [
    "Dunnes", "Penneys", "Smyths", "Easons", "Harvey Norman",
    "Currys", "JD Sports", "Lifestyle Sports", "Elvery's", "SuperValu"
]

# Irish names for story problems
IRISH_NAMES = [
    "Aoife", "Cian", "Saoirse", "Oisín", "Niamh", "Conor", "Ciara", "Seán",
    "Róisín", "Darragh", "Caoimhe", "Fionn", "Éabha", "Tadhg", "Ava", "Liam"
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def round_currency(value):
    """Round to 2 decimal places for currency"""
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def round_percent(value):
    """Round percentage to 1 decimal place"""
    return float(Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def generate_wrong_answers_currency(correct, difficulty, min_val=0):
    """Generate plausible wrong currency answers"""
    wrong = set()
    correct = round_currency(correct)
    
    attempts = 0
    while len(wrong) < 4 and attempts < 30:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.choice([1, 2, 5, 10, -1, -2, -5]) 
        elif difficulty == 'intermediate':
            offset = random.choice([0.5, 1, 2, 5, 10, 15, -0.5, -1, -2, -5])
        else:
            # Common calculation errors
            error_type = random.choice(['percent_error', 'digit_swap', 'random'])
            if error_type == 'percent_error':
                offset = correct * random.choice([0.1, 0.05, -0.1, -0.05, 0.23, -0.23])
            elif error_type == 'digit_swap':
                offset = random.choice([10, -10, 100, -100, 1, -1])
            else:
                offset = random.uniform(-correct * 0.2, correct * 0.2)
        
        candidate = round_currency(correct + offset)
        
        if candidate > min_val and candidate != correct:
            wrong.add(candidate)
    
    # Fallback
    fallback_offsets = [1, 2, 5, 10, 0.50, 1.50, 3, 7]
    for offset in fallback_offsets:
        if len(wrong) >= 3:
            break
        candidate = round_currency(correct + offset)
        if candidate > min_val and candidate != correct:
            wrong.add(candidate)
        candidate = round_currency(correct - offset)
        if candidate > min_val and candidate != correct:
            wrong.add(candidate)
    
    return [round_currency(w) for w in list(wrong)]


def generate_wrong_answers_percent(correct, difficulty):
    """Generate plausible wrong percentage answers"""
    wrong = set()
    correct = round_percent(correct)
    
    attempts = 0
    while len(wrong) < 4 and attempts < 30:
        attempts += 1
        
        if difficulty == 'beginner':
            offset = random.choice([5, 10, -5, -10, 15, -15])
        elif difficulty == 'intermediate':
            offset = random.choice([2, 5, 8, 10, -2, -5, -8, -10])
        else:
            # Common errors
            offset = random.choice([1, 2, 3, 5, 10, -1, -2, -3, -5, -10, correct * 0.1, -correct * 0.1])
        
        candidate = round_percent(correct + offset)
        
        if 0 <= candidate <= 200 and candidate != correct:
            wrong.add(candidate)
    
    # Fallback
    for offset in [5, 10, 2, 15, 1, 3, 7]:
        if len(wrong) >= 3:
            break
        for sign in [1, -1]:
            candidate = round_percent(correct + offset * sign)
            if 0 <= candidate <= 200 and candidate != correct:
                wrong.add(candidate)
    
    return [round_percent(w) for w in list(wrong)]


def format_euro(value):
    """Format value as euro currency"""
    return f"€{value:.2f}"


# ============================================================================
# QUESTION GENERATORS BY TOPIC
# ============================================================================

def generate_basic_percentage_questions(difficulty='beginner'):
    """Generate basic percentage calculation questions"""
    questions = []
    
    if difficulty == 'beginner':
        # Simple percentages of round numbers
        whole = random.choice([100, 200, 50, 80, 120, 150, 200, 250])
        percent = random.choice([10, 20, 25, 50, 75])
        
        correct = round_currency((percent / 100) * whole)
        wrong = generate_wrong_answers_currency(correct, difficulty)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"What is {percent}% of €{whole}?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{percent}% of €{whole} = ({percent}/100) × {whole} = €{correct:.2f}",
            'difficulty': difficulty,
        })
        
        # Reverse: find what percentage
        part = random.choice([10, 20, 25, 40, 50])
        whole = random.choice([100, 200])
        correct_pct = (part / whole) * 100
        
        wrong = generate_wrong_answers_percent(correct_pct, difficulty)
        options = [correct_pct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"€{part} is what percentage of €{whole}?",
            'options': [f"{o}%" for o in options],
            'correct': options.index(correct_pct),
            'explanation': f"(€{part} ÷ €{whole}) × 100 = {correct_pct}%",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Less friendly numbers
        whole = random.randint(50, 300)
        percent = random.choice([15, 17.5, 22, 35, 45, 65])
        
        correct = round_currency((percent / 100) * whole)
        wrong = generate_wrong_answers_currency(correct, difficulty)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Calculate {percent}% of €{whole}.",
            'options': [format_euro(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{percent}% of €{whole} = ({percent}/100) × {whole} = €{correct:.2f}",
            'difficulty': difficulty,
        })
        
        # Find original amount given percentage
        percent = random.choice([20, 25, 40])
        result = random.choice([20, 30, 40, 50, 60])
        original = result / (percent / 100)
        
        wrong = generate_wrong_answers_currency(original, difficulty)
        options = [round_currency(original)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"If {percent}% of an amount is €{result}, what is the original amount?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(original)),
            'explanation': f"If {percent}% = €{result}, then 100% = €{result} ÷ {percent} × 100 = €{original:.2f}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Complex calculations
        whole = random.randint(150, 500)
        percent = round(random.uniform(12.5, 37.5), 1)
        
        correct = round_currency((percent / 100) * whole)
        wrong = generate_wrong_answers_currency(correct, difficulty)
        options = [correct] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Calculate {percent}% of €{whole}.",
            'options': [format_euro(o) for o in options],
            'correct': options.index(correct),
            'explanation': f"{percent}% of €{whole} = ({percent}/100) × {whole} = €{correct:.2f}",
            'difficulty': difficulty,
        })
        
        # Percentage of a percentage
        original = random.randint(200, 500)
        first_pct = random.choice([20, 25, 30])
        second_pct = random.choice([10, 15, 20])
        
        after_first = original * (1 - first_pct/100)
        after_second = after_first * (1 - second_pct/100)
        
        wrong = generate_wrong_answers_currency(after_second, difficulty)
        options = [round_currency(after_second)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"An item costs €{original}. It is reduced by {first_pct}%, then reduced by a further {second_pct}%. What is the final price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(after_second)),
            'explanation': f"After {first_pct}% off: €{original} × 0.{100-first_pct} = €{after_first:.2f}. After further {second_pct}% off: €{after_first:.2f} × 0.{100-second_pct} = €{after_second:.2f}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_increase_decrease_questions(difficulty='beginner'):
    """Generate percentage increase/decrease questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    context = random.choice(list(CONTEXTS.keys()))
    item = random.choice(CONTEXTS[context]['items'])
    item_name = item['name']
    
    if difficulty == 'beginner':
        original = random.choice([50, 80, 100, 120, 150, 200])
        percent = random.choice([10, 20, 25, 50])
        
        # Increase
        increase = original * (percent / 100)
        new_price = original + increase
        
        wrong = generate_wrong_answers_currency(new_price, difficulty)
        options = [round_currency(new_price)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A {item_name} costs €{original}. The price increases by {percent}%. What is the new price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(new_price)),
            'explanation': f"Increase = {percent}% of €{original} = €{increase:.2f}. New price = €{original} + €{increase:.2f} = €{new_price:.2f}",
            'difficulty': difficulty,
        })
        
        # Decrease (sale)
        original = random.choice([40, 60, 80, 100, 120])
        percent = random.choice([10, 20, 25, 50])
        
        decrease = original * (percent / 100)
        sale_price = original - decrease
        
        wrong = generate_wrong_answers_currency(sale_price, difficulty)
        options = [round_currency(sale_price)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} sees a {item_name} with {percent}% off. The original price was €{original}. What is the sale price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(sale_price)),
            'explanation': f"Discount = {percent}% of €{original} = €{decrease:.2f}. Sale price = €{original} - €{decrease:.2f} = €{sale_price:.2f}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Find percentage change
        old_price = random.randint(40, 100)
        new_price = old_price + random.randint(5, 30)
        
        percent_change = ((new_price - old_price) / old_price) * 100
        
        wrong = generate_wrong_answers_percent(percent_change, difficulty)
        options = [round_percent(percent_change)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"The price of a {item_name} went from €{old_price} to €{new_price}. What is the percentage increase?",
            'options': [f"{o}%" for o in options],
            'correct': options.index(round_percent(percent_change)),
            'explanation': f"Increase = €{new_price} - €{old_price} = €{new_price - old_price}. Percentage = (€{new_price - old_price} ÷ €{old_price}) × 100 = {percent_change:.1f}%",
            'difficulty': difficulty,
        })
        
        # Reverse calculation - find original
        sale_price = random.randint(40, 100)
        percent_off = random.choice([20, 25, 30])
        original = sale_price / (1 - percent_off/100)
        
        wrong = generate_wrong_answers_currency(original, difficulty)
        options = [round_currency(original)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"After a {percent_off}% discount, a {item_name} costs €{sale_price}. What was the original price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(original)),
            'explanation': f"If {100-percent_off}% = €{sale_price}, then 100% = €{sale_price} ÷ {100-percent_off} × 100 = €{original:.2f}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Reverse percentage increase
        new_price = random.randint(80, 200)
        percent_increase = random.choice([15, 20, 25])
        original = new_price / (1 + percent_increase/100)
        
        wrong = generate_wrong_answers_currency(original, difficulty)
        options = [round_currency(original)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"After a {percent_increase}% price increase, a {item_name} now costs €{new_price}. What was the original price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(original)),
            'explanation': f"New price = original × 1.{percent_increase}. So original = €{new_price} ÷ 1.{percent_increase} = €{original:.2f}",
            'difficulty': difficulty,
        })
        
        # Compare percentage changes
        price_a = random.randint(50, 100)
        increase_a = random.randint(10, 30)
        price_b = random.randint(80, 150)
        increase_b = random.randint(5, 25)
        
        pct_a = (increase_a / price_a) * 100
        pct_b = (increase_b / price_b) * 100
        
        if pct_a > pct_b:
            correct = "Item A"
            explanation = f"A: {pct_a:.1f}%, B: {pct_b:.1f}%. A had the bigger percentage increase."
        elif pct_b > pct_a:
            correct = "Item B"
            explanation = f"A: {pct_a:.1f}%, B: {pct_b:.1f}%. B had the bigger percentage increase."
        else:
            correct = "Same"
            explanation = f"Both had {pct_a:.1f}% increase."
        
        options = ["Item A", "Item B", "Same", "Cannot tell"]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Item A increased from €{price_a} by €{increase_a}. Item B increased from €{price_b} by €{increase_b}. Which had the bigger percentage increase?",
            'options': options,
            'correct': options.index(correct),
            'explanation': explanation,
            'difficulty': difficulty,
        })
    
    return questions


def generate_profit_loss_questions(difficulty='beginner'):
    """Generate profit and loss questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    shop = random.choice(SHOP_NAMES)
    
    if difficulty == 'beginner':
        # Simple profit
        cost_price = random.choice([20, 30, 40, 50, 60, 80, 100])
        selling_price = cost_price + random.choice([5, 10, 15, 20])
        profit = selling_price - cost_price
        
        wrong = generate_wrong_answers_currency(profit, difficulty, min_val=0)
        options = [round_currency(profit)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} buys an item for €{cost_price} and sells it for €{selling_price}. What is the profit?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(profit)),
            'explanation': f"Profit = Selling Price - Cost Price = €{selling_price} - €{cost_price} = €{profit}",
            'difficulty': difficulty,
        })
        
        # Simple loss
        cost_price = random.choice([50, 60, 80, 100])
        selling_price = cost_price - random.choice([5, 10, 15])
        loss = cost_price - selling_price
        
        wrong = generate_wrong_answers_currency(loss, difficulty, min_val=0)
        options = [round_currency(loss)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A shop buys stock for €{cost_price} but has to sell it for €{selling_price}. What is the loss?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(loss)),
            'explanation': f"Loss = Cost Price - Selling Price = €{cost_price} - €{selling_price} = €{loss}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Percentage profit on cost price
        cost_price = random.randint(40, 120)
        profit_pct = random.choice([20, 25, 30, 40, 50])
        profit = cost_price * (profit_pct / 100)
        selling_price = cost_price + profit
        
        wrong = generate_wrong_answers_currency(selling_price, difficulty)
        options = [round_currency(selling_price)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{shop} buys items for €{cost_price} each and sells them at a {profit_pct}% profit. What is the selling price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(selling_price)),
            'explanation': f"Profit = {profit_pct}% of €{cost_price} = €{profit:.2f}. Selling price = €{cost_price} + €{profit:.2f} = €{selling_price:.2f}",
            'difficulty': difficulty,
        })
        
        # Find percentage profit
        cost_price = random.randint(50, 100)
        selling_price = cost_price + random.randint(10, 40)
        profit = selling_price - cost_price
        profit_pct = (profit / cost_price) * 100
        
        wrong = generate_wrong_answers_percent(profit_pct, difficulty)
        options = [round_percent(profit_pct)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} buys something for €{cost_price} and sells it for €{selling_price}. What is the percentage profit?",
            'options': [f"{o}%" for o in options],
            'correct': options.index(round_percent(profit_pct)),
            'explanation': f"Profit = €{selling_price} - €{cost_price} = €{profit}. % Profit = (€{profit} ÷ €{cost_price}) × 100 = {profit_pct:.1f}%",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Mark-up vs Margin
        cost_price = random.randint(60, 150)
        markup_pct = random.choice([25, 30, 40, 50])
        selling_price = cost_price * (1 + markup_pct/100)
        profit = selling_price - cost_price
        margin_pct = (profit / selling_price) * 100
        
        wrong = generate_wrong_answers_percent(margin_pct, difficulty)
        options = [round_percent(margin_pct)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"An item has a cost price of €{cost_price} and a mark-up of {markup_pct}%. What is the margin (profit as % of selling price)?",
            'options': [f"{o}%" for o in options],
            'correct': options.index(round_percent(margin_pct)),
            'explanation': f"Selling price = €{cost_price} × 1.{markup_pct} = €{selling_price:.2f}. Profit = €{profit:.2f}. Margin = (€{profit:.2f} ÷ €{selling_price:.2f}) × 100 = {margin_pct:.1f}%",
            'difficulty': difficulty,
        })
        
        # Find cost price given selling price and margin
        selling_price = random.randint(80, 200)
        margin_pct = random.choice([20, 25, 30])
        profit = selling_price * (margin_pct / 100)
        cost_price = selling_price - profit
        
        wrong = generate_wrong_answers_currency(cost_price, difficulty)
        options = [round_currency(cost_price)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"An item sells for €{selling_price} with a {margin_pct}% margin. What is the cost price?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(cost_price)),
            'explanation': f"Margin = {margin_pct}% of selling price = €{profit:.2f}. Cost price = €{selling_price} - €{profit:.2f} = €{cost_price:.2f}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_vat_questions(difficulty='beginner'):
    """Generate VAT calculation questions with Irish rates"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Add VAT at standard rate
        price_ex_vat = random.choice([50, 80, 100, 120, 150, 200])
        vat_rate = 23  # Standard Irish VAT
        vat_amount = price_ex_vat * (vat_rate / 100)
        price_inc_vat = price_ex_vat + vat_amount
        
        wrong = generate_wrong_answers_currency(price_inc_vat, difficulty)
        options = [round_currency(price_inc_vat)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A laptop costs €{price_ex_vat} before VAT. If VAT is {vat_rate}%, what is the price including VAT?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(price_inc_vat)),
            'explanation': f"VAT = {vat_rate}% of €{price_ex_vat} = €{vat_amount:.2f}. Total = €{price_ex_vat} + €{vat_amount:.2f} = €{price_inc_vat:.2f}",
            'difficulty': difficulty,
        })
        
        # Calculate VAT amount
        price_ex_vat = random.choice([40, 60, 80, 100])
        vat_rate = 23
        vat_amount = price_ex_vat * (vat_rate / 100)
        
        wrong = generate_wrong_answers_currency(vat_amount, difficulty)
        options = [round_currency(vat_amount)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"An item costs €{price_ex_vat} excluding VAT. How much is the VAT at {vat_rate}%?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(vat_amount)),
            'explanation': f"VAT = {vat_rate}% of €{price_ex_vat} = €{price_ex_vat} × 0.23 = €{vat_amount:.2f}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Find price before VAT
        price_inc_vat = random.choice([123, 150, 184.50, 200, 246])
        vat_rate = 23
        price_ex_vat = price_inc_vat / 1.23
        
        wrong = generate_wrong_answers_currency(price_ex_vat, difficulty)
        options = [round_currency(price_ex_vat)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A phone costs €{price_inc_vat:.2f} including VAT at {vat_rate}%. What is the price before VAT?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(price_ex_vat)),
            'explanation': f"Price including VAT = 123% of original. Original = €{price_inc_vat:.2f} ÷ 1.23 = €{price_ex_vat:.2f}",
            'difficulty': difficulty,
        })
        
        # Different VAT rates
        price_ex_vat = random.randint(50, 150)
        vat_rate = random.choice([9, 13.5, 23])  # Irish rates
        vat_amount = price_ex_vat * (vat_rate / 100)
        
        wrong = generate_wrong_answers_currency(vat_amount, difficulty)
        options = [round_currency(vat_amount)] + wrong[:3]
        random.shuffle(options)
        
        rate_name = {9: "reduced (hospitality)", 13.5: "second reduced", 23: "standard"}[vat_rate]
        
        questions.append({
            'question_text': f"A service costs €{price_ex_vat} before VAT. Calculate the VAT at the {rate_name} rate of {vat_rate}%.",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(vat_amount)),
            'explanation': f"VAT = {vat_rate}% of €{price_ex_vat} = €{vat_amount:.2f}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Complex: find VAT from total
        price_inc_vat = random.randint(100, 300)
        vat_rate = 23
        price_ex_vat = price_inc_vat / 1.23
        vat_amount = price_inc_vat - price_ex_vat
        
        wrong = generate_wrong_answers_currency(vat_amount, difficulty)
        options = [round_currency(vat_amount)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"An invoice shows a total of €{price_inc_vat} including VAT at 23%. How much of this is VAT?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(vat_amount)),
            'explanation': f"Price ex VAT = €{price_inc_vat} ÷ 1.23 = €{price_ex_vat:.2f}. VAT = €{price_inc_vat} - €{price_ex_vat:.2f} = €{vat_amount:.2f}",
            'difficulty': difficulty,
        })
        
        # VAT comparison
        item_a_ex = random.randint(80, 120)
        item_a_vat = 23
        item_b_ex = random.randint(90, 130)
        item_b_vat = 13.5
        
        total_a = item_a_ex * (1 + item_a_vat/100)
        total_b = item_b_ex * (1 + item_b_vat/100)
        
        cheaper = "Item A" if total_a < total_b else "Item B" if total_b < total_a else "Same price"
        diff = abs(total_a - total_b)
        
        options = ["Item A", "Item B", "Same price", "Cannot determine"]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Item A costs €{item_a_ex} + {item_a_vat}% VAT. Item B costs €{item_b_ex} + {item_b_vat}% VAT. Which is cheaper overall?",
            'options': options,
            'correct': options.index(cheaper),
            'explanation': f"A total = €{total_a:.2f}, B total = €{total_b:.2f}. {cheaper} is cheaper by €{diff:.2f}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_compound_interest_questions(difficulty='intermediate'):
    """Generate compound interest questions (up to 3 years as per curriculum)"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'intermediate':
        # 1 year compound interest
        principal = random.choice([500, 1000, 1500, 2000])
        rate = random.choice([2, 3, 4, 5])
        years = 1
        
        amount = principal * (1 + rate/100) ** years
        interest = amount - principal
        
        wrong = generate_wrong_answers_currency(amount, difficulty)
        options = [round_currency(amount)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} invests €{principal} at {rate}% per year compound interest. How much will they have after {years} year?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(amount)),
            'explanation': f"Amount = €{principal} × (1 + {rate}/100)^{years} = €{principal} × {1 + rate/100} = €{amount:.2f}",
            'difficulty': difficulty,
        })
        
        # 2 years
        principal = random.choice([1000, 2000, 5000])
        rate = random.choice([3, 4, 5])
        years = 2
        
        amount = principal * (1 + rate/100) ** years
        
        wrong = generate_wrong_answers_currency(amount, difficulty)
        options = [round_currency(amount)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"€{principal} is invested at {rate}% compound interest per year. What is the total after {years} years?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(amount)),
            'explanation': f"Amount = €{principal} × (1.0{rate})^{years} = €{amount:.2f}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # 3 years compound interest
        principal = random.choice([2000, 3000, 5000])
        rate = random.choice([3, 4, 5, 6])
        years = 3
        
        amount = principal * (1 + rate/100) ** years
        total_interest = amount - principal
        
        wrong = generate_wrong_answers_currency(total_interest, difficulty)
        options = [round_currency(total_interest)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} puts €{principal} in a savings account at {rate}% compound interest per year. How much interest is earned after {years} years?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(total_interest)),
            'explanation': f"Amount after {years} years = €{principal} × (1.0{rate})^{years} = €{amount:.2f}. Interest = €{amount:.2f} - €{principal} = €{total_interest:.2f}",
            'difficulty': difficulty,
        })
        
        # Compare simple vs compound
        principal = 1000
        rate = 5
        years = 3
        
        simple_interest = principal * (rate/100) * years
        compound_amount = principal * (1 + rate/100) ** years
        compound_interest = compound_amount - principal
        difference = compound_interest - simple_interest
        
        wrong = generate_wrong_answers_currency(difference, difficulty)
        options = [round_currency(difference)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"€{principal} at {rate}% for {years} years. How much MORE interest is earned with compound vs simple interest?",
            'options': [format_euro(o) for o in options],
            'correct': options.index(round_currency(difference)),
            'explanation': f"Simple interest = €{simple_interest:.2f}. Compound interest = €{compound_interest:.2f}. Difference = €{difference:.2f}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_value_for_money_questions(difficulty='intermediate'):
    """Generate value for money comparison questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    shop = random.choice(SHOP_NAMES)
    
    if difficulty == 'intermediate':
        # Unit price comparison
        item = random.choice(['milk', 'orange juice', 'pasta', 'rice', 'cereal'])
        
        size_a = random.choice([500, 750])
        price_a = round(random.uniform(1.5, 3), 2)
        unit_price_a = (price_a / size_a) * 1000  # per kg or litre
        
        size_b = random.choice([1000, 1500])
        # Make one slightly better value
        if random.random() > 0.5:
            unit_price_b = unit_price_a * random.uniform(0.8, 0.95)
        else:
            unit_price_b = unit_price_a * random.uniform(1.05, 1.2)
        price_b = (unit_price_b * size_b) / 1000
        price_b = round(price_b, 2)
        
        # Recalculate actual unit prices
        unit_price_a = (price_a / size_a) * 1000
        unit_price_b = (price_b / size_b) * 1000
        
        better_value = f"{size_a}ml for €{price_a:.2f}" if unit_price_a < unit_price_b else f"{size_b}ml for €{price_b:.2f}"
        
        options = [f"{size_a}ml for €{price_a:.2f}", f"{size_b}ml for €{price_b:.2f}", "Same value", "Cannot compare"]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Which is better value for {item}: {size_a}ml for €{price_a:.2f} or {size_b}ml for €{price_b:.2f}?",
            'options': options,
            'correct': options.index(better_value),
            'explanation': f"Unit price A = €{unit_price_a:.3f}/L. Unit price B = €{unit_price_b:.3f}/L. {better_value} is better value.",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Multi-buy comparison
        item = random.choice(['chocolate bars', 'cans of cola', 'packets of crisps'])
        
        single_price = round(random.uniform(0.8, 1.5), 2)
        multipack_qty = random.choice([4, 6, 8])
        # Usually a small discount
        discount_pct = random.randint(10, 25)
        multipack_price = round(single_price * multipack_qty * (1 - discount_pct/100), 2)
        
        unit_single = single_price
        unit_multi = multipack_price / multipack_qty
        
        savings_per_item = unit_single - unit_multi
        savings_pct = (savings_per_item / unit_single) * 100
        
        wrong = generate_wrong_answers_percent(savings_pct, difficulty)
        options = [round_percent(savings_pct)] + wrong[:3]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{item.capitalize()} cost €{single_price:.2f} each or a pack of {multipack_qty} for €{multipack_price:.2f}. What percentage do you save per item by buying the multipack?",
            'options': [f"{o}%" for o in options],
            'correct': options.index(round_percent(savings_pct)),
            'explanation': f"Single: €{unit_single:.2f} each. Multipack: €{unit_multi:.2f} each. Saving = {savings_pct:.1f}%",
            'difficulty': difficulty,
        })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_percentage_questions(question_type, difficulty, count=5, output_dir=None):
    """
    Generate percentage questions.
    
    Args:
        question_type: 'basic', 'increase_decrease', 'profit_loss', 'vat', 
                       'compound_interest', 'value_for_money', or 'mixed'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of question sets to generate
        output_dir: Directory for any images (not used currently but kept for consistency)
    
    Returns:
        List of question dictionaries
    """
    all_questions = []
    
    generators = {
        'basic': generate_basic_percentage_questions,
        'increase_decrease': generate_increase_decrease_questions,
        'profit_loss': generate_profit_loss_questions,
        'vat': generate_vat_questions,
        'compound_interest': generate_compound_interest_questions,
        'value_for_money': generate_value_for_money_questions,
    }
    
    for i in range(count):
        if question_type == 'mixed':
            # Pick random type appropriate for difficulty
            if difficulty == 'beginner':
                chosen_type = random.choice(['basic', 'increase_decrease', 'profit_loss', 'vat'])
            else:
                chosen_type = random.choice(list(generators.keys()))
        else:
            chosen_type = question_type
        
        # Skip compound interest for beginners
        if difficulty == 'beginner' and chosen_type == 'compound_interest':
            chosen_type = 'basic'
        
        generator = generators.get(chosen_type)
        if generator:
            questions = generator(difficulty)
            for q in questions:
                q['image_url'] = None
                q['image_caption'] = None
                q['topic'] = 'percentages'
                q['sub_type'] = chosen_type
                all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_percentages_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for percentages question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-percentages-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_percentages_questions():
        """Generate percentage and financial maths questions"""
        from flask import request, jsonify
        
        data = request.json or {}
        
        question_types = data.get('question_types', 
            ['basic', 'increase_decrease', 'profit_loss', 'vat', 'compound_interest', 'value_for_money'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        sets_per_type = data.get('sets_per_type', 3)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for q_type in question_types:
            for difficulty in difficulties:
                # Skip compound interest for beginners
                if difficulty == 'beginner' and q_type == 'compound_interest':
                    continue
                
                questions = generate_percentage_questions(
                    question_type=q_type,
                    difficulty=difficulty,
                    count=sets_per_type,
                )
                
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
                        'topic': 'percentages',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='percentages',
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
                "SELECT COUNT(*) FROM questions WHERE topic = 'percentages' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/percentages-generator-status', methods=['GET'])
    @admin_required_api
    def percentages_generator_status():
        """Check percentages generator status"""
        from flask import jsonify
        
        return jsonify({
            'available': True,
            'question_types': ['basic', 'increase_decrease', 'profit_loss', 'vat', 'compound_interest', 'value_for_money', 'mixed'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
            'irish_vat_rates': VAT_RATES,
        })


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("Testing Percentages Question Generator...")
    print("=" * 60)
    
    question_types = ['basic', 'increase_decrease', 'profit_loss', 'vat', 'compound_interest', 'value_for_money']
    
    for q_type in question_types:
        print(f"\n{q_type.upper().replace('_', ' ')} QUESTIONS:")
        
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            if difficulty == 'beginner' and q_type == 'compound_interest':
                continue
            
            questions = generate_percentage_questions(q_type, difficulty, count=1)
            
            if questions:
                print(f"\n  {difficulty.capitalize()}:")
                for q in questions[:2]:
                    print(f"    Q: {q['question_text'][:70]}...")
                    print(f"    Options: {q['options']}")
                    print(f"    Answer: {q['options'][q['correct']]}")
