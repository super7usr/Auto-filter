"""
File mapping utilities for connecting file_id to message_id and vice versa.
This module acts as a bridge between the database and streaming functionality.
"""

import logging
from info import BIN_CHANNEL
from utils import temp

# In-memory cache to reduce database lookups
file_message_cache = {}

async def get_message_id_from_file_id(file_id):
    """
    Look up a message_id based on a file_id.
    First checks the in-memory cache, then queries Telegram.
    
    Args:
        file_id: The file_id to look up
        
    Returns:
        int: message_id if found, None otherwise
    """
    try:
        # First check our cache
        if file_id in file_message_cache:
            return file_message_cache[file_id]
            
        # If not in cache, we need to search for it
        # This is an expensive operation that should be avoided
        # The better solution is to store both file_id and message_id when indexing files
        if not temp.BOT:
            logging.error("Bot instance not available for lookup")
            return None
            
        # Query the last 1000 messages in the bin channel
        # This is a limitation, but it's better than nothing
        messages = []
        try:
            async for msg in temp.BOT.iter_messages(BIN_CHANNEL, limit=1000):
                messages.append(msg)
        except Exception as e:
            logging.error(f"Error iterating messages: {str(e)}")
            return None
            
        # Look for a message that contains the file_id
        for msg in messages:
            if msg.media:
                # Extract the file_id from the message
                msg_file_id = None
                if hasattr(msg, 'document') and msg.document:
                    msg_file_id = msg.document.file_id
                elif hasattr(msg, 'video') and msg.video:
                    msg_file_id = msg.video.file_id
                elif hasattr(msg, 'audio') and msg.audio:
                    msg_file_id = msg.audio.file_id
                elif hasattr(msg, 'photo') and msg.photo:
                    if len(msg.photo) > 0:
                        msg_file_id = msg.photo[-1].file_id
                
                # For simplicity in comparing file_ids, we'll just check if one contains the other
                # This is not 100% accurate but should work for most cases
                if msg_file_id and (file_id in msg_file_id or msg_file_id in file_id):
                    # Found a match, cache it and return
                    file_message_cache[file_id] = msg.id
                    return msg.id
        
        # If we get here, no match was found
        logging.warning(f"No message found for file_id: {file_id}")
        return None
        
    except Exception as e:
        logging.error(f"Error in get_message_id_from_file_id: {str(e)}")
        return None

async def get_file_id_from_message_id(message_id):
    """
    Look up a file_id based on a message_id.
    
    Args:
        message_id: The message_id to look up
        
    Returns:
        str: file_id if found, None otherwise
    """
    try:
        # Check if we have this message_id cached
        for file_id, cached_msg_id in file_message_cache.items():
            if cached_msg_id == message_id:
                return file_id
                
        # If not in cache, fetch the message
        if not temp.BOT:
            logging.error("Bot instance not available for lookup")
            return None
            
        try:
            message = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
            if not message or not message.media:
                logging.warning(f"No media found in message with ID: {message_id}")
                return None
                
            # Extract file_id from the message
            file_id = None
            if hasattr(message, 'document') and message.document:
                file_id = message.document.file_id
            elif hasattr(message, 'video') and message.video:
                file_id = message.video.file_id
            elif hasattr(message, 'audio') and message.audio:
                file_id = message.audio.file_id
            elif hasattr(message, 'photo') and message.photo:
                if len(message.photo) > 0:
                    file_id = message.photo[-1].file_id
                    
            if file_id:
                # Cache this mapping for future lookups
                file_message_cache[file_id] = message_id
                return file_id
            else:
                logging.warning(f"Could not extract file_id from message with ID: {message_id}")
                return None
        except Exception as e:
            logging.error(f"Error fetching message with ID {message_id}: {str(e)}")
            return None
    
    except Exception as e:
        logging.error(f"Error in get_file_id_from_message_id: {str(e)}")
        return None