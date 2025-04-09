from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, DateTime, func, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
import json
import datetime
from typing import List, Dict, Any, Optional
import time

Base = declarative_base()

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Print for debugging
print(f"Using database URL: {DATABASE_URL}")

class Media(Base):
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(String(255), unique=True, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    caption = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "caption": self.caption
        }

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    banned = Column(Boolean, default=False)
    ban_reason = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    verified_time = Column(Integer, default=0)
    verify_token = Column(String(255), nullable=True)
    verify_link = Column(String(255), nullable=True)
    expire_time = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "banned": self.banned,
            "ban_reason": self.ban_reason,
            "is_verified": self.verified,
            "verified_time": self.verified_time,
            "verify_token": self.verify_token,
            "link": self.verify_link,
            "expire_time": self.expire_time
        }

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    banned = Column(Boolean, default=False)
    ban_reason = Column(String(255), nullable=True)
    settings = Column(Text, nullable=True)  # JSON string
    
    def to_dict(self):
        return {
            "id": self.chat_id,
            "title": self.title,
            "banned": self.banned,
            "ban_reason": self.ban_reason,
            "settings": json.loads(self.settings) if self.settings else {}
        }

class SqlAdapter:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def new_user(self, user_id, name):
        """Add a new user to the database"""
        with self.Session() as session:
            existing_user = session.query(User).filter(User.user_id == user_id).first()
            if existing_user:
                return False
            
            new_user = User(user_id=user_id, name=name)
            session.add(new_user)
            session.commit()
            return True
    
    def new_group(self, chat_id, title):
        """Add a new group to the database"""
        with self.Session() as session:
            existing_chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if existing_chat:
                return False
            
            default_settings = {
                'auto_filter': True,
                'file_secure': False,
                'imdb': True,
                'spell_check': True,
                'auto_delete': False,
                'welcome': False,
                'welcome_text': "👋 Hello {mention}, Welcome to {title} group! 💞",
                'template': "✅ I Found: <code>{query}</code>\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating} / 10</a>\n☀️ Languages: {languages}\n📀 RunTime: {runtime} Minutes\n\n🗣 Requested by: {message.from_user.mention}\n©️ Powered by: <b>{message.chat.title}</b>",
                'caption': "<i>{file_name}</i>\n\n🚫 ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ sᴇᴇɴ ᴛʜᴇ ᴍᴏᴠɪᴇ 🚫",
                'url': "mdiskshortner.link",
                'api': "36f1ae74ba1aa01e5bd73bdd0bc22aa915443501",
                'shortlink': False,
                'tutorial': "https://t.me/HA_Bots",
                'links': True,
                'fsub': [],
                'is_stream': True
            }
            
            new_chat = Chat(
                chat_id=chat_id, 
                title=title, 
                settings=json.dumps(default_settings)
            )
            session.add(new_chat)
            session.commit()
            return True
    
    def add_user(self, user_id, name):
        """Add a user to the database or update if exists"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.name = name
                session.commit()
                return False
            
            new_user = User(user_id=user_id, name=name)
            session.add(new_user)
            session.commit()
            return True
    
    def is_user_exist(self, user_id):
        """Check if a user exists in the database"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            return bool(user)
    
    def total_users_count(self):
        """Get total number of users"""
        with self.Session() as session:
            return session.query(User).count()
    
    def get_all_users(self):
        """Get all users"""
        with self.Session() as session:
            users = session.query(User).all()
            return [user.to_dict() for user in users]
    
    def delete_user(self, user_id):
        """Delete a user from database"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
    
    def remove_ban(self, user_id):
        """Remove ban from a user"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.banned = False
                user.ban_reason = None
                session.commit()
                return True
            return False
    
    def ban_user(self, user_id, ban_reason="No Reason"):
        """Ban a user"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.banned = True
                user.ban_reason = ban_reason
                session.commit()
                return True
            return False
    
    def get_ban_status(self, user_id):
        """Get ban status of a user"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None
            
            return {"banned": user.banned, "ban_reason": user.ban_reason}
    
    def get_banned(self):
        """Get all banned users"""
        with self.Session() as session:
            users = session.query(User).filter(User.banned == True).all()
            return [user.to_dict() for user in users]
    
    def add_chat(self, chat_id, title):
        """Add a chat to database or update if exists"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                chat.title = title
                session.commit()
                return False
            
            return self.new_group(chat_id, title)
    
    def get_chat(self, chat_id):
        """Get a chat from database"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if not chat:
                return None
            
            return chat.to_dict()
    
    def re_enable_chat(self, chat_id):
        """Re-enable a banned chat"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                chat.banned = False
                chat.ban_reason = None
                session.commit()
                return True
            return False
    
    def update_settings(self, chat_id, settings_dict):
        """Update settings for a chat"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if not chat:
                return False
            
            # Get current settings
            current_settings = json.loads(chat.settings) if chat.settings else {}
            
            # Update with new settings
            current_settings.update(settings_dict)
            
            # Save updated settings
            chat.settings = json.dumps(current_settings)
            session.commit()
            return True
    
    def get_settings(self, chat_id):
        """Get settings for a chat"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if not chat or not chat.settings:
                # Return default settings
                return {
                    'auto_filter': True,
                    'file_secure': False,
                    'imdb': True,
                    'spell_check': True,
                    'auto_delete': False,
                    'welcome': False,
                    'welcome_text': "👋 Hello {mention}, Welcome to {title} group! 💞",
                    'template': "✅ I Found: <code>{query}</code>\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating} / 10</a>\n☀️ Languages: {languages}\n📀 RunTime: {runtime} Minutes\n\n🗣 Requested by: {message.from_user.mention}\n©️ Powered by: <b>{message.chat.title}</b>",
                    'caption': "<i>{file_name}</i>\n\n🚫 ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ sᴇᴇɴ ᴛʜᴇ ᴍᴏᴠɪᴇ 🚫",
                    'url': "mdiskshortner.link",
                    'api': "36f1ae74ba1aa01e5bd73bdd0bc22aa915443501",
                    'shortlink': False,
                    'tutorial': "https://t.me/HA_Bots",
                    'links': True,
                    'fsub': [],
                    'is_stream': True
                }
            
            return json.loads(chat.settings)
    
    def disable_chat(self, chat_id, reason="No Reason"):
        """Ban a chat"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                chat.banned = True
                chat.ban_reason = reason
                session.commit()
                return True
            return False
    
    def total_chat_count(self):
        """Get total number of chats"""
        with self.Session() as session:
            return session.query(Chat).count()
    
    def get_all_chats(self):
        """Get all chats"""
        with self.Session() as session:
            chats = session.query(Chat).all()
            return [chat.to_dict() for chat in chats]
    
    def get_db_size(self):
        """Get database size - approximate implementation for PostgreSQL"""
        with self.Session() as session:
            # Count total rows as a simple approximation
            media_count = session.query(Media).count()
            users_count = session.query(User).count()
            chats_count = session.query(Chat).count()
            
            # Rough estimate - 1KB per row
            return (media_count + users_count + chats_count) * 1024
    
    def delete_chat(self, chat_id):
        """Delete a chat from database"""
        with self.Session() as session:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                session.delete(chat)
                session.commit()
                return True
            return False
    
    def get_verify_status(self, user_id):
        """Get verification status of a user"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {
                    "is_verified": False,
                    "verified_time": 0,
                    "verify_token": "",
                    "link": "",
                    "expire_time": 0
                }
                
            return {
                "is_verified": user.verified,
                "verified_time": user.verified_time,
                "verify_token": user.verify_token,
                "link": user.verify_link,
                "expire_time": user.expire_time
            }
    
    def update_verify_status(self, user_id, verify_data):
        """Update verification status for a user"""
        with self.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            user.verified = verify_data.get("is_verified", user.verified)
            user.verified_time = verify_data.get("verified_time", user.verified_time)
            user.verify_token = verify_data.get("verify_token", user.verify_token)
            user.verify_link = verify_data.get("link", user.verify_link)
            user.expire_time = verify_data.get("expire_time", user.expire_time)
            
            session.commit()
            return True
    
    # Media functions
    def save_file(self, media_data):
        """Save a file to the database"""
        with self.Session() as session:
            file_id = media_data.get("file_id")
            
            # Check if file already exists
            existing = session.query(Media).filter(Media.file_id == file_id).first()
            if existing:
                return False
            
            new_media = Media(
                file_id=file_id,
                file_name=media_data.get("file_name"),
                file_size=media_data.get("file_size"),
                caption=media_data.get("caption")
            )
            
            session.add(new_media)
            session.commit()
            return True
    
    def get_search_results(self, query, max_results=10, offset=0):
        """Get search results for a query"""
        with self.Session() as session:
            # SQL LIKE search with case insensitivity
            search_pattern = f"%{query}%"
            results = session.query(Media).filter(
                Media.file_name.ilike(search_pattern)
            ).offset(offset).limit(max_results).all()
            
            return [media.to_dict() for media in results]
    
    def delete_files(self, query):
        """Delete files matching a query"""
        with self.Session() as session:
            search_pattern = f"%{query}%"
            files = session.query(Media).filter(Media.file_name.ilike(search_pattern)).all()
            
            if not files:
                return False
            
            for file in files:
                session.delete(file)
            
            session.commit()
            return len(files)
    
    def get_file_details(self, query):
        """Get details of a file"""
        with self.Session() as session:
            search_pattern = f"%{query}%"
            files = session.query(Media).filter(Media.file_name.ilike(search_pattern)).all()
            
            return [media.to_dict() for media in files]
    
    def get_mood_results(self, primary_keyword, additional_keywords=None, max_results=10, offset=0):
        """
        Get search results based on mood keywords
        
        Args:
            primary_keyword: The main mood keyword to search for
            additional_keywords: List of additional keywords to filter by
            max_results: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of matching media files
        """
        if additional_keywords is None:
            additional_keywords = []
            
        with self.Session() as session:
            # Base query with primary keyword
            base_query = session.query(Media).filter(
                Media.file_name.ilike(f"%{primary_keyword}%") |
                func.coalesce(Media.caption, "").ilike(f"%{primary_keyword}%")
            )
            
            # If we have additional keywords, filter further
            if additional_keywords:
                # Build OR condition for each additional keyword
                additional_filters = []
                for keyword in additional_keywords:
                    additional_filters.append(
                        Media.file_name.ilike(f"%{keyword}%") | 
                        func.coalesce(Media.caption, "").ilike(f"%{keyword}%")
                    )
                
                if additional_filters:
                    # Add any of the additional filters
                    from sqlalchemy import or_
                    combined_filter = or_(*additional_filters)
                    base_query = base_query.filter(combined_filter)
            
            # Apply pagination
            results = base_query.offset(offset).limit(max_results).all()
            return [media.to_dict() for media in results]

# Initialize the adapter
db_adapter = SqlAdapter()