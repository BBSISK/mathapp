# config.py
# Configuration file that loads from environment variables
# Create a .env file based on .env.example and add your actual credentials there

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY')
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Database configuration
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///mathquiz.db')

# Validate critical environment variables
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set!")

# Warning for email configuration (only if being used)
if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("WARNING: Email credentials not configured. Password reset functionality will not work.")
