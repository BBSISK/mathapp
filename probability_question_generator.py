#!/usr/bin/env python3
"""
Probability Question Generator for AgentMath.app

Generates probability questions aligned with Irish Junior Cycle Mathematics:
- Basic probability concepts (likelihood, certainty, impossibility)
- Single event probability (coins, dice, spinners, cards)
- Sample space and listing outcomes
- Two-event probability (combined events)
- Expected frequency and relative frequency
- Probability from experiments
- Tree diagrams (conceptual)
- Real-world contexts for 14-year-olds in Ireland

Each question type has beginner, intermediate, and advanced variants.
"""

import os
import random
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

# ============================================================================
# IRISH CONTEXT DATA
# ============================================================================

# Irish names for story problems
IRISH_NAMES = [
    "Aoife", "Cian", "Saoirse", "Oisín", "Niamh", "Conor", "Ciara", "Seán",
    "Róisín", "Darragh", "Caoimhe", "Fionn", "Éabha", "Tadhg", "Ava", "Liam",
    "Molly", "Jack", "Emma", "Ryan", "Sophie", "Dylan", "Grace", "Adam"
]

# Irish school/teen contexts
IRISH_CONTEXTS = {
    'sports': ['football', 'hurling', 'camogie', 'Gaelic football', 'rugby', 'soccer'],
    'schools': ['Palmerstown CS', 'the local school', 'St. Mary\'s', 'the community college'],
    'places': ['Dublin', 'Cork', 'Galway', 'Limerick', 'the local shop', 'SuperValu'],
    'sweets': ['Tayto', 'club milk', 'chocolate', 'jellies', 'crisps', 'biscuits'],
}

# Spinner configurations
SPINNER_CONFIGS = {
    'colours': {
        'items': ['red', 'blue', 'green', 'yellow', 'purple', 'orange'],
        'emoji': '🎨'
    },
    'numbers': {
        'items': ['1', '2', '3', '4', '5', '6', '7', '8'],
        'emoji': '🔢'
    },
    'animals': {
        'items': ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster'],
        'emoji': '🐾'
    }
}

# Card deck info
CARD_SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
CARD_VALUES = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
RED_SUITS = ['hearts', 'diamonds']
BLACK_SUITS = ['clubs', 'spades']
FACE_CARDS = ['Jack', 'Queen', 'King']


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def simplify_fraction(numerator, denominator):
    """Return simplified fraction as string"""
    if denominator == 0:
        return "undefined"
    f = Fraction(numerator, denominator)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def fraction_to_decimal(numerator, denominator):
    """Convert fraction to decimal rounded to 2 places"""
    if denominator == 0:
        return 0
    return round(numerator / denominator, 2)


def generate_wrong_fractions(correct_num, correct_den, count=3):
    """Generate plausible wrong fraction answers"""
    wrong = set()
    correct_str = simplify_fraction(correct_num, correct_den)
    
    attempts = 0
    while len(wrong) < count and attempts < 30:
        attempts += 1
        
        # Common mistakes
        error_type = random.choice([
            'swap', 'off_by_one_num', 'off_by_one_den', 
            'complement', 'double', 'half', 'random'
        ])
        
        if error_type == 'swap':
            new_num, new_den = correct_den, correct_num
        elif error_type == 'off_by_one_num':
            new_num = correct_num + random.choice([-1, 1])
            new_den = correct_den
        elif error_type == 'off_by_one_den':
            new_num = correct_num
            new_den = correct_den + random.choice([-1, 1, 2])
        elif error_type == 'complement':
            new_num = correct_den - correct_num
            new_den = correct_den
        elif error_type == 'double':
            new_num = correct_num * 2
            new_den = correct_den
        elif error_type == 'half':
            new_num = correct_num
            new_den = correct_den * 2
        else:
            new_num = random.randint(1, correct_den)
            new_den = correct_den
        
        if new_num > 0 and new_den > 0 and new_num <= new_den:
            wrong_str = simplify_fraction(new_num, new_den)
            if wrong_str != correct_str and wrong_str not in wrong:
                wrong.add(wrong_str)
    
    # Fallback
    for i in range(1, correct_den + 1):
        if len(wrong) >= count:
            break
        candidate = simplify_fraction(i, correct_den)
        if candidate != correct_str and candidate not in wrong:
            wrong.add(candidate)
    
    return list(wrong)[:count]


def generate_wrong_integers(correct, max_val, min_val=0):
    """Generate plausible wrong integer answers"""
    wrong = set()
    
    offsets = [1, -1, 2, -2, 3, -3, 5, -5]
    for offset in offsets:
        candidate = correct + offset
        if min_val <= candidate <= max_val and candidate != correct:
            wrong.add(candidate)
    
    # Add some random ones
    for _ in range(5):
        candidate = random.randint(min_val, max_val)
        if candidate != correct:
            wrong.add(candidate)
    
    return list(wrong)[:3]


def generate_wrong_decimals(correct, count=3):
    """Generate plausible wrong decimal probability answers"""
    wrong = set()
    
    offsets = [0.1, -0.1, 0.15, -0.15, 0.2, -0.2, 0.25, -0.25, 0.05, -0.05]
    for offset in offsets:
        candidate = round(correct + offset, 2)
        if 0 <= candidate <= 1 and candidate != correct:
            wrong.add(candidate)
    
    return list(wrong)[:count]


# ============================================================================
# QUESTION GENERATORS BY TOPIC
# ============================================================================

def generate_basic_probability_questions(difficulty='beginner'):
    """Generate basic probability concept questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Likelihood scale questions
        events = [
            ("The sun will rise tomorrow", "certain", "This is certain to happen - the sun rises every day."),
            ("You will roll a 7 on a standard six-sided dice", "impossible", "A standard dice only has numbers 1-6, so rolling a 7 is impossible."),
            ("It will rain sometime this month in Ireland", "very likely", "Rain is very common in Ireland, so this is very likely."),
            ("You flip a coin and get heads", "even chance", "A fair coin has equal chance of heads or tails - 50/50."),
            ("You pick a red card from a shuffled deck", "even chance", "Half the cards are red, half are black - even chance."),
            ("A baby born today will be a girl", "even chance", "Roughly equal chance of boy or girl."),
            ("You roll an even number on a dice", "even chance", "Three even numbers (2,4,6) out of six - even chance."),
            ("Ireland wins the next World Cup", "unlikely", "While possible, this would be considered unlikely."),
        ]
        
        event, correct, explanation = random.choice(events)
        
        options = ["certain", "very likely", "even chance", "unlikely", "impossible"]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"How would you describe the likelihood of this event: \"{event}\"?",
            'options': options,
            'correct': options.index(correct),
            'explanation': explanation,
            'difficulty': difficulty,
        })
        
        # Probability as fraction
        scenarios = [
            ("A bag contains 1 red marble and 1 blue marble. What is the probability of picking the red marble?", 1, 2),
            ("A bag contains 1 green sweet and 3 red sweets. What is the probability of picking the green sweet?", 1, 4),
            ("A spinner has 4 equal sections: 1 blue, 3 yellow. What is the probability of landing on blue?", 1, 4),
        ]
        
        question, num, den = random.choice(scenarios)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': question,
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"There is {num} favourable outcome out of {den} total outcomes, so the probability is {correct_str}.",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Probability scale 0 to 1
        scenarios = [
            ("An event that is impossible", 0, "Impossible events have probability 0."),
            ("An event that is certain", 1, "Certain events have probability 1."),
            ("Flipping a fair coin and getting heads", 0.5, "Equal chance means probability of 0.5 or 1/2."),
            ("Rolling a 6 on a fair dice", round(1/6, 2), "One favourable outcome out of 6, so 1/6 ≈ 0.17."),
        ]
        
        question_text, correct, explanation = random.choice(scenarios)
        
        wrong = generate_wrong_decimals(correct)
        options = [correct] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"On a probability scale from 0 to 1, what is the probability of: {question_text}?",
            'options': [str(o) for o in options],
            'correct': options.index(correct),
            'explanation': explanation,
            'difficulty': difficulty,
        })
        
        # Complementary probability
        prob = random.choice([0.2, 0.3, 0.4, 0.6, 0.7, 0.8])
        complement = round(1 - prob, 1)
        
        wrong = generate_wrong_decimals(complement)
        options = [complement] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"The probability of an event happening is {prob}. What is the probability of it NOT happening?",
            'options': [str(o) for o in options],
            'correct': options.index(complement),
            'explanation': f"P(not happening) = 1 - P(happening) = 1 - {prob} = {complement}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Sum of all probabilities = 1
        p1 = random.choice([0.2, 0.25, 0.3])
        p2 = random.choice([0.3, 0.35, 0.4])
        p3 = round(1 - p1 - p2, 2)
        
        wrong = generate_wrong_decimals(p3)
        options = [p3] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A spinner has three colours. The probability of landing on red is {p1} and blue is {p2}. What is the probability of landing on green?",
            'options': [str(o) for o in options],
            'correct': options.index(p3),
            'explanation': f"All probabilities must sum to 1. P(green) = 1 - {p1} - {p2} = {p3}",
            'difficulty': difficulty,
        })
        
        # Impossible vs unlikely
        questions.append({
            'question_text': "Which statement is TRUE about probability?",
            'options': [
                "A probability of 0 means an event is unlikely",
                "A probability of 0 means an event is impossible",
                "A probability of 0.5 means an event is unlikely",
                "A probability of 1 means an event might happen"
            ],
            'correct': 1,
            'explanation': "A probability of 0 means impossible, 1 means certain, and 0.5 means equally likely.",
            'difficulty': difficulty,
        })
    
    return questions


def generate_dice_questions(difficulty='beginner'):
    """Generate dice probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Single dice, simple events
        events = [
            ("rolling a 4", 1, 6, "There is one 4 on the dice."),
            ("rolling an even number", 3, 6, "Even numbers are 2, 4, 6 - that's 3 outcomes."),
            ("rolling an odd number", 3, 6, "Odd numbers are 1, 3, 5 - that's 3 outcomes."),
            ("rolling a number greater than 4", 2, 6, "Numbers greater than 4 are 5 and 6 - that's 2 outcomes."),
            ("rolling a number less than 3", 2, 6, "Numbers less than 3 are 1 and 2 - that's 2 outcomes."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} rolls a fair six-sided dice. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"{explanation} Probability = {num}/{den} = {correct_str}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Two dice - sum questions
        target_sum = random.choice([7, 8, 9, 6])
        
        # Calculate favourable outcomes for sum
        favourable = 0
        for d1 in range(1, 7):
            for d2 in range(1, 7):
                if d1 + d2 == target_sum:
                    favourable += 1
        
        correct_str = simplify_fraction(favourable, 36)
        wrong = generate_wrong_fractions(favourable, 36)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} rolls two fair dice and adds the numbers. What is the probability of getting a total of {target_sum}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"There are 36 possible outcomes when rolling two dice. {favourable} combinations give a sum of {target_sum}. Probability = {favourable}/36 = {correct_str}",
            'difficulty': difficulty,
        })
        
        # Sample space size
        questions.append({
            'question_text': "How many different outcomes are possible when rolling two fair dice?",
            'options': ["12", "36", "6", "24"],
            'correct': 1,
            'explanation': "Each dice has 6 outcomes. Total outcomes = 6 × 6 = 36.",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Two dice - specific conditions
        conditions = [
            ("getting a double (both dice show the same number)", 6, 36, "Doubles are (1,1), (2,2), (3,3), (4,4), (5,5), (6,6) - that's 6 outcomes."),
            ("getting a total greater than 10", 3, 36, "Totals > 10 are 11 and 12. Ways to get 11: (5,6), (6,5). Ways to get 12: (6,6). That's 3 outcomes."),
            ("both dice showing an even number", 9, 36, "Each dice can show 2, 4, or 6. That's 3 × 3 = 9 outcomes."),
        ]
        
        condition, num, den, explanation = random.choice(conditions)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Two fair dice are rolled. What is the probability of {condition}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"{explanation} Probability = {num}/36 = {correct_str}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_coin_questions(difficulty='beginner'):
    """Generate coin probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Single coin
        questions.append({
            'question_text': f"{name} flips a fair coin. What is the probability of getting heads?",
            'options': ["1/2", "1/4", "1/3", "2/3"],
            'correct': 0,
            'explanation': "A fair coin has 2 equally likely outcomes: heads or tails. P(heads) = 1/2.",
            'difficulty': difficulty,
        })
        
        # Two coins - listing outcomes
        questions.append({
            'question_text': "Two coins are flipped. How many different outcomes are possible?",
            'options': ["2", "3", "4", "6"],
            'correct': 2,
            'explanation': "The outcomes are: HH, HT, TH, TT. That's 4 different outcomes.",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Two coins - probability
        events = [
            ("getting exactly one head", 2, 4, "One head occurs in HT and TH - 2 outcomes out of 4."),
            ("getting two heads", 1, 4, "Two heads is only HH - 1 outcome out of 4."),
            ("getting at least one head", 3, 4, "At least one head: HH, HT, TH - 3 outcomes out of 4."),
            ("getting no heads", 1, 4, "No heads is only TT - 1 outcome out of 4."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} flips two fair coins. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"Possible outcomes: HH, HT, TH, TT. {explanation}",
            'difficulty': difficulty,
        })
        
        # Three coins - sample space
        questions.append({
            'question_text': "Three coins are flipped. How many different outcomes are possible?",
            'options': ["6", "8", "9", "12"],
            'correct': 1,
            'explanation': "Each coin has 2 outcomes. Total = 2 × 2 × 2 = 8 outcomes.",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Three coins - probability
        events = [
            ("getting exactly two heads", 3, 8, "Two heads: HHT, HTH, THH - 3 outcomes."),
            ("getting all heads", 1, 8, "All heads is only HHH - 1 outcome."),
            ("getting at least two heads", 4, 8, "At least two heads: HHH, HHT, HTH, THH - 4 outcomes."),
            ("getting more heads than tails", 4, 8, "More heads than tails: HHH (3H), HHT, HTH, THH (2H each) - 4 outcomes."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} flips three fair coins. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"There are 8 possible outcomes (HHH, HHT, HTH, THH, HTT, THT, TTH, TTT). {explanation} Probability = {correct_str}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_card_questions(difficulty='beginner'):
    """Generate playing card probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Simple card questions
        events = [
            ("picking a heart", 13, 52, "There are 13 hearts in a deck of 52 cards."),
            ("picking a red card", 26, 52, "There are 26 red cards (hearts and diamonds) in a deck of 52."),
            ("picking an Ace", 4, 52, "There are 4 Aces in a deck of 52 cards."),
            ("picking a King", 4, 52, "There are 4 Kings in a deck of 52 cards."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} picks one card at random from a standard deck of 52 cards. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"{explanation} Probability = {num}/52 = {correct_str}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # More complex card questions
        events = [
            ("picking a face card (Jack, Queen, or King)", 12, 52, "There are 12 face cards (4 Jacks + 4 Queens + 4 Kings)."),
            ("picking a black Ace", 2, 52, "There are 2 black Aces (Ace of clubs and Ace of spades)."),
            ("picking a number card (2-10)", 36, 52, "There are 9 number cards per suit × 4 suits = 36 number cards."),
            ("picking a card that is NOT a heart", 39, 52, "52 - 13 hearts = 39 non-hearts."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A card is drawn at random from a standard 52-card deck. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"{explanation} Probability = {num}/52 = {correct_str}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Compound card questions
        events = [
            ("picking a red face card", 6, 52, "Red face cards: 3 in hearts + 3 in diamonds = 6."),
            ("picking an Ace or a King", 8, 52, "4 Aces + 4 Kings = 8 cards."),
            ("picking a heart or a face card", 22, 52, "13 hearts + 12 face cards - 3 heart face cards = 22."),
        ]
        
        event, num, den, explanation = random.choice(events)
        correct_str = simplify_fraction(num, den)
        wrong = generate_wrong_fractions(num, den)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A card is drawn at random from a standard 52-card deck. What is the probability of {event}?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"{explanation} Probability = {num}/52 = {correct_str}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_bag_questions(difficulty='beginner'):
    """Generate bag/marble probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Simple bag questions
        red = random.randint(2, 5)
        blue = random.randint(2, 5)
        total = red + blue
        
        correct_str = simplify_fraction(red, total)
        wrong = generate_wrong_fractions(red, total)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A bag contains {red} red marbles and {blue} blue marbles. {name} picks one marble at random. What is the probability of picking a red marble?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"There are {red} red marbles out of {total} total. Probability = {red}/{total} = {correct_str}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Three colours
        red = random.randint(2, 4)
        blue = random.randint(2, 4)
        green = random.randint(1, 3)
        total = red + blue + green
        
        # Pick which colour to ask about
        colour, count = random.choice([('red', red), ('blue', blue), ('green', green)])
        
        correct_str = simplify_fraction(count, total)
        wrong = generate_wrong_fractions(count, total)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A bag contains {red} red, {blue} blue, and {green} green marbles. What is the probability of picking a {colour} marble at random?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"There are {count} {colour} marbles out of {total} total. Probability = {count}/{total} = {correct_str}",
            'difficulty': difficulty,
        })
        
        # NOT a certain colour
        not_colour = random.choice(['red', 'blue', 'green'])
        if not_colour == 'red':
            not_count = blue + green
        elif not_colour == 'blue':
            not_count = red + green
        else:
            not_count = red + blue
        
        correct_str = simplify_fraction(not_count, total)
        wrong = generate_wrong_fractions(not_count, total)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A bag contains {red} red, {blue} blue, and {green} green marbles. What is the probability of NOT picking a {not_colour} marble?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"NOT {not_colour} means any other colour. There are {not_count} non-{not_colour} marbles out of {total}. Probability = {not_count}/{total} = {correct_str}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # With replacement vs without
        red = random.randint(3, 5)
        blue = random.randint(3, 5)
        total = red + blue
        
        # Probability of red AND blue (with replacement)
        p_red = Fraction(red, total)
        p_blue = Fraction(blue, total)
        p_both = p_red * p_blue
        
        correct_str = f"{p_both.numerator}/{p_both.denominator}"
        wrong = generate_wrong_fractions(p_both.numerator, p_both.denominator)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A bag contains {red} red and {blue} blue marbles. {name} picks a marble, replaces it, then picks again. What is the probability of picking red first AND blue second?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"P(red) = {red}/{total}, P(blue) = {blue}/{total}. With replacement, P(red then blue) = {red}/{total} × {blue}/{total} = {correct_str}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_expected_frequency_questions(difficulty='beginner'):
    """Generate expected frequency questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'beginner':
        # Simple expected frequency
        trials = random.choice([60, 100, 120])
        probability = Fraction(1, 6)
        expected = trials // 6
        
        wrong = generate_wrong_integers(expected, trials)
        options = [str(expected)] + [str(w) for w in wrong]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} rolls a fair dice {trials} times. How many times would you expect to roll a 6?",
            'options': options,
            'correct': options.index(str(expected)),
            'explanation': f"Expected frequency = probability × number of trials = 1/6 × {trials} = {expected}",
            'difficulty': difficulty,
        })
        
        # Coin expected
        trials = random.choice([50, 100, 200])
        expected = trials // 2
        
        wrong = generate_wrong_integers(expected, trials)
        options = [str(expected)] + [str(w) for w in wrong]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A fair coin is flipped {trials} times. How many heads would you expect?",
            'options': options,
            'correct': options.index(str(expected)),
            'explanation': f"Expected frequency = 1/2 × {trials} = {expected}",
            'difficulty': difficulty,
        })
    
    elif difficulty == 'intermediate':
        # Spinner expected
        sections = random.randint(4, 8)
        target_sections = random.randint(1, sections // 2)
        trials = random.choice([40, 60, 80, 100])
        expected = (target_sections * trials) // sections
        
        wrong = generate_wrong_integers(expected, trials)
        options = [str(expected)] + [str(w) for w in wrong]
        random.shuffle(options)
        
        colour = random.choice(['red', 'blue', 'green'])
        
        questions.append({
            'question_text': f"A spinner has {sections} equal sections. {target_sections} sections are {colour}. If the spinner is spun {trials} times, how many times would you expect to land on {colour}?",
            'options': options,
            'correct': options.index(str(expected)),
            'explanation': f"P({colour}) = {target_sections}/{sections}. Expected = {target_sections}/{sections} × {trials} = {expected}",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Reverse - find probability from expected
        trials = random.choice([100, 200, 500])
        expected = random.choice([20, 25, 40, 50])
        probability = expected / trials
        
        wrong = generate_wrong_decimals(probability)
        options = [str(probability)] + [str(w) for w in wrong]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"In {trials} trials, an event is expected to occur {expected} times. What is the probability of the event?",
            'options': options,
            'correct': options.index(str(probability)),
            'explanation': f"Probability = expected frequency ÷ trials = {expected} ÷ {trials} = {probability}",
            'difficulty': difficulty,
        })
    
    return questions


def generate_relative_frequency_questions(difficulty='intermediate'):
    """Generate relative frequency / experimental probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'intermediate':
        # Calculate relative frequency
        trials = random.choice([50, 100, 200])
        successes = random.randint(trials // 5, trials // 2)
        rel_freq = round(successes / trials, 2)
        
        wrong = generate_wrong_decimals(rel_freq)
        options = [str(rel_freq)] + [str(w) for w in wrong]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"{name} flipped a coin {trials} times and got heads {successes} times. What is the relative frequency of heads?",
            'options': options,
            'correct': options.index(str(rel_freq)),
            'explanation': f"Relative frequency = number of heads ÷ total flips = {successes} ÷ {trials} = {rel_freq}",
            'difficulty': difficulty,
        })
        
        # Is the coin fair?
        trials = 100
        heads = random.choice([48, 52, 35, 65])
        
        if 45 <= heads <= 55:
            correct = "Yes, close enough to 50%"
            explanation = f"{heads}% is close to 50%, suggesting the coin is fair."
        else:
            correct = "No, too far from 50%"
            explanation = f"{heads}% is quite different from 50%, suggesting the coin may be biased."
        
        options = ["Yes, close enough to 50%", "No, too far from 50%", "Cannot tell from this data", "Need more information"]
        random.shuffle(options)
        
        questions.append({
            'question_text': f"A coin is flipped {trials} times. It lands on heads {heads} times. Does this suggest the coin is fair?",
            'options': options,
            'correct': options.index(correct),
            'explanation': explanation,
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # Compare theoretical and experimental
        trials = 60
        sixes = random.choice([8, 10, 12, 15])
        rel_freq = round(sixes / trials, 2)
        theoretical = round(1/6, 2)
        
        difference = abs(rel_freq - theoretical)
        
        questions.append({
            'question_text': f"A dice is rolled {trials} times and shows a 6 exactly {sixes} times. The theoretical probability of rolling a 6 is {theoretical}. The relative frequency is {rel_freq}. What can we conclude?",
            'options': [
                "The relative frequency is close to theoretical - dice seems fair",
                "The relative frequency is very different - dice may be biased",
                "We need exactly the same values for the dice to be fair",
                "Relative frequency always equals theoretical probability"
            ],
            'correct': 0 if difference < 0.05 else 1,
            'explanation': f"The difference between relative frequency ({rel_freq}) and theoretical ({theoretical}) is {round(difference, 2)}. " + 
                          ("This is small, suggesting fair dice." if difference < 0.05 else "This difference suggests possible bias."),
            'difficulty': difficulty,
        })
    
    return questions


def generate_combined_events_questions(difficulty='intermediate'):
    """Generate combined events (AND/OR) probability questions"""
    questions = []
    name = random.choice(IRISH_NAMES)
    
    if difficulty == 'intermediate':
        # Independent events - coin and dice
        questions.append({
            'question_text': f"{name} flips a coin and rolls a dice. What is the probability of getting heads AND a 6?",
            'options': ["1/12", "1/6", "1/2", "7/12"],
            'correct': 0,
            'explanation': "P(heads) = 1/2, P(6) = 1/6. For independent events: P(heads AND 6) = 1/2 × 1/6 = 1/12",
            'difficulty': difficulty,
        })
        
        # Sample space size
        questions.append({
            'question_text': "A coin is flipped and a dice is rolled. How many different outcomes are in the sample space?",
            'options': ["8", "12", "6", "36"],
            'correct': 1,
            'explanation': "Coin has 2 outcomes, dice has 6 outcomes. Total = 2 × 6 = 12 outcomes.",
            'difficulty': difficulty,
        })
    
    else:  # advanced
        # OR probability (mutually exclusive)
        questions.append({
            'question_text': "A card is drawn from a standard deck. What is the probability of drawing a King OR a Queen?",
            'options': ["8/52", "4/52", "2/52", "16/52"],
            'correct': 0,
            'explanation': "P(King) = 4/52, P(Queen) = 4/52. These are mutually exclusive, so P(King OR Queen) = 4/52 + 4/52 = 8/52 = 2/13",
            'difficulty': difficulty,
        })
        
        # Two spinners
        spinner1 = ['A', 'B', 'C']
        spinner2 = ['1', '2', '3', '4']
        total_outcomes = len(spinner1) * len(spinner2)
        
        # Specific outcome
        correct_str = simplify_fraction(1, total_outcomes)
        wrong = generate_wrong_fractions(1, total_outcomes)
        options = [correct_str] + wrong
        random.shuffle(options)
        
        questions.append({
            'question_text': f"Spinner 1 has letters A, B, C (equal sections). Spinner 2 has numbers 1, 2, 3, 4 (equal sections). Both are spun. What is the probability of getting 'B' AND '3'?",
            'options': options,
            'correct': options.index(correct_str),
            'explanation': f"P(B) = 1/3, P(3) = 1/4. P(B AND 3) = 1/3 × 1/4 = 1/{total_outcomes}",
            'difficulty': difficulty,
        })
    
    return questions


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_probability_questions(question_type, difficulty, count=5, output_dir=None):
    """
    Generate probability questions.
    
    Args:
        question_type: 'basic', 'dice', 'coins', 'cards', 'bags', 
                       'expected_frequency', 'relative_frequency', 'combined_events', or 'mixed'
        difficulty: 'beginner', 'intermediate', or 'advanced'
        count: Number of question sets to generate
        output_dir: Directory for any images (not used currently)
    
    Returns:
        List of question dictionaries
    """
    all_questions = []
    
    generators = {
        'basic': generate_basic_probability_questions,
        'dice': generate_dice_questions,
        'coins': generate_coin_questions,
        'cards': generate_card_questions,
        'bags': generate_bag_questions,
        'expected_frequency': generate_expected_frequency_questions,
        'relative_frequency': generate_relative_frequency_questions,
        'combined_events': generate_combined_events_questions,
    }
    
    for i in range(count):
        if question_type == 'mixed':
            # Pick random type appropriate for difficulty
            if difficulty == 'beginner':
                chosen_type = random.choice(['basic', 'dice', 'coins', 'cards', 'bags', 'expected_frequency'])
            else:
                chosen_type = random.choice(list(generators.keys()))
        else:
            chosen_type = question_type
        
        # Skip some advanced topics for beginners
        if difficulty == 'beginner' and chosen_type in ['relative_frequency', 'combined_events']:
            chosen_type = 'basic'
        
        generator = generators.get(chosen_type)
        if generator:
            questions = generator(difficulty)
            for q in questions:
                q['image_url'] = None
                q['image_caption'] = None
                q['topic'] = 'probability'
                q['sub_type'] = chosen_type
                all_questions.append(q)
    
    return all_questions


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def register_probability_generator_routes(app, db, Question, admin_required_api):
    """Register Flask routes for probability question generation"""
    from sqlalchemy import text
    
    @app.route('/api/admin/generate-probability-questions', methods=['POST'])
    @admin_required_api
    def admin_generate_probability_questions():
        """Generate probability questions"""
        from flask import request, jsonify
        
        data = request.json or {}
        
        question_types = data.get('question_types', 
            ['basic', 'dice', 'coins', 'cards', 'bags', 'expected_frequency', 'relative_frequency', 'combined_events'])
        difficulties = data.get('difficulties', ['beginner', 'intermediate', 'advanced'])
        sets_per_type = data.get('sets_per_type', 3)
        
        all_generated = []
        saved_count = 0
        skipped_count = 0
        
        for q_type in question_types:
            for difficulty in difficulties:
                # Skip some combinations
                if difficulty == 'beginner' and q_type in ['relative_frequency', 'combined_events']:
                    continue
                
                questions = generate_probability_questions(
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
                        'topic': 'probability',
                        'difficulty': q['difficulty'],
                        'question_text': q['question_text']
                    }).fetchone()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new question
                    new_question = Question(
                        topic='probability',
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
                "SELECT COUNT(*) FROM questions WHERE topic = 'probability' AND difficulty = :difficulty"
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
    
    @app.route('/api/admin/probability-generator-status', methods=['GET'])
    @admin_required_api
    def probability_generator_status():
        """Check probability generator status"""
        from flask import jsonify
        
        return jsonify({
            'available': True,
            'question_types': ['basic', 'dice', 'coins', 'cards', 'bags', 'expected_frequency', 'relative_frequency', 'combined_events', 'mixed'],
            'difficulties': ['beginner', 'intermediate', 'advanced'],
        })


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("Testing Probability Question Generator...")
    print("=" * 60)
    
    question_types = ['basic', 'dice', 'coins', 'cards', 'bags', 'expected_frequency', 'combined_events']
    
    for q_type in question_types:
        print(f"\n{q_type.upper().replace('_', ' ')} QUESTIONS:")
        
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            if difficulty == 'beginner' and q_type in ['relative_frequency', 'combined_events']:
                continue
            
            questions = generate_probability_questions(q_type, difficulty, count=1)
            
            if questions:
                print(f"\n  {difficulty.capitalize()}:")
                for q in questions[:2]:
                    print(f"    Q: {q['question_text'][:70]}...")
                    print(f"    Options: {q['options']}")
                    print(f"    Answer: {q['options'][q['correct']]}")
    
    print("\n" + "=" * 60)
    print("✅ Probability generator test complete!")
