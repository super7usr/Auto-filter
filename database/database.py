import motor.motor_asyncio
import datetime
from config import LOGGER, COLLECTION_NAME

class Database:
    def __init__(self, uri, database_name):
        """
        Initialize database connection
        """
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.filters = self.db[COLLECTION_NAME]
        self.connections = self.db.connections
        LOGGER.info("Database connection established")
        
    async def create_index(self):
        """
        Create indices for efficient querying
        """
        await self.col.create_index("user_id")
        await self.grp.create_index("chat_id")
        await self.filters.create_index("chat_id")
        await self.filters.create_index("text")
        await self.connections.create_index("user_id")
        LOGGER.info("Database indices created")

    async def add_user(self, user_id, username=None):
        """
        Add a new user or update an existing user in database
        """
        user = await self.col.find_one({"user_id": user_id})
        if user:
            # User exists, update username if provided
            if username and user.get("username") != username:
                await self.col.update_one(
                    {"user_id": user_id},
                    {"$set": {"username": username}}
                )
            return
        
        # New user, add to database
        await self.col.insert_one({
            "user_id": user_id,
            "username": username,
            "join_date": datetime.datetime.now()
        })

    async def add_chat(self, chat_id, title):
        """
        Add a new chat or update an existing chat in database
        """
        chat = await self.grp.find_one({"chat_id": chat_id})
        if chat:
            # Chat exists, update title if it changed
            if title and chat.get("title") != title:
                await self.grp.update_one(
                    {"chat_id": chat_id},
                    {"$set": {"title": title}}
                )
            return
        
        # New chat, add to database
        await self.grp.insert_one({
            "chat_id": chat_id,
            "title": title,
            "add_date": datetime.datetime.now()
        })

    async def get_user_count(self):
        """
        Get the number of users in the database
        """
        return await self.col.count_documents({})

    async def get_chat_count(self):
        """
        Get the number of chats in the database
        """
        return await self.grp.count_documents({})

    async def add_filter(self, chat_id, file_id, text, file_name, file_size, file_type):
        """
        Add a new filter to the database
        """
        await self.filters.insert_one({
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text.lower(),
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "add_date": datetime.datetime.now()
        })

    async def find_filters(self, chat_id, query, limit=10):
        """
        Find filters in the database based on query
        """
        query = query.lower()
        pipeline = [
            {
                "$match": {
                    "chat_id": chat_id,
                    "text": {"$regex": f".*{query}.*"}
                }
            },
            {"$limit": limit}
        ]
        
        return await self.filters.aggregate(pipeline).to_list(limit)

    async def total_filters_count(self, chat_id=None):
        """
        Get the total number of filters
        """
        if chat_id:
            return await self.filters.count_documents({"chat_id": chat_id})
        return await self.filters.count_documents({})

    async def delete_filter(self, chat_id, file_id):
        """
        Delete a specific filter
        """
        await self.filters.delete_one({
            "chat_id": chat_id,
            "file_id": file_id
        })

    async def delete_all_filters(self, chat_id):
        """
        Delete all filters for a specific chat
        """
        await self.filters.delete_many({"chat_id": chat_id})

    async def get_filter_chats(self):
        """
        Get all chats that have filters
        """
        chats = await self.filters.distinct("chat_id")
        return chats

    # Connection related methods
    async def add_connection(self, user_id, chat_id):
        """
        Add a connection between user and chat
        """
        await self.connections.update_one(
            {"user_id": user_id},
            {"$addToSet": {"connected_chats": chat_id}},
            upsert=True
        )

    async def remove_connection(self, user_id, chat_id):
        """
        Remove a connection between user and chat
        """
        await self.connections.update_one(
            {"user_id": user_id},
            {"$pull": {"connected_chats": chat_id}}
        )

    async def get_connections(self, user_id):
        """
        Get all connections for a user
        """
        connections = await self.connections.find_one({"user_id": user_id})
        if connections:
            return connections.get("connected_chats", [])
        return []

    async def is_connected(self, user_id, chat_id):
        """
        Check if a user is connected to a chat
        """
        connections = await self.get_connections(user_id)
        return chat_id in connections
