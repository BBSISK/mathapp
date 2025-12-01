"""
Update Database with Barry's Dinosaur Images - FINAL VERSION
=============================================================

All filenames matched exactly to your uploads.

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python update_dino_final.py
"""

import sys
sys.path.insert(0, '/home/bbsisk/mathapp')

# Exact mapping: Database name -> Your uploaded filename
DINOSAUR_MAPPING = {
    'Tyrannosaurus Rex': 'tyrannosaurus_rex.jpg',
    'Velociraptor': 'Velociraptor.jpg',
    'Spinosaurus': 'Spinosaurus.jpg',
    'Carnotaurus': 'Carnotaurus.jpg',
    'Allosaurus': 'allosaurus.jpg',
    'Dilophosaurus': 'Dilophosaurus.jpg',
    'Giganotosaurus': 'Giganotosaurus.jpg',
    'Therizinosaurus': 'Therizinosaurus.jpg',
    'Brachiosaurus': 'brachiosaurus.jpg',
    'Diplodocus': 'diplodocus.jpg',
    'Argentinosaurus': 'Argentinosaurus.jpg',
    'Brontosaurus': 'brontosaurus.jpg',
    'Amargasaurus': 'amargasaurus.jpg',
    'Triceratops': 'Triceratops.jpg',
    'Styracosaurus': 'Styracosaurus.jpg',
    'Pachyrhinosaurus': 'pachyrhinosaurus.jpg',
    'Protoceratops': None,  # Not uploaded - will need to add or skip
    'Ankylosaurus': 'Ankylosaurus.jpg',
    'Euoplocephalus': 'Euoplocephalus.jpg',
    'Nodosaurus': 'nodosaurus.jpg',
    'Stegosaurus': 'Stegosaurus.jpg',
    'Kentrosaurus': 'Kentrosaurus.jpg',
    'Parasaurolophus': 'Parasaurolophus.jpg',
    'Corythosaurus': None,  # Not uploaded - will need to add or skip
    'Edmontosaurus': 'Edmontosaurus.jpg',
    'Iguanodon': 'Iguanodon.jpg',
    'Pachycephalosaurus': 'Pachycephalosaurus.jpg',
    'Gallimimus': 'Gallimimus.jpg',
    'Pteranodon': 'pteranodon.jpg',
    'Quetzalcoatlus': 'quetzalcoatlus.jpg',
    'Mosasaurus': 'mosasaurus.jpg',
    'Plesiosaurus': 'plesiosaurus.jpg',
    'Baryonyx': 'Baryonyx.jpg',
    'Oviraptor': None,  # Not uploaded - will need to add or skip
    'Deinonychus': 'Deinonychus.jpg',
    'Compsognathus': 'compsognathus.jpg',
    'Coelophysis': 'Coelophysis.jpg',
}

# Your extra uploads that could be added as new questions later:
# archaeopteryx.jpg, Ceratosaurus.jpg, Deinocheirus.jpg, Maiasaura.jpg,
# Mamenchisaurus.jpg, Megalosaurus.jpg, Microraptor.jpg, Ornithomimus.jpg,
# Ouranosaurus.jpg, Plateosaurus.jpg, Shunosaurus.jpg, Torvosaurus.jpg,
# Tyrannosaurus.jpg, Utahraptor.jpg


def update_database():
    from app import app, db
    from sqlalchemy import text
    
    with app.app_context():
        print("=" * 60)
        print("🦕 FINAL UPDATE: DINOSAUR IMAGES")
        print("=" * 60)
        
        # Get all dinosaur questions
        questions = db.session.execute(text("""
            SELECT id, correct_answer, image_url 
            FROM bonus_questions 
            WHERE category = 'dinosaurs'
        """)).fetchall()
        
        print(f"\n📋 Found {len(questions)} dinosaur questions\n")
        
        updated = 0
        missing = []
        
        for q in questions:
            name = q.correct_answer
            
            if name in DINOSAUR_MAPPING and DINOSAUR_MAPPING[name]:
                filename = DINOSAUR_MAPPING[name]
                new_url = f"/static/bonus_images/dinosaurs/{filename}"
                
                db.session.execute(text("""
                    UPDATE bonus_questions 
                    SET image_url = :url 
                    WHERE id = :id
                """), {'url': new_url, 'id': q.id})
                
                print(f"✓ [{q.id}] {name} → {filename}")
                updated += 1
            else:
                print(f"✗ [{q.id}] {name} → NO IMAGE")
                missing.append((q.id, name))
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Updated {updated} of {len(questions)} dinosaurs!")
        print("=" * 60)
        
        if missing:
            print(f"\n⚠️  Missing {len(missing)} images:")
            for qid, name in missing:
                print(f"   - ID {qid}: {name}")
            print("\n💡 Options for missing dinosaurs:")
            print("   1. Add images: protoceratops.jpg, corythosaurus.jpg, oviraptor.jpg")
            print("   2. Or disable these questions in admin dashboard")
        
        print("\n🧪 Test at: https://bbsisk.pythonanywhere.com/test-dino-image")
        print("=" * 60)


if __name__ == '__main__':
    update_database()
