#!/bin/bash

# Load environment variables
source .env

# Fix case sensitivity issue in database name
export DATABASE_NAME=Cluster0

# Print startup message
echo "Starting Telegram Bot..."
echo "Started at $(date)"

# Run the bot
python run.py
