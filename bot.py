import os
import time
import asyncio
import uvloop
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# pyrogram imports
from pyrogram import types
from pyrogram import Client
from pyrogram.errors import FloodWait

# aiohttp imports
from aiohttp import web
from typing import Union, Optional, AsyncGenerator

# local imports
from web import web_app
from info import LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, PORT, BIN_CHANNEL, ADMINS, SECOND_DATABASE_URL, DATABASE_URL, USE_POSTGRES
from utils import temp, get_readable_time

# Import database modules
if USE_POSTGRES:
    # Use PostgreSQL adapter
    print("Using PostgreSQL database adapter")
    import database.pg_database as db
    from database.pg_database import Media
else:
    # Use MongoDB adapter
    print("Using MongoDB database adapter")
    from database.users_chats_db import db
    from database.ia_filterdb import Media
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi

uvloop.install()

# Helper function to safely get the ADMINS list
def get_admins_list():
    admins_str = os.environ.get('ADMINS', '')
    if not admins_str:
        return []
    try:
        return [int(admin.strip()) for admin in admins_str.split() if admin.strip()]
    except:
        return []

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )

    async def start(self):
        try:
            await super().start()
        except FloodWait as e:
            time_ = get_readable_time(e.value)
            print(f"Warning - Flood Wait Occured, Wait For: {time_}")
            await asyncio.sleep(e.value)
            print("Info - Now Ready For Deploying !")
        temp.START_TIME = time.time()
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        # Database connection test
        if not USE_POSTGRES and DATABASE_URL and DATABASE_URL.startswith('mongodb'):
            # For MongoDB
            client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))
            try:
                client.admin.command('ping')
                print("Info - Successfully connected to MongoDB DATABASE_URL")
            except Exception as e:
                print(f"Error - Make sure MongoDB DATABASE_URL is correct: {e}")
                exit()

            if SECOND_DATABASE_URL:
                client2 = MongoClient(SECOND_DATABASE_URL, server_api=ServerApi('1'))
                try:
                    client2.admin.command('ping')
                    print("Info - Successfully connected to SECOND_DATABASE_URL")
                except:
                    print("Error - Make sure SECOND_DATABASE_URL is correct, exiting now")
                    exit()
        elif USE_POSTGRES:
            # For PostgreSQL - connection is already tested in pg_database.py
            print("Info - Using PostgreSQL database")
        else:
            print("Error - No valid database connection. Exiting.")
            exit()

        if os.path.exists('restart.txt'):
            with open("restart.txt") as file:
                chat_id, msg_id = map(int, file)
            try:
                await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
            except:
                pass
            os.remove('restart.txt')
        temp.BOT = self
        # Only create indexes for MongoDB
        if DATABASE_URL and DATABASE_URL.startswith('mongodb'):
            await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        username = '@' + me.username
        print(f"{me.first_name} is started now 🤗 (DC ID - {me.dc_id})")
        app = web.AppRunner(web_app)
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        try:
            # Create backup
            from utils import create_backup_and_send
            admins_list = get_admins_list()
            admin_id = admins_list[0] if admins_list else None  # Get the first admin ID
            
            # Create single restart notification
            restart_time = time.strftime('%Y-%m-%d %H:%M:%S')
            restart_message = f"""<b>✅ {me.mention} Bot Restarted! 🤖</b>

• <b>Bot Version:</b> 1.0
• <b>Restart Time:</b> {restart_time}
• <b>Status:</b> Online and operational

<i>Creating and attaching backup file...</i>"""
            
            # Send to LOG_CHANNEL with backup attached
            log_msg = await self.send_message(chat_id=LOG_CHANNEL, text=restart_message)
            
            # Send to admin
            if admin_id:
                await self.send_message(chat_id=admin_id, text=restart_message)
            
            # Create and send backup to LOG_CHANNEL as reply to the restart message
            print(f"Creating backup and sending to log channel")
            await create_backup_and_send(self, LOG_CHANNEL, reply_to_message_id=log_msg.id)

        except Exception as e:
            print(f"Error - Issue sending restart notification or creating backup: {e}")
            print("Warning - Continuing execution despite error")

        try:
            m = await self.send_message(chat_id=BIN_CHANNEL, text="Test")
            await m.delete()
        except:
            print("Error - Make sure bot admin in BIN_CHANNEL, exiting now")
            exit()
        # Notify all admins about the restart (except the first admin who was already notified)
        admins_list = get_admins_list()
        first_admin = admins_list[0] if admins_list else None
        for admin in ADMINS:
            if admin != first_admin and first_admin is not None:  # Skip the first admin as they already received a notification
                try:
                    await self.send_message(chat_id=admin, text="<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ</b>")
                except Exception as e:
                    print(f"Info - Admin ({admin}) not started this bot yet: {e}")

        # Process messages that were missed while the bot was offline
        try:
            from plugins.offline_handler import process_missed_messages
            print("Starting to process missed messages...")
            await process_missed_messages(self)
            print("Finished processing missed messages")
        except Exception as e:
            print(f"Error processing missed messages: {e}")

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped! Bye...")

    async def iter_messages(self: Client, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``):
                Identifier of the last message to be returned.

            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                async for message in app.iter_messages("pyrogram", 1000, 100):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1

app = Bot()
app.run()