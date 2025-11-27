#!/usr/bin/env python3
"""
Add minimum_level column to prizes table
Run this once after deploying Phase 3

Usage: python add_minimum_level_column.py
"""

from app import app, db

with app.app_context():
    try:
        # Try to add the column
        db.engine.execute('ALTER TABLE prizes ADD COLUMN minimum_level INTEGER DEFAULT 0')
        print('✅ Column minimum_level added to prizes table!')
    except Exception as e:
        error_msg = str(e).lower()
        if 'duplicate column' in error_msg or 'already exists' in error_msg:
            print('ℹ️  Column already exists - no action needed')
        else:
            print(f'Error: {e}')
