from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, FloodWait
import asyncio
from info import ADMINS

# Helper function to extract user and reason from command
async def extract_user_and_reason(message):
    """Extract the user and reason from a message"""
    args = message.text.split(None, 2)
    
    if len(args) < 2:
        return None, None
    
    user = args[1]
    reason = args[2] if len(args) > 2 else None
    
    # Handle user mention, id, or username
    if user.startswith("@"):
        # It's a username
        username = user
        user_obj = await message.chat.get_member(username)
        user = user_obj.user.id
    elif user.isdigit():
        # It's a user id
        user = int(user)
    elif message.reply_to_message:
        # It's a reply to a message
        user = message.reply_to_message.from_user.id
        reason = args[1] if len(args) > 1 else None
    else:
        return None, None
    
    return user, reason

# Ban command
@Client.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    """Ban a user from the group"""
    # Check if the bot is an admin
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_restrict_members:
        await message.reply_text("I don't have permission to ban users.")
        return
    
    # Check if the command sender is an admin
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_restrict_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to ban users.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to ban.")
        return
    
    # Check if the user to ban is an admin
    try:
        member = await message.chat.get_member(user_id)
        if member.status in ("administrator", "creator"):
            await message.reply_text("I can't ban an admin.")
            return
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        return
    
    # Ban the user
    try:
        await message.chat.ban_member(user_id)
        
        # Get user info
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send ban message
        text = f"{user_mention} has been banned."
        if reason:
            text += f"\nReason: {reason}"
        
        await message.reply_text(text)
    except UserAdminInvalid:
        await message.reply_text("I can't ban an admin.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to ban users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Unban command
@Client.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    """Unban a user from the group"""
    # Check if the bot is an admin
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_restrict_members:
        await message.reply_text("I don't have permission to unban users.")
        return
    
    # Check if the command sender is an admin
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_restrict_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to unban users.")
        return
    
    # Extract user and reason
    user_id, _ = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to unban.")
        return
    
    # Unban the user
    try:
        await message.chat.unban_member(user_id)
        
        # Get user info
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send unban message
        await message.reply_text(f"{user_mention} has been unbanned.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to unban users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Mute command
@Client.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    """Mute a user in the group"""
    # Check if the bot is an admin
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_restrict_members:
        await message.reply_text("I don't have permission to mute users.")
        return
    
    # Check if the command sender is an admin
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_restrict_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to mute users.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to mute.")
        return
    
    # Check if the user to mute is an admin
    try:
        member = await message.chat.get_member(user_id)
        if member.status in ("administrator", "creator"):
            await message.reply_text("I can't mute an admin.")
            return
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        return
    
    # Mute the user
    try:
        await message.chat.restrict_member(
            user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
        )
        
        # Get user info
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send mute message
        text = f"{user_mention} has been muted."
        if reason:
            text += f"\nReason: {reason}"
        
        await message.reply_text(text)
    except UserAdminInvalid:
        await message.reply_text("I can't mute an admin.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to mute users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Unmute command
@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    """Unmute a user in the group"""
    # Check if the bot is an admin
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_restrict_members:
        await message.reply_text("I don't have permission to unmute users.")
        return
    
    # Check if the command sender is an admin
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_restrict_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to unmute users.")
        return
    
    # Extract user
    user_id, _ = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to unmute.")
        return
    
    # Unmute the user
    try:
        await message.chat.restrict_member(
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        
        # Get user info
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send unmute message
        await message.reply_text(f"{user_mention} has been unmuted.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to unmute users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Kick command
@Client.on_message(filters.command("kick") & filters.group)
async def kick_user(client, message: Message):
    """Kick a user from the group"""
    # Check if the bot is an admin
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_restrict_members:
        await message.reply_text("I don't have permission to kick users.")
        return
    
    # Check if the command sender is an admin
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_restrict_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to kick users.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to kick.")
        return
    
    # Check if the user to kick is an admin
    try:
        member = await message.chat.get_member(user_id)
        if member.status in ("administrator", "creator"):
            await message.reply_text("I can't kick an admin.")
            return
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        return
    
    # Kick the user
    try:
        await message.chat.ban_member(user_id)
        await asyncio.sleep(1)  # Wait a bit before unbanning
        await message.chat.unban_member(user_id)  # Unban to make it a kick
        
        # Get user info
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send kick message
        text = f"{user_mention} has been kicked."
        if reason:
            text += f"\nReason: {reason}"
        
        await message.reply_text(text)
    except UserAdminInvalid:
        await message.reply_text("I can't kick an admin.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to kick users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Pin command
@Client.on_message(filters.command("pin") & filters.group)
async def pin_message(client, message: Message):
    """Pin a message in the group"""
    # Check if the bot is an admin with pin permission
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_pin_messages:
        await message.reply_text("I don't have permission to pin messages.")
        return
    
    # Check if the command sender is an admin with pin permission
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_pin_messages and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to pin messages.")
        return
    
    # Check if the message is a reply
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to pin it.")
        return
    
    # Pin the message
    try:
        await message.reply_to_message.pin()
        await message.reply_text("Message pinned successfully.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Unpin command
@Client.on_message(filters.command("unpin") & filters.group)
async def unpin_message(client, message: Message):
    """Unpin a message in the group"""
    # Check if the bot is an admin with pin permission
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_pin_messages:
        await message.reply_text("I don't have permission to unpin messages.")
        return
    
    # Check if the command sender is an admin with pin permission
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_pin_messages and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to unpin messages.")
        return
    
    # Check if the command has arguments
    if len(message.command) > 1 and message.command[1].lower() == "all":
        # Unpin all messages
        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply_text("All pinned messages have been unpinned.")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        # Check if the message is a reply
        if not message.reply_to_message:
            # Unpin the last pinned message
            try:
                await client.unpin_chat_message(message.chat.id)
                await message.reply_text("Last pinned message has been unpinned.")
            except Exception as e:
                await message.reply_text(f"Error: {str(e)}")
        else:
            # Unpin the replied message
            try:
                await message.reply_to_message.unpin()
                await message.reply_text("Message unpinned successfully.")
            except Exception as e:
                await message.reply_text(f"Error: {str(e)}")

# Promote command
@Client.on_message(filters.command("promote") & filters.group)
async def promote_user(client, message: Message):
    """Promote a user to admin in the group"""
    # Check if the bot is an admin with promote permission
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_promote_members:
        await message.reply_text("I don't have permission to promote users.")
        return
    
    # Check if the command sender is an admin with promote permission
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_promote_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to promote users.")
        return
    
    # Extract user
    user_id, _ = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to promote.")
        return
    
    # Promote the user
    try:
        await message.chat.promote_member(
            user_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True
        )
        
        # Get user info
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send promote message
        await message.reply_text(f"{user_mention} has been promoted to admin.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to promote users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Demote command
@Client.on_message(filters.command("demote") & filters.group)
async def demote_user(client, message: Message):
    """Demote an admin to normal user in the group"""
    # Check if the bot is an admin with promote permission
    bot_member = await message.chat.get_member("me")
    if not bot_member.can_promote_members:
        await message.reply_text("I don't have permission to demote users.")
        return
    
    # Check if the command sender is an admin with promote permission
    user_member = await message.chat.get_member(message.from_user.id)
    if not user_member.can_promote_members and message.from_user.id not in ADMINS:
        await message.reply_text("You don't have permission to demote users.")
        return
    
    # Extract user
    user_id, _ = await extract_user_and_reason(message)
    
    if not user_id:
        await message.reply_text("You need to specify a user to demote.")
        return
    
    # Check if the user is an admin
    try:
        member = await message.chat.get_member(user_id)
        if member.status != "administrator":
            await message.reply_text("This user is not an admin.")
            return
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        return
    
    # Demote the user
    try:
        await message.chat.promote_member(
            user_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False
        )
        
        # Get user info
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            user_mention = user.mention
        else:
            try:
                user = await client.get_users(user_id)
                user_mention = user.mention
            except:
                user_mention = f"User {user_id}"
        
        # Send demote message
        await message.reply_text(f"{user_mention} has been demoted.")
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to demote users.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
