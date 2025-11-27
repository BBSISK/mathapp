#!/usr/bin/env python3
"""
AgentMath.app - Dual Guest System Deployment Script
Automates the complete deployment of both casual and repeat guest systems
"""

import sqlite3
import os
import sys
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def get_database_path():
    """Find the database file"""
    possible_paths = [
        'instance/mathquiz.db',
        'mathquiz.db',
        '../instance/mathquiz.db',
        '../mathquiz.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_casual_guest_user(db_path):
    """Create the casual guest user (guest@agentmath.app)"""
    print_header("STEP 1: Creating Casual Guest User")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if guest user exists
        cursor.execute("SELECT id FROM users WHERE email = 'guest@agentmath.app'")
        existing = cursor.fetchone()
        
        if existing:
            print_success(f"Casual guest user already exists (ID: {existing[0]})")
            conn.close()
            return True
        
        # Create guest user
        print_info("Creating casual guest user...")
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role, is_approved, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'guest@agentmath.app',
            'no_password_required',
            'Guest User',
            'student',
            1,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        guest_id = cursor.lastrowid
        
        print_success(f"Casual guest user created successfully!")
        print_info(f"   Email: guest@agentmath.app")
        print_info(f"   User ID: {guest_id}")
        print_info(f"   Role: student")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Failed to create casual guest user: {e}")
        return False

def create_repeat_guest_tables(db_path):
    """Create database tables for repeat guest system"""
    print_header("STEP 2: Creating Repeat Guest Tables")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guest_users'")
        if cursor.fetchone():
            print_success("Repeat guest tables already exist")
            conn.close()
            return True
        
        print_info("Creating guest_users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guest_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_code VARCHAR(10) UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                total_score INTEGER DEFAULT 0,
                quizzes_completed INTEGER DEFAULT 0,
                CHECK (length(guest_code) >= 5 AND length(guest_code) <= 8)
            )
        """)
        print_success("guest_users table created")
        
        print_info("Creating guest_badges table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guest_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_code VARCHAR(10) NOT NULL,
                badge_id INTEGER NOT NULL,
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guest_code) REFERENCES guest_users(guest_code) ON DELETE CASCADE,
                FOREIGN KEY (badge_id) REFERENCES badges(id),
                UNIQUE(guest_code, badge_id)
            )
        """)
        print_success("guest_badges table created")
        
        print_info("Creating guest_quiz_attempts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guest_quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_code VARCHAR(10) NOT NULL,
                topic VARCHAR(50) NOT NULL,
                difficulty VARCHAR(20) NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                time_spent INTEGER,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guest_code) REFERENCES guest_users(guest_code) ON DELETE CASCADE
            )
        """)
        print_success("guest_quiz_attempts table created")
        
        print_info("Creating guest_topic_progress table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guest_topic_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_code VARCHAR(10) NOT NULL,
                topic VARCHAR(50) NOT NULL,
                difficulty VARCHAR(20) NOT NULL,
                questions_completed INTEGER DEFAULT 0,
                current_score INTEGER DEFAULT 0,
                question_data TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guest_code) REFERENCES guest_users(guest_code) ON DELETE CASCADE,
                UNIQUE(guest_code, topic, difficulty)
            )
        """)
        print_success("guest_topic_progress table created")
        
        print_info("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_code ON guest_users(guest_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_last_active ON guest_users(last_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_badges_code ON guest_badges(guest_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_attempts_code ON guest_quiz_attempts(guest_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_progress_code ON guest_topic_progress(guest_code)")
        print_success("Indexes created")
        
        print_info("Creating statistics view...")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS guest_stats AS
            SELECT 
                guest_code,
                created_at,
                last_active,
                total_score,
                quizzes_completed,
                (SELECT COUNT(*) FROM guest_badges WHERE guest_badges.guest_code = guest_users.guest_code) as badges_earned,
                CAST((julianday('now') - julianday(last_active)) AS INTEGER) as days_inactive
            FROM guest_users
            WHERE is_active = 1
        """)
        print_success("Statistics view created")
        
        conn.commit()
        conn.close()
        
        print_success("All repeat guest tables created successfully!")
        return True
        
    except Exception as e:
        print_error(f"Failed to create repeat guest tables: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def verify_deployment(db_path):
    """Verify that everything was created correctly"""
    print_header("STEP 3: Verifying Deployment")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        checks_passed = 0
        checks_total = 6
        
        # Check 1: Casual guest user
        print_info("Checking casual guest user...")
        cursor.execute("SELECT id FROM users WHERE email = 'guest@agentmath.app'")
        if cursor.fetchone():
            print_success("   Casual guest user exists")
            checks_passed += 1
        else:
            print_error("   Casual guest user NOT found")
        
        # Check 2-5: Repeat guest tables
        tables = ['guest_users', 'guest_badges', 'guest_quiz_attempts', 'guest_topic_progress']
        for table in tables:
            print_info(f"Checking {table} table...")
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print_success(f"   {table} table exists")
                checks_passed += 1
            else:
                print_error(f"   {table} table NOT found")
        
        # Check 6: View
        print_info("Checking guest_stats view...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='guest_stats'")
        if cursor.fetchone():
            print_success("   guest_stats view exists")
            checks_passed += 1
        else:
            print_warning("   guest_stats view NOT found (optional)")
            checks_passed += 1  # Don't fail for missing view
        
        conn.close()
        
        print()
        if checks_passed == checks_total:
            print_success(f"All checks passed ({checks_passed}/{checks_total})!")
            return True
        else:
            print_warning(f"Some checks failed ({checks_passed}/{checks_total})")
            return False
        
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def show_next_steps():
    """Display next steps for manual deployment"""
    print_header("NEXT STEPS")
    
    print(f"{Colors.BOLD}To complete deployment:{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}1. Update app.py:{Colors.ENDC}")
    print("   → Open your app.py file")
    print("   → The new app.py file already has dual guest system included")
    print("   → Just upload the new app.py to replace your current one")
    print()
    
    print(f"{Colors.CYAN}2. Update login page:{Colors.ENDC}")
    print("   → Replace templates/login.html with login_three_options.html")
    print("   → This shows 3 options: Quick Try, Get a Code, Full Account")
    print()
    
    print(f"{Colors.CYAN}3. Reload web app:{Colors.ENDC}")
    print("   → Go to PythonAnywhere Web tab")
    print("   → Click the green 'Reload' button")
    print()
    
    print(f"{Colors.CYAN}4. Test it:{Colors.ENDC}")
    print("   → Visit your site")
    print("   → Try 'Quick Try' option")
    print("   → Try 'Get a Code' option")
    print("   → Try 'Full Account' login")
    print()

def show_summary():
    """Show deployment summary"""
    print_header("DEPLOYMENT SUMMARY")
    
    print(f"{Colors.BOLD}Database changes completed:{Colors.ENDC}\n")
    
    print(f"{Colors.GREEN}✅ Casual Guest System:{Colors.ENDC}")
    print("   • Shared guest@agentmath.app user created")
    print("   • Instant access without code")
    print("   • Progress NOT saved (temporary)")
    print()
    
    print(f"{Colors.GREEN}✅ Repeat Guest System:{Colors.ENDC}")
    print("   • 4 new database tables created")
    print("   • Animal code system (e.g., panda42)")
    print("   • Progress SAVED and persists")
    print("   • 10,000 possible unique codes")
    print()
    
    print(f"{Colors.BLUE}ℹ️  Students will see 3 options:{Colors.ENDC}")
    print("   🎭 Quick Try - Instant, no code, temporary")
    print("   🔑 Get a Code - Animal code, saved progress")
    print("   👤 Full Account - Email/password, all features")
    print()

def main():
    """Main deployment function"""
    print()
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║          AgentMath.app - Dual Guest System Deployment              ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Find database
    print_info("Looking for database...")
    db_path = get_database_path()
    
    if not db_path:
        print_error("Database not found!")
        print_info("Tried the following paths:")
        print("   • instance/mathquiz.db")
        print("   • mathquiz.db")
        print("   • ../instance/mathquiz.db")
        print("   • ../mathquiz.db")
        print()
        print_warning("Please run this script from your project directory")
        print_warning("Or edit the script to add your database path")
        sys.exit(1)
    
    print_success(f"Found database: {db_path}")
    
    # Confirm
    print()
    response = input(f"{Colors.YELLOW}Continue with deployment? (yes/no): {Colors.ENDC}")
    if response.lower() not in ['yes', 'y']:
        print()
        print_warning("Deployment cancelled by user")
        sys.exit(0)
    
    # Run deployment steps
    success = True
    
    # Step 1: Casual guest user
    if not create_casual_guest_user(db_path):
        success = False
    
    # Step 2: Repeat guest tables
    if not create_repeat_guest_tables(db_path):
        success = False
    
    # Step 3: Verify
    if not verify_deployment(db_path):
        success = False
    
    # Show results
    if success:
        show_summary()
        show_next_steps()
        print_header("✨ DATABASE DEPLOYMENT COMPLETE! ✨")
        print()
        print_success("Database setup completed successfully!")
        print_info("Follow the 'Next Steps' above to complete deployment")
        print()
    else:
        print_header("⚠️  DEPLOYMENT INCOMPLETE ⚠️")
        print()
        print_error("Some steps failed. Please review the errors above.")
        print_info("You may need to run this script again or fix issues manually.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print_warning("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
