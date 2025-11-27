# Utility Scripts

This directory contains maintenance, diagnostic, and administration scripts for the AgentMath.app application.

## User Management

- **`change_admin.py`** - Change admin user credentials
- **`change_password.py`** - Change user passwords
- **`quick_reset_admin.py`** - Quick admin password reset
- **`reset_admin.py`** - Full admin account reset
- **`reset_password.py`** - Password reset utility
- **`fix_existing_students.py`** - Fix student account issues

## Database & Data Management

- **`cleanup_mastery_data.py`** - Clean up mastery tracking data
- **`migrate_domain_restriction.py`** - Migrate domain restriction settings
- **`fix_valid_topics.py`** - Fix topic validation issues

## Diagnostics

- **`diagnose_and_fix_auth.py`** - Diagnose authentication issues
- **`diagnose_loading_error.py`** - Diagnose page loading errors
- **`diagnose_number_systems.py`** - Debug number systems questions
- **`verify_installation.py`** - Verify app installation and dependencies

## Feature Fixes

- **`fix_domain_filtering.py`** - Fix teacher domain filtering
- **`fix_number_systems_display.py`** - Fix number systems display issues

## Code Additions (Reference)

These files contain code snippets that were integrated into the main app:

- **`admin_domain_routes.py`** - Admin domain management routes
- **`teacher_domain_routes.py`** - Teacher domain routes
- **`question_flagging_routes.py`** - Question flagging functionality
- **`teacher_routes_modifications.py`** - Teacher route modifications
- **`badges_code_additions.py`** - Badge system code
- **`domain_helpers.py`** - Domain helper functions
- **`domain_models.py`** - Domain data models

## Usage

Run these scripts from the project root with the virtual environment activated:

```bash
cd ~/mathapp
source venv/bin/activate
python scripts/utils/script_name.py
```

**Warning:** Many of these scripts modify the database. Always backup before running database modification scripts.
