"""
Seed script for Bonus Questions - Dinosaurs
Run this once to populate the bonus_questions table

Usage: python seed_bonus_questions.py

Images sourced from Wikimedia Commons (public domain / CC licensed)
"""

import sqlite3
import os

# Dinosaur data with high-quality Wikipedia/Wikimedia images
DINOSAURS = [
    # ==================== THEROPODS (Carnivores) ====================
    {
        "correct_answer": "Tyrannosaurus Rex",
        "option_a": "Tyrannosaurus Rex",
        "option_b": "Giganotosaurus",
        "option_c": "Carcharodontosaurus",
        "option_d": "Tarbosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/1280px-Tyrannosaurus_Rex_Holotype.jpg",
        "fun_fact": "T. Rex had the strongest bite force of any land animal ever - about 12,800 pounds, enough to crush a car!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Velociraptor",
        "option_a": "Deinonychus",
        "option_b": "Velociraptor",
        "option_c": "Utahraptor",
        "option_d": "Dromaeosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Velociraptor_Restoration.png/1280px-Velociraptor_Restoration.png",
        "fun_fact": "Real Velociraptors were only about the size of a turkey! The 'raptors' in Jurassic Park were actually based on Deinonychus.",
        "era_or_region": "Late Cretaceous, Mongolia",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Spinosaurus",
        "option_a": "Baryonyx",
        "option_b": "Suchomimus",
        "option_c": "Spinosaurus",
        "option_d": "Irritator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Spinosaurus_swimming.jpg/1280px-Spinosaurus_swimming.jpg",
        "fun_fact": "Spinosaurus is the largest carnivorous dinosaur ever discovered, even bigger than T. Rex! It was also semi-aquatic and hunted fish.",
        "era_or_region": "Late Cretaceous, North Africa",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Carnotaurus",
        "option_a": "Abelisaurus",
        "option_b": "Carnotaurus",
        "option_c": "Majungasaurus",
        "option_d": "Skorpiovenator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Carnotaurus_DB_2.jpg/1280px-Carnotaurus_DB_2.jpg",
        "fun_fact": "Carnotaurus means 'meat-eating bull' because of its distinctive horns above its eyes. It had the smallest arms of any large theropod!",
        "era_or_region": "Late Cretaceous, South America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Allosaurus",
        "option_a": "Allosaurus",
        "option_b": "Saurophaganax",
        "option_c": "Torvosaurus",
        "option_d": "Ceratosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Allosaurus_Revised.jpg/1280px-Allosaurus_Revised.jpg",
        "fun_fact": "Allosaurus was the apex predator of the Jurassic period, 150 million years ago. It may have hunted in packs to take down giant sauropods!",
        "era_or_region": "Late Jurassic, North America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Dilophosaurus",
        "option_a": "Coelophysis",
        "option_b": "Liliensternus",
        "option_c": "Dilophosaurus",
        "option_d": "Zupaysaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Dilophosaurus_wetherilli.png/1280px-Dilophosaurus_wetherilli.png",
        "fun_fact": "Despite Jurassic Park, Dilophosaurus had no frill and couldn't spit venom! It was actually 6 meters long - much bigger than shown in the movie.",
        "era_or_region": "Early Jurassic, North America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Giganotosaurus",
        "option_a": "Tyrannosaurus Rex",
        "option_b": "Mapusaurus",
        "option_c": "Giganotosaurus",
        "option_d": "Acrocanthosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Giganotosaurus_carolinii_by_Paleocolour.jpg/1280px-Giganotosaurus_carolinii_by_Paleocolour.jpg",
        "fun_fact": "Giganotosaurus from Argentina was slightly longer than T. Rex but had a smaller brain. Its name means 'giant southern lizard'!",
        "era_or_region": "Late Cretaceous, South America",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Therizinosaurus",
        "option_a": "Deinocheirus",
        "option_b": "Therizinosaurus",
        "option_c": "Nothronychus",
        "option_d": "Segnosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Therizinosaurus_IGM_100_15.png/1280px-Therizinosaurus_IGM_100_15.png",
        "fun_fact": "Therizinosaurus had the longest claws of any animal ever - up to 1 meter long! Despite looking scary, it was actually a herbivore.",
        "era_or_region": "Late Cretaceous, Mongolia",
        "difficulty": "hard"
    },
    
    # ==================== SAUROPODS (Long-necked herbivores) ====================
    {
        "correct_answer": "Brachiosaurus",
        "option_a": "Brachiosaurus",
        "option_b": "Giraffatitan",
        "option_c": "Camarasaurus",
        "option_d": "Sauroposeidon",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Brachiosaurus_DB.jpg/1280px-Brachiosaurus_DB.jpg",
        "fun_fact": "Brachiosaurus held its neck upright like a giraffe! It was so tall it could look into a 4th floor window. Its nostrils were on top of its head.",
        "era_or_region": "Late Jurassic, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Diplodocus",
        "option_a": "Apatosaurus",
        "option_b": "Diplodocus",
        "option_c": "Barosaurus",
        "option_d": "Supersaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Diplodocus_carnegii.jpg/1280px-Diplodocus_carnegii.jpg",
        "fun_fact": "Diplodocus was one of the longest dinosaurs at 27 meters! Its tail could crack like a whip at supersonic speeds.",
        "era_or_region": "Late Jurassic, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Argentinosaurus",
        "option_a": "Patagotitan",
        "option_b": "Dreadnoughtus",
        "option_c": "Argentinosaurus",
        "option_d": "Futalognkosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Argentinosaurus_DSC_2943.jpg/1280px-Argentinosaurus_DSC_2943.jpg",
        "fun_fact": "Argentinosaurus may be the heaviest land animal ever - weighing up to 100 tons! That's as heavy as 14 elephants.",
        "era_or_region": "Late Cretaceous, South America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Brontosaurus",
        "option_a": "Apatosaurus",
        "option_b": "Brontosaurus",
        "option_c": "Diplodocus",
        "option_d": "Camarasaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Brontosaurus_by_Tom_Parker.png/1280px-Brontosaurus_by_Tom_Parker.png",
        "fun_fact": "For over 100 years, scientists thought Brontosaurus was the same as Apatosaurus. In 2015, it was officially recognized as its own species again!",
        "era_or_region": "Late Jurassic, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Amargasaurus",
        "option_a": "Dicraeosaurus",
        "option_b": "Amargasaurus",
        "option_c": "Nigersaurus",
        "option_d": "Rebbachisaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Amargasaurus_BW.jpg/1280px-Amargasaurus_BW.jpg",
        "fun_fact": "Amargasaurus had two rows of tall spines along its neck that may have supported a sail or made sounds to communicate!",
        "era_or_region": "Early Cretaceous, South America",
        "difficulty": "hard"
    },
    
    # ==================== CERATOPSIANS (Horned dinosaurs) ====================
    {
        "correct_answer": "Triceratops",
        "option_a": "Triceratops",
        "option_b": "Torosaurus",
        "option_c": "Chasmosaurus",
        "option_d": "Pentaceratops",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Triceratops_Restoration.png/1280px-Triceratops_Restoration.png",
        "fun_fact": "Triceratops' horns could be over 1 meter long! Its skull alone was one-third of its entire body length.",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Styracosaurus",
        "option_a": "Centrosaurus",
        "option_b": "Styracosaurus",
        "option_c": "Einiosaurus",
        "option_d": "Achelousaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Styracosaurus_BW.jpg/1280px-Styracosaurus_BW.jpg",
        "fun_fact": "Styracosaurus had one of the most spectacular frills, with 6 long spikes. Its name means 'spiked lizard'!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Pachyrhinosaurus",
        "option_a": "Achelousaurus",
        "option_b": "Einiosaurus",
        "option_c": "Pachyrhinosaurus",
        "option_d": "Centrosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Pachyrhinosaurus_BW.jpg/1280px-Pachyrhinosaurus_BW.jpg",
        "fun_fact": "Instead of a nose horn, Pachyrhinosaurus had a massive bony boss (bump) on its nose that it may have used for head-butting!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Protoceratops",
        "option_a": "Leptoceratops",
        "option_b": "Protoceratops",
        "option_c": "Psittacosaurus",
        "option_d": "Bagaceratops",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Protoceratops_BW.jpg/1280px-Protoceratops_BW.jpg",
        "fun_fact": "A famous fossil shows a Protoceratops and Velociraptor locked in combat - they died fighting and were buried together!",
        "era_or_region": "Late Cretaceous, Mongolia",
        "difficulty": "medium"
    },
    
    # ==================== ANKYLOSAURS (Armored dinosaurs) ====================
    {
        "correct_answer": "Ankylosaurus",
        "option_a": "Euoplocephalus",
        "option_b": "Ankylosaurus",
        "option_c": "Nodosaurus",
        "option_d": "Tarchia",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Ankylosaurus_magniventris_reconstruction.png/1280px-Ankylosaurus_magniventris_reconstruction.png",
        "fun_fact": "Ankylosaurus' tail club could swing with enough force to break a T. Rex's leg! Even its eyelids were armored.",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Euoplocephalus",
        "option_a": "Ankylosaurus",
        "option_b": "Scolosaurus",
        "option_c": "Euoplocephalus",
        "option_d": "Dyoplosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Euoplocephalus_tutus.jpg/1280px-Euoplocephalus_tutus.jpg",
        "fun_fact": "Euoplocephalus means 'well-armored head'. It had bony armor covering most of its body and even had armored eyelids!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Nodosaurus",
        "option_a": "Edmontonia",
        "option_b": "Sauropelta",
        "option_c": "Nodosaurus",
        "option_d": "Pawpawsaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Nodosaurus_NT_small.jpg/1280px-Nodosaurus_NT_small.jpg",
        "fun_fact": "Unlike Ankylosaurus, Nodosaurus had no tail club. Instead, it relied on its heavily armored body and shoulder spikes for defense!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "hard"
    },
    
    # ==================== STEGOSAURS (Plated dinosaurs) ====================
    {
        "correct_answer": "Stegosaurus",
        "option_a": "Stegosaurus",
        "option_b": "Kentrosaurus",
        "option_c": "Tuojiangosaurus",
        "option_d": "Huayangosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Stegosaurus_BW.jpg/1280px-Stegosaurus_BW.jpg",
        "fun_fact": "Stegosaurus had a brain the size of a walnut - one of the smallest brain-to-body ratios of any dinosaur! Its plates may have helped regulate body temperature.",
        "era_or_region": "Late Jurassic, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Kentrosaurus",
        "option_a": "Stegosaurus",
        "option_b": "Kentrosaurus",
        "option_c": "Gigantspinosaurus",
        "option_d": "Chungkingosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Kentrosaurus_aethiopicus.jpg/1280px-Kentrosaurus_aethiopicus.jpg",
        "fun_fact": "Kentrosaurus from Africa had more spikes than Stegosaurus - spikes ran from its shoulders all the way down its tail!",
        "era_or_region": "Late Jurassic, Africa",
        "difficulty": "hard"
    },
    
    # ==================== HADROSAURS (Duck-billed dinosaurs) ====================
    {
        "correct_answer": "Parasaurolophus",
        "option_a": "Corythosaurus",
        "option_b": "Parasaurolophus",
        "option_c": "Lambeosaurus",
        "option_d": "Hypacrosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Parasaurolophus_cyrtocristatus.jpg/1280px-Parasaurolophus_cyrtocristatus.jpg",
        "fun_fact": "Parasaurolophus' crest was hollow and connected to its nose - it could produce deep, foghorn-like calls to communicate!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Corythosaurus",
        "option_a": "Parasaurolophus",
        "option_b": "Lambeosaurus",
        "option_c": "Corythosaurus",
        "option_d": "Olorotitan",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Corythosaurus_BW.jpg/1280px-Corythosaurus_BW.jpg",
        "fun_fact": "Corythosaurus' helmet-shaped crest gave it its name, which means 'helmet lizard'. It had up to 300 teeth for grinding plants!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Edmontosaurus",
        "option_a": "Maiasaura",
        "option_b": "Hadrosaurus",
        "option_c": "Edmontosaurus",
        "option_d": "Shantungosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Edmontosaurus_BW.jpg/1280px-Edmontosaurus_BW.jpg",
        "fun_fact": "A mummified Edmontosaurus was found with preserved skin, revealing it had a fleshy comb on its head like a rooster!",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Iguanodon",
        "option_a": "Mantellisaurus",
        "option_b": "Iguanodon",
        "option_c": "Ouranosaurus",
        "option_d": "Lurdusaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Iguanodon_NT.jpg/1280px-Iguanodon_NT.jpg",
        "fun_fact": "Iguanodon was one of the first dinosaurs ever discovered! Its thumb spike was originally thought to be a nose horn.",
        "era_or_region": "Early Cretaceous, Europe",
        "difficulty": "medium"
    },
    
    # ==================== PACHYCEPHALOSAURS (Dome-headed dinosaurs) ====================
    {
        "correct_answer": "Pachycephalosaurus",
        "option_a": "Stygimoloch",
        "option_b": "Pachycephalosaurus",
        "option_c": "Dracorex",
        "option_d": "Prenocephale",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Pachycephalosaurus_wyomingensis.png/1280px-Pachycephalosaurus_wyomingensis.png",
        "fun_fact": "Pachycephalosaurus' skull was 25cm thick! Scientists debate whether they head-butted like rams or used their heads for display.",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "medium"
    },
    
    # ==================== ORNITHOMIMIDS (Ostrich-like dinosaurs) ====================
    {
        "correct_answer": "Gallimimus",
        "option_a": "Ornithomimus",
        "option_b": "Struthiomimus",
        "option_c": "Gallimimus",
        "option_d": "Dromiceiomimus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Gallimimus_Steveoc86.jpg/1280px-Gallimimus_Steveoc86.jpg",
        "fun_fact": "Gallimimus was one of the fastest dinosaurs, running at speeds up to 70 km/h! It was toothless and probably ate plants, insects, and small animals.",
        "era_or_region": "Late Cretaceous, Mongolia",
        "difficulty": "medium"
    },
    
    # ==================== PTEROSAURS (Flying reptiles - technically not dinosaurs but often grouped) ====================
    {
        "correct_answer": "Pteranodon",
        "option_a": "Pteranodon",
        "option_b": "Pterodactylus",
        "option_c": "Quetzalcoatlus",
        "option_d": "Rhamphorhynchus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Pteranodon_longiceps_mmartyniuk_wiki.png/1280px-Pteranodon_longiceps_mmartyniuk_wiki.png",
        "fun_fact": "Pteranodon had a wingspan of up to 7 meters but weighed only about 25kg! Its iconic crest may have been used for steering in flight.",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "easy"
    },
    {
        "correct_answer": "Quetzalcoatlus",
        "option_a": "Hatzegopteryx",
        "option_b": "Quetzalcoatlus",
        "option_c": "Pteranodon",
        "option_d": "Tupuxuara",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Quetzalcoatlus_sp.jpg/1280px-Quetzalcoatlus_sp.jpg",
        "fun_fact": "Quetzalcoatlus was the largest flying animal ever, with a wingspan of 10-11 meters - as big as a small airplane! Standing, it was as tall as a giraffe.",
        "era_or_region": "Late Cretaceous, North America",
        "difficulty": "medium"
    },
    
    # ==================== MARINE REPTILES (Not dinosaurs but often grouped) ====================
    {
        "correct_answer": "Mosasaurus",
        "option_a": "Tylosaurus",
        "option_b": "Mosasaurus",
        "option_c": "Prognathodon",
        "option_d": "Hainosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Mosasaurus_beaugei1DB.jpg/1280px-Mosasaurus_beaugei1DB.jpg",
        "fun_fact": "Mosasaurus was a giant marine lizard that could grow up to 17 meters long! It was the apex predator of Late Cretaceous seas.",
        "era_or_region": "Late Cretaceous, Worldwide",
        "difficulty": "medium"
    },
    {
        "correct_answer": "Plesiosaurus",
        "option_a": "Elasmosaurus",
        "option_b": "Plesiosaurus",
        "option_c": "Cryptoclidus",
        "option_d": "Muraenosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Plesiosaurus_dolichodeirus.png/1280px-Plesiosaurus_dolichodeirus.png",
        "fun_fact": "Plesiosaurus couldn't turn its head back to bite - instead, it swung its long neck from side to side to catch fish!",
        "era_or_region": "Early Jurassic, Europe",
        "difficulty": "medium"
    },
    
    # ==================== MORE THEROPODS ====================
    {
        "correct_answer": "Baryonyx",
        "option_a": "Spinosaurus",
        "option_b": "Suchomimus",
        "option_c": "Baryonyx",
        "option_d": "Irritator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Baryonyx_walkeri_restoration.png/1280px-Baryonyx_walkeri_restoration.png",
        "fun_fact": "Baryonyx was discovered with fish scales in its stomach! Its name means 'heavy claw' after its 30cm thumb claw used for fishing.",
        "era_or_region": "Early Cretaceous, Europe",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Oviraptor",
        "option_a": "Citipati",
        "option_b": "Oviraptor",
        "option_c": "Khaan",
        "option_d": "Conchoraptor",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Oviraptor_philoceratops_restoration.png/1280px-Oviraptor_philoceratops_restoration.png",
        "fun_fact": "Oviraptor means 'egg thief' but this is unfair! It was found on a nest of eggs that were actually its own - it was protecting them, not stealing!",
        "era_or_region": "Late Cretaceous, Mongolia",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Deinonychus",
        "option_a": "Velociraptor",
        "option_b": "Deinonychus",
        "option_c": "Utahraptor",
        "option_d": "Achillobator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Deinonychus_BW-2.png/1280px-Deinonychus_BW-2.png",
        "fun_fact": "Deinonychus is the dinosaur the Jurassic Park 'Velociraptors' are actually based on! It was 3.4 meters long with a deadly sickle claw.",
        "era_or_region": "Early Cretaceous, North America",
        "difficulty": "hard"
    },
    {
        "correct_answer": "Compsognathus",
        "option_a": "Sinosauropteryx",
        "option_b": "Compsognathus",
        "option_c": "Juravenator",
        "option_d": "Scipionyx",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Compsognathus_BW.jpg/1280px-Compsognathus_BW.jpg",
        "fun_fact": "Compsognathus was one of the smallest dinosaurs - only about the size of a chicken! For over 100 years, it was considered the smallest dinosaur.",
        "era_or_region": "Late Jurassic, Europe",
        "difficulty": "hard"
    },
    
    # ==================== EARLY DINOSAURS ====================
    {
        "correct_answer": "Coelophysis",
        "option_a": "Herrerasaurus",
        "option_b": "Coelophysis",
        "option_c": "Eoraptor",
        "option_d": "Staurikosaurus",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Coelophysis_size.jpg/1280px-Coelophysis_size.jpg",
        "fun_fact": "Thousands of Coelophysis fossils were found at Ghost Ranch, New Mexico - one of the largest dinosaur fossil sites ever discovered!",
        "era_or_region": "Late Triassic, North America",
        "difficulty": "hard"
    },
]


def seed_database():
    """Insert dinosaur questions into the database"""
    
    # Find the database
    db_paths = [
        'mathquiz.db',
        'instance/mathquiz.db',
        '../mathquiz.db',
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database not found! Make sure you run this from the mathapp directory.")
        print("   Looked in: " + ", ".join(db_paths))
        return False
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bonus_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            image_url TEXT NOT NULL,
            fun_fact TEXT,
            difficulty TEXT DEFAULT 'medium',
            era_or_region TEXT,
            is_active INTEGER DEFAULT 1,
            times_shown INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attempts table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bonus_question_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            user_id INTEGER,
            guest_code TEXT,
            selected_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            points_earned INTEGER DEFAULT 0,
            quiz_topic TEXT,
            quiz_score INTEGER,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES bonus_questions(id)
        )
    """)
    
    # Check existing count
    cursor.execute("SELECT COUNT(*) FROM bonus_questions WHERE category = 'dinosaurs'")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing dinosaur questions.")
        response = input("   Do you want to delete them and re-seed? (y/N): ")
        if response.lower() == 'y':
            cursor.execute("DELETE FROM bonus_questions WHERE category = 'dinosaurs'")
            print("   Deleted existing questions.")
        else:
            print("   Keeping existing questions. Skipping seed.")
            conn.close()
            return True
    
    # Insert dinosaurs
    inserted = 0
    for dino in DINOSAURS:
        try:
            cursor.execute("""
                INSERT INTO bonus_questions 
                (category, correct_answer, option_a, option_b, option_c, option_d, 
                 image_url, fun_fact, difficulty, era_or_region)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'dinosaurs',
                dino['correct_answer'],
                dino['option_a'],
                dino['option_b'],
                dino['option_c'],
                dino['option_d'],
                dino['image_url'],
                dino['fun_fact'],
                dino.get('difficulty', 'medium'),
                dino.get('era_or_region', '')
            ))
            inserted += 1
        except Exception as e:
            print(f"   ❌ Error inserting {dino['correct_answer']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully inserted {inserted} dinosaur questions!")
    print(f"   Categories: dinosaurs")
    print(f"   Difficulty breakdown:")
    
    easy = sum(1 for d in DINOSAURS if d.get('difficulty') == 'easy')
    medium = sum(1 for d in DINOSAURS if d.get('difficulty', 'medium') == 'medium')
    hard = sum(1 for d in DINOSAURS if d.get('difficulty') == 'hard')
    print(f"     Easy: {easy}")
    print(f"     Medium: {medium}")
    print(f"     Hard: {hard}")
    
    return True


if __name__ == '__main__':
    print("🦕 AgentMath Bonus Questions Seeder")
    print("=" * 40)
    seed_database()
