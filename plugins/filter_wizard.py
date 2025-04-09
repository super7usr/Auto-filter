import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from info import ADMINS, LOG_CHANNEL, INDEX_CHANNELS
from utils import get_settings, save_group_settings, temp
from Script import script

# Track wizard state for users
wizard_states = {}
WIZARD_TIMEOUT = 300  # 5 minutes timeout

class WizardState:
    """Class to track user's current state in the wizard"""
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.step = 0
        self.settings = {}
        self.last_activity = asyncio.get_event_loop().time()
        self.msg_to_delete = []
    
    def update_activity(self):
        """Update the last activity time"""
        self.last_activity = asyncio.get_event_loop().time()
    
    def add_message_to_delete(self, message_id):
        """Add a message to be deleted when wizard completes"""
        self.msg_to_delete.append(message_id)
        
    def is_expired(self):
        """Check if the wizard session has expired"""
        current_time = asyncio.get_event_loop().time()
        return (current_time - self.last_activity) > WIZARD_TIMEOUT


# Command to start the filter wizard
@Client.on_message(filters.command("setup_filters") & filters.group)
async def start_filter_wizard(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is admin
    is_admin = False
    try:
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception as e:
        pass
    
    if not is_admin and user_id not in ADMINS:
        await message.reply("You need to be an admin to use this command.")
        return
    
    # Create a new wizard state
    wizard_states[user_id] = WizardState(user_id, chat_id)
    
    # Get current settings
    current_settings = await get_settings(chat_id)
    wizard_states[user_id].settings = current_settings
    
    # Introduction message
    intro_text = (
        "🧙‍♂️ <b>Welcome to the Filter Setup Wizard!</b>\n\n"
        "This wizard will help you configure your filtering preferences step by step. "
        "At each step, you can choose your preferred settings.\n\n"
        "<b>What would you like to configure?</b>"
    )
    
    # Main configuration options
    buttons = [
        [InlineKeyboardButton("📝 Auto Filter Settings", callback_data="wizard_auto_filter")],
        [InlineKeyboardButton("🔍 Search & Results Settings", callback_data="wizard_search_settings")],
        [InlineKeyboardButton("🎬 Media Display Settings", callback_data="wizard_media_settings")],
        [InlineKeyboardButton("⏰ Time & Delete Settings", callback_data="wizard_time_settings")],
        [InlineKeyboardButton("❌ Cancel Setup", callback_data="wizard_cancel")]
    ]
    
    reply = await message.reply(
        intro_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    
    # Add this message to the list to delete later
    wizard_states[user_id].add_message_to_delete(reply.id)
    wizard_states[user_id].add_message_to_delete(message.id)


# Handle wizard callback queries
@Client.on_callback_query(filters.regex('^wizard_'))
async def filter_wizard_callback(client, query):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    callback_data = query.data
    
    # Check if there's an active wizard session for this user
    if user_id not in wizard_states:
        await query.answer("Wizard session expired. Please start again with /setup_filters", show_alert=True)
        return
    
    # Get wizard state
    wizard = wizard_states[user_id]
    
    # Check if wizard has timed out
    if wizard.is_expired():
        await query.answer("Wizard session timed out. Please start again with /setup_filters", show_alert=True)
        del wizard_states[user_id]
        return
    
    # Update activity timestamp
    wizard.update_activity()
    
    # Process based on callback data
    if callback_data == "wizard_cancel":
        await handle_wizard_cancel(client, query)
        return
    
    elif callback_data == "wizard_complete":
        await handle_wizard_complete(client, query)
        return
    
    elif callback_data == "wizard_auto_filter":
        await show_auto_filter_settings(client, query)
        return
        
    elif callback_data == "wizard_search_settings":
        await show_search_settings(client, query)
        return
        
    elif callback_data == "wizard_media_settings":
        await show_media_settings(client, query)
        return
        
    elif callback_data == "wizard_time_settings":
        await show_time_settings(client, query)
        return
    
    # Handle specific settings toggles
    elif callback_data.startswith("toggle_"):
        await handle_toggle_setting(client, query)
        return
        
    # Handle back button
    elif callback_data == "wizard_back_to_main":
        await show_main_menu(client, query)
        return
        
    # Handle time setting changes
    elif callback_data.startswith("set_time_"):
        await handle_time_setting(client, query)
        return


async def show_main_menu(client, query):
    """Show the main wizard menu"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    
    intro_text = (
        "🧙‍♂️ <b>Filter Setup Wizard</b>\n\n"
        "What would you like to configure?"
    )
    
    buttons = [
        [InlineKeyboardButton("📝 Auto Filter Settings", callback_data="wizard_auto_filter")],
        [InlineKeyboardButton("🔍 Search & Results Settings", callback_data="wizard_search_settings")],
        [InlineKeyboardButton("🎬 Media Display Settings", callback_data="wizard_media_settings")],
        [InlineKeyboardButton("⏰ Time & Delete Settings", callback_data="wizard_time_settings")],
        [InlineKeyboardButton("✅ Complete Setup", callback_data="wizard_complete")],
        [InlineKeyboardButton("❌ Cancel Setup", callback_data="wizard_cancel")]
    ]
    
    await query.message.edit_text(
        intro_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def show_auto_filter_settings(client, query):
    """Show auto filter settings options"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    settings = wizard.settings
    
    auto_filter_status = "✅ Enabled" if settings["auto_filter"] else "❌ Disabled"
    spell_check_status = "✅ Enabled" if settings["spell_check"] else "❌ Disabled"
    
    text = (
        "📝 <b>Auto Filter Settings</b>\n\n"
        "Configure how the bot searches and filters content.\n\n"
        "Auto Filter: {0}\n"
        "Automatically respond to queries with matching files.\n\n"
        "Spell Check: {1}\n"
        "Suggest corrections when no results are found."
    ).format(auto_filter_status, spell_check_status)
    
    buttons = [
        [InlineKeyboardButton("Toggle Auto Filter", callback_data="toggle_auto_filter")],
        [InlineKeyboardButton("Toggle Spell Check", callback_data="toggle_spell_check")],
        [InlineKeyboardButton("« Back", callback_data="wizard_back_to_main")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def show_search_settings(client, query):
    """Show search and results settings"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    settings = wizard.settings
    
    links_status = "✅ Enabled" if settings["links"] else "❌ Disabled"
    
    text = (
        "🔍 <b>Search & Results Settings</b>\n\n"
        "Configure how search results are displayed.\n\n"
        "Link Mode: {0}\n"
        "Show results as links instead of buttons.\n\n"
    ).format(links_status)
    
    buttons = [
        [InlineKeyboardButton("Toggle Link Mode", callback_data="toggle_links")],
        [InlineKeyboardButton("« Back", callback_data="wizard_back_to_main")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def show_media_settings(client, query):
    """Show media display settings"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    settings = wizard.settings
    
    imdb_status = "✅ Enabled" if settings["imdb"] else "❌ Disabled"
    shortlink_status = "✅ Enabled" if settings["shortlink"] else "❌ Disabled"
    
    text = (
        "🎬 <b>Media Display Settings</b>\n\n"
        "Configure how media information is displayed.\n\n"
        "IMDb Details: {0}\n"
        "Show IMDb information with search results.\n\n"
        "Use Shortlink: {1}\n"
        "Use shortlinks for sharing files."
    ).format(imdb_status, shortlink_status)
    
    buttons = [
        [InlineKeyboardButton("Toggle IMDb Details", callback_data="toggle_imdb")],
        [InlineKeyboardButton("Toggle Shortlink", callback_data="toggle_shortlink")],
        [InlineKeyboardButton("« Back", callback_data="wizard_back_to_main")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def show_time_settings(client, query):
    """Show time-related settings"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    settings = wizard.settings
    
    from utils import get_readable_time
    from info import DELETE_TIME
    
    auto_delete_status = "✅ Enabled ({0})".format(get_readable_time(DELETE_TIME)) if settings["auto_delete"] else "❌ Disabled"
    
    text = (
        "⏰ <b>Time & Delete Settings</b>\n\n"
        "Configure auto-deletion and time-related settings.\n\n"
        "Auto Delete: {0}\n"
        "Automatically delete search results after a period of time.\n\n"
        "Choose how long to keep messages before deletion:"
    ).format(auto_delete_status)
    
    buttons = [
        [InlineKeyboardButton("Toggle Auto Delete", callback_data="toggle_auto_delete")],
        [
            InlineKeyboardButton("5 Minutes", callback_data="set_time_300"),
            InlineKeyboardButton("15 Minutes", callback_data="set_time_900")
        ],
        [
            InlineKeyboardButton("30 Minutes", callback_data="set_time_1800"),
            InlineKeyboardButton("1 Hour", callback_data="set_time_3600")
        ],
        [InlineKeyboardButton("« Back", callback_data="wizard_back_to_main")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def handle_toggle_setting(client, query):
    """Handle toggling a specific setting"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    chat_id = wizard.chat_id
    settings = wizard.settings
    setting_name = query.data.replace("toggle_", "")
    
    # Toggle the setting
    current_value = settings.get(setting_name, False)
    settings[setting_name] = not current_value
    
    # Save to database
    await save_group_settings(chat_id, setting_name, not current_value)
    
    # Update wizard state
    wizard.settings = settings
    
    # Show success message
    new_status = "enabled" if not current_value else "disabled"
    await query.answer(f"{setting_name.replace('_', ' ').title()} {new_status}", show_alert=True)
    
    # Return to the appropriate settings menu
    if setting_name in ["auto_filter", "spell_check"]:
        await show_auto_filter_settings(client, query)
    elif setting_name in ["links"]:
        await show_search_settings(client, query)
    elif setting_name in ["imdb", "shortlink"]:
        await show_media_settings(client, query)
    elif setting_name in ["auto_delete"]:
        await show_time_settings(client, query)


async def handle_time_setting(client, query):
    """Handle setting time duration for auto-delete"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    chat_id = wizard.chat_id
    
    # Extract time in seconds from callback data
    seconds = int(query.data.split("_")[2])
    
    # We need to update DELETE_TIME in info.py, but since that would require
    # editing the file, we'll store this in settings with a special key
    await save_group_settings(chat_id, "delete_time", seconds)
    wizard.settings["delete_time"] = seconds
    
    # Turn on auto_delete if not already on
    if not wizard.settings["auto_delete"]:
        await save_group_settings(chat_id, "auto_delete", True)
        wizard.settings["auto_delete"] = True
    
    await query.answer(f"Auto-delete time set to {seconds//60} minutes", show_alert=True)
    await show_time_settings(client, query)


async def handle_wizard_cancel(client, query):
    """Handle cancellation of the wizard"""
    user_id = query.from_user.id
    
    # Delete all wizard messages
    for msg_id in wizard_states[user_id].msg_to_delete:
        try:
            await client.delete_messages(query.message.chat.id, msg_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    # Delete the wizard state
    del wizard_states[user_id]
    
    # Send cancellation message
    await query.message.edit_text(
        "❌ Filter setup wizard cancelled.\n\nNo changes were made to your filter settings.",
        parse_mode=enums.ParseMode.HTML
    )


async def handle_wizard_complete(client, query):
    """Handle completion of the wizard"""
    user_id = query.from_user.id
    wizard = wizard_states[user_id]
    
    # Prepare a summary of changes
    settings = wizard.settings
    summary_text = (
        "✅ <b>Filter Setup Complete!</b>\n\n"
        "<b>Your filter settings:</b>\n"
        f"• Auto Filter: {'Enabled' if settings['auto_filter'] else 'Disabled'}\n"
        f"• Spell Check: {'Enabled' if settings['spell_check'] else 'Disabled'}\n"
        f"• IMDb Details: {'Enabled' if settings['imdb'] else 'Disabled'}\n"
        f"• Link Mode: {'Enabled' if settings['links'] else 'Disabled'}\n"
        f"• Shortlink: {'Enabled' if settings['shortlink'] else 'Disabled'}\n"
        f"• Auto Delete: {'Enabled' if settings['auto_delete'] else 'Disabled'}\n"
    )
    
    if settings.get('auto_delete', False):
        from utils import get_readable_time
        delete_time = settings.get('delete_time', 300)  # Default 5 minutes
        summary_text += f"• Delete After: {get_readable_time(delete_time)}\n"
    
    summary_text += "\nYou can change these settings anytime with /settings command."
    
    # Send completion message
    await query.message.edit_text(
        summary_text,
        parse_mode=enums.ParseMode.HTML
    )
    
    # Delete the wizard state
    del wizard_states[user_id]


# Cleanup expired wizard sessions
async def cleanup_expired_sessions():
    while True:
        try:
            # Check for expired sessions
            expired_users = []
            for user_id, wizard in wizard_states.items():
                if wizard.is_expired():
                    expired_users.append(user_id)
            
            # Remove expired sessions
            for user_id in expired_users:
                del wizard_states[user_id]
                
        except Exception as e:
            print(f"Error in cleanup: {e}")
            
        # Check every minute
        await asyncio.sleep(60)


# Start cleanup task when bot starts
@Client.on_message(filters.command("start_filter_wizard_cleanup") & filters.user(ADMINS))
async def start_cleanup_task(client, message):
    asyncio.create_task(cleanup_expired_sessions())
    await message.reply("Filter wizard cleanup task started.")