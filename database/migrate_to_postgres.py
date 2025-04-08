import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from database.sql_adapter import SqlAdapter
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

async def migrate_mongodb_to_postgres():
    # Check if migration is needed
    if not DATABASE_URL or not DATABASE_URL.startswith('mongodb'):
        print("No MongoDB URL found, skipping migration")
        return
    
    print("Starting migration from MongoDB to PostgreSQL...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DATABASE_NAME]
    
    # Initialize SQL adapter
    sql_adapter = SqlAdapter()
    
    # Migrate users
    users_collection = db.get_collection('users')
    user_count = 0
    
    async for user in users_collection.find({}):
        user_id = user.get('id')
        name = user.get('name', 'Unknown')
        
        # Save to PostgreSQL
        sql_adapter.add_user(user_id, name)
        
        # Handle ban status
        if user.get('status') == 'banned':
            ban_reason = user.get('ban_reason', 'No reason')
            sql_adapter.ban_user(user_id, ban_reason)
        
        # Handle verification status
        verification = user.get('verification', {})
        if verification:
            verify_data = {
                "is_verified": verification.get('is_verified', False),
                "verified_time": verification.get('verified_time', 0),
                "verify_token": verification.get('verify_token', ''),
                "link": verification.get('link', ''),
                "expire_time": verification.get('expire_time', 0)
            }
            sql_adapter.update_verify_status(user_id, verify_data)
        
        user_count += 1
    
    print(f"Migrated {user_count} users")
    
    # Migrate chats
    chats_collection = db.get_collection('chats')
    chat_count = 0
    
    async for chat in chats_collection.find({}):
        chat_id = chat.get('id')
        title = chat.get('title', 'Unknown')
        
        # Save to PostgreSQL
        sql_adapter.add_chat(chat_id, title)
        
        # Handle ban status
        if chat.get('status') == 'disabled':
            ban_reason = chat.get('reason', 'No reason')
            sql_adapter.disable_chat(chat_id, ban_reason)
        
        # Handle settings
        settings = chat.get('settings', {})
        if settings:
            sql_adapter.update_settings(chat_id, settings)
        
        chat_count += 1
    
    print(f"Migrated {chat_count} chats")
    
    # Migrate media files
    files_collection = db.get_collection(COLLECTION_NAME)
    file_count = 0
    
    async for file in files_collection.find({}):
        try:
            file_data = {
                "file_id": file.get('_id'),
                "file_name": file.get('file_name', ''),
                "file_size": file.get('file_size', 0),
                "caption": file.get('caption', None)
            }
            
            # Save to PostgreSQL
            sql_adapter.save_file(file_data)
            file_count += 1
        except Exception as e:
            print(f"Error migrating file: {e}")
    
    print(f"Migrated {file_count} files")
    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_mongodb_to_postgres())