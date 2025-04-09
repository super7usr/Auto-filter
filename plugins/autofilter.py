import re
import asyncio
import logging
from typing import List, Dict, Any
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified
from info import MAX_BUTTONS, BUTTON_ROW_COUNT, ADMINS
import logging

LOGGER = logging.getLogger(__name__)

@Client.on_message(filters.text & filters.group)
async def auto_filter(client, message):
    """
    Filter messages in a group and respond with matching files
    """
    # Skip if the message has less than 3 characters
    if len(message.text) < 3:
        return
    
    # Get the chat ID and query text
    chat_id = message.chat.id
    query = message.text.strip()
    
    # Check if this chat has filters
    filter_chats = await client.db.get_filter_chats()
    if not filter_chats:
        # No filter chats configured
        return
    
    # Search for filters
    search_results = []
    for filter_chat_id in filter_chats:
        # Search in each filter chat
        results = await client.db.find_filters(filter_chat_id, query, limit=MAX_BUTTONS)
        search_results.extend(results)
    
    if not search_results:
        # No results found
        return
    
    # Create buttons for search results
    buttons = []
    for result in search_results[:MAX_BUTTONS]:
        # Format file size
        size = result["file_size"]
        size_text = ""
        if size:
            if size < 1024 * 1024:  # Less than 1MB
                size_text = f" [{size / 1024:.1f} KB]"
            else:  # 1MB or larger
                size_text = f" [{size / (1024 * 1024):.1f} MB]"
        
        # Create button text and data
        button_text = f"{result['file_name']}{size_text}"
        button_data = f"file_{result['file_id']}"
        
        buttons.append([InlineKeyboardButton(button_text, callback_data=button_data)])
    
    # Add a search button
    buttons.append([
        InlineKeyboardButton("🔍 Search Again", switch_inline_query_current_chat=query)
    ])
    
    # Organize buttons into rows
    keyboard = []
    for i in range(0, len(buttons), BUTTON_ROW_COUNT):
        row = []
        for j in range(i, min(i + BUTTON_ROW_COUNT, len(buttons))):
            row.extend(buttons[j])
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the search results
    try:
        await message.reply_text(
            f"Found {len(search_results)} results for '{query}':",
            reply_markup=reply_markup,
            quote=True
        )
    except FloodWait as e:
        # Handle flood wait
        LOGGER.warning(f"FloodWait: Sleeping for {e.x} seconds")
        await asyncio.sleep(e.x)
        await message.reply_text(
            f"Found {len(search_results)} results for '{query}':",
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        LOGGER.error(f"Error in auto_filter: {str(e)}")

@Client.on_callback_query(filters.regex(r"^file_(.*)"))
async def file_callback(client, callback_query):
    """
    Handle file button callbacks
    """
    file_id = callback_query.data.split("_", 1)[1]
    
    try:
        # Send the file
        await client.send_cached_media(
            chat_id=callback_query.message.chat.id,
            file_id=file_id,
            reply_to_message_id=callback_query.message.reply_to_message.message_id if callback_query.message.reply_to_message else None
        )
        # Answer the callback query
        await callback_query.answer("File sent successfully!")
    except Exception as e:
        LOGGER.error(f"Error sending file: {str(e)}")
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@Client.on_message(filters.command(["add", "filter"]) & filters.user(ADMINS))
async def add_filter_command(client, message: Message):
    """
    Add a new channel for filtering content
    """
    args = message.text.split(" ", 1)
    
    if len(args) < 2:
        # Missing channel ID or username
        await message.reply_text(
            "Please provide a channel ID or username.\n"
            "Usage: `/add channel_id` or `/add @username`"
        )
        return
    
    channel = args[1].strip()
    
    # Try to get chat ID from username or ID
    try:
        if channel.startswith("@"):
            chat = await client.get_chat(channel)
        else:
            chat = await client.get_chat(int(channel))
        
        chat_id = chat.id
        chat_title = chat.title
        
        # Check if bot is admin in the channel
        bot_member = await client.get_chat_member(chat_id, "me")
        if bot_member.status != "administrator":
            await message.reply_text(
                f"I need to be an administrator in {chat_title} to index files."
            )
            return
        
        # Save the channel to database and index files
        await client.db.add_chat(chat_id, chat_title)
        await message.reply_text(
            f"Successfully added channel: {chat_title}\n"
            f"Now indexing files from this channel. This might take some time."
        )
        
        # Start indexing
        await index_files(client, chat_id, message)
        
    except Exception as e:
        LOGGER.error(f"Error adding channel: {str(e)}")
        await message.reply_text(f"Error: {str(e)}")

async def index_files(client, chat_id, message=None):
    """
    Index all media files from a chat
    """
    try:
        # Get chat information
        chat = await client.get_chat(chat_id)
        
        # Send status message
        if message:
            status_message = await message.reply_text(
                f"Indexing files from {chat.title}. This might take some time..."
            )
        
        # Initialize counters
        total_messages = 0
        indexed_files = 0
        
        # Iterate through all messages in the chat
        async for msg in client.get_chat_history(chat_id):
            total_messages += 1
            
            # Update status every 100 messages
            if message and total_messages % 100 == 0:
                try:
                    await status_message.edit_text(
                        f"Indexing files from {chat.title}...\n"
                        f"Total messages scanned: {total_messages}\n"
                        f"Indexed files: {indexed_files}"
                    )
                except MessageNotModified:
                    pass
                
            # Check for media types
            if msg.document:
                media = msg.document
                file_type = "document"
            elif msg.video:
                media = msg.video
                file_type = "video"
            elif msg.audio:
                media = msg.audio
                file_type = "audio"
            elif msg.photo:
                media = msg.photo
                file_type = "photo"
            else:
                # Skip if no media
                continue
                
            # Get file name
            if hasattr(media, 'file_name') and media.file_name:
                file_name = media.file_name
            else:
                # Generate a name if none is available
                file_name = f"{file_type}_{media.file_id[-8:]}"
                
            # Get file size
            if hasattr(media, 'file_size'):
                file_size = media.file_size
            else:
                file_size = 0
                
            # Extract text for search
            if msg.caption:
                text = msg.caption
            else:
                text = file_name
                
            # Add file to database
            await client.db.add_filter(
                chat_id=chat_id,
                file_id=media.file_id,
                text=text,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type
            )
            
            indexed_files += 1
            
        # Send final status
        if message:
            await status_message.edit_text(
                f"✅ Successfully indexed {indexed_files} files from {chat.title}.\n"
                f"Total messages scanned: {total_messages}"
            )
            
    except Exception as e:
        LOGGER.error(f"Error indexing files: {str(e)}")
        if message:
            await message.reply_text(f"Error indexing files: {str(e)}")

@Client.on_message(filters.command("del") & filters.user(ADMINS))
async def delete_filter_command(client, message: Message):
    """
    Delete a channel from filter list
    """
    args = message.text.split(" ", 1)
    
    if len(args) < 2:
        # Missing channel ID or username
        await message.reply_text(
            "Please provide a channel ID or username.\n"
            "Usage: `/del channel_id` or `/del @username`"
        )
        return
    
    channel = args[1].strip()
    
    try:
        if channel.startswith("@"):
            chat = await client.get_chat(channel)
            chat_id = chat.id
        else:
            chat_id = int(channel)
            chat = await client.get_chat(chat_id)
        
        # Delete all filters for this chat
        await client.db.delete_all_filters(chat_id)
        
        await message.reply_text(
            f"Successfully deleted all filters from: {chat.title}"
        )
        
    except Exception as e:
        LOGGER.error(f"Error deleting filters: {str(e)}")
        await message.reply_text(f"Error: {str(e)}")

@Client.on_message(filters.command("delall") & filters.user(ADMINS))
async def delete_all_filters_command(client, message: Message):
    """
    Delete all filters from all channels
    """
    # Confirm with the user
    await message.reply_text(
        "This will delete ALL filters from ALL channels.\n"
        "Are you sure? Send `/delall confirm` to proceed."
    )
    
    # Check if the user sent the confirmation
    if len(message.text.split()) == 2 and message.text.split()[1].lower() == "confirm":
        # Get all filter chats
        filter_chats = await client.db.get_filter_chats()
        
        if not filter_chats:
            await message.reply_text("No filters to delete.")
            return
        
        # Delete all filters from each chat
        for chat_id in filter_chats:
            await client.db.delete_all_filters(chat_id)
        
        await message.reply_text("Successfully deleted all filters.")
    
@Client.on_message(filters.command("filters") & filters.user(ADMINS))
async def list_filters_command(client, message: Message):
    """
    List all filter channels
    """
    filter_chats = await client.db.get_filter_chats()
    
    if not filter_chats:
        await message.reply_text("No filter channels are set up.")
        return
    
    text = "**Filter Channels:**\n\n"
    
    for index, chat_id in enumerate(filter_chats, 1):
        try:
            chat = await client.get_chat(chat_id)
            filter_count = await client.db.total_filters_count(chat_id)
            text += f"{index}. {chat.title} [`{chat_id}`] - {filter_count} filters\n"
        except Exception as e:
            text += f"{index}. Unknown [`{chat_id}`] - Error: {str(e)}\n"
    
    await message.reply_text(text)
