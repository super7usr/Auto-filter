"""
Notification database module

This module provides database operations for managing notifications.
"""

import logging
import motor.motor_asyncio
import pymongo
import datetime
import os
from typing import Dict, List, Optional, Any, Union
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "")

class NotificationDB:
    """Notification database operations"""
    
    def __init__(self):
        """Initialize database connection"""
        self.client = None
        self.db = None
        self.notifications = None
        
        try:
            # Connect to MongoDB
            self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
            self.db = self.client.get_database("Cluster0")  # Use the default database name
            self.notifications = self.db.notifications
            
            # Create indexes for better query performance - using async call later
            logger.info("NotificationDB initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NotificationDB: {e}")
    
    async def _create_indexes(self):
        """Create indexes for notification collection"""
        try:
            # Create index on created_at for sorting by date
            await self.notifications.create_index([("created_at", pymongo.DESCENDING)])
            
            # Create index on is_read and category for filtering
            await self.notifications.create_index([
                ("is_read", pymongo.ASCENDING),
                ("category", pymongo.ASCENDING)
            ])
            
            # Create index on expires_at for auto-deletion of old notifications
            await self.notifications.create_index([("expires_at", pymongo.ASCENDING)])
            
            logger.info("NotificationDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating NotificationDB indexes: {e}")
    
    async def add_notification(self, notification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a new notification to the database
        
        Args:
            notification: Notification object to add
            
        Returns:
            The added notification with ID, or None if failed
        """
        try:
            # Insert the notification
            result = await self.notifications.insert_one(notification)
            
            # Return the notification with ID
            if result.inserted_id:
                notification['_id'] = str(result.inserted_id)
                return notification
            return None
        except Exception as e:
            logger.error(f"Error adding notification: {e}")
            return None
    
    async def get_notifications(self, limit: int = 20, skip: int = 0, 
                               is_read: Optional[bool] = None, 
                               category: Optional[str] = None,
                               include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        Get notifications from the database
        
        Args:
            limit: Maximum number of notifications to return
            skip: Number of notifications to skip (for pagination)
            is_read: Filter by read status (True/False) or None for all
            category: Filter by category or None for all
            include_expired: Whether to include expired notifications
            
        Returns:
            List of notification objects
        """
        try:
            # Build the query
            query = {}
            
            # Filter by read status if specified
            if is_read is not None:
                query['is_read'] = is_read
            
            # Filter by category if specified
            if category:
                query['category'] = category
            
            # Exclude expired notifications unless specified
            if not include_expired:
                now = datetime.datetime.now().isoformat()
                query['$or'] = [
                    {'expires_at': {'$exists': False}},
                    {'expires_at': {'$gt': now}}
                ]
            
            # Execute the query
            cursor = self.notifications.find(query).sort("created_at", pymongo.DESCENDING).skip(skip).limit(limit)
            
            # Convert ObjectId to string for JSON serialization
            notifications = []
            async for document in cursor:
                document['_id'] = str(document['_id'])
                notifications.append(document)
            
            return notifications
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string ID to ObjectId
            from bson.objectid import ObjectId
            object_id = ObjectId(notification_id)
            
            # Update the notification
            result = await self.notifications.update_one(
                {'_id': object_id},
                {'$set': {'is_read': True}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: ID of the notification to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string ID to ObjectId
            from bson.objectid import ObjectId
            object_id = ObjectId(notification_id)
            
            # Delete the notification
            result = await self.notifications.delete_one({'_id': object_id})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False
    
    async def delete_expired_notifications(self) -> int:
        """
        Delete all expired notifications
        
        Returns:
            Number of deleted notifications
        """
        try:
            now = datetime.datetime.now().isoformat()
            result = await self.notifications.delete_many({
                'expires_at': {'$exists': True, '$lt': now}
            })
            
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting expired notifications: {e}")
            return 0
    
    async def get_unread_count(self, category: Optional[str] = None) -> int:
        """
        Get count of unread notifications
        
        Args:
            category: Filter by category or None for all
            
        Returns:
            Count of unread notifications
        """
        try:
            # Build the query
            query = {'is_read': False}
            
            # Filter by category if specified
            if category:
                query['category'] = category
            
            # Exclude expired notifications
            now = datetime.datetime.now().isoformat()
            query['$or'] = [
                {'expires_at': {'$exists': False}},
                {'expires_at': {'$gt': now}}
            ]
            
            # Get count
            count = await self.notifications.count_documents(query)
            
            return count
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    async def mark_all_as_read(self, category: Optional[str] = None) -> int:
        """
        Mark all notifications as read
        
        Args:
            category: Filter by category or None for all
            
        Returns:
            Number of updated notifications
        """
        try:
            # Build the query
            query = {'is_read': False}
            
            # Filter by category if specified
            if category:
                query['category'] = category
            
            # Update all matching notifications
            result = await self.notifications.update_many(
                query,
                {'$set': {'is_read': True}}
            )
            
            return result.modified_count
        except Exception as e:
            logger.error(f"Error marking all as read: {e}")
            return 0
            
    async def get_notification_categories(self) -> List[str]:
        """
        Get list of all notification categories
        
        Returns:
            List of category names
        """
        try:
            # Aggregate to get distinct categories
            pipeline = [
                {'$group': {'_id': '$category'}},
                {'$sort': {'_id': 1}}
            ]
            
            cursor = self.notifications.aggregate(pipeline)
            
            # Extract categories from results
            categories = []
            async for document in cursor:
                if document['_id']:
                    categories.append(document['_id'])
            
            return categories
        except Exception as e:
            logger.error(f"Error getting notification categories: {e}")
            return []
