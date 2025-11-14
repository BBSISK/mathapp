# Question Generation Scripts

This directory contains scripts that generate and populate math questions in the database.

## Scripts

- **`add_probability_questions.py`** - Adds 120 probability questions (40 per difficulty level)
- **`add_decimals_questions.py`** - Adds 120 decimal questions
- **`add_number_systems_questions.py`** - Adds number systems questions (binary, octal, hex)
- **`add_surds_questions.py`** - Adds 120 surds questions
- **`add_more_questions.py`** - Expands existing topics with additional questions
- **`populate_mult_div_questions.py`** - Populates multiplication and division questions
- **`complex_numbers_VALIDATED.py`** - Adds validated complex numbers questions
- **`complex_numbers_questions_FIXED.py`** - Fixed version of complex numbers questions
- **`complex_numbers_restructured.py`** - Restructured complex numbers questions
- **`surds_questions.py`** - Alternative surds question generator
- **`update_arithmetic_questions.py`** - Updates arithmetic questions
- **`expand_questions.py`** - Expands question sets
- **`debug_questions.py`** - Debugging utility for questions

## Usage

These scripts are typically run once during initial setup or when adding new topics. They insert questions directly into the database.

**Example:**
```bash
cd ~/mathapp
source venv/bin/activate
python scripts/questions/add_probability_questions.py
```

**Warning:** Running these scripts multiple times may create duplicate questions. Check the database count before and after running.

## Question Topics

The scripts populate these topics:
- Arithmetic
- Fractions
- Decimals
- Multiplication & Division
- Number Systems
- BODMAS
- Functions
- Probability
- Sets
- Surds
- Complex Numbers (Intro & Expanded)

Total: ~1,516 questions across 12 topics with 3 difficulty levels each.
