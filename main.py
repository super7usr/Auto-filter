#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv
import subprocess
import signal
import threading
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('main.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables to track processes
telegram_bot_process = None
web_server_process = None
control_panel_process = None
process_lock = threading.Lock()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'BOT_TOKEN',
        'API_ID',
        'API_HASH',
        'ADMINS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def setup_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Set default values for optional variables
    os.environ.setdefault('PORT', '8080')
    
    return check_environment()

def kill_process(process):
    """Safely kill a process"""
    if process is None:
        return
    
    try:
        if process.poll() is None:
            process.terminate()
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()
    except Exception as e:
        logger.exception(f"Error killing process: {e}")

def run_bot():
    """Run the Telegram bot"""
    global telegram_bot_process
    
    with process_lock:
        logger.info("Starting Telegram bot...")
        try:
            # Make sure the script is executable
            subprocess.run(['chmod', '+x', 'run_bot.sh'])
            
            # Start the bot process
            telegram_bot_process = subprocess.Popen(
                ['./run_bot.sh'],
                stdout=open('bot.log', 'w'),
                stderr=subprocess.STDOUT
            )
            logger.info(f"Telegram bot started with PID {telegram_bot_process.pid}")
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")

def run_web():
    """Run the web interface"""
    global web_server_process
    
    with process_lock:
        logger.info("Starting web server...")
        try:
            # Make sure the script is executable
            subprocess.run(['chmod', '+x', 'run_web.sh'])
            
            # Start the web server process
            web_server_process = subprocess.Popen(
                ['./run_web.sh'],
                stdout=open('web.log', 'w'),
                stderr=subprocess.STDOUT
            )
            logger.info(f"Web server started with PID {web_server_process.pid}")
        except Exception as e:
            logger.error(f"Error starting web server: {e}")

def run_control_panel():
    """Run the control panel"""
    global control_panel_process
    
    with process_lock:
        logger.info("Starting control panel...")
        try:
            control_panel_process = subprocess.Popen(
                ['python', 'control_panel.py'],
                stdout=open('control_panel.log', 'w'),
                stderr=subprocess.STDOUT
            )
            logger.info(f"Control panel started with PID {control_panel_process.pid}")
        except Exception as e:
            logger.error(f"Error starting control panel: {e}")

def signal_handler(signum, frame):
    """Handle termination signals to shut down cleanly"""
    logger.info(f"Received signal {signum}, shutting down...")
    
    with process_lock:
        if telegram_bot_process:
            kill_process(telegram_bot_process)
        if web_server_process:
            kill_process(web_server_process)
        if control_panel_process:
            kill_process(control_panel_process)
    
    sys.exit(0)

def main():
    """Main function that starts all services"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Movie Series Bot services...")
    
    # Load environment variables
    if not setup_environment():
        logger.error("Failed to set up environment. Check the required variables.")
        return
    
    # Start all services
    run_control_panel()  # Start control panel first
    time.sleep(2)  # Give control panel time to start
    
    # Optionally auto-start the bot and web server
    run_bot()
    run_web()
    
    try:
        logger.info("All services started. Press Ctrl+C to stop.")
        # Keep the main thread alive
        while True:
            time.sleep(60)
            
            # Check if processes are still running and restart if needed
            with process_lock:
                if control_panel_process and control_panel_process.poll() is not None:
                    logger.warning("Control panel stopped. Restarting...")
                    run_control_panel()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()