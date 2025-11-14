# Auto Backup to GitHub - Setup Guide

This guide shows you how to set up automatic backups to GitHub every 6 hours.

## What Gets Backed Up

- Database file (`instance/mathquiz.db`) with all user data, questions, and progress
- Automatic commits with timestamps
- Local backups in `/backups` folder (kept for 14 days)

## Setup Options

Choose **Option A** for PythonAnywhere or **Option B** for your local machine.

---

## Option A: PythonAnywhere Setup (RECOMMENDED for production)

### Step 1: Upload Backup Script

The backup script is already in your repository at:
```
scripts/utils/auto_backup_to_github.py
```

After pulling the latest code on PythonAnywhere, make it executable:

```bash
cd ~/mathapp
chmod +x scripts/utils/auto_backup_to_github.py
```

### Step 2: Test the Backup Script

Run it manually to make sure it works:

```bash
cd ~/mathapp
python scripts/utils/auto_backup_to_github.py
```

You should see output like:
```
[2025-11-14 22:30:00] Starting automatic GitHub backup...
[2025-11-14 22:30:01] Found 1 changed file(s)
[2025-11-14 22:30:02] ✅ Successfully pushed to GitHub
[2025-11-14 22:30:03] Backup completed successfully!
```

### Step 3: Schedule with PythonAnywhere Tasks

1. Go to the **"Tasks"** tab in your PythonAnywhere dashboard
2. Under **"Scheduled tasks"** section
3. Click **"Create a new scheduled task"**
4. Set up the schedule:

**Every 6 hours (recommended):**
- Create 4 tasks at: `00:00`, `06:00`, `12:00`, `18:00`
- Command: `/home/yourusername/mathapp/scripts/utils/auto_backup_to_github.py`

**Or simpler - Daily at 2 AM:**
- Time: `02:00`
- Command: `/home/yourusername/mathapp/scripts/utils/auto_backup_to_github.py`

**Important:** Replace `yourusername` with your actual PythonAnywhere username!

### Step 4: View Logs

Check backup logs anytime:

```bash
tail -50 ~/mathapp/logs/auto_backup.log
```

---

## Option B: Local Machine Setup (Linux/Mac with cron)

### Step 1: Make Script Executable

```bash
cd ~/mathapp
chmod +x scripts/utils/auto_backup_to_github.py
```

### Step 2: Test the Script

```bash
python scripts/utils/auto_backup_to_github.py
```

### Step 3: Set Up Cron Job

Edit your crontab:

```bash
crontab -e
```

Add this line for backups every 6 hours:

```cron
0 */6 * * * cd /path/to/mathapp && python scripts/utils/auto_backup_to_github.py >> logs/cron.log 2>&1
```

**Or** for specific times (midnight, 6am, noon, 6pm):

```cron
0 0,6,12,18 * * * cd /path/to/mathapp && python scripts/utils/auto_backup_to_github.py >> logs/cron.log 2>&1
```

**Important:** Replace `/path/to/mathapp` with your actual path!

### Step 4: Verify Cron Setup

List your cron jobs:

```bash
crontab -l
```

Check logs:

```bash
tail -f ~/mathapp/logs/auto_backup.log
```

---

## Option C: Windows Setup (Task Scheduler)

### Step 1: Test the Script

```powershell
cd C:\path\to\mathapp
python scripts\utils\auto_backup_to_github.py
```

### Step 2: Create Scheduled Task

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name: `Math Master GitHub Backup`
4. Trigger: **Daily**
5. Start time: `00:00` (midnight)
6. Repeat task every: **6 hours**
7. Duration: **Indefinitely**
8. Action: **Start a program**
   - Program: `C:\path\to\python.exe`
   - Arguments: `C:\path\to\mathapp\scripts\utils\auto_backup_to_github.py`
   - Start in: `C:\path\to\mathapp`
9. Click **Finish**

---

## What the Backup Script Does

1. **Checks for changes** - Only runs if database has changed
2. **Creates commit** - With timestamp and change count
3. **Pushes to GitHub** - With retry logic (4 attempts with exponential backoff)
4. **Creates local backup** - Saves copy in `/backups` folder
5. **Cleans old backups** - Removes backups older than 14 days
6. **Logs everything** - All activity logged to `logs/auto_backup.log`

---

## Backup Schedule Examples

**Every 6 hours (4 times daily):**
- `00:00` - Midnight
- `06:00` - 6 AM
- `12:00` - Noon
- `18:00` - 6 PM

**Cron format:** `0 */6 * * *` or `0 0,6,12,18 * * *`

**Every 12 hours (2 times daily):**
- `00:00` - Midnight
- `12:00` - Noon

**Cron format:** `0 */12 * * *` or `0 0,12 * * *`

**Daily (once):**
- `02:00` - 2 AM

**Cron format:** `0 2 * * *`

---

## Monitoring & Troubleshooting

### Check Last Backup

```bash
tail -20 ~/mathapp/logs/auto_backup.log
```

### Check GitHub History

```bash
cd ~/mathapp
git log --oneline -10 --grep="Automated backup"
```

### Manual Backup

```bash
cd ~/mathapp
python scripts/utils/auto_backup_to_github.py
```

### Common Issues

**Issue: "No changes to backup"**
- Normal if database hasn't changed
- Check: `git status`

**Issue: "Failed to push"**
- Check internet connection
- Verify GitHub credentials work: `git push origin branch-name`
- Check network is not blocking git

**Issue: Script not running**
- Check cron/task scheduler is active
- Verify script has execute permissions: `ls -l scripts/utils/auto_backup_to_github.py`
- Check script path is correct in cron/task

**Issue: "Permission denied"**
```bash
chmod +x scripts/utils/auto_backup_to_github.py
```

---

## Backup Retention

**GitHub:** All backups kept indefinitely (git history)
**Local backups:** Kept for 14 days, then auto-deleted

To change retention period, edit line in script:
```python
cutoff_time = datetime.now().timestamp() - (14 * 24 * 60 * 60)  # Change 14 to desired days
```

---

## Security Notes

- ✅ Backups only commit database changes
- ✅ `.env` file excluded (contains secrets)
- ✅ Respects `.gitignore` rules
- ✅ Logs don't contain sensitive information
- ✅ Uses existing git credentials (no password in script)

---

## Quick Reference

**Test backup:**
```bash
python scripts/utils/auto_backup_to_github.py
```

**View logs:**
```bash
tail -50 logs/auto_backup.log
```

**View backups:**
```bash
ls -lh backups/
```

**View recent commits:**
```bash
git log --oneline -10 --grep="Automated"
```

**Disable backups:**
- Remove from cron: `crontab -e`
- Or disable in PythonAnywhere Tasks tab
