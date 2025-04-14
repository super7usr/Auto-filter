import os
import json
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, LOG_CHANNEL, SECOND_DATABASE_URL
from database.mongodb_utils import get_mongodb_stats, move_data_between_mongodb, get_all_mongodb_urls
from Script import script
from .check_user_status import handle_check_user_status, handle_check_group_status

logger = logging.getLogger(__name__)

# Command to show MongoDB status
@Client.on_message(filters.command("mongodb_status") & filters.user(ADMINS))
async def mongodb_status_handler(client, message):
    """
    Show status of all configured MongoDB instances
    Usage: /mongodb_status
    """
    await handle_check_user_status(client, message)
    await handle_check_group_status(client, message)
    
    # Send initial processing message
    status_msg = await message.reply_text("<i>Fetching MongoDB status...</i>")
    
    try:
        # Get MongoDB stats
        stats = await get_mongodb_stats()
        
        if not stats:
            await status_msg.edit_text("No MongoDB instances configured.")
            return
        
        # Create status text
        status_text = "<b>📊 MongoDB Status</b>\n\n"
        
        for db in stats:
            status_text += f"<b>🗄️ {db['instance']} ({db.get('url', 'unknown')})</b>\n"
            
            if 'error' in db:
                status_text += f"❌ Error: {db['error']}\n\n"
                continue
                
            status_text += f"📁 Documents: <code>{db['doc_count']:,}</code>\n"
            status_text += f"💾 Storage: <code>{db['storage_size_mb']} MB</code>\n"
            status_text += f"📊 Collection Size: <code>{db['collection_size_mb']} MB</code>\n"
            
            if db['avg_obj_size_kb'] > 0:
                status_text += f"📏 Avg Doc Size: <code>{db['avg_obj_size_kb']} KB</code>\n"
            
            status_text += "\n"
        
        # Add MongoDB management options
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_mongodb_status"),
                InlineKeyboardButton("🔁 Move Data", callback_data="mongodb_move_data")
            ]
        ]
        
        # Add button to go back to admin panel if it exists
        buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])
        
        await status_msg.edit_text(
            status_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    except Exception as e:
        error_msg = f"Error fetching MongoDB status: {e}"
        logger.error(error_msg)
        await status_msg.edit_text(error_msg)


# Callback handler for MongoDB operations
@Client.on_callback_query(filters.regex(r'^(refresh_mongodb_status|mongodb_move_data|confirm_move_data)') & filters.user(ADMINS))
async def mongodb_callback_handler(client, callback_query):
    """Handle MongoDB-related callback queries"""
    query_data = callback_query.data
    
    if query_data == "refresh_mongodb_status":
        # Refresh MongoDB status
        await callback_query.edit_message_text("<i>Refreshing MongoDB status...</i>")
        
        try:
            # Get MongoDB stats
            stats = await get_mongodb_stats()
            
            if not stats:
                await callback_query.edit_message_text("No MongoDB instances configured.")
                return
            
            # Create status text
            status_text = "<b>📊 MongoDB Status</b>\n\n"
            
            for db in stats:
                status_text += f"<b>🗄️ {db['instance']} ({db.get('url', 'unknown')})</b>\n"
                
                if 'error' in db:
                    status_text += f"❌ Error: {db['error']}\n\n"
                    continue
                    
                status_text += f"📁 Documents: <code>{db['doc_count']:,}</code>\n"
                status_text += f"💾 Storage: <code>{db['storage_size_mb']} MB</code>\n"
                status_text += f"📊 Collection Size: <code>{db['collection_size_mb']} MB</code>\n"
                
                if db['avg_obj_size_kb'] > 0:
                    status_text += f"📏 Avg Doc Size: <code>{db['avg_obj_size_kb']} KB</code>\n"
                
                status_text += "\n"
            
            # Add MongoDB management options
            buttons = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_mongodb_status"),
                    InlineKeyboardButton("🔁 Move Data", callback_data="mongodb_move_data")
                ]
            ]
            
            # Add button to go back to admin panel if it exists
            buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])
            
            await callback_query.edit_message_text(
                status_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
        except Exception as e:
            error_msg = f"Error refreshing MongoDB status: {e}"
            logger.error(error_msg)
            await callback_query.edit_message_text(error_msg)
    
    elif query_data == "mongodb_move_data":
        # Show data migration options
        urls = get_all_mongodb_urls()
        
        if len(urls) < 2:
            await callback_query.answer("Need at least 2 MongoDB instances to move data", show_alert=True)
            return
        
        # Create selection buttons for source DB
        buttons = []
        for i, url in enumerate(urls):
            domain = url.split('@')[-1].split('/')[0]  # Extract domain only for security
            buttons.append([
                InlineKeyboardButton(
                    f"Source: DB #{i+1} ({domain})",
                    callback_data=f"select_source_db_{i}"
                )
            ])
        
        # Add back button
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="refresh_mongodb_status")])
        
        await callback_query.edit_message_text(
            "<b>MongoDB Data Migration</b>\n\n"
            "Select the <b>source</b> database to move data from:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query_data.startswith("select_source_db_"):
        # User selected source DB, now select target DB
        source_idx = int(query_data.split("_")[-1])
        urls = get_all_mongodb_urls()
        
        if source_idx >= len(urls):
            await callback_query.answer("Invalid source database", show_alert=True)
            return
        
        # Create selection buttons for target DB
        buttons = []
        for i, url in enumerate(urls):
            if i == source_idx:
                continue  # Skip source DB
                
            domain = url.split('@')[-1].split('/')[0]  # Extract domain only for security
            buttons.append([
                InlineKeyboardButton(
                    f"Target: DB #{i+1} ({domain})",
                    callback_data=f"confirm_move_{source_idx}_to_{i}"
                )
            ])
        
        # Add back button
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="mongodb_move_data")])
        
        source_domain = urls[source_idx].split('@')[-1].split('/')[0]
        await callback_query.edit_message_text(
            f"<b>MongoDB Data Migration</b>\n\n"
            f"Selected source: <b>DB #{source_idx+1}</b> ({source_domain})\n\n"
            f"Now select the <b>target</b> database to move data to:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query_data.startswith("confirm_move_"):
        # Confirm data migration between databases
        parts = query_data.split("_")
        source_idx = int(parts[2])
        target_idx = int(parts[4])
        
        urls = get_all_mongodb_urls()
        if source_idx >= len(urls) or target_idx >= len(urls):
            await callback_query.answer("Invalid database selection", show_alert=True)
            return
        
        source_domain = urls[source_idx].split('@')[-1].split('/')[0]
        target_domain = urls[target_idx].split('@')[-1].split('/')[0]
        
        buttons = [
            [
                InlineKeyboardButton(
                    "✅ Confirm Migration",
                    callback_data=f"start_migration_{source_idx}_to_{target_idx}"
                )
            ],
            [InlineKeyboardButton("🔙 Back", callback_data=f"select_source_db_{source_idx}")]
        ]
        
        await callback_query.edit_message_text(
            f"<b>Confirm MongoDB Data Migration</b>\n\n"
            f"You are about to move data from:\n"
            f"<b>Source:</b> DB #{source_idx+1} ({source_domain})\n"
            f"<b>Target:</b> DB #{target_idx+1} ({target_domain})\n\n"
            f"⚠️ <b>Warning:</b> This operation will:\n"
            f"• Copy all documents from source to target\n"
            f"• Skip documents that already exist in target\n"
            f"• May take a long time for large databases\n\n"
            f"Are you sure you want to continue?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query_data.startswith("start_migration_"):
        # Start the actual migration process
        parts = query_data.split("_")
        source_idx = int(parts[2])
        target_idx = int(parts[4])
        
        urls = get_all_mongodb_urls()
        if source_idx >= len(urls) or target_idx >= len(urls):
            await callback_query.answer("Invalid database selection", show_alert=True)
            return
        
        # Update message to show progress
        await callback_query.edit_message_text(
            "<b>MongoDB Data Migration In Progress</b>\n\n"
            "The migration process has started. This may take some time depending on the amount of data.\n\n"
            "<i>Please wait...</i>"
        )
        
        try:
            # Start data migration
            result = await move_data_between_mongodb(source_idx, target_idx)
            
            if "error" in result:
                error_msg = f"Migration failed: {result['error']}"
                logger.error(error_msg)
                
                buttons = [
                    [InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_mongodb_status")]
                ]
                
                await callback_query.edit_message_text(
                    f"<b>MongoDB Data Migration Failed</b>\n\n"
                    f"❌ Error: {result['error']}",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            
            # Create success message
            success_msg = f"<b>MongoDB Data Migration Complete</b>\n\n"
            success_msg += f"<b>Source:</b> {result['source']}\n"
            success_msg += f"<b>Target:</b> {result['target']}\n\n"
            success_msg += f"<b>Documents Processed:</b> {result['processed']:,}\n"
            success_msg += f"<b>Documents Migrated:</b> {result['moved']:,}\n"
            
            if result.get('duplicates', 0) > 0:
                success_msg += f"<b>Duplicates Skipped:</b> {result['duplicates']:,}\n"
            
            if result.get('errors', 0) > 0:
                success_msg += f"<b>Errors:</b> {result['errors']:,}\n"
            
            # Add button to go back to status
            buttons = [
                [InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_mongodb_status")]
            ]
            
            await callback_query.edit_message_text(
                success_msg,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
            # Log the migration to LOG_CHANNEL
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"<b>MongoDB Data Migration Completed</b>\n\n"
                    f"Admin: {callback_query.from_user.mention}\n"
                    f"<b>Source:</b> {result['source']}\n"
                    f"<b>Target:</b> {result['target']}\n"
                    f"<b>Documents Migrated:</b> {result['moved']:,}/{result['processed']:,}\n"
                    f"<b>Duplicates Skipped:</b> {result.get('duplicates', 0):,}\n"
                    f"<b>Errors:</b> {result.get('errors', 0):,}"
                )
            except Exception as e:
                logger.error(f"Failed to log migration to LOG_CHANNEL: {e}")
        
        except Exception as e:
            error_msg = f"Migration failed with error: {e}"
            logger.error(error_msg)
            
            buttons = [
                [InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_mongodb_status")]
            ]
            
            await callback_query.edit_message_text(
                f"<b>MongoDB Data Migration Failed</b>\n\n"
                f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )