#!/usr/bin/env python3
"""
BONUS QUESTIONS DATABASE MIGRATION
===================================
This script creates the bonus_questions and bonus_question_attempts tables
and seeds them with initial dinosaur questions.

Run this on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python create_bonus_questions_tables.py
"""

import sqlite3
import os
from datetime import datetime

# Path to database
DB_PATH = 'instance/mathquiz.db'

def create_tables():
    """Create the bonus_questions and bonus_question_attempts tables"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='bonus_questions'
    """)
    
    if cursor.fetchone():
        print("⚠ bonus_questions table already exists!")
        conn.close()
        return False
    
    print("Creating bonus_questions table...")
    cursor.execute("""
        CREATE TABLE bonus_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(50) NOT NULL,
            correct_answer VARCHAR(100) NOT NULL,
            option_a VARCHAR(100) NOT NULL,
            option_b VARCHAR(100) NOT NULL,
            option_c VARCHAR(100) NOT NULL,
            option_d VARCHAR(100) NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            fun_fact TEXT,
            difficulty VARCHAR(20) DEFAULT 'medium',
            era_or_region VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            times_shown INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created bonus_questions table")
    
    print("Creating bonus_question_attempts table...")
    cursor.execute("""
        CREATE TABLE bonus_question_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            user_id INTEGER,
            guest_code VARCHAR(20),
            selected_answer VARCHAR(100) NOT NULL,
            is_correct BOOLEAN NOT NULL,
            points_earned INTEGER DEFAULT 0,
            quiz_topic VARCHAR(50),
            quiz_score INTEGER,
            attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES bonus_questions(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✓ Created bonus_question_attempts table")
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_bonus_q_category ON bonus_questions(category)")
    cursor.execute("CREATE INDEX idx_bonus_q_active ON bonus_questions(is_active)")
    cursor.execute("CREATE INDEX idx_bonus_attempts_user ON bonus_question_attempts(user_id)")
    cursor.execute("CREATE INDEX idx_bonus_attempts_guest ON bonus_question_attempts(guest_code)")
    print("✓ Created indexes")
    
    conn.commit()
    conn.close()
    return True

def seed_dinosaur_questions():
    """Add initial dinosaur questions"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if we already have dinosaur questions
    cursor.execute("SELECT COUNT(*) FROM bonus_questions WHERE category = 'dinosaurs'")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"⚠ Already have {count} dinosaur questions, skipping seed")
        conn.close()
        return
    
    print("Seeding dinosaur questions...")
    
    # Dinosaur questions with Wikipedia/Wikimedia Commons images (public domain)
    dinosaurs = [
        {
            'correct_answer': 'Tyrannosaurus Rex',
            'option_a': 'Tyrannosaurus Rex',
            'option_b': 'Allosaurus',
            'option_c': 'Spinosaurus',
            'option_d': 'Carnotaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/1280px-Tyrannosaurus_Rex_Holotype.jpg',
            'fun_fact': 'T-Rex had the strongest bite of any land animal ever! Its bite force was over 12,000 pounds.',
            'difficulty': 'easy',
            'era_or_region': 'Late Cretaceous, North America'
        },
        {
            'correct_answer': 'Triceratops',
            'option_a': 'Stegosaurus',
            'option_b': 'Triceratops',
            'option_c': 'Pachycephalosaurus',
            'option_d': 'Ankylosaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Triceratops_mount.jpg/1280px-Triceratops_mount.jpg',
            'fun_fact': 'Triceratops means "three-horned face"! They used their horns for defense against T-Rex.',
            'difficulty': 'easy',
            'era_or_region': 'Late Cretaceous, North America'
        },
        {
            'correct_answer': 'Stegosaurus',
            'option_a': 'Ankylosaurus',
            'option_b': 'Triceratops',
            'option_c': 'Stegosaurus',
            'option_d': 'Kentrosaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Stegosaurus_stenops_Life_Restoration.png/1280px-Stegosaurus_stenops_Life_Restoration.png',
            'fun_fact': 'Stegosaurus had a brain the size of a walnut! But it had a second "brain" near its tail.',
            'difficulty': 'easy',
            'era_or_region': 'Late Jurassic, North America'
        },
        {
            'correct_answer': 'Velociraptor',
            'option_a': 'Deinonychus',
            'option_b': 'Velociraptor',
            'option_c': 'Utahraptor',
            'option_d': 'Oviraptor',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Velociraptor_Fighting_Dinosaur.jpg/1280px-Velociraptor_Fighting_Dinosaur.jpg',
            'fun_fact': 'Real Velociraptors were only about the size of a turkey! The ones in movies are based on larger relatives.',
            'difficulty': 'medium',
            'era_or_region': 'Late Cretaceous, Mongolia'
        },
        {
            'correct_answer': 'Brachiosaurus',
            'option_a': 'Diplodocus',
            'option_b': 'Apatosaurus',
            'option_c': 'Brachiosaurus',
            'option_d': 'Argentinosaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Brachiosaurus_mounted_front_view.jpg/800px-Brachiosaurus_mounted_front_view.jpg',
            'fun_fact': 'Brachiosaurus could reach 40 feet high - as tall as a 4-story building! It needed to eat 400 pounds of plants daily.',
            'difficulty': 'medium',
            'era_or_region': 'Late Jurassic, North America'
        },
        {
            'correct_answer': 'Pteranodon',
            'option_a': 'Pterodactyl',
            'option_b': 'Pteranodon',
            'option_c': 'Quetzalcoatlus',
            'option_d': 'Dimorphodon',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Pteranodon_longiceps.jpg/1280px-Pteranodon_longiceps.jpg',
            'fun_fact': 'Pteranodon wasn\'t actually a dinosaur - it was a flying reptile! Its wingspan was up to 23 feet.',
            'difficulty': 'medium',
            'era_or_region': 'Late Cretaceous, North America'
        },
        {
            'correct_answer': 'Spinosaurus',
            'option_a': 'Baryonyx',
            'option_b': 'Suchomimus',
            'option_c': 'Spinosaurus',
            'option_d': 'Irritator',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Spinosaurus_skeleton.jpg/1280px-Spinosaurus_skeleton.jpg',
            'fun_fact': 'Spinosaurus was even bigger than T-Rex! It\'s the largest carnivorous dinosaur ever discovered, at up to 59 feet long.',
            'difficulty': 'medium',
            'era_or_region': 'Mid Cretaceous, North Africa'
        },
        {
            'correct_answer': 'Ankylosaurus',
            'option_a': 'Euoplocephalus',
            'option_b': 'Nodosaurus',
            'option_c': 'Ankylosaurus',
            'option_d': 'Polacanthus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ankylosaur_head_-_cast_-_Senckenberg_Museum_-_Frankfurt.jpg/1280px-Ankylosaur_head_-_cast_-_Senckenberg_Museum_-_Frankfurt.jpg',
            'fun_fact': 'Ankylosaurus was like a living tank! Its tail club could break the bones of a T-Rex.',
            'difficulty': 'hard',
            'era_or_region': 'Late Cretaceous, North America'
        },
        {
            'correct_answer': 'Parasaurolophus',
            'option_a': 'Corythosaurus',
            'option_b': 'Lambeosaurus',
            'option_c': 'Parasaurolophus',
            'option_d': 'Hadrosaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Parasaurolophus_cyrtocristatus.jpg/1280px-Parasaurolophus_cyrtocristatus.jpg',
            'fun_fact': 'Parasaurolophus used its hollow crest like a trumpet to make sounds that could travel for miles!',
            'difficulty': 'hard',
            'era_or_region': 'Late Cretaceous, North America'
        },
        {
            'correct_answer': 'Dilophosaurus',
            'option_a': 'Dilophosaurus',
            'option_b': 'Coelophysis',
            'option_c': 'Ceratosaurus',
            'option_d': 'Megalosaurus',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Dilophosaurus_wetherilli.jpg/1280px-Dilophosaurus_wetherilli.jpg',
            'fun_fact': 'Unlike in Jurassic Park, Dilophosaurus couldn\'t spit venom and didn\'t have a frill! It was also much bigger in real life.',
            'difficulty': 'hard',
            'era_or_region': 'Early Jurassic, North America'
        }
    ]
    
    for dino in dinosaurs:
        cursor.execute("""
            INSERT INTO bonus_questions 
            (category, correct_answer, option_a, option_b, option_c, option_d, 
             image_url, fun_fact, difficulty, era_or_region, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            'dinosaurs',
            dino['correct_answer'],
            dino['option_a'],
            dino['option_b'],
            dino['option_c'],
            dino['option_d'],
            dino['image_url'],
            dino['fun_fact'],
            dino['difficulty'],
            dino['era_or_region']
        ))
    
    conn.commit()
    print(f"✓ Added {len(dinosaurs)} dinosaur questions")
    
    conn.close()

def verify_tables():
    """Verify the tables were created correctly"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check bonus_questions
    cursor.execute("SELECT COUNT(*) FROM bonus_questions")
    q_count = cursor.fetchone()[0]
    
    # Check table structure
    cursor.execute("PRAGMA table_info(bonus_questions)")
    columns = cursor.fetchall()
    
    print(f"\n✓ bonus_questions table has {q_count} questions")
    print(f"✓ Table has {len(columns)} columns")
    
    # Show sample question
    cursor.execute("SELECT correct_answer, difficulty FROM bonus_questions LIMIT 3")
    samples = cursor.fetchall()
    print("\nSample questions:")
    for sample in samples:
        print(f"  - {sample[0]} ({sample[1]})")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("BONUS QUESTIONS DATABASE MIGRATION")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("Make sure you're running this from the mathapp directory")
        exit(1)
    
    print(f"✓ Found database at {DB_PATH}")
    
    # Create tables
    tables_created = create_tables()
    
    # Seed questions (only if tables were just created or empty)
    if tables_created:
        seed_dinosaur_questions()
    else:
        # Check if we need to seed anyway
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bonus_questions")
        if cursor.fetchone()[0] == 0:
            conn.close()
            seed_dinosaur_questions()
        else:
            conn.close()
    
    # Verify
    verify_tables()
    
    print("\n" + "=" * 50)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 50)
    print("\nThe Dino Challenge should now work.")
    print("Test by completing a quiz with 80%+ score.")
