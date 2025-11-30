#!/usr/bin/env python3
"""
RACING CAR PHASE 3 - RACE ENGINE & API ROUTES
==============================================
Add these routes to app.py for the racing system.

Run on PythonAnywhere:
    cd ~/mathapp
    source venv/bin/activate
    python add_racing_car_phase3_routes.py
"""

import shutil
from datetime import datetime

APP_FILE = 'app.py'

PHASE3_ROUTES = '''

# =====================================================
# RACING CAR PHASE 3 - WEEKLY RACES
# =====================================================

import random
from datetime import datetime, timedelta

# Points for finishing positions
RACE_POINTS = {1: 500, 2: 350, 3: 250, 4: 180, 5: 140, 6: 110, 7: 85, 8: 65, 9: 50, 10: 25}


def calculate_car_performance(user_id=None, guest_code=None):
    """Calculate total car performance from upgrades"""
    from sqlalchemy import text
    
    base_performance = 50  # Base from completed car
    
    try:
        if guest_code:
            result = db.session.execute(text("""
                SELECT COALESCE(SUM(u.performance_boost), 0)
                FROM user_car_upgrades uc
                JOIN car_upgrades u ON uc.upgrade_id = u.id
                WHERE uc.guest_code = :code
            """), {"code": guest_code}).fetchone()
        else:
            result = db.session.execute(text("""
                SELECT COALESCE(SUM(u.performance_boost), 0)
                FROM user_car_upgrades uc
                JOIN car_upgrades u ON uc.upgrade_id = u.id
                WHERE uc.user_id = :uid
            """), {"uid": user_id}).fetchone()
        
        upgrade_bonus = result[0] if result else 0
        return base_performance + upgrade_bonus
    except:
        return base_performance


def get_upgrade_breakdown(user_id=None, guest_code=None):
    """Get performance breakdown by category"""
    from sqlalchemy import text
    
    breakdown = {'driver': 0, 'aero': 0, 'engine': 0, 'tyres': 0, 'team': 0}
    
    try:
        if guest_code:
            results = db.session.execute(text("""
                SELECT u.category, SUM(u.performance_boost)
                FROM user_car_upgrades uc
                JOIN car_upgrades u ON uc.upgrade_id = u.id
                WHERE uc.guest_code = :code
                GROUP BY u.category
            """), {"code": guest_code}).fetchall()
        else:
            results = db.session.execute(text("""
                SELECT u.category, SUM(u.performance_boost)
                FROM user_car_upgrades uc
                JOIN car_upgrades u ON uc.upgrade_id = u.id
                WHERE uc.user_id = :uid
                GROUP BY u.category
            """), {"uid": user_id}).fetchall()
        
        for cat, boost in results:
            if cat in breakdown:
                breakdown[cat] = boost
    except:
        pass
    
    return breakdown


def simulate_race(user_performance, user_breakdown, race, ai_drivers, is_wet):
    """
    Simulate a race and return results.
    Returns list of (position, name, is_player, performance_score, highlight)
    """
    results = []
    
    # Calculate player's race score
    player_score = calculate_race_score(
        base_perf=user_performance,
        breakdown=user_breakdown,
        race=race,
        is_wet=is_wet,
        is_ai=False
    )
    results.append({
        'name': 'YOU',
        'is_player': True,
        'score': player_score,
        'team': 'Your Team',
        'flag': '🏁'
    })
    
    # Calculate AI scores
    for ai in ai_drivers:
        ai_breakdown = {
            'driver': ai['base_skill'] * 0.4,
            'aero': 30 + random.randint(-5, 5),
            'engine': 30 + random.randint(-5, 5),
            'tyres': ai['tyre_management'] * 0.3,
            'team': 25 + random.randint(-5, 5)
        }
        
        ai_base = 50 + (ai['base_skill'] - 80) * 2  # Scale AI skill to performance
        
        ai_score = calculate_race_score(
            base_perf=ai_base,
            breakdown=ai_breakdown,
            race=race,
            is_wet=is_wet,
            is_ai=True,
            ai_data=ai
        )
        
        results.append({
            'name': ai['name'],
            'is_player': False,
            'score': ai_score,
            'team': ai['team'],
            'flag': ai['flag'],
            'ai_id': ai['id']
        })
    
    # Sort by score (higher is better)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Assign positions and generate highlights
    for i, r in enumerate(results):
        r['position'] = i + 1
        r['points'] = RACE_POINTS.get(i + 1, 10)
        r['highlight'] = generate_highlight(r, i + 1, is_wet, race)
    
    return results


def calculate_race_score(base_perf, breakdown, race, is_wet, is_ai=False, ai_data=None):
    """Calculate race performance score"""
    
    # Base score from car performance
    score = base_perf * 10
    
    # Apply track factors
    score += breakdown.get('aero', 0) * race['aero_factor'] * 20
    score += breakdown.get('engine', 0) * race['engine_factor'] * 20
    score += breakdown.get('driver', 0) * race['driver_factor'] * 20
    score += breakdown.get('tyres', 0) * race['tyre_factor'] * 20
    score += breakdown.get('team', 0) * race['team_factor'] * 20
    
    # Weather effect
    if is_wet:
        if is_ai and ai_data:
            wet_bonus = (ai_data['wet_skill'] - 80) * 3
            score += wet_bonus
        else:
            # Player wet performance based on driver upgrades
            driver_skill = breakdown.get('driver', 0)
            wet_bonus = (driver_skill - 20) * 2
            score += wet_bonus
    
    # Consistency factor (AI only)
    if is_ai and ai_data:
        consistency = ai_data['consistency']
        variance = (100 - consistency) * 2
        score += random.randint(-variance, variance)
    
    # Random race events (luck factor)
    luck = random.randint(-50, 50)
    score += luck
    
    # Small random variance
    score += random.randint(-20, 20)
    
    return max(0, score)


def generate_highlight(result, position, is_wet, race):
    """Generate a race highlight text"""
    name = result['name']
    
    if result['is_player']:
        if position == 1:
            highlights = [
                "🏆 VICTORY! Incredible drive from start to finish!",
                "🏆 WINNER! You dominated the {track}!",
                "🏆 P1! A masterclass performance today!"
            ]
        elif position <= 3:
            highlights = [
                f"🥈 P{position}! Brilliant podium finish!",
                f"🥉 P{position}! Fought hard for that podium!",
                f"🏅 P{position}! Great result at {race['name']}!"
            ]
        elif position <= 6:
            highlights = [
                f"✓ P{position} - Solid points finish",
                f"✓ P{position} - Good pace throughout",
                f"✓ P{position} - Consistent drive"
            ]
        else:
            highlights = [
                f"P{position} - Struggled with pace today",
                f"P{position} - Tough race, but finished",
                f"P{position} - More upgrades needed!"
            ]
    else:
        if position == 1:
            highlights = [f"{name} takes victory!", f"{name} wins at {race['name']}!"]
        elif position <= 3:
            highlights = [f"{name} claims P{position}", f"{name} on the podium"]
        else:
            highlights = [f"{name} finishes P{position}", f"{name} in P{position}"]
    
    text = random.choice(highlights)
    return text.format(track=race['name'])


@app.route('/api/racing-car/race/current')
@guest_or_login_required  
def get_current_race():
    """Get the current race information"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    current_year = datetime.now().year
    
    # TEST MODE
    test_mode = request.args.get('test') == 'race'
    
    try:
        # Get current race from calendar
        race = db.session.execute(text("""
            SELECT rc.id, rc.race_number, rc.name, rc.country, rc.flag, rc.track_type,
                   rc.aero_factor, rc.engine_factor, rc.driver_factor, rc.tyre_factor, 
                   rc.team_factor, rc.rain_chance, rc.description, rc.race_date
            FROM race_calendar rc
            JOIN race_season_status rs ON rc.season_year = rs.season_year
            WHERE rc.season_year = :year AND rc.race_number = rs.current_race_number
        """), {"year": current_year}).fetchone()
        
        if not race:
            return jsonify({'error': 'No active race found', 'has_race': False})
        
        # Check if user already raced this
        if guest_code:
            existing = db.session.execute(text(
                "SELECT id, finish_position, points_earned FROM race_results WHERE race_id = :rid AND guest_code = :code"
            ), {"rid": race[0], "code": guest_code}).fetchone()
        else:
            existing = db.session.execute(text(
                "SELECT id, finish_position, points_earned FROM race_results WHERE race_id = :rid AND user_id = :uid"
            ), {"rid": race[0], "uid": user_id}).fetchone()
        
        already_raced = existing is not None
        
        # Get user's car performance
        car_performance = calculate_car_performance(user_id, guest_code)
        breakdown = get_upgrade_breakdown(user_id, guest_code)
        
        # Check if car is complete (or test mode)
        if guest_code:
            car = db.session.execute(text(
                "SELECT parts_unlocked FROM user_race_cars WHERE guest_code = :code"
            ), {"code": guest_code}).fetchone()
        else:
            car = db.session.execute(text(
                "SELECT parts_unlocked FROM user_race_cars WHERE user_id = :uid"
            ), {"uid": user_id}).fetchone()
        
        car_complete = (car and car[0] >= 50) or test_mode
        
        return jsonify({
            'has_race': True,
            'race': {
                'id': race[0],
                'number': race[1],
                'name': race[2],
                'country': race[3],
                'flag': race[4],
                'track_type': race[5],
                'factors': {
                    'aero': race[6],
                    'engine': race[7],
                    'driver': race[8],
                    'tyres': race[9],
                    'team': race[10]
                },
                'rain_chance': race[11],
                'description': race[12],
                'date': race[13]
            },
            'already_raced': already_raced,
            'previous_result': {
                'position': existing[1],
                'points': existing[2]
            } if existing else None,
            'car_complete': car_complete,
            'car_performance': car_performance,
            'performance_breakdown': breakdown
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'has_race': False})


@app.route('/api/racing-car/race/start', methods=['POST'])
@guest_or_login_required
def start_race():
    """Start/simulate a race"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    data = request.get_json()
    
    race_id = data.get('race_id')
    tyre_choice = data.get('tyre_choice', 'medium')  # soft, medium, hard
    test_mode = data.get('test_mode', False)
    
    if not race_id:
        return jsonify({'error': 'No race specified'}), 400
    
    try:
        # Get race details
        race_row = db.session.execute(text("""
            SELECT id, race_number, name, country, flag, track_type,
                   aero_factor, engine_factor, driver_factor, tyre_factor, 
                   team_factor, rain_chance, description
            FROM race_calendar WHERE id = :rid
        """), {"rid": race_id}).fetchone()
        
        if not race_row:
            return jsonify({'error': 'Race not found'}), 404
        
        race = {
            'id': race_row[0], 'number': race_row[1], 'name': race_row[2],
            'country': race_row[3], 'flag': race_row[4], 'track_type': race_row[5],
            'aero_factor': race_row[6], 'engine_factor': race_row[7],
            'driver_factor': race_row[8], 'tyre_factor': race_row[9],
            'team_factor': race_row[10], 'rain_chance': race_row[11],
            'description': race_row[12]
        }
        
        # Check if already raced
        if guest_code:
            existing = db.session.execute(text(
                "SELECT id FROM race_results WHERE race_id = :rid AND guest_code = :code"
            ), {"rid": race_id, "code": guest_code}).fetchone()
        else:
            existing = db.session.execute(text(
                "SELECT id FROM race_results WHERE race_id = :rid AND user_id = :uid"
            ), {"rid": race_id, "uid": user_id}).fetchone()
        
        if existing:
            return jsonify({'error': 'Already raced this week!'}), 400
        
        # Determine weather
        is_wet = random.randint(1, 100) <= race['rain_chance']
        
        # Get AI drivers
        ai_rows = db.session.execute(text("""
            SELECT id, name, team, nationality, flag, driving_style,
                   base_skill, consistency, aggression, wet_skill, tyre_management
            FROM ai_race_drivers
        """)).fetchall()
        
        ai_drivers = [{
            'id': a[0], 'name': a[1], 'team': a[2], 'nationality': a[3],
            'flag': a[4], 'driving_style': a[5], 'base_skill': a[6],
            'consistency': a[7], 'aggression': a[8], 'wet_skill': a[9],
            'tyre_management': a[10]
        } for a in ai_rows]
        
        # Get user's car performance
        car_performance = calculate_car_performance(user_id, guest_code)
        breakdown = get_upgrade_breakdown(user_id, guest_code)
        
        # Apply tyre choice bonus
        tyre_bonus = {'soft': 15, 'medium': 8, 'hard': 0}
        breakdown['tyres'] = breakdown.get('tyres', 0) + tyre_bonus.get(tyre_choice, 8)
        
        # Simulate the race!
        results = simulate_race(car_performance, breakdown, race, ai_drivers, is_wet)
        
        # Find player result
        player_result = next(r for r in results if r['is_player'])
        position = player_result['position']
        points = player_result['points']
        highlight = player_result['highlight']
        
        # Save player result
        if guest_code:
            db.session.execute(text("""
                INSERT INTO race_results 
                (race_id, guest_code, finish_position, points_earned, tyre_choice, 
                 is_wet_race, race_performance_score, highlight_text, created_at)
                VALUES (:rid, :code, :pos, :pts, :tyre, :wet, :score, :highlight, :now)
            """), {
                "rid": race_id, "code": guest_code, "pos": position, "pts": points,
                "tyre": tyre_choice, "wet": is_wet, "score": player_result['score'],
                "highlight": highlight, "now": datetime.utcnow()
            })
        else:
            db.session.execute(text("""
                INSERT INTO race_results 
                (race_id, user_id, finish_position, points_earned, tyre_choice, 
                 is_wet_race, race_performance_score, highlight_text, created_at)
                VALUES (:rid, :uid, :pos, :pts, :tyre, :wet, :score, :highlight, :now)
            """), {
                "rid": race_id, "uid": user_id, "pos": position, "pts": points,
                "tyre": tyre_choice, "wet": is_wet, "score": player_result['score'],
                "highlight": highlight, "now": datetime.utcnow()
            })
        
        # Update championship standings
        current_year = datetime.now().year
        if guest_code:
            db.session.execute(text("""
                INSERT INTO championship_standings (season_year, guest_code, total_points, races_entered, wins, podiums, best_finish, last_updated)
                VALUES (:year, :code, :pts, 1, :wins, :podiums, :pos, :now)
                ON CONFLICT(season_year, guest_code) DO UPDATE SET
                    total_points = total_points + :pts,
                    races_entered = races_entered + 1,
                    wins = wins + :wins,
                    podiums = podiums + :podiums,
                    best_finish = CASE WHEN :pos < best_finish OR best_finish = 0 THEN :pos ELSE best_finish END,
                    last_updated = :now
            """), {
                "year": current_year, "code": guest_code, "pts": points,
                "wins": 1 if position == 1 else 0,
                "podiums": 1 if position <= 3 else 0,
                "pos": position, "now": datetime.utcnow()
            })
        else:
            db.session.execute(text("""
                INSERT INTO championship_standings (season_year, user_id, total_points, races_entered, wins, podiums, best_finish, last_updated)
                VALUES (:year, :uid, :pts, 1, :wins, :podiums, :pos, :now)
                ON CONFLICT(season_year, user_id) DO UPDATE SET
                    total_points = total_points + :pts,
                    races_entered = races_entered + 1,
                    wins = wins + :wins,
                    podiums = podiums + :podiums,
                    best_finish = CASE WHEN :pos < best_finish OR best_finish = 0 THEN :pos ELSE best_finish END,
                    last_updated = :now
            """), {
                "year": current_year, "uid": user_id, "pts": points,
                "wins": 1 if position == 1 else 0,
                "podiums": 1 if position <= 3 else 0,
                "pos": position, "now": datetime.utcnow()
            })
        
        # Award points to user's total score
        if guest_code:
            db.session.execute(text(
                "UPDATE guest_users SET total_score = total_score + :pts WHERE guest_code = :code"
            ), {"pts": points, "code": guest_code})
        else:
            db.session.execute(text(
                "UPDATE user_stats SET total_points = total_points + :pts WHERE user_id = :uid"
            ), {"pts": points, "uid": user_id})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'race_name': race['name'],
            'is_wet': is_wet,
            'weather': 'Wet' if is_wet else 'Dry',
            'results': results,
            'player_position': position,
            'player_points': points,
            'player_highlight': highlight,
            'tyre_choice': tyre_choice
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/racing-car/championship')
@guest_or_login_required
def get_championship_standings():
    """Get championship standings"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    current_year = datetime.now().year
    
    try:
        # Get user's standing
        if guest_code:
            user_standing = db.session.execute(text("""
                SELECT total_points, races_entered, wins, podiums, best_finish
                FROM championship_standings
                WHERE season_year = :year AND guest_code = :code
            """), {"year": current_year, "code": guest_code}).fetchone()
        else:
            user_standing = db.session.execute(text("""
                SELECT total_points, races_entered, wins, podiums, best_finish
                FROM championship_standings
                WHERE season_year = :year AND user_id = :uid
            """), {"year": current_year, "uid": user_id}).fetchone()
        
        # Get race history
        if guest_code:
            history = db.session.execute(text("""
                SELECT rc.name, rc.flag, rr.finish_position, rr.points_earned, rr.is_wet_race, rr.highlight_text
                FROM race_results rr
                JOIN race_calendar rc ON rr.race_id = rc.id
                WHERE rr.guest_code = :code AND rc.season_year = :year
                ORDER BY rc.race_number
            """), {"code": guest_code, "year": current_year}).fetchall()
        else:
            history = db.session.execute(text("""
                SELECT rc.name, rc.flag, rr.finish_position, rr.points_earned, rr.is_wet_race, rr.highlight_text
                FROM race_results rr
                JOIN race_calendar rc ON rr.race_id = rc.id
                WHERE rr.user_id = :uid AND rc.season_year = :year
                ORDER BY rc.race_number
            """), {"uid": user_id, "year": current_year}).fetchall()
        
        return jsonify({
            'season': current_year,
            'standing': {
                'total_points': user_standing[0] if user_standing else 0,
                'races_entered': user_standing[1] if user_standing else 0,
                'wins': user_standing[2] if user_standing else 0,
                'podiums': user_standing[3] if user_standing else 0,
                'best_finish': user_standing[4] if user_standing else 0
            },
            'race_history': [{
                'name': h[0],
                'flag': h[1],
                'position': h[2],
                'points': h[3],
                'wet': h[4],
                'highlight': h[5]
            } for h in history]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/racing-car/ai-drivers')
@guest_or_login_required
def get_ai_drivers():
    """Get list of AI competitors"""
    from sqlalchemy import text
    
    try:
        drivers = db.session.execute(text("""
            SELECT id, name, team, nationality, flag, driving_style, 
                   base_skill, personality_desc, avatar_color
            FROM ai_race_drivers
            ORDER BY base_skill DESC
        """)).fetchall()
        
        return jsonify({
            'drivers': [{
                'id': d[0],
                'name': d[1],
                'team': d[2],
                'nationality': d[3],
                'flag': d[4],
                'style': d[5],
                'skill': d[6],
                'description': d[7],
                'color': d[8]
            } for d in drivers]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'drivers': []})


@app.route('/api/racing-car/tracks')
@guest_or_login_required
def get_race_tracks():
    """Get all available tracks for practice mode"""
    from sqlalchemy import text
    
    current_year = datetime.now().year
    
    try:
        tracks = db.session.execute(text("""
            SELECT id, race_number, name, country, flag, track_type,
                   aero_factor, engine_factor, driver_factor, tyre_factor, 
                   team_factor, rain_chance, description
            FROM race_calendar
            WHERE season_year = :year
            ORDER BY race_number
        """), {"year": current_year}).fetchall()
        
        return jsonify({
            'tracks': [{
                'id': t[0],
                'number': t[1],
                'name': t[2],
                'country': t[3],
                'flag': t[4],
                'track_type': t[5],
                'factors': {
                    'aero': t[6],
                    'engine': t[7],
                    'driver': t[8],
                    'tyres': t[9],
                    'team': t[10]
                },
                'rain_chance': t[11],
                'description': t[12]
            } for t in tracks]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'tracks': []})


@app.route('/api/racing-car/race/practice', methods=['POST'])
@guest_or_login_required
def practice_race():
    """Run a practice race - no points awarded, just for testing"""
    from sqlalchemy import text
    
    user_id = session.get('user_id')
    guest_code = session.get('guest_code')
    data = request.get_json()
    
    track_id = data.get('track_id', 'random')
    tyre_choice = data.get('tyre_choice', 'medium')
    
    current_year = datetime.now().year
    
    try:
        # Get track - either specific or random
        if track_id == 'random':
            race_row = db.session.execute(text("""
                SELECT id, race_number, name, country, flag, track_type,
                       aero_factor, engine_factor, driver_factor, tyre_factor, 
                       team_factor, rain_chance, description
                FROM race_calendar 
                WHERE season_year = :year
                ORDER BY RANDOM()
                LIMIT 1
            """), {"year": current_year}).fetchone()
        else:
            race_row = db.session.execute(text("""
                SELECT id, race_number, name, country, flag, track_type,
                       aero_factor, engine_factor, driver_factor, tyre_factor, 
                       team_factor, rain_chance, description
                FROM race_calendar WHERE id = :tid
            """), {"tid": track_id}).fetchone()
        
        if not race_row:
            return jsonify({'error': 'Track not found'}), 404
        
        race = {
            'id': race_row[0], 'number': race_row[1], 'name': race_row[2],
            'country': race_row[3], 'flag': race_row[4], 'track_type': race_row[5],
            'aero_factor': race_row[6], 'engine_factor': race_row[7],
            'driver_factor': race_row[8], 'tyre_factor': race_row[9],
            'team_factor': race_row[10], 'rain_chance': race_row[11],
            'description': race_row[12]
        }
        
        # Determine weather
        is_wet = random.randint(1, 100) <= race['rain_chance']
        
        # Get AI drivers
        ai_rows = db.session.execute(text("""
            SELECT id, name, team, nationality, flag, driving_style,
                   base_skill, consistency, aggression, wet_skill, tyre_management
            FROM ai_race_drivers
        """)).fetchall()
        
        ai_drivers = [{
            'id': a[0], 'name': a[1], 'team': a[2], 'nationality': a[3],
            'flag': a[4], 'driving_style': a[5], 'base_skill': a[6],
            'consistency': a[7], 'aggression': a[8], 'wet_skill': a[9],
            'tyre_management': a[10]
        } for a in ai_rows]
        
        # Get user's car performance
        car_performance = calculate_car_performance(user_id, guest_code)
        breakdown = get_upgrade_breakdown(user_id, guest_code)
        
        # Apply tyre choice bonus
        tyre_bonus = {'soft': 15, 'medium': 8, 'hard': 0}
        breakdown['tyres'] = breakdown.get('tyres', 0) + tyre_bonus.get(tyre_choice, 8)
        
        # Simulate the race!
        results = simulate_race(car_performance, breakdown, race, ai_drivers, is_wet)
        
        # Find player result
        player_result = next(r for r in results if r['is_player'])
        position = player_result['position']
        
        # Modify highlight for practice
        highlight = player_result['highlight']
        if 'pts' in highlight.lower() or 'points' in highlight.lower():
            highlight = highlight.replace('points', 'practice result').replace('pts', '')
        
        return jsonify({
            'success': True,
            'is_practice': True,
            'race_name': race['name'],
            'race_number': race['number'],
            'is_wet': is_wet,
            'weather': 'Wet' if is_wet else 'Dry',
            'results': results,
            'player_position': position,
            'player_points': 0,  # No points for practice
            'player_highlight': highlight,
            'tyre_choice': tyre_choice
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# END RACING CAR PHASE 3 ROUTES
# =====================================================
'''


def main():
    print("=" * 60)
    print("🏁 ADDING RACING CAR PHASE 3 ROUTES TO APP.PY")
    print("=" * 60)
    
    # Backup
    backup_name = f"{APP_FILE}.backup_phase3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(APP_FILE, backup_name)
    print(f"\n✓ Backup created: {backup_name}")
    
    # Read current app.py
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Check if already added
    if 'RACE_POINTS' in content and 'racing-car/race/current' in content:
        print("\n⚠️ Phase 3 routes appear to already exist in app.py")
        print("  Skipping to avoid duplicates.")
        return
    
    # Find insertion point
    if "if __name__ == '__main__':" in content:
        insertion_point = content.rfind("if __name__ == '__main__':")
        new_content = content[:insertion_point] + PHASE3_ROUTES + "\n\n" + content[insertion_point:]
    else:
        new_content = content + PHASE3_ROUTES
    
    with open(APP_FILE, 'w') as f:
        f.write(new_content)
    
    print("\n✓ Phase 3 routes added to app.py")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)
    print("""
Next steps:
1. Run: python racing_car_phase3_migration.py (create race tables)
2. Upload the updated racing_car.html template (with race UI)
3. Reload your web app
4. Race! 🏎️
""")


if __name__ == '__main__':
    main()
