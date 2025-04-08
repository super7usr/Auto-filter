#!/bin/bash

# Load environment variables
source .env

echo "Starting Auto Filter Bot Services"
echo "================================="
echo "Started at $(date)"
echo

# Start the web server in the background
echo "Starting Web Server..."
python web_server.py &
WEB_PID=$!
echo "Web Server started with PID: $WEB_PID"
echo

# Give the web server a moment to start
sleep 2

echo "Note: To fully start the Telegram bot, you need valid LOG_CHANNEL and BIN_CHANNEL IDs"
echo "where the bot is an admin. Update these in the .env file."
echo
echo "To start the bot manually, run: ./run_bot.sh"
echo
echo "Web server is running at http://0.0.0.0:5000"
echo

# Wait for the web server process
wait $WEB_PID
