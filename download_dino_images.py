"""
Download Dinosaur Images Script
================================

This script downloads all dinosaur images from Wikipedia URLs
and saves them locally, then updates the database to use local paths.

This fixes the "Image failed to load" issue caused by Wikipedia's
hotlink protection blocking external requests.

Usage:
    cd /home/bbsisk/mathapp
    source venv/bin/activate
    python download_dino_images.py

The script will:
1. Create a static/bonus_images/dinosaurs/ folder
2. Download each image from Wikipedia
3. Update the bonus_questions table with local paths
"""

import os
import sys
import requests
import time
from urllib.parse import urlparse

# Add the app directory to path
sys.path.insert(0, '/home/bbsisk/mathapp')

def download_images():
    from app import app, db
    from sqlalchemy import text
    
    with app.app_context():
        print("=" * 60)
        print("🦕 DINOSAUR IMAGE DOWNLOAD SCRIPT")
        print("=" * 60)
        
        # Create directory for images
        image_dir = os.path.join(app.static_folder, 'bonus_images', 'dinosaurs')
        os.makedirs(image_dir, exist_ok=True)
        print(f"\n📁 Image directory: {image_dir}")
        
        # Get all bonus questions with external URLs
        questions = db.session.execute(text("""
            SELECT id, correct_answer, image_url 
            FROM bonus_questions 
            WHERE category = 'dinosaurs'
            AND image_url LIKE 'http%'
        """)).fetchall()
        
        print(f"📋 Found {len(questions)} dinosaur questions with external URLs\n")
        
        success_count = 0
        fail_count = 0
        
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://en.wikipedia.org/'
        }
        
        for q in questions:
            question_id = q.id
            answer = q.correct_answer
            url = q.image_url
            
            # Create safe filename from answer
            safe_name = answer.lower().replace(' ', '_').replace("'", "")
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
            
            # Get file extension from URL
            parsed = urlparse(url)
            path = parsed.path
            ext = os.path.splitext(path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                ext = '.jpg'  # Default to jpg
            
            filename = f"{safe_name}{ext}"
            filepath = os.path.join(image_dir, filename)
            
            print(f"[{question_id}] {answer}")
            print(f"    URL: {url[:60]}...")
            
            # Check if already downloaded
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                print(f"    ✓ Already exists: {filename}")
                # Update database with local path
                local_url = f"/static/bonus_images/dinosaurs/{filename}"
                db.session.execute(text("""
                    UPDATE bonus_questions SET image_url = :local_url WHERE id = :id
                """), {'local_url': local_url, 'id': question_id})
                success_count += 1
                continue
            
            # Download the image
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    # Check if we got an actual image
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type or len(response.content) > 5000:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        # Update database with local path
                        local_url = f"/static/bonus_images/dinosaurs/{filename}"
                        db.session.execute(text("""
                            UPDATE bonus_questions SET image_url = :local_url WHERE id = :id
                        """), {'local_url': local_url, 'id': question_id})
                        
                        print(f"    ✓ Downloaded: {filename} ({len(response.content)} bytes)")
                        success_count += 1
                    else:
                        print(f"    ✗ Not an image (Content-Type: {content_type})")
                        fail_count += 1
                else:
                    print(f"    ✗ HTTP {response.status_code}")
                    fail_count += 1
                    
            except requests.exceptions.Timeout:
                print(f"    ✗ Timeout")
                fail_count += 1
            except Exception as e:
                print(f"    ✗ Error: {str(e)[:50]}")
                fail_count += 1
            
            # Be nice to Wikipedia servers
            time.sleep(0.5)
        
        # Commit all database changes
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE: {success_count} succeeded, {fail_count} failed")
        print("=" * 60)
        
        if fail_count > 0:
            print("\n⚠️  Some images failed to download.")
            print("You may need to manually find replacement images for those.")
            print("\nTo see which ones failed, run:")
            print("  SELECT id, correct_answer, image_url FROM bonus_questions")
            print("  WHERE category='dinosaurs' AND image_url LIKE 'http%'")


def check_status():
    """Check current status of images"""
    from app import app, db
    from sqlalchemy import text
    
    with app.app_context():
        # Count local vs external URLs
        local = db.session.execute(text("""
            SELECT COUNT(*) FROM bonus_questions 
            WHERE category = 'dinosaurs' AND image_url LIKE '/static/%'
        """)).fetchone()[0]
        
        external = db.session.execute(text("""
            SELECT COUNT(*) FROM bonus_questions 
            WHERE category = 'dinosaurs' AND image_url LIKE 'http%'
        """)).fetchone()[0]
        
        print(f"\n📊 Current Status:")
        print(f"   Local images: {local}")
        print(f"   External URLs: {external}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', action='store_true', help='Just check status')
    args = parser.parse_args()
    
    if args.status:
        check_status()
    else:
        download_images()
        check_status()
