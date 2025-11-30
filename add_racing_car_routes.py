#!/usr/bin/env python3
"""
ADD RACING CAR ROUTES TO APP.PY
================================
This script adds the racing car feature routes to app.py.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python add_racing_car_routes.py
"""

import re
import shutil
from datetime import datetime

APP_FILE = 'app.py'

RACING_CAR_ROUTES = '''

# =====================================================
# RACING CAR CHALLENGE ROUTES
# =====================================================

@app.route('/racing-car')
@guest_or_login_required
def racing_car_page():
    """Racing Car 3D viewer page"""
    return render_template('racing_car.html')


@app.route('/api/racing-car/status')
@guest_or_login_required
def get_racing_car_status():
    """Get the user's racing car status including parts unlocked, points, next part"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    
    if not user_id and not guest_code:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get current points
    current_points = 0
    if guest_code:
        result = db.session.execute(text(
            "SELECT total_score FROM guest_users WHERE guest_code = :code"
        ), {"code": guest_code}).fetchone()
        current_points = result[0] if result else 0
    elif user_id:
        stats = UserStats.query.filter_by(user_id=user_id).first()
        current_points = stats.total_points if stats else 0
    
    # Get or create user's race car record
    try:
        if guest_code:
            car = db.session.execute(text(
                "SELECT id, user_id, guest_code, parts_unlocked, highest_points_seen, car_name, primary_color, secondary_color FROM user_race_cars WHERE guest_code = :code"
            ), {"code": guest_code}).fetchone()
            
            if not car:
                db.session.execute(text("""
                    INSERT INTO user_race_cars (guest_code, parts_unlocked, highest_points_seen, created_at, updated_at)
                    VALUES (:code, 0, :points, :now, :now)
                """), {"code": guest_code, "points": current_points, "now": datetime.utcnow()})
                db.session.commit()
                car = db.session.execute(text(
                    "SELECT id, user_id, guest_code, parts_unlocked, highest_points_seen, car_name, primary_color, secondary_color FROM user_race_cars WHERE guest_code = :code"
                ), {"code": guest_code}).fetchone()
        else:
            car = db.session.execute(text(
                "SELECT id, user_id, guest_code, parts_unlocked, highest_points_seen, car_name, primary_color, secondary_color FROM user_race_cars WHERE user_id = :uid"
            ), {"uid": user_id}).fetchone()
            
            if not car:
                db.session.execute(text("""
                    INSERT INTO user_race_cars (user_id, parts_unlocked, highest_points_seen, created_at, updated_at)
                    VALUES (:uid, 0, :points, :now, :now)
                """), {"uid": user_id, "points": current_points, "now": datetime.utcnow()})
                db.session.commit()
                car = db.session.execute(text(
                    "SELECT id, user_id, guest_code, parts_unlocked, highest_points_seen, car_name, primary_color, secondary_color FROM user_race_cars WHERE user_id = :uid"
                ), {"uid": user_id}).fetchone()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}', 'parts_unlocked': 0, 'current_points': current_points, 'all_parts': []})
    
    car_columns = ['id', 'user_id', 'guest_code', 'parts_unlocked', 'highest_points_seen', 'car_name', 'primary_color', 'secondary_color']
    car_dict = dict(zip(car_columns, car)) if car else {}
    
    # Calculate parts that should be unlocked (1 part per 1000 points)
    parts_should_have = min(50, current_points // 1000)
    current_parts = car_dict.get('parts_unlocked', 0)
    
    # Check for new unlocks
    new_unlocks = []
    if parts_should_have > current_parts:
        try:
            new_parts = db.session.execute(text("""
                SELECT part_number, part_name, category, description, points_required
                FROM car_parts
                WHERE part_number > :current AND part_number <= :new
                ORDER BY part_number
            """), {"current": current_parts, "new": parts_should_have}).fetchall()
            
            for part in new_parts:
                new_unlocks.append({
                    'part_number': part[0],
                    'part_name': part[1],
                    'category': part[2],
                    'description': part[3],
                    'points_required': part[4]
                })
                
                # Record unlock
                try:
                    if guest_code:
                        db.session.execute(text("""
                            INSERT INTO car_part_unlocks (guest_code, part_id, unlocked_at, points_at_unlock)
                            SELECT :code, id, :now, :points FROM car_parts WHERE part_number = :pnum
                        """), {"code": guest_code, "now": datetime.utcnow(), "points": current_points, "pnum": part[0]})
                    else:
                        db.session.execute(text("""
                            INSERT INTO car_part_unlocks (user_id, part_id, unlocked_at, points_at_unlock)
                            SELECT :uid, id, :now, :points FROM car_parts WHERE part_number = :pnum
                        """), {"uid": user_id, "now": datetime.utcnow(), "points": current_points, "pnum": part[0]})
                except:
                    pass
            
            # Update car record
            if guest_code:
                db.session.execute(text("""
                    UPDATE user_race_cars 
                    SET parts_unlocked = :parts, highest_points_seen = :points, updated_at = :now
                    WHERE guest_code = :code
                """), {"parts": parts_should_have, "points": current_points, "now": datetime.utcnow(), "code": guest_code})
            else:
                db.session.execute(text("""
                    UPDATE user_race_cars 
                    SET parts_unlocked = :parts, highest_points_seen = :points, updated_at = :now
                    WHERE user_id = :uid
                """), {"parts": parts_should_have, "points": current_points, "now": datetime.utcnow(), "uid": user_id})
            
            db.session.commit()
            current_parts = parts_should_have
        except Exception as e:
            print(f"Error updating parts: {e}")
    
    # Get next part
    next_part = None
    if current_parts < 50:
        try:
            next_result = db.session.execute(text("""
                SELECT part_number, part_name, category, description, points_required
                FROM car_parts WHERE part_number = :next_num
            """), {"next_num": current_parts + 1}).fetchone()
            
            if next_result:
                next_part = {
                    'part_number': next_result[0],
                    'part_name': next_result[1],
                    'category': next_result[2],
                    'description': next_result[3],
                    'points_required': next_result[4]
                }
        except:
            pass
    
    # Get all parts
    all_parts_list = []
    try:
        all_parts = db.session.execute(text("""
            SELECT part_number, part_name, category, description, points_required
            FROM car_parts ORDER BY part_number
        """)).fetchall()
        
        all_parts_list = [{
            'part_number': p[0],
            'part_name': p[1],
            'category': p[2],
            'description': p[3],
            'points_required': p[4]
        } for p in all_parts]
    except:
        pass
    
    return jsonify({
        'parts_unlocked': current_parts,
        'current_points': current_points,
        'car_name': car_dict.get('car_name') or 'Your F1 Car',
        'primary_color': car_dict.get('primary_color', '#e10600'),
        'secondary_color': car_dict.get('secondary_color', '#1e1e1e'),
        'next_part': next_part,
        'new_unlocks': new_unlocks,
        'all_parts': all_parts_list,
        'completion_percentage': round((current_parts / 50) * 100, 1)
    })


@app.route('/api/racing-car/parts')
@guest_or_login_required
def get_racing_car_parts():
    """Get the full catalog of car parts"""
    from sqlalchemy import text
    
    try:
        parts = db.session.execute(text("""
            SELECT part_number, part_name, category, description, points_required, model_component
            FROM car_parts ORDER BY part_number
        """)).fetchall()
        
        return jsonify({
            'parts': [{
                'part_number': p[0],
                'part_name': p[1],
                'category': p[2],
                'description': p[3],
                'points_required': p[4],
                'model_component': p[5]
            } for p in parts]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'parts': []})


@app.route('/api/racing-car/customize', methods=['POST'])
@guest_or_login_required
def customize_racing_car():
    """Update car name and colors"""
    from sqlalchemy import text
    import re
    
    data = request.get_json()
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    
    car_name = data.get('car_name', '')[:100]
    primary_color = data.get('primary_color', '#e10600')
    secondary_color = data.get('secondary_color', '#1e1e1e')
    
    hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
    if not hex_pattern.match(primary_color):
        primary_color = '#e10600'
    if not hex_pattern.match(secondary_color):
        secondary_color = '#1e1e1e'
    
    try:
        if guest_code:
            db.session.execute(text("""
                UPDATE user_race_cars 
                SET car_name = :name, primary_color = :pc, secondary_color = :sc, updated_at = :now
                WHERE guest_code = :code
            """), {"name": car_name, "pc": primary_color, "sc": secondary_color, 
                   "now": datetime.utcnow(), "code": guest_code})
        else:
            db.session.execute(text("""
                UPDATE user_race_cars 
                SET car_name = :name, primary_color = :pc, secondary_color = :sc, updated_at = :now
                WHERE user_id = :uid
            """), {"name": car_name, "pc": primary_color, "sc": secondary_color,
                   "now": datetime.utcnow(), "uid": user_id})
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Car customization saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# =====================================================
# END RACING CAR ROUTES
# =====================================================
'''


def main():
    print("=" * 60)
    print("🏎️ ADDING RACING CAR ROUTES TO APP.PY")
    print("=" * 60)
    
    # Backup
    backup_name = f"{APP_FILE}.backup_racing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(APP_FILE, backup_name)
    print(f"\n✓ Backup created: {backup_name}")
    
    # Read current app.py
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Check if already added
    if 'racing-car' in content:
        print("\n⚠️ Racing car routes appear to already exist in app.py")
        print("  Skipping to avoid duplicates.")
        return
    
    # Find a good insertion point (before the last if __name__ block or at end)
    if "if __name__ == '__main__':" in content:
        # Insert before the main block
        insertion_point = content.rfind("if __name__ == '__main__':")
        new_content = content[:insertion_point] + RACING_CAR_ROUTES + "\n\n" + content[insertion_point:]
    else:
        # Append to end
        new_content = content + RACING_CAR_ROUTES
    
    # Write updated content
    with open(APP_FILE, 'w') as f:
        f.write(new_content)
    
    print("\n✓ Racing car routes added to app.py")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)
    print("""
Next steps:
1. Run: python racing_car_migration.py (to create database tables)
2. Upload templates/racing_car.html
3. Reload your web app
4. Visit /racing-car to see your car!
""")


if __name__ == '__main__':
    main()
