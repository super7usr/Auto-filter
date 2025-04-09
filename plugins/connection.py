from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from config import ADMINS

@Client.on_message(filters.command("connect") & filters.private)
async def connect_command(client, message):
    """
    Connect to a chat for managing filters in PM
    """
    if len(message.command) > 1:
        chat_id = message.command[1]
        
        try:
            chat_id = int(chat_id)
        except ValueError:
            await message.reply_text("Invalid chat ID. Please provide a valid chat ID.")
            return
        
        # Try to get chat info
        try:
            chat = await client.get_chat(chat_id)
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            return
        
        # Check if bot is admin in the chat
        try:
            member = await client.get_chat_member(chat_id, "me")
            if member.status != "administrator":
                await message.reply_text(
                    f"I need to be an administrator in {chat.title} to manage filters."
                )
                return
        except UserNotParticipant:
            await message.reply_text(f"I'm not a member of {chat.title}.")
            return
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            return
        
        # Check if user is admin in the chat
        try:
            user_member = await client.get_chat_member(chat_id, message.from_user.id)
            if user_member.status not in ("administrator", "creator") and message.from_user.id not in ADMINS:
                await message.reply_text(
                    f"You need to be an administrator in {chat.title} to connect to it."
                )
                return
        except UserNotParticipant:
            await message.reply_text(f"You are not a member of {chat.title}.")
            return
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            return
        
        # Save connection to database
        await client.db.add_connection(message.from_user.id, chat_id)
        
        await message.reply_text(
            f"Successfully connected to {chat.title}.\n"
            f"Now you can manage filters of {chat.title} from here."
        )
    else:
        # List all chats the user can connect to
        keyboard = []
        async for dialog in client.get_dialogs():
            if dialog.chat.type in ("supergroup", "channel"):
                # Check if bot is admin in the chat
                try:
                    member = await client.get_chat_member(dialog.chat.id, "me")
                    if member.status == "administrator":
                        # Check if user is admin in the chat
                        try:
                            user_member = await client.get_chat_member(dialog.chat.id, message.from_user.id)
                            if user_member.status in ("administrator", "creator") or message.from_user.id in ADMINS:
                                keyboard.append(
                                    [InlineKeyboardButton(
                                        dialog.chat.title, 
                                        callback_data=f"connect_{dialog.chat.id}"
                                    )]
                                )
                        except Exception:
                            pass
                except Exception:
                    pass
        
        if keyboard:
            await message.reply_text(
                "Select a chat to connect:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await message.reply_text(
                "You don't have any chats where both you and I are administrators.\n"
                "First add me to a chat as an administrator, then you can connect to it."
            )

@Client.on_callback_query(filters.regex(r"^connect_(.*)"))
async def connect_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    
    # Try to get chat info
    try:
        chat = await client.get_chat(chat_id)
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
        return
    
    # Save connection to database
    await client.db.add_connection(user_id, chat_id)
    
    await callback_query.edit_message_text(
        f"Successfully connected to {chat.title}.\n"
        f"Now you can manage filters of {chat.title} from here."
    )

@Client.on_message(filters.command("disconnect") & filters.private)
async def disconnect_command(client, message):
    """
    Disconnect from a currently connected chat
    """
    # Get user connections
    connections = await client.db.get_connections(message.from_user.id)
    
    if not connections:
        await message.reply_text("You are not connected to any chats.")
        return
    
    # If command has argument, disconnect from specific chat
    if len(message.command) > 1:
        try:
            chat_id = int(message.command[1])
            if chat_id not in connections:
                await message.reply_text("You are not connected to this chat.")
                return
            
            # Remove connection
            await client.db.remove_connection(message.from_user.id, chat_id)
            
            # Get chat info
            try:
                chat = await client.get_chat(chat_id)
                chat_title = chat.title
            except:
                chat_title = f"Chat {chat_id}"
            
            await message.reply_text(f"Disconnected from {chat_title}.")
        except ValueError:
            await message.reply_text("Invalid chat ID. Please provide a valid chat ID.")
    else:
        # Create keyboard with all connections
        keyboard = []
        
        for chat_id in connections:
            try:
                chat = await client.get_chat(chat_id)
                keyboard.append(
                    [InlineKeyboardButton(
                        chat.title, 
                        callback_data=f"disconnect_{chat_id}"
                    )]
                )
            except:
                keyboard.append(
                    [InlineKeyboardButton(
                        f"Unknown Chat {chat_id}", 
                        callback_data=f"disconnect_{chat_id}"
                    )]
                )
        
        await message.reply_text(
            "Select a chat to disconnect from:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

@Client.on_callback_query(filters.regex(r"^disconnect_(.*)"))
async def disconnect_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    
    # Remove connection
    await client.db.remove_connection(user_id, chat_id)
    
    # Get chat info
    try:
        chat = await client.get_chat(chat_id)
        chat_title = chat.title
    except:
        chat_title = f"Chat {chat_id}"
    
    await callback_query.edit_message_text(f"Disconnected from {chat_title}.")

@Client.on_message(filters.command("connections") & filters.private)
async def connections_command(client, message):
    """
    List all connected chats
    """
    # Get user connections
    connections = await client.db.get_connections(message.from_user.id)
    
    if not connections:
        await message.reply_text("You are not connected to any chats.")
        return
    
    text = "**Connected Chats:**\n\n"
    
    for index, chat_id in enumerate(connections, 1):
        try:
            chat = await client.get_chat(chat_id)
            text += f"{index}. {chat.title} [`{chat_id}`]\n"
        except Exception as e:
            text += f"{index}. Unknown [`{chat_id}`] - Error: {str(e)}\n"
    
    await message.reply_text(text)
