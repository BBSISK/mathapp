#!/usr/bin/env python3
"""
Raffle Auto-Draw Scheduled Task Script
=======================================

This script is designed to run as a PythonAnywhere Scheduled Task.
It checks for raffles that need automatic draws and executes them.

Setup Instructions:
-------------------
1. Upload this file to your PythonAnywhere home directory: /home/bbsisk/raffle_auto_draw.py
2. Go to PythonAnywhere Dashboard > Tasks
3. Create a new scheduled task:
   - Command: /home/bbsisk/mathapp/venv/bin/python /home/bbsisk/raffle_auto_draw.py
   - Frequency: Hourly (or at specific times like 15:00 daily)

The script will:
- Check all active raffles with auto_draw_enabled=True
- For weekly raffles: Draw on the specified day at the specified time
- For daily raffles: Draw once per day at the specified time
- For monthly raffles: Draw on the 1st of each month
- Skip raffles that have already been drawn in the current period
- Skip raffles with no entries

Logs are written to: /home/bbsisk/raffle_auto_draw.log
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, '/home/bbsisk/mathapp')

# Set up logging
LOG_FILE = '/home/bbsisk/raffle_auto_draw.log'

def log(message):
    """Write to log file and print"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + '\n')
    except Exception as e:
        print(f"Could not write to log: {e}")

def run_auto_draws():
    """Main function to check and run raffle auto-draws"""
    log("=" * 60)
    log("RAFFLE AUTO-DRAW TASK STARTED")
    log("=" * 60)
    
    try:
        # Import app and database
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            now = datetime.now()
            current_day = now.weekday()  # 0=Monday, 6=Sunday
            current_time = now.strftime('%H:%M')
            
            log(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            log(f"Current day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][current_day]}")
            
            # Find raffles due for auto-draw
            raffles = db.session.execute(text("""
                SELECT * FROM raffles
                WHERE is_active = 1 
                AND auto_draw_enabled = 1
                AND draw_frequency IN ('weekly', 'daily', 'monthly')
            """)).fetchall()
            
            log(f"Found {len(raffles)} active auto-draw raffles")
            
            drawn_count = 0
            skipped_count = 0
            
            for raffle in raffles:
                try:
                    log(f"\nChecking raffle: {raffle.name} (ID: {raffle.id})")
                    log(f"  Frequency: {raffle.draw_frequency}, Day: {raffle.draw_day_of_week}, Time: {raffle.draw_time}")
                    
                    should_draw = False
                    reason = ""
                    
                    # Check if already drawn today
                    today_draw = db.session.execute(text("""
                        SELECT id FROM raffle_draws 
                        WHERE raffle_id = :raffle_id 
                        AND DATE(drawn_at) = DATE('now')
                    """), {'raffle_id': raffle.id}).fetchone()
                    
                    if today_draw:
                        log(f"  SKIP: Already drawn today")
                        skipped_count += 1
                        continue
                    
                    # Check draw frequency
                    if raffle.draw_frequency == 'daily':
                        draw_time = raffle.draw_time or '15:00'
                        if current_time >= draw_time[:5]:
                            should_draw = True
                            reason = f"Daily draw time ({draw_time[:5]}) reached"
                        else:
                            log(f"  SKIP: Daily draw time ({draw_time[:5]}) not yet reached")
                            
                    elif raffle.draw_frequency == 'weekly':
                        draw_day = raffle.draw_day_of_week if raffle.draw_day_of_week is not None else 4
                        draw_time = raffle.draw_time or '15:00'
                        
                        if current_day == draw_day:
                            if current_time >= draw_time[:5]:
                                # Check if already drawn this week
                                week_start = now.date() - timedelta(days=current_day)
                                week_draw = db.session.execute(text("""
                                    SELECT id FROM raffle_draws 
                                    WHERE raffle_id = :raffle_id 
                                    AND DATE(drawn_at) >= :week_start
                                """), {'raffle_id': raffle.id, 'week_start': week_start}).fetchone()
                                
                                if not week_draw:
                                    should_draw = True
                                    reason = f"Weekly draw ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][draw_day]}) at {draw_time[:5]}"
                                else:
                                    log(f"  SKIP: Already drawn this week")
                            else:
                                log(f"  SKIP: Draw time ({draw_time[:5]}) not yet reached")
                        else:
                            log(f"  SKIP: Not draw day ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][draw_day]})")
                            
                    elif raffle.draw_frequency == 'monthly':
                        if now.day == 1:
                            draw_time = raffle.draw_time or '15:00'
                            if current_time >= draw_time[:5]:
                                month_draw = db.session.execute(text("""
                                    SELECT id FROM raffle_draws 
                                    WHERE raffle_id = :raffle_id 
                                    AND strftime('%Y-%m', drawn_at) = strftime('%Y-%m', 'now')
                                """), {'raffle_id': raffle.id}).fetchone()
                                
                                if not month_draw:
                                    should_draw = True
                                    reason = "Monthly draw (1st of month)"
                                else:
                                    log(f"  SKIP: Already drawn this month")
                            else:
                                log(f"  SKIP: Draw time ({draw_time[:5]}) not yet reached")
                        else:
                            log(f"  SKIP: Not 1st of month (monthly draw)")
                    
                    if should_draw:
                        # Check if there are entries
                        entry_count = db.session.execute(text("""
                            SELECT COUNT(*) as cnt FROM raffle_entries
                            WHERE raffle_id = :raffle_id AND is_active = 1
                        """), {'raffle_id': raffle.id}).fetchone()
                        
                        if entry_count and entry_count.cnt > 0:
                            log(f"  DRAWING: {reason} ({entry_count.cnt} entries)")
                            
                            # Import and call the draw function
                            from app import perform_raffle_draw
                            draw_id = perform_raffle_draw(raffle.id)
                            
                            if draw_id:
                                log(f"  SUCCESS: Draw ID {draw_id}")
                                drawn_count += 1
                            else:
                                log(f"  ERROR: Draw function returned None")
                        else:
                            log(f"  SKIP: No entries to draw from")
                            skipped_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    log(f"  ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            log("")
            log("=" * 60)
            log(f"COMPLETED: {drawn_count} drawn, {skipped_count} skipped")
            log("=" * 60)
            
            return {'drawn': drawn_count, 'skipped': skipped_count}
            
    except Exception as e:
        log(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

if __name__ == '__main__':
    run_auto_draws()
