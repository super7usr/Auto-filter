import asyncio
import logging
from info import ADMINS, AUTO_FILTER, BUTTON_LOCK, WELCOME
from database.users_chats_db import db

logger = logging.getLogger(__name__)

async def handle_check_user_status(client, message):
    """
    Check if user is banned and restrict accordingly
    Args:
        client: Pyrogram client instance
        message: Message object
    """
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # Skip check for admins
    if user_id in ADMINS:
        return
        
    # Check if user is banned
    user = await db.get_user(user_id)
    if user and user.get('banned'):
        try:
            await message.reply_text(f"Sorry, you are banned from using this bot.")
            return False
        except Exception as e:
            logger.error(f"Error in handle_check_user_status: {e}")
    
    return True

async def handle_check_group_status(client, message):
    """
    Check if group is banned and restrict accordingly
    Args:
        client: Pyrogram client instance
        message: Message object
    """
    # Only proceed if message is in a group
    if not message.chat or message.chat.type not in ["group", "supergroup"]:
        return True
        
    chat_id = message.chat.id
    
    # Check if group is banned
    chat = await db.get_chat(chat_id)
    if chat and chat.get('is_disabled'):
        try:
            await message.reply_text("Sorry, this group is banned from using this bot.")
            await client.leave_chat(chat_id)
            return False
        except Exception as e:
            logger.error(f"Error in handle_check_group_status: {e}")
    
    return True
