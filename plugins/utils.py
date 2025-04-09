import re
import time
import logging
import asyncio
import datetime
from typing import Dict, List
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified, FloodWait
from config import ADMINS, LOGGER

# Helper functions
def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to readable time format
    """
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

def get_readable_size(size_in_bytes: int) -> str:
    """
    Convert size in bytes to human-readable format
    """
    if size_in_bytes is None:
        return "0B"
    
    index = 0
    size_units = ["B", "KB", "MB", "GB", "TB", "PB"]
    
    while size_in_bytes >= 1024 and index < len(size_units) - 1:
        size_in_bytes /= 1024
        index += 1
        
    return f"{size_in_bytes:.2f}{size_units[index]}"

# Command handlers
@Client.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    """
    Check bot response time
    """
    start_time = time.time()
    msg = await message.reply_text("Pinging...")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000, 3)
    uptime = get_readable_time((time.time() - client.start_time))
    
    await msg.edit_text(
        f"**PONG!**\n⏱️ `{ping_time}ms`\n⬆️ Uptime: {uptime}"
    )

@Client.on_message(filters.command("info"))
async def info_command(client, message: Message):
    """
    Get information about a user
    """
    # Check if command is a reply to a message
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        # Get user by username or id
        try:
            user_id = message.command[1]
            if user_id.startswith("@"):
                # It's a username
                user = await client.get_users(user_id)
            elif user_id.isdigit():
                # It's a user id
                user = await client.get_users(int(user_id))
            else:
                await message.reply_text("Invalid username or ID.")
                return
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            return
    else:
        # Get info of the command sender
        user = message.from_user
    
    # Create message
    text = f"**User Information**\n\n"
    text += f"**Name:** {user.mention}\n"
    text += f"**ID:** `{user.id}`\n"
    text += f"**Username:** @{user.username if user.username else 'None'}\n"
    text += f"**DC ID:** {user.dc_id if user.dc_id else 'Unknown'}\n"
    text += f"**Status:** {user.status if hasattr(user, 'status') else 'Unknown'}\n"
    text += f"**Is Bot:** {'Yes' if user.is_bot else 'No'}\n"
    text += f"**Is Scam:** {'Yes' if user.is_scam else 'No'}\n"
    text += f"**Is Verified:** {'Yes' if user.is_verified else 'No'}\n"
    
    # Create keyboard
    keyboard = [
        [InlineKeyboardButton("Profile Link", url=f"tg://user?id={user.id}")]
    ]
    
    # Add admin check button if in a group
    if message.chat.type != "private":
        keyboard.append([InlineKeyboardButton("Check Admin Rights", callback_data=f"check_admin_{user.id}")])
    
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex(r"^check_admin_(.*)"))
async def check_admin_callback(client, callback_query):
    """
    Check admin rights of a user
    """
    user_id = int(callback_query.data.split("_")[2])
    chat_id = callback_query.message.chat.id
    
    try:
        # Get the admin status
        member = await client.get_chat_member(chat_id, user_id)
        
        if member.status == "creator":
            status_text = "👑 Owner"
        elif member.status == "administrator":
            status_text = "⚜️ Administrator"
            
            # Check admin rights
            admin_rights = []
            if member.can_change_info:
                admin_rights.append("Change Chat Info")
            if member.can_delete_messages:
                admin_rights.append("Delete Messages")
            if member.can_restrict_members:
                admin_rights.append("Ban Users")
            if member.can_invite_users:
                admin_rights.append("Invite Users")
            if member.can_pin_messages:
                admin_rights.append("Pin Messages")
            if member.can_promote_members:
                admin_rights.append("Add Admins")
            
            status_text += "\n**Privileges:**\n- " + "\n- ".join(admin_rights)
        else:
            status_text = "Not an Admin"
        
        await callback_query.answer(f"Admin status: {member.status}", show_alert=True)
        await callback_query.edit_message_text(
            callback_query.message.text + f"\n\n**Admin Status:** {status_text}"
        )
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@Client.on_message(filters.command("purge") & filters.group)
async def purge_command(client, message: Message):
    """
    Purge messages from a user
    """
    # Check if the bot has delete permission
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_delete_messages:
        await message.reply_text("I don't have permission to delete messages.")
        return
    
    # Check if the user has delete permission
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_delete_messages and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to delete messages.")
        return
    
    # Check if the message is a reply
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to start purging from.")
        return
    
    # Get message IDs
    start_message_id = message.reply_to_message.message_id
    end_message_id = message.message_id
    
    # Create a list of message IDs to delete
    message_ids = list(range(start_message_id, end_message_id + 1))
    
    # Count number of messages to delete
    msg_count = len(message_ids)
    
    # Check if there are too many messages to delete
    if msg_count > 100:
        await message.reply_text(
            "You can only purge up to 100 messages at once."
        )
        return
    
    # Delete messages
    deleted_count = 0
    try:
        # Delete messages
        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=message_ids
        )
        deleted_count = msg_count
    except Exception as e:
        LOGGER.error(f"Error in purge: {str(e)}")
        # Try one by one if bulk delete fails
        for msg_id in message_ids:
            try:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=[msg_id]
                )
                deleted_count += 1
            except Exception:
                pass
    
    # Send success message
    purge_msg = await message.reply_text(f"Purged {deleted_count} messages.")
    
    # Delete the success message after 5 seconds
    await asyncio.sleep(5)
    await purge_msg.delete()
