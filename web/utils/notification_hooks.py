"""
Notification hooks for connecting events to the notification system

This module provides hooks for various events in the system to generate notifications.
It serves as a central location for other parts of the application to trigger notifications.
"""

import logging
import asyncio
import datetime
import time
import os
import sys
from typing import Optional, Dict, Any, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import notification manager
try:
    from web.utils.notification_manager import (
        notify_system_update,
        notify_new_user,
        notify_new_group,
        notify_storage_alert,
        notify_backup_completed,
        notify_error,
        notify_file_indexed,
        notify_usage_report
    )
except ImportError as e:
    logger.error(f"Error importing notification manager: {e}")
    # Create dummy functions to avoid errors
    def notify_system_update(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_new_user(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_new_group(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_storage_alert(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_backup_completed(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_error(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_file_indexed(message): logger.warning(f"Notification manager not loaded: {message}")
    def notify_usage_report(message): logger.warning(f"Notification manager not loaded: {message}")

class NotificationHooks:
    """Hooks for connecting events to the notification system"""
    
    def __init__(self):
        """Initialize notification hooks"""
        self.last_notification_time = {}
        self.throttle_intervals = {
            'system_update': 3600,  # 1 hour
            'new_user': 60,         # 1 minute
            'new_group': 60,        # 1 minute
            'storage_alert': 86400, # 24 hours
            'backup': 3600,         # 1 hour
            'error': 300,           # 5 minutes
            'files_indexed': 60,    # 1 minute
            'usage_report': 86400   # 24 hours
        }
    
    def _should_throttle(self, hook_type: str, key: Union[str, int]) -> bool:
        """
        Check if notification should be throttled
        
        Args:
            hook_type: Type of notification
            key: Unique key for throttling (e.g., user_id, group_id)
            
        Returns:
            bool: True if should throttle, False otherwise
        """
        throttle_key = f"{hook_type}:{key}"
        current_time = time.time()
        
        # Check if throttling applies
        if throttle_key in self.last_notification_time:
            last_time = self.last_notification_time[throttle_key]
            throttle_interval = self.throttle_intervals.get(hook_type, 60)  # Default 1 minute
            
            if current_time - last_time < throttle_interval:
                logger.info(f"Throttling notification {hook_type} for {key}")
                return True
        
        # Update last notification time
        self.last_notification_time[throttle_key] = current_time
        return False
    
    async def on_system_update(self, version: Optional[str] = None, details: Optional[str] = None) -> None:
        """
        Hook for system update events
        
        Args:
            version: New version number
            details: Update details
        """
        if self._should_throttle('system_update', 'system'):
            return
        
        message = "System has been updated"
        if version:
            message += f" to version {version}"
        if details:
            message += f": {details}"
        
        notify_system_update(message)
        logger.info(f"System update notification: {message}")
    
    async def on_new_user(self, user_id: int, name: Optional[str] = None, username: Optional[str] = None) -> None:
        """
        Hook for new user events
        
        Args:
            user_id: User ID
            name: User's name
            username: User's username
        """
        if self._should_throttle('new_user', user_id):
            return
        
        message = f"New user joined"
        if name:
            message += f": {name}"
        message += f" (ID: {user_id})"
        if username:
            message += f" @{username}"
        
        notify_new_user(message)
        logger.info(f"New user notification: {message}")
    
    async def on_new_group(self, group_id: int, title: Optional[str] = None, member_count: Optional[int] = None) -> None:
        """
        Hook for new group events
        
        Args:
            group_id: Group ID
            title: Group title
            member_count: Number of members in the group
        """
        if self._should_throttle('new_group', group_id):
            return
        
        message = f"Bot was added to new group"
        if title:
            message += f": {title}"
        message += f" (ID: {group_id})"
        if member_count:
            message += f" with {member_count} members"
        
        notify_new_group(message)
        logger.info(f"New group notification: {message}")
    
    async def on_storage_limit(self, percentage: int, available_space: Optional[str] = None) -> None:
        """
        Hook for storage limit events
        
        Args:
            percentage: Percentage of storage used
            available_space: Available space remaining
        """
        # Use the percentage as the key for throttling
        throttle_key = f"storage_{percentage // 5 * 5}"  # Round to nearest 5%
        if self._should_throttle('storage_alert', throttle_key):
            return
        
        message = f"Database storage is at {percentage}% capacity"
        if available_space:
            message += f" ({available_space} remaining)"
        
        notify_storage_alert(message)
        logger.info(f"Storage alert notification: {message}")
    
    async def on_backup_created(self, backup_file: Optional[str] = None, size: Optional[str] = None) -> None:
        """
        Hook for backup creation events
        
        Args:
            backup_file: Backup file name
            size: Backup size
        """
        if self._should_throttle('backup', 'system'):
            return
        
        message = "Database backup completed successfully"
        if backup_file:
            message += f" ({backup_file}"
            if size:
                message += f", {size}"
            message += ")"
        
        notify_backup_completed(message)
        logger.info(f"Backup completed notification: {message}")
    
    async def on_error(self, error_type: str, details: Optional[str] = None) -> None:
        """
        Hook for error events
        
        Args:
            error_type: Type of error
            details: Error details
        """
        if self._should_throttle('error', error_type):
            return
        
        message = f"Error detected: {error_type}"
        if details:
            message += f" - {details}"
        
        notify_error(message)
        logger.info(f"Error notification: {message}")
    
    async def on_files_indexed(self, count: int, source: Optional[str] = None) -> None:
        """
        Hook for files indexed events
        
        Args:
            count: Number of files indexed
            source: Source of the files
        """
        throttle_key = 'files_indexed'
        if self._should_throttle(throttle_key, 'system'):
            return
        
        message = f"{count} new files indexed"
        if source:
            message += f" from {source}"
        
        notify_file_indexed(message)
        logger.info(f"Files indexed notification: {message}")
    
    async def on_usage_report(self, details: Optional[str] = None) -> None:
        """
        Hook for usage report events
        
        Args:
            details: Report details
        """
        if self._should_throttle('usage_report', 'system'):
            return
        
        message = "Weekly usage report is available"
        if details:
            message += f": {details}"
        
        notify_usage_report(message)
        logger.info(f"Usage report notification: {message}")

# Create a singleton instance
hooks = NotificationHooks()

def install_notification_hooks(web_app=None):
    """
    Install notification hooks into the web application
    
    Args:
        web_app: The web application instance
    """
    try:
        logger.info("Installing notification hooks")
        
        # Install hooks into various parts of the application
        # This might involve registering callbacks, etc.
        
        # Store references in the web app if provided
        if web_app:
            web_app['notification_hooks'] = hooks
        
        logger.info("Notification hooks installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing notification hooks: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False