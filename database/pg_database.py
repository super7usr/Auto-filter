import os
import time
import datetime
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor, Json
import json
from info import DATABASE_URL

# Create a connection pool for PostgreSQL
try:
    connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
    if connection_pool:
        print("PostgreSQL connection pool created successfully")
    
    # Test connection
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL database version: {version}")
    
    # Return connection to the pool
    connection_pool.putconn(conn)
except Exception as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    exit()

# Function to initialize the database tables
def init_tables():
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Create users_chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_chats (
                id BIGINT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                username TEXT,
                chat_status TEXT DEFAULT 'active',
                ban_status JSONB DEFAULT '{"is_banned": false, "ban_reason": ""}'::jsonb,
                ban_reason TEXT DEFAULT '',
                join_date TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create files table for managing media files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                file_name TEXT,
                file_size BIGINT DEFAULT 0,
                chat_id BIGINT,
                message_id BIGINT,
                media_type TEXT,
                mime_type TEXT,
                caption TEXT,
                file_ref TEXT,
                date TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create index on file_name to improve search performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS files_file_name_idx ON files (file_name);
        """)
        
        # Create settings table for groups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                chat_id BIGINT PRIMARY KEY,
                settings JSONB DEFAULT '{}'::jsonb
            );
        """)
        
        # Create verification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                verify_token TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                link TEXT,
                expire_time BIGINT DEFAULT 0
            );
        """)
        
        # Create shorteners table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shorteners (
                chat_id BIGINT PRIMARY KEY,
                shortener_site TEXT,
                shortener_api TEXT
            );
        """)
        
        # Create broadcast_status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_status (
                id SERIAL PRIMARY KEY,
                message_id BIGINT,
                users_count INTEGER DEFAULT 0,
                groups_count INTEGER DEFAULT 0,
                success INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ongoing',
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP
            );
        """)
        
        conn.commit()
        print("PostgreSQL tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        connection_pool.putconn(conn)

# Initialize tables
init_tables()

# User and Chat Database Operations
class Database:
    # Add a new user or chat to DB
    @staticmethod
    def add_user(id, type, name=None, username=None):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users_chats (id, type, name, username) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (id) DO UPDATE 
                SET name = EXCLUDED.name, username = EXCLUDED.username
                RETURNING id;
                """, 
                (id, type, name, username)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
        except Exception as e:
            print(f"Error adding user/chat: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    # Get user details from DB
    @staticmethod
    def get_user(id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM users_chats WHERE id = %s", (id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error getting user/chat: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    # Get all users from DB
    @staticmethod
    def get_all_users():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM users_chats WHERE type = 'user'")
            users = cursor.fetchall()
            return [dict(user) for user in users]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            connection_pool.putconn(conn)
    
    # Get all chats from DB
    @staticmethod
    def get_all_chats():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM users_chats WHERE type = 'group' OR type = 'channel'")
            chats = cursor.fetchall()
            return [dict(chat) for chat in chats]
        except Exception as e:
            print(f"Error getting all chats: {e}")
            return []
        finally:
            connection_pool.putconn(conn)
    
    # Count total users and chats
    @staticmethod
    def total_users_count():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users_chats WHERE type = 'user'")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    def total_chats_count():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users_chats WHERE type = 'group' OR type = 'channel'")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error counting chats: {e}")
            return 0
        finally:
            connection_pool.putconn(conn)
    
    # Delete a user/chat
    @staticmethod
    def delete_user(id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users_chats WHERE id = %s RETURNING id", (id,))
            deleted_id = cursor.fetchone()
            conn.commit()
            return deleted_id[0] if deleted_id else None
        except Exception as e:
            print(f"Error deleting user/chat: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    # Ban/Unban functions
    @staticmethod
    def ban_user(user_id, ban_reason="No reason"):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            ban_status = json.dumps({"is_banned": True, "ban_reason": ban_reason})
            cursor.execute(
                """
                UPDATE users_chats 
                SET ban_status = %s, chat_status = 'banned', ban_reason = %s 
                WHERE id = %s
                """, 
                (ban_status, ban_reason, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error banning user: {e}")
            return False
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    def unban_user(user_id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            ban_status = json.dumps({"is_banned": False, "ban_reason": ""})
            cursor.execute(
                """
                UPDATE users_chats 
                SET ban_status = %s, chat_status = 'active', ban_reason = '' 
                WHERE id = %s
                """, 
                (ban_status, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error unbanning user: {e}")
            return False
        finally:
            connection_pool.putconn(conn)
    
    # Get banned users and chats
    @staticmethod
    async def get_banned():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute(
                """
                SELECT id, type FROM users_chats 
                WHERE chat_status = 'banned' 
                AND (ban_status->>'is_banned')::boolean = true
                """
            )
            results = cursor.fetchall()
            banned_users = []
            banned_chats = []
            
            for result in results:
                if result['type'] == 'user':
                    banned_users.append(result['id'])
                else:
                    banned_chats.append(result['id'])
                    
            return banned_users, banned_chats
        except Exception as e:
            print(f"Error getting banned users/chats: {e}")
            return [], []
        finally:
            if 'conn' in locals() and conn is not None:
                connection_pool.putconn(conn)

# Media File Management
class Media:
    @staticmethod
    async def save_file(file_name, file_id, file_ref=None, media_type=None, mime_type=None, chat_id=None, message_id=None, caption=None, size=0):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO files (file_name, file_id, file_ref, media_type, mime_type, chat_id, message_id, caption, file_size) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, 
                (file_name, file_id, file_ref, media_type, mime_type, chat_id, message_id, caption, size)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def find_file(query, filter=None, file_type=None):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            # Create a pattern for case-insensitive search
            pattern = f"%{query}%"
            
            # Base query
            sql = "SELECT * FROM files WHERE LOWER(file_name) LIKE LOWER(%s)"
            params = [pattern]
            
            # Add media type filter if specified
            if file_type:
                sql += " AND media_type = %s"
                params.append(file_type)
            
            # Add MIME type filter if specified
            if filter:
                sql += " AND mime_type = %s"
                params.append(filter)
            
            # Add limit
            sql += " LIMIT 10"
            
            cursor.execute(sql, params)
            files = cursor.fetchall()
            return [dict(file) for file in files]
        except Exception as e:
            print(f"Error finding files: {e}")
            return []
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def count_documents():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def get_file_by_id(file_id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM files WHERE file_id = %s", (file_id,))
            file = cursor.fetchone()
            return dict(file) if file else None
        except Exception as e:
            print(f"Error getting file by ID: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def delete_file(query):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            
            # Create a pattern for case-insensitive search
            pattern = f"%{query}%"
            
            cursor.execute("DELETE FROM files WHERE LOWER(file_name) LIKE LOWER(%s) RETURNING id", (pattern,))
            deleted_ids = cursor.fetchall()
            conn.commit()
            return len(deleted_ids)
        except Exception as e:
            print(f"Error deleting files: {e}")
            return 0
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def delete_all_files():
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files")
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting all files: {e}")
            return False
        finally:
            connection_pool.putconn(conn)
    
    # For creating indexes, PostgreSQL creates them during table creation
    @staticmethod
    async def ensure_indexes():
        return True

# Settings Management
class Settings:
    @staticmethod
    async def get_settings(chat_id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT settings FROM settings WHERE chat_id = %s", (chat_id,))
            result = cursor.fetchone()
            
            if result:
                return result['settings']
            else:
                # Create default settings for new group
                default_settings = json.dumps({
                    'auto_filter': True,
                    'auto_delete': True,
                    'imdb': True,
                    'spell_check': True,
                    'welcome': True,
                    'shortlink': False,
                    'permdb': False,
                    'auto_f_fix': False
                })
                
                cursor.execute(
                    "INSERT INTO settings (chat_id, settings) VALUES (%s, %s)", 
                    (chat_id, default_settings)
                )
                conn.commit()
                return json.loads(default_settings)
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def save_settings(chat_id, key, value):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            
            # Get current settings
            cursor.execute("SELECT settings FROM settings WHERE chat_id = %s", (chat_id,))
            result = cursor.fetchone()
            
            if result:
                settings = result[0]
                settings[key] = value
                
                cursor.execute(
                    "UPDATE settings SET settings = %s WHERE chat_id = %s",
                    (Json(settings), chat_id)
                )
            else:
                # Create new settings
                settings = {key: value}
                cursor.execute(
                    "INSERT INTO settings (chat_id, settings) VALUES (%s, %s)",
                    (chat_id, Json(settings))
                )
                
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
        finally:
            connection_pool.putconn(conn)

# Verification Management
class Verification:
    @staticmethod
    async def get_verify_status(user_id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM verifications WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting verification status: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def update_verify_status(user_id, verify_token="", is_verified=False, link="", expire_time=0):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO verifications (user_id, verify_token, is_verified, link, expire_time)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET verify_token = EXCLUDED.verify_token,
                    is_verified = EXCLUDED.is_verified,
                    link = EXCLUDED.link,
                    expire_time = EXCLUDED.expire_time
                """,
                (user_id, verify_token, is_verified, link, expire_time)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating verification status: {e}")
            return False
        finally:
            connection_pool.putconn(conn)

# Shortener Management
class Shortener:
    @staticmethod
    async def get_shortlink(chat_id):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM shorteners WHERE chat_id = %s", (chat_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting shortlink: {e}")
            return None
        finally:
            connection_pool.putconn(conn)
    
    @staticmethod
    async def save_shortlink(chat_id, site, api):
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO shorteners (chat_id, shortener_site, shortener_api)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE
                SET shortener_site = EXCLUDED.shortener_site,
                    shortener_api = EXCLUDED.shortener_api
                """,
                (chat_id, site, api)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving shortlink: {e}")
            return False
        finally:
            connection_pool.putconn(conn)