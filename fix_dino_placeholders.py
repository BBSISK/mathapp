"""
Plan B: Use Data URL Placeholders for Dinosaurs
================================================

This creates colored placeholder images as data URLs.
These are embedded directly in the HTML so they ALWAYS work.

No external requests needed!

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python fix_dino_placeholders.py
"""

import sys
import base64
sys.path.insert(0, '/home/bbsisk/mathapp')

# Generate a simple SVG placeholder for each dinosaur
def create_dino_svg(name, color):
    """Create an SVG placeholder with dinosaur name and emoji"""
    # Escape any special characters in name
    safe_name = name.replace("'", "").replace('"', '')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1a1a2e;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bg)"/>
  <text x="200" y="100" font-size="80" text-anchor="middle" fill="white">🦕</text>
  <text x="200" y="180" font-size="24" font-family="Arial, sans-serif" text-anchor="middle" fill="white" font-weight="bold">{safe_name}</text>
  <text x="200" y="220" font-size="14" font-family="Arial, sans-serif" text-anchor="middle" fill="#aaa">Identify this dinosaur!</text>
</svg>'''
    return svg

def svg_to_data_url(svg):
    """Convert SVG to data URL"""
    # Encode as base64
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

# Different colors for variety
COLORS = [
    '#4a0e4e',  # Deep purple
    '#1e3a5f',  # Deep blue
    '#0d4d4d',  # Deep teal
    '#3d0c02',  # Deep red
    '#2d3a0c',  # Deep olive
    '#4a2c0d',  # Deep brown
    '#0c2d3a',  # Deep ocean
    '#3a0c2d',  # Deep magenta
]

def update_to_placeholders():
    from app import app, db
    from sqlalchemy import text
    
    with app.app_context():
        print("=" * 60)
        print("🦕 PLAN B: CREATE PLACEHOLDER IMAGES")
        print("=" * 60)
        print("\nGenerating SVG placeholders (no external URLs needed!)...")
        
        # Get all dinosaur questions
        questions = db.session.execute(text("""
            SELECT id, correct_answer 
            FROM bonus_questions 
            WHERE category = 'dinosaurs'
        """)).fetchall()
        
        print(f"\n📋 Found {len(questions)} dinosaur questions\n")
        
        for i, q in enumerate(questions):
            name = q.correct_answer
            color = COLORS[i % len(COLORS)]
            
            # Create SVG and convert to data URL
            svg = create_dino_svg(name, color)
            data_url = svg_to_data_url(svg)
            
            # Update database
            db.session.execute(text("""
                UPDATE bonus_questions 
                SET image_url = :url 
                WHERE id = :id
            """), {'url': data_url, 'id': q.id})
            
            print(f"✓ [{q.id}] {name}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Updated all {len(questions)} dinosaurs with placeholders!")
        print("=" * 60)
        print("\n💡 These placeholders will ALWAYS work because they're")
        print("   embedded directly in the page (no external requests).")
        print("\n   You can later replace them with real images by")
        print("   manually uploading images to static/bonus_images/")


if __name__ == '__main__':
    update_to_placeholders()
