#!/bin/bash

# Load environment variables
source .env

# Print startup message
echo "Starting Web Server..."
echo "Started at $(date)"

# Run the web server
python web_server.py
