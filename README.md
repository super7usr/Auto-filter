# Auto Filter Bot with Shortener

A sophisticated Telegram bot for filtering and sharing content with powerful features including auto-filtering, file-management, and URL shortener integration.

## Features

- **Automatic Content Filtering**: Intelligently filter and organize content in your Telegram groups
- **URL Shortener Integration**: Monetize links with your preferred URL shortener
- **Web Admin Interface**: Manage your bot through a convenient web interface
- **MongoDB Database**: Reliable storage for bot data
- **Telegram API Integration**: Built with Pyrogram for seamless Telegram interaction
- **Automatic Backup**: Creates backups of the code and sends to the admin when the bot restarts

## Setup Instructions

1. Update the `.env` file with your configuration:
   - **Required**: Replace `LOG_CHANNEL` and `BIN_CHANNEL` with valid Telegram channel IDs where the bot is an admin
   - Configure your MongoDB connection (already set up)
   - Set your admin user ID, shortener API details, etc.

2. Start the web server:
   ```bash
   ./run_web.sh
   ```

3. Once valid channel IDs are configured, start the bot:
   ```bash
   ./run_bot.sh
   ```

## Important Notes

- The bot must be an admin in both `LOG_CHANNEL` and `BIN_CHANNEL` Telegram channels
- The MongoDB database name is case-sensitive (`Cluster0`)
- To add the bot to a group, make it an admin with appropriate permissions
- Configure your URL shortener details in the group settings after adding the bot

## Web Interface

The web interface is available at `http://0.0.0.0:5000` and provides streaming functionality and admin controls.

## Commands

| Command | Description |
|---------|-------------|
| /start | Start the bot |
| /settings | Configure group settings |
| /help | Show help message |
| /stats | Show bot statistics (admin only) |
| /set_shortlink | Set up your URL shortener |

For more commands, use `/help` after starting the bot.
