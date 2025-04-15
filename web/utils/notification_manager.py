"""
Notification manager module

This module handles sending and managing notifications in the application.
It provides functions to create, store, and retrieve notifications of various types.
"""

import logging
import asyncio
import datetime
import json
from typing import Optional, Dict, Any, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database functionality
try:
    from database.notification_db import NotificationDB
    notification_db = NotificationDB()
except ImportError as e:
    logger.error(f"Failed to import notification database: {e}")
    notification_db = None

# Function to get notifications
async def get_notifications(limit: int = 20, skip: int = 0, 
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
    if not notification_db:
        logger.warning("Cannot get notifications: database not available")
        return []
        
    return await notification_db.get_notifications(
        limit=limit,
        skip=skip,
        is_read=is_read,
        category=category,
        include_expired=include_expired
    )

async def get_notification_by_id(notification_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific notification by ID
    
    Args:
        notification_id: ID of the notification to retrieve
        
    Returns:
        The notification object or None if not found
    """
    if not notification_db:
        logger.warning(f"Cannot get notification {notification_id}: database not available")
        return None
    
    # Get notifications with a filter for the specific ID
    try:
        # Since we don't have a direct method in the database class, we'll implement it here
        # Convert string ID to ObjectId using the database module's method
        from bson.objectid import ObjectId
        
        # Query directly using MongoDB's find_one
        if notification_db.notifications:
            result = await notification_db.notifications.find_one({"_id": ObjectId(notification_id)})
            if result:
                # Convert ObjectId to string for JSON serialization
                result["_id"] = str(result["_id"])
                return result
        return None
    except Exception as e:
        logger.error(f"Error getting notification by ID: {e}")
        return None

async def mark_notification_read(notification_id: str) -> bool:
    """
    Mark a notification as read
    
    Args:
        notification_id: ID of the notification to mark as read
        
    Returns:
        True if successful, False otherwise
    """
    if not notification_db:
        logger.warning(f"Cannot mark notification {notification_id} as read: database not available")
        return False
        
    return await notification_db.mark_as_read(notification_id)

async def delete_notification(notification_id: str) -> bool:
    """
    Delete a notification
    
    Args:
        notification_id: ID of the notification to delete
        
    Returns:
        True if successful, False otherwise
    """
    if not notification_db:
        logger.warning(f"Cannot delete notification {notification_id}: database not available")
        return False
        
    return await notification_db.delete_notification(notification_id)

async def mark_all_read(category: Optional[str] = None) -> int:
    """
    Mark all notifications as read
    
    Args:
        category: Filter by category or None for all
        
    Returns:
        Number of updated notifications
    """
    if not notification_db:
        logger.warning("Cannot mark all notifications as read: database not available")
        return 0
        
    return await notification_db.mark_all_as_read(category)

async def get_unread_count(category: Optional[str] = None) -> int:
    """
    Get the count of unread notifications
    
    Args:
        category: Filter by category or None for all
        
    Returns:
        Count of unread notifications
    """
    if not notification_db:
        logger.warning("Cannot get unread count: database not available")
        return 0
        
    # Get unread notifications count from database
    try:
        return await notification_db.get_unread_count(category=category)
    except Exception as e:
        logger.error(f"Error getting unread notification count: {e}")
        return 0

# Notification levels
NOTIFICATION_LEVELS = {
    'info': 'info',
    'success': 'success',
    'warning': 'warning',
    'error': 'error'
}

async def _create_notification(message: str, level: str = 'info', 
                      category: str = 'system', metadata: Optional[Dict[str, Any]] = None,
                      expiry: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Create a notification and store it in the database
    
    Args:
        message: The notification message
        level: Notification level (info, success, warning, error)
        category: Notification category (system, user, group, etc.)
        metadata: Additional metadata for the notification
        expiry: Expiry time in seconds from now
        
    Returns:
        The created notification or None if failed
    """
    if not notification_db:
        logger.warning(f"Notification not stored (DB unavailable): {message}")
        return None
        
    # Validate level
    if level not in NOTIFICATION_LEVELS:
        level = 'info'
    
    # Create notification object
    notification = {
        'message': message,
        'level': level,
        'category': category,
        'created_at': datetime.datetime.now().isoformat(),
        'is_read': False,
        'metadata': metadata or {}
    }
    
    # Add expiry if provided
    if expiry:
        notification['expires_at'] = (
            datetime.datetime.now() + datetime.timedelta(seconds=expiry)
        ).isoformat()
    
    # Store in database
    try:
        stored_notification = await notification_db.add_notification(notification)
        if stored_notification:
            logger.info(f"Notification created: {message}")
            return stored_notification
        logger.warning(f"Failed to store notification: {message}")
        return None
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return None

# Helper functions for specific notification types

async def notify_system_update(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a system update notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='success',
        category='system_update',
        metadata=metadata,
        expiry=86400 * 7  # 7 days
    )

async def notify_new_user(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new user notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='info',
        category='user',
        metadata=metadata,
        expiry=86400 * 3  # 3 days
    )

async def notify_new_group(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new group notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='info',
        category='group',
        metadata=metadata,
        expiry=86400 * 3  # 3 days
    )

async def notify_storage_alert(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a storage alert notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='warning',
        category='storage',
        metadata=metadata,
        expiry=86400 * 1  # 1 day
    )

async def notify_backup_completed(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a backup completed notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='success',
        category='backup',
        metadata=metadata,
        expiry=86400 * 3  # 3 days
    )

async def notify_error(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create an error notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='error',
        category='error',
        metadata=metadata,
        expiry=86400 * 7  # 7 days
    )

async def notify_file_indexed(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a file indexed notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='info',
        category='files',
        metadata=metadata,
        expiry=86400 * 1  # 1 day
    )

async def notify_usage_report(message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create a usage report notification
    
    Args:
        message: The notification message
        metadata: Additional metadata
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level='info',
        category='usage',
        metadata=metadata,
        expiry=86400 * 7  # 7 days
    )

# Synchronous wrapper functions for notification functions
# These are used for compatibility with non-async code
def notify_system_update_sync(message, metadata=None):
    """Synchronous wrapper for notify_system_update"""
    asyncio.run(_create_notification(
        message=message,
        level='success',
        category='system_update',
        metadata=metadata,
        expiry=86400 * 7
    ))

def notify_new_user_sync(message, metadata=None):
    """Synchronous wrapper for notify_new_user"""
    asyncio.run(_create_notification(
        message=message,
        level='info',
        category='user',
        metadata=metadata,
        expiry=86400 * 3
    ))

def notify_new_group_sync(message, metadata=None):
    """Synchronous wrapper for notify_new_group"""
    asyncio.run(_create_notification(
        message=message,
        level='info',
        category='group',
        metadata=metadata,
        expiry=86400 * 3
    ))

def notify_storage_alert_sync(message, metadata=None):
    """Synchronous wrapper for notify_storage_alert"""
    asyncio.run(_create_notification(
        message=message,
        level='warning',
        category='storage',
        metadata=metadata,
        expiry=86400 * 1
    ))

def notify_backup_completed_sync(message, metadata=None):
    """Synchronous wrapper for notify_backup_completed"""
    asyncio.run(_create_notification(
        message=message,
        level='success',
        category='backup',
        metadata=metadata,
        expiry=86400 * 3
    ))

def notify_error_sync(message, metadata=None):
    """Synchronous wrapper for notify_error"""
    asyncio.run(_create_notification(
        message=message,
        level='error',
        category='error',
        metadata=metadata,
        expiry=86400 * 7
    ))

def notify_file_indexed_sync(message, metadata=None):
    """Synchronous wrapper for notify_file_indexed"""
    asyncio.run(_create_notification(
        message=message,
        level='info',
        category='files',
        metadata=metadata,
        expiry=86400 * 1
    ))

def notify_usage_report_sync(message, metadata=None):
    """Synchronous wrapper for notify_usage_report"""
    asyncio.run(_create_notification(
        message=message,
        level='info',
        category='usage',
        metadata=metadata,
        expiry=86400 * 7
    ))

# Create synchronous version of get_unread_count
def get_unread_count_sync(category=None):
    """Synchronous wrapper for get_unread_count"""
    try:
        return asyncio.run(get_unread_count(category=category))
    except Exception as e:
        logger.error(f"Error in get_unread_count_sync: {e}")
        return 0

async def add_notification(message: str, level: str = 'info', 
                  category: str = 'system', metadata: Optional[Dict[str, Any]] = None,
                  expiry: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Public function to add a notification
    
    Args:
        message: The notification message
        level: Notification level (info, success, warning, error)
        category: Notification category (system, user, group, etc.)
        metadata: Additional metadata
        expiry: Expiry time in seconds
        
    Returns:
        The created notification or None if failed
    """
    return await _create_notification(
        message=message,
        level=level,
        category=category,
        metadata=metadata,
        expiry=expiry
    )

def add_notification_sync(message, level='info', category='system', metadata=None, expiry=None):
    """Synchronous wrapper for add_notification"""
    try:
        return asyncio.run(add_notification(
            message=message,
            level=level,
            category=category,
            metadata=metadata,
            expiry=expiry
        ))
    except Exception as e:
        logger.error(f"Error in add_notification_sync: {e}")
        return None

# For compatibility with imports in notification_hooks.py
# These will be replaced by the async versions in future
notify_system_update = notify_system_update_sync
notify_new_user = notify_new_user_sync
notify_new_group = notify_new_group_sync
notify_storage_alert = notify_storage_alert_sync
notify_backup_completed = notify_backup_completed_sync
notify_error = notify_error_sync
notify_file_indexed = notify_file_indexed_sync
notify_usage_report = notify_usage_report_sync
