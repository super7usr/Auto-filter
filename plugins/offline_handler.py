import asyncio
import logging
from pyrogram import Client, filters
from datetime import datetime, timedelta
from info import LOG_CHANNEL, ADMINS
from utils import temp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_missed_messages(bot):
    """
    Process messages that were sent while the bot was offline
    """
    try:
        # Get the time when the bot was last online (from temp.START_TIME)
        last_online_time = datetime.fromtimestamp(temp.START_TIME) if hasattr(temp, 'START_TIME') and temp.START_TIME > 0 else datetime.now() - timedelta(hours=1)

        logger.info(f"Checking for missed messages since {last_online_time}")

        # Skip sending additional messages - we already sent a consolidated message in bot.py
        logger.info(f"Processing missed messages since {last_online_time}")

        # Get recent messages from the log channel (as a reference point)
        chats_processed = 0
        messages_processed = 0

        # Get list of active chats from the database
        from database.users_chats_db import db
        chats = await db.get_all_chats()

        async for chat in chats:
            # Skip chats that are disabled
            if chat.get('chat_status', {}).get('is_disabled', False):
                continue

            chat_id = chat['id']

            try:
                # Unfortunately, bots cannot get chat history with get_chat_history method
                # We'll check for mentions and reply to them if possible
                try:
                    chat_info = await bot.get_chat(chat_id)
                    if chat_info.type != "private":  # Only send to groups, not private chats
                        # First, send a notification that we're back online
                        notification_msg = f"""<b>🤖 Bot is back online!</b>

<i>I was offline since {last_online_time.strftime('%Y-%m-%d %H:%M:%S')}.</i>

<b>Processing any pending search queries... Please wait.</b>"""

                        status_msg = await bot.send_message(
                            chat_id=chat_id,
                            text=notification_msg
                        )

                        # Now let's try to get recent messages that might be search queries
                        # We can only get messages where the bot was mentioned or replied to
                        try:
                            # Import the auto_filter function from pm_filter.py
                            from plugins.pm_filter import auto_filter

                            # Get the bot's username
                            bot_username = (await bot.get_me()).username

                            # Find recent messages with search queries
                            pending_count = 0
                            processed_count = 0

                            # We'll process up to 10 recent messages that might be search queries
                            # This is a workaround since we can't get full chat history
                            try:
                                async for message in bot.iter_messages(chat_id, limit=50):
                                    # Skip messages from before the bot was offline
                                    if message.date and last_online_time and message.date.timestamp() < last_online_time.timestamp():
                                        continue

                                    # Skip bot messages
                                    if message.from_user and message.from_user.is_bot:
                                        continue

                                    # Skip commands
                                    if message.text and message.text.startswith('/'):
                                        continue

                                    # Check if message contains a search query (text longer than 2 chars)
                                    if message.text and len(message.text) > 2:
                                        # Check if bot was mentioned or replied to
                                        if (bot_username in message.text or 
                                            (message.reply_to_message and message.reply_to_message.from_user and 
                                             message.reply_to_message.from_user.is_bot and 
                                             message.reply_to_message.from_user.id == bot.me.id)):

                                            pending_count += 1
                                            # Process the search query
                                            try:
                                                reply_msg = await message.reply(f"<b><i>⚠️ Processing delayed query: `{message.text}` ...</i></b>")
                                                await auto_filter(bot, message, reply_msg)
                                                processed_count += 1
                                                messages_processed += 1
                                            except Exception as e:
                                                logger.error(f"Error processing search query: {e}")
                            except Exception as e:
                                logger.error(f"Error iterating messages: {e}")

                            # Update the status message
                            if pending_count > 0:
                                await status_msg.edit_text(f"""<b>🤖 Bot is back online!</b>

<i>I was offline since {last_online_time.strftime('%Y-%m-%d %H:%M:%S')}.</i>

<b>✅ Processed {processed_count} out of {pending_count} pending search queries.</b>

<i>If you sent any queries that weren't processed, please send them again.</i>""")
                            else:
                                await status_msg.edit_text(f"""<b>🤖 Bot is back online!</b>

<i>I was offline since {last_online_time.strftime('%Y-%m-%d %H:%M:%S')}.</i>

<b>No pending search queries found.</b>

<i>If you sent any search queries while I was offline, please send them again.</i>""")

                        except Exception as e:
                            logger.error(f"Error processing pending messages: {e}")
                            await status_msg.edit_text(f"""<b>🤖 Bot is back online!</b>

<i>I was offline since {last_online_time.strftime('%Y-%m-%d %H:%M:%S')}. There was an error processing pending messages.</i>

<b>If you sent any search queries or commands while I was offline, please send them again.</b>""")

                        logger.info(f"Processed offline messages in chat {chat_id}: {processed_count} of {pending_count}")
                except Exception as chat_error:
                    logger.error(f"Could not send notification to chat {chat_id}: {chat_error}")

                chats_processed += 1
                # Sleep briefly to avoid hitting rate limits
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing missed messages for chat {chat_id}: {e}")

        # Log completion but don't send additional messages
        completion_msg = f"✅ <b>Recovery Process Completed</b>\nProcessed {chats_processed} chats and handled {messages_processed} missed messages."
        logger.info(completion_msg)
        # Only update the console log, don't send another message to the channel

    except Exception as e:
        error_msg = f"❌ <b>Recovery Process Failed</b>\nError: {str(e)}"
        logger.error(error_msg)
        await bot.send_message(chat_id=LOG_CHANNEL, text=error_msg)