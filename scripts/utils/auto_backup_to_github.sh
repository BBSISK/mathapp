#!/bin/bash
#
# Auto Backup to GitHub
# This script automatically commits and pushes database changes to GitHub
# Run this via cron/scheduled task to maintain regular backups
#

set -e  # Exit on error

# Configuration
REPO_DIR="$HOME/mathapp"
BRANCH="claude/app-review-01RJ8RCovWD2PJ2eLiA3v2gf"
BACKUP_DIR="$HOME/mathapp/backups"

# Log file
LOG_FILE="$REPO_DIR/logs/auto_backup.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting automatic GitHub backup..."

# Navigate to repo
cd "$REPO_DIR" || {
    log "ERROR: Could not navigate to $REPO_DIR"
    exit 1
}

# Check if there are changes
if git diff-index --quiet HEAD -- 2>/dev/null; then
    log "No changes to backup. Exiting."
    exit 0
fi

# Get current date for commit message
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
CHANGES=$(git status --short | wc -l)

log "Found $CHANGES changed files"

# Stage changes (database only, respecting .gitignore)
git add instance/mathquiz.db 2>/dev/null || log "No database changes to stage"

# Check if there's anything staged
if git diff-index --quiet --cached HEAD -- 2>/dev/null; then
    log "No staged changes after adding database. Exiting."
    exit 0
fi

# Create commit
log "Creating backup commit..."
git commit -m "Automated backup: $TIMESTAMP

Changes: $CHANGES file(s) modified
Backup type: Scheduled automatic backup
" || {
    log "ERROR: Failed to create commit"
    exit 1
}

# Push to GitHub with retry logic
log "Pushing to GitHub..."
MAX_RETRIES=4
RETRY_DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
    if git push origin "$BRANCH"; then
        log "✅ Successfully pushed to GitHub (attempt $i/$MAX_RETRIES)"

        # Also create a local database backup
        if [ -f "$REPO_DIR/instance/mathquiz.db" ]; then
            BACKUP_FILE="$BACKUP_DIR/mathquiz_$(date +%Y%m%d_%H%M%S).db"
            cp "$REPO_DIR/instance/mathquiz.db" "$BACKUP_FILE"
            log "✅ Local backup created: $BACKUP_FILE"

            # Clean up old backups (keep last 14 days)
            find "$BACKUP_DIR" -name "mathquiz_*.db" -mtime +14 -delete 2>/dev/null || true
        fi

        log "Backup completed successfully!"
        log "========================================="
        exit 0
    else
        log "⚠️  Push failed (attempt $i/$MAX_RETRIES)"

        if [ $i -lt $MAX_RETRIES ]; then
            WAIT_TIME=$((RETRY_DELAY * 2**(i-1)))
            log "Retrying in ${WAIT_TIME}s..."
            sleep $WAIT_TIME
        fi
    fi
done

log "❌ ERROR: Failed to push after $MAX_RETRIES attempts"
log "========================================="
exit 1
