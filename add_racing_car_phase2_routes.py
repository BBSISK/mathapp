#!/usr/bin/env python3
"""
ADD RACING CAR PHASE 2 ROUTES TO APP.PY
========================================
Adds the upgrade shop routes to app.py.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python add_racing_car_phase2_routes.py
"""

import shutil
from datetime import datetime

APP_FILE = 'app.py'

PHASE2_ROUTES = '''

# =====================================================
# RACING CAR PHASE 2 - UPGRADE SHOP ROUTES
# =====================================================

UPGRADE_BUDGET = 20000  # Maximum points user can spend on upgrades


@app.route('/api/racing-car/upgrades')
@guest_or_login_required
def get_racing_car_upgrades():
    """Get all available upgrades and user's current purchases"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    
    if not user_id and not guest_code:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # TEST MODE: Allow ?test=upgrades to bypass car completion check
    test_mode = request.args.get('test') == 'upgrades'
    
    # Check if car is complete (50 parts)
    parts_unlocked = 0
    budget_used = 0
    
    try:
        if guest_code:
            car = db.session.execute(text(
                "SELECT parts_unlocked, upgrade_budget_used FROM user_race_cars WHERE guest_code = :code"
            ), {"code": guest_code}).fetchone()
            
            # Create car record if doesn't exist
            if not car:
                db.session.execute(text("""
                    INSERT INTO user_race_cars (guest_code, parts_unlocked, highest_points_seen, upgrade_budget_used, created_at, updated_at)
                    VALUES (:code, 0, 0, 0, :now, :now)
                """), {"code": guest_code, "now": datetime.utcnow()})
                db.session.commit()
                car = (0, 0)
        else:
            car = db.session.execute(text(
                "SELECT parts_unlocked, upgrade_budget_used FROM user_race_cars WHERE user_id = :uid"
            ), {"uid": user_id}).fetchone()
            
            # Create car record if doesn't exist
            if not car:
                db.session.execute(text("""
                    INSERT INTO user_race_cars (user_id, parts_unlocked, highest_points_seen, upgrade_budget_used, created_at, updated_at)
                    VALUES (:uid, 0, 0, 0, :now, :now)
                """), {"uid": user_id, "now": datetime.utcnow()})
                db.session.commit()
                car = (0, 0)
        
        parts_unlocked = car[0] or 0
        budget_used = car[1] or 0
        
        # Allow access if car complete OR test mode
        if parts_unlocked < 50 and not test_mode:
            return jsonify({
                'car_complete': False,
                'parts_unlocked': parts_unlocked,
                'parts_needed': 50 - parts_unlocked,
                'message': f'Complete your car first! {50 - parts_unlocked} parts remaining.'
            })
    except Exception as e:
        # In test mode, continue even if there's a car record issue
        if not test_mode:
            return jsonify({'error': str(e), 'car_complete': False})
    
    # Get all upgrades
    try:
        upgrades = db.session.execute(text("""
            SELECT id, upgrade_number, category, name, description, cost, performance_boost, icon, stat_key
            FROM car_upgrades ORDER BY category, upgrade_number
        """)).fetchall()
    except Exception as e:
        return jsonify({'error': f'Failed to load upgrades: {str(e)}', 'car_complete': True})
    
    # Get user's purchased upgrades
    try:
        if guest_code:
            purchased = db.session.execute(text(
                "SELECT upgrade_id FROM user_car_upgrades WHERE guest_code = :code"
            ), {"code": guest_code}).fetchall()
        else:
            purchased = db.session.execute(text(
                "SELECT upgrade_id FROM user_car_upgrades WHERE user_id = :uid"
            ), {"uid": user_id}).fetchall()
        purchased_ids = [p[0] for p in purchased]
    except:
        purchased_ids = []
    
    # Format upgrades by category
    upgrades_by_category = {}
    total_boost = 0
    
    for u in upgrades:
        cat = u[2]
        if cat not in upgrades_by_category:
            upgrades_by_category[cat] = []
        
        is_owned = u[0] in purchased_ids
        if is_owned:
            total_boost += u[6]
        
        upgrades_by_category[cat].append({
            'id': u[0], 'number': u[1], 'category': u[2], 'name': u[3],
            'description': u[4], 'cost': u[5], 'boost': u[6],
            'icon': u[7], 'stat_key': u[8], 'owned': is_owned
        })
    
    return jsonify({
        'car_complete': True,
        'budget_total': UPGRADE_BUDGET,
        'budget_used': budget_used,
        'budget_remaining': UPGRADE_BUDGET - budget_used,
        'total_performance_boost': total_boost,
        'upgrades_by_category': upgrades_by_category,
        'purchased_count': len(purchased_ids),
        'total_upgrades': len(upgrades)
    })


@app.route('/api/racing-car/upgrades/buy', methods=['POST'])
@guest_or_login_required
def buy_racing_car_upgrade():
    """Purchase an upgrade"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    data = request.get_json()
    upgrade_id = data.get('upgrade_id')
    test_mode = data.get('test_mode', False)
    
    if not upgrade_id:
        return jsonify({'error': 'No upgrade specified'}), 400
    
    try:
        upgrade = db.session.execute(text(
            "SELECT id, name, cost, performance_boost FROM car_upgrades WHERE id = :uid"
        ), {"uid": upgrade_id}).fetchone()
        
        if not upgrade:
            return jsonify({'error': 'Upgrade not found'}), 404
        
        upgrade_cost = upgrade[2]
        
        if guest_code:
            car = db.session.execute(text(
                "SELECT parts_unlocked, upgrade_budget_used FROM user_race_cars WHERE guest_code = :code"
            ), {"code": guest_code}).fetchone()
        else:
            car = db.session.execute(text(
                "SELECT parts_unlocked, upgrade_budget_used FROM user_race_cars WHERE user_id = :uid"
            ), {"uid": user_id}).fetchone()
        
        # Allow if car complete OR test mode
        if not car or (car[0] < 50 and not test_mode):
            return jsonify({'error': 'Car must be complete to buy upgrades'}), 400
        
        budget_used = car[1] or 0
        budget_remaining = UPGRADE_BUDGET - budget_used
        
        if upgrade_cost > budget_remaining:
            return jsonify({'error': 'Not enough budget', 'cost': upgrade_cost, 'budget_remaining': budget_remaining}), 400
        
        # Check if already owned
        if guest_code:
            existing = db.session.execute(text(
                "SELECT id FROM user_car_upgrades WHERE guest_code = :code AND upgrade_id = :uid"
            ), {"code": guest_code, "uid": upgrade_id}).fetchone()
        else:
            existing = db.session.execute(text(
                "SELECT id FROM user_car_upgrades WHERE user_id = :uid AND upgrade_id = :upid"
            ), {"uid": user_id, "upid": upgrade_id}).fetchone()
        
        if existing:
            return jsonify({'error': 'Upgrade already owned'}), 400
        
        # Purchase
        if guest_code:
            db.session.execute(text("""
                INSERT INTO user_car_upgrades (guest_code, upgrade_id, purchased_at, points_spent)
                VALUES (:code, :uid, :now, :cost)
            """), {"code": guest_code, "uid": upgrade_id, "now": datetime.utcnow(), "cost": upgrade_cost})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = upgrade_budget_used + :cost, updated_at = :now
                WHERE guest_code = :code
            """), {"cost": upgrade_cost, "now": datetime.utcnow(), "code": guest_code})
        else:
            db.session.execute(text("""
                INSERT INTO user_car_upgrades (user_id, upgrade_id, purchased_at, points_spent)
                VALUES (:uid, :upid, :now, :cost)
            """), {"uid": user_id, "upid": upgrade_id, "now": datetime.utcnow(), "cost": upgrade_cost})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = upgrade_budget_used + :cost, updated_at = :now
                WHERE user_id = :uid
            """), {"cost": upgrade_cost, "now": datetime.utcnow(), "uid": user_id})
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Purchased {upgrade[1]}!', 'upgrade_name': upgrade[1],
                       'cost': upgrade_cost, 'boost': upgrade[3], 'budget_remaining': budget_remaining - upgrade_cost})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/racing-car/upgrades/sell', methods=['POST'])
@guest_or_login_required
def sell_racing_car_upgrade():
    """Sell an upgrade for full refund"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    data = request.get_json()
    upgrade_id = data.get('upgrade_id')
    
    if not upgrade_id:
        return jsonify({'error': 'No upgrade specified'}), 400
    
    try:
        upgrade = db.session.execute(text(
            "SELECT id, name, cost FROM car_upgrades WHERE id = :uid"
        ), {"uid": upgrade_id}).fetchone()
        
        if not upgrade:
            return jsonify({'error': 'Upgrade not found'}), 404
        
        upgrade_cost = upgrade[2]
        
        if guest_code:
            owned = db.session.execute(text(
                "SELECT id FROM user_car_upgrades WHERE guest_code = :code AND upgrade_id = :uid"
            ), {"code": guest_code, "uid": upgrade_id}).fetchone()
        else:
            owned = db.session.execute(text(
                "SELECT id FROM user_car_upgrades WHERE user_id = :uid AND upgrade_id = :upid"
            ), {"uid": user_id, "upid": upgrade_id}).fetchone()
        
        if not owned:
            return jsonify({'error': 'You do not own this upgrade'}), 400
        
        if guest_code:
            db.session.execute(text(
                "DELETE FROM user_car_upgrades WHERE guest_code = :code AND upgrade_id = :uid"
            ), {"code": guest_code, "uid": upgrade_id})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = MAX(0, upgrade_budget_used - :cost), updated_at = :now
                WHERE guest_code = :code
            """), {"cost": upgrade_cost, "now": datetime.utcnow(), "code": guest_code})
        else:
            db.session.execute(text(
                "DELETE FROM user_car_upgrades WHERE user_id = :uid AND upgrade_id = :upid"
            ), {"uid": user_id, "upid": upgrade_id})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = MAX(0, upgrade_budget_used - :cost), updated_at = :now
                WHERE user_id = :uid
            """), {"cost": upgrade_cost, "now": datetime.utcnow(), "uid": user_id})
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Sold {upgrade[1]}', 'refund': upgrade_cost})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/racing-car/upgrades/reset', methods=['POST'])
@guest_or_login_required
def reset_racing_car_upgrades():
    """Reset all upgrades and refund budget"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    
    try:
        if guest_code:
            db.session.execute(text("DELETE FROM user_car_upgrades WHERE guest_code = :code"), {"code": guest_code})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = 0, updated_at = :now WHERE guest_code = :code
            """), {"now": datetime.utcnow(), "code": guest_code})
        else:
            db.session.execute(text("DELETE FROM user_car_upgrades WHERE user_id = :uid"), {"uid": user_id})
            db.session.execute(text("""
                UPDATE user_race_cars SET upgrade_budget_used = 0, updated_at = :now WHERE user_id = :uid
            """), {"now": datetime.utcnow(), "uid": user_id})
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'All upgrades reset!', 'budget_remaining': UPGRADE_BUDGET})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================================
# END RACING CAR PHASE 2 ROUTES
# =====================================================
'''


def main():
    print("=" * 60)
    print("🏎️ ADDING RACING CAR PHASE 2 ROUTES TO APP.PY")
    print("=" * 60)
    
    # Backup
    backup_name = f"{APP_FILE}.backup_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(APP_FILE, backup_name)
    print(f"\n✓ Backup created: {backup_name}")
    
    # Read current app.py
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Check if already added
    if 'UPGRADE_BUDGET' in content and 'racing-car/upgrades' in content:
        print("\n⚠️ Phase 2 routes appear to already exist in app.py")
        print("  Skipping to avoid duplicates.")
        return
    
    # Find insertion point (after Phase 1 routes or before main block)
    if "# END RACING CAR ROUTES" in content:
        insertion_point = content.find("# END RACING CAR ROUTES") + len("# END RACING CAR ROUTES")
        new_content = content[:insertion_point] + PHASE2_ROUTES + content[insertion_point:]
    elif "if __name__ == '__main__':" in content:
        insertion_point = content.rfind("if __name__ == '__main__':")
        new_content = content[:insertion_point] + PHASE2_ROUTES + "\n\n" + content[insertion_point:]
    else:
        new_content = content + PHASE2_ROUTES
    
    with open(APP_FILE, 'w') as f:
        f.write(new_content)
    
    print("\n✓ Phase 2 routes added to app.py")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)
    print("""
Next steps:
1. Run: python racing_car_phase2_migration.py (create upgrade tables)
2. Upload the updated racing_car.html template
3. Reload your web app
4. Complete 50 car parts to unlock the Upgrades tab!
""")


if __name__ == '__main__':
    main()
