#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "API_ID", "API_HASH", "BOT_TOKEN",
        "ADMINS", "LOG_CHANNEL", "BIN_CHANNEL"
    ]
    
    # Check for either DATABASE_URL (PostgreSQL) or DATABASE_URI (MongoDB)
    if not os.environ.get("DATABASE_URL") and not os.environ.get("DATABASE_URI"):
        required_vars.append("DATABASE_URI or DATABASE_URL")
    
    missing_vars = []
    for var in required_vars:
        if "or" not in var and not os.environ.get(var):
            missing_vars.append(var)
    
    return missing_vars

def setup_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Check for missing required variables
    missing_vars = check_environment()
    if missing_vars:
        print("Error: The following environment variables are required but not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in the .env file and try again.")
        sys.exit(1)

def run_bot():
    """Run the Telegram bot"""
    setup_environment()
    
    # We're now using MongoDB instead of PostgreSQL
    if os.environ.get('DATABASE_URI', '').startswith('mongodb'):
        print("MongoDB database detected. Using MongoDB for storage...")
    
    print("Starting Telegram bot...")
    subprocess.run(["python3", "bot.py"], check=True)

def run_web():
    """Run the web interface"""
    setup_environment()
    from web import web_app
    
    host = os.environ.get('WEB_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    print(f"Starting web server on {host}:{port}...")
    
    # Run the aiohttp web app
    from aiohttp import web
    web.run_app(web_app, host=host, port=port)

if __name__ == "__main__":
    # Default to running the bot
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Error running bot: {e}")