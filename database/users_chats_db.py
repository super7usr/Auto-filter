import os
import time
import datetime
from info import TIME_ZONE, ADMINS, DATABASE_NAME, DATABASE_URL, SECOND_DATABASE_URL, FORCE_SUB_CHANNELS, IMDB_TEMPLATE, WELCOME_TEXT, LINK_MODE, TUTORIAL, SHORTLINK_URL, SHORTLINK_API, SHORTLINK, FILE_CAPTION, IMDB, WELCOME, SPELL_CHECK, PROTECT_CONTENT, AUTO_FILTER, AUTO_DELETE, IS_STREAM, VERIFY_EXPIRE

# Check if we're using PostgreSQL
if DATABASE_URL and not DATABASE_URL.startswith('mongodb'):
    from database.sql_adapter import db_adapter
    using_postgres = True
else:
    # Use MongoDB
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(DATABASE_URL)
    mydb = client[DATABASE_NAME]
    
    if SECOND_DATABASE_URL:
        second_client = AsyncIOMotorClient(SECOND_DATABASE_URL)
        second_db = second_client[DATABASE_NAME]
    
    using_postgres = False

class Database:
    default_setgs = {
        'auto_filter': AUTO_FILTER,
        'file_secure': PROTECT_CONTENT,
        'imdb': IMDB,
        'spell_check': SPELL_CHECK,
        'auto_delete': AUTO_DELETE,
        'welcome': WELCOME,
        'welcome_text': WELCOME_TEXT,
        'template': IMDB_TEMPLATE,
        'caption': FILE_CAPTION,
        'url': SHORTLINK_URL,
        'api': SHORTLINK_API,
        'shortlink': SHORTLINK,
        'tutorial': TUTORIAL,
        'links': LINK_MODE,
        'fsub': FORCE_SUB_CHANNELS,
        'is_stream': IS_STREAM
    }

    default_verify = {
        'is_verified': False,
        'verified_time': 0,
        'verify_token': "",
        'link': "",
        'expire_time': 0
    }
    
    def __init__(self):
        if using_postgres:
            # PostgreSQL version
            self.adapter = db_adapter
        else:
            # MongoDB version
            self.col = mydb.Users
            self.grp = mydb.Groups
            self.prm_users = mydb.Premium_Users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            verify_status=self.default_verify
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
            settings=self.default_setgs
        )
    
    async def add_user(self, id, name):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.add_user(id, name)
        else:
            # MongoDB version
            user = self.new_user(id, name)
            await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.is_user_exist(id)
        else:
            # MongoDB version
            user = await self.col.find_one({'id':int(id)})
            return bool(user)
    
    async def total_users_count(self):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.total_users_count()
        else:
            # MongoDB version
            count = await self.col.count_documents({})
            return count
    
    async def remove_ban(self, id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.remove_ban(id)
        else:
            # MongoDB version
            ban_status = dict(
                is_banned=False,
                ban_reason=''
            )
            await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.ban_user(user_id, ban_reason)
        else:
            # MongoDB version
            ban_status = dict(
                is_banned=True,
                ban_reason=ban_reason
            )
            await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        if using_postgres:
            # PostgreSQL version
            status = self.adapter.get_ban_status(id)
            if not status:
                return {
                    "is_banned": False,
                    "ban_reason": ""
                }
            return status
        else:
            # MongoDB version
            default = dict(
                is_banned=False,
                ban_reason=''
            )
            user = await self.col.find_one({'id':int(id)})
            if not user:
                return default
            return user.get('ban_status', default)

    async def get_all_users(self):
        if using_postgres:
            # PostgreSQL version
            # Convert to a format that matches MongoDB cursor
            users = self.adapter.get_all_users()
            
            class UsersCursor:
                def __init__(self, users_list):
                    self.users = users_list
                    self.index = 0
                
                def __aiter__(self):
                    return self
                
                async def __anext__(self):
                    if self.index >= len(self.users):
                        raise StopAsyncIteration
                    
                    user = self.users[self.index]
                    self.index += 1
                    return user
            
            return UsersCursor(users)
        else:
            # MongoDB version
            return self.col.find({})
    
    async def delete_user(self, user_id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.delete_user(user_id)
        else:
            # MongoDB version
            await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, grp_id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.delete_chat(grp_id)
        else:
            # MongoDB version
            await self.grp.delete_many({'id': int(grp_id)})

    async def get_banned(self):
        if using_postgres:
            # PostgreSQL version
            banned_users = [user['id'] for user in self.adapter.get_banned()]
            banned_chats = []
            
            # Get all chats and filter banned ones
            for chat in self.adapter.get_all_chats():
                if chat.get('banned', False):
                    banned_chats.append(chat['id'])
            
            return banned_users, banned_chats
        else:
            # MongoDB version
            users = self.col.find({'ban_status.is_banned': True})
            chats = self.grp.find({'chat_status.is_disabled': True})
            b_chats = [chat['id'] async for chat in chats]
            b_users = [user['id'] async for user in users]
            return b_users, b_chats
    
    async def add_chat(self, chat, title):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.add_chat(chat, title)
        else:
            # MongoDB version
            chat = self.new_group(chat, title)
            await self.grp.insert_one(chat)

    async def get_chat(self, chat):
        if using_postgres:
            # PostgreSQL version
            chat_info = self.adapter.get_chat(chat)
            if not chat_info:
                return False
            
            # Create compatible chat_status structure
            status = {
                "is_disabled": chat_info.get("banned", False),
                "reason": chat_info.get("ban_reason", "")
            }
            return status
        else:
            # MongoDB version
            chat = await self.grp.find_one({'id':int(chat)})
            return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.re_enable_chat(id)
        else:
            # MongoDB version
            chat_status=dict(
                is_disabled=False,
                reason="",
                )
            await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.update_settings(id, settings)
        else:
            # MongoDB version
            await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})      
    
    async def get_settings(self, id):
        if using_postgres:
            # PostgreSQL version
            chat_settings = self.adapter.get_settings(id)
            return chat_settings
        else:
            # MongoDB version
            chat = await self.grp.find_one({'id':int(id)})
            if chat:
                return chat.get('settings', self.default_setgs)
            return self.default_setgs
    
    async def disable_chat(self, chat, reason="No Reason"):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.disable_chat(chat, reason)
        else:
            # MongoDB version
            chat_status=dict(
                is_disabled=True,
                reason=reason,
                )
            await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def get_verify_status(self, user_id):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.get_verify_status(user_id)
        else:
            # MongoDB version
            user = await self.col.find_one({'id':int(user_id)})
            if user:
                info = user.get('verify_status', self.default_verify)
                try:
                    info.get('expire_time')
                except:
                    expire_time = info.get('verified_time') + datetime.timedelta(seconds=VERIFY_EXPIRE)
                    info.append({
                        'expire_time': expire_time
                    })
                return info
            return self.default_verify
        
    async def update_verify_status(self, user_id, verify):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.update_verify_status(user_id, verify)
        else:
            # MongoDB version
            await self.col.update_one({'id': int(user_id)}, {'$set': {'verify_status': verify}})
    
    async def total_chat_count(self):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.total_chat_count()
        else:
            # MongoDB version
            count = await self.grp.count_documents({})
            return count
    
    async def get_all_chats(self):
        if using_postgres:
            # PostgreSQL version
            # Convert to a format that matches MongoDB cursor
            chats = self.adapter.get_all_chats()
            
            class ChatsCursor:
                def __init__(self, chats_list):
                    self.chats = chats_list
                    self.index = 0
                
                def __aiter__(self):
                    return self
                
                async def __anext__(self):
                    if self.index >= len(self.chats):
                        raise StopAsyncIteration
                    
                    chat = self.chats[self.index]
                    self.index += 1
                    return chat
            
            return ChatsCursor(chats)
        else:
            # MongoDB version
            return self.grp.find({})
    
    async def get_db_size(self):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.get_db_size()
        else:
            # MongoDB version
            return (await mydb.command("dbstats"))['dataSize']
   
    async def get_second_db_size(self):
        if using_postgres:
            # PostgreSQL version - no second DB in PostgreSQL implementation
            return 0
        else:
            # MongoDB version
            if SECOND_DATABASE_URL:
                return (await second_db.command("dbstats"))['dataSize']
            return 0
    
    async def get_all_chats_count(self):
        if using_postgres:
            # PostgreSQL version
            return self.adapter.total_chat_count()
        else:
            # MongoDB version
            grp = await self.grp.count_documents({})
            return grp
        
db = Database()
