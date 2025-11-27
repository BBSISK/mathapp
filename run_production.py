#!/usr/bin/env python3
"""
Production server using Gunicorn
Usage: python run_production.py

This script starts the AgentMath.app app using Gunicorn,
a production-ready WSGI server.
"""
import os
import subprocess
import sys

def check_gunicorn():
    """Check if Gunicorn is installed"""
    try:
        import gunicorn
        return True
    except ImportError:
        return False

def main():
    # Check if Gunicorn is installed
    if not check_gunicorn():
        print("❌ Gunicorn is not installed!")
        print("Install it with: pip install gunicorn")
        sys.exit(1)
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Configuration
    workers = 4  # Number of worker processes (2-4 x CPU cores recommended)
    port = 8000  # Port to bind
    host = '0.0.0.0'  # Listen on all network interfaces
    
    # Build Gunicorn command
    cmd = [
        'gunicorn',
        '--bind', f'{host}:{port}',
        '--workers', str(workers),
        '--timeout', '120',
        '--access-logfile', 'access.log',
        '--error-logfile', 'error.log',
        '--log-level', 'info',
        'app_with_auth:app'
    ]
    
    print("=" * 60)
    print("🚀 Starting AgentMath.app in PRODUCTION mode")
    print("=" * 60)
    print(f"Server: Gunicorn (production WSGI server)")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    print(f"URL: http://localhost:{port}")
    print(f"Logs: access.log and error.log")
    print("=" * 60)
    print("\n✅ Production server is ready!")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down gracefully...")
        print("Goodbye! 👋")
        sys.exit(0)
    except FileNotFoundError:
        print("\n❌ Error: app_with_auth.py not found!")
        print("Make sure you're in the correct directory.")
        sys.exit(1)

if __name__ == '__main__':
    main()
