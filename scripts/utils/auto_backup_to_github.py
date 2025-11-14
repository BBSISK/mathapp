#!/usr/bin/env python3
"""
Auto Backup to GitHub (Python version)
This script automatically commits and pushes database changes to GitHub
Safer alternative to bash script with better error handling
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

# Configuration
REPO_DIR = Path.home() / "mathapp"
BRANCH = "claude/app-review-01RJ8RCovWD2PJ2eLiA3v2gf"
BACKUP_DIR = REPO_DIR / "backups"
LOG_FILE = REPO_DIR / "logs" / "auto_backup.log"

# Create directories
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def log(message):
    """Log message to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")


def run_command(cmd, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            check=check,
            shell=isinstance(cmd, str)
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def has_changes():
    """Check if there are uncommitted changes"""
    success, stdout, _ = run_command(["git", "diff-index", "--quiet", "HEAD", "--"], check=False)
    return not success  # Returns True if there ARE changes


def has_staged_changes():
    """Check if there are staged changes"""
    success, stdout, _ = run_command(["git", "diff-index", "--quiet", "--cached", "HEAD", "--"], check=False)
    return not success


def get_changed_files_count():
    """Count number of changed files"""
    success, stdout, _ = run_command(["git", "status", "--short"])
    if success:
        return len([line for line in stdout.strip().split("\n") if line])
    return 0


def create_local_backup():
    """Create local database backup"""
    db_file = REPO_DIR / "instance" / "mathquiz.db"

    if not db_file.exists():
        log("⚠️  Database file not found, skipping local backup")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"mathquiz_{timestamp}.db"

    try:
        import shutil
        shutil.copy2(db_file, backup_file)
        log(f"✅ Local backup created: {backup_file.name}")

        # Clean up old backups (keep last 14 days)
        cutoff_time = datetime.now().timestamp() - (14 * 24 * 60 * 60)
        for old_backup in BACKUP_DIR.glob("mathquiz_*.db"):
            if old_backup.stat().st_mtime < cutoff_time:
                old_backup.unlink()
                log(f"🗑️  Removed old backup: {old_backup.name}")

        return True
    except Exception as e:
        log(f"⚠️  Failed to create local backup: {e}")
        return False


def push_with_retry(max_retries=4):
    """Push to GitHub with exponential backoff retry"""
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        log(f"Pushing to GitHub (attempt {attempt}/{max_retries})...")

        success, stdout, stderr = run_command(["git", "push", "origin", BRANCH], check=False)

        if success:
            log(f"✅ Successfully pushed to GitHub")
            return True
        else:
            log(f"⚠️  Push failed: {stderr.strip()}")

            if attempt < max_retries:
                wait_time = retry_delay * (2 ** (attempt - 1))
                log(f"Retrying in {wait_time}s...")
                sleep(wait_time)

    return False


def main():
    """Main backup function"""
    log("=" * 50)
    log("Starting automatic GitHub backup...")

    # Check for changes
    if not has_changes():
        log("No changes to backup. Exiting.")
        return 0

    changes_count = get_changed_files_count()
    log(f"Found {changes_count} changed file(s)")

    # Stage database changes
    log("Staging database changes...")
    run_command(["git", "add", "instance/mathquiz.db"], check=False)

    # Check if anything was staged
    if not has_staged_changes():
        log("No staged changes after adding database. Exiting.")
        return 0

    # Create commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"""Automated backup: {timestamp}

Changes: {changes_count} file(s) modified
Backup type: Scheduled automatic backup
"""

    log("Creating backup commit...")
    success, stdout, stderr = run_command(
        ["git", "commit", "-m", commit_message],
        check=False
    )

    if not success:
        log(f"❌ Failed to create commit: {stderr}")
        return 1

    # Push to GitHub
    if not push_with_retry():
        log("❌ Failed to push after multiple retries")
        return 1

    # Create local backup
    create_local_backup()

    log("Backup completed successfully!")
    log("=" * 50)
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        log(f"❌ FATAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
