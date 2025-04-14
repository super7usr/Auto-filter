"""
API routes for the notification system

This module provides API endpoints for retrieving, marking as read,
and managing notifications.
"""

import logging
import json
import time
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import notification manager
try:
    from web.utils.notification_manager import (
        get_notifications,
        mark_notification_read,
        mark_all_read,
        delete_notification,
        get_unread_count,
        add_notification,
        get_notification_by_id
    )
except ImportError as e:
    logger.error(f"Error importing notification manager: {e}")
    
    # Create dummy functions for testing
    _notifications = []
    
    async def get_notifications(limit=10, skip=0, include_read=False):
        return _notifications
    
    async def mark_notification_read(notification_id):
        for notification in _notifications:
            if notification.get('id') == notification_id:
                notification['read'] = True
                return True
        return False
    
    async def mark_all_read():
        for notification in _notifications:
            notification['read'] = True
        return True
    
    async def delete_notification(notification_id):
        global _notifications
        _notifications = [n for n in _notifications if n.get('id') != notification_id]
        return True
    
    async def get_unread_count():
        return len([n for n in _notifications if not n.get('read', False)])
    
    async def add_notification(type, message, data=None):
        notification_id = int(time.time() * 1000)
        _notifications.append({
            'id': notification_id,
            'type': type,
            'message': message,
            'data': data,
            'read': False,
            'timestamp': datetime.now().isoformat()
        })
        return notification_id
    
    async def get_notification_by_id(notification_id):
        for notification in _notifications:
            if notification.get('id') == notification_id:
                return notification
        return None

# API endpoints
async def get_notifications_handler(request):
    """Handle GET /api/notifications"""
    try:
        # Parse query parameters
        limit = int(request.query.get('limit', 10))
        skip = int(request.query.get('skip', 0))
        include_read = request.query.get('include_read', 'false').lower() == 'true'
        
        # Get notifications
        notifications = await get_notifications(limit, skip, include_read)
        
        # Return JSON response
        return web.json_response({
            'success': True,
            'notifications': notifications,
            'unread_count': await get_unread_count()
        })
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_unread_count_handler(request):
    """Handle GET /api/notifications/unread"""
    try:
        # Get unread count
        unread_count = await get_unread_count()
        
        # Return JSON response
        return web.json_response({
            'success': True,
            'unread_count': unread_count
        })
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def mark_read_handler(request):
    """Handle POST /api/notifications/read/{id}"""
    try:
        # Get notification ID from URL
        notification_id = request.match_info.get('id')
        
        # Mark notification as read
        success = await mark_notification_read(notification_id)
        
        # Return JSON response
        return web.json_response({
            'success': success,
            'unread_count': await get_unread_count()
        })
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def mark_all_read_handler(request):
    """Handle POST /api/notifications/read-all"""
    try:
        # Mark all notifications as read
        success = await mark_all_read()
        
        # Return JSON response
        return web.json_response({
            'success': success,
            'unread_count': 0
        })
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def delete_notification_handler(request):
    """Handle DELETE /api/notifications/{id}"""
    try:
        # Get notification ID from URL
        notification_id = request.match_info.get('id')
        
        # Delete notification
        success = await delete_notification(notification_id)
        
        # Return JSON response
        return web.json_response({
            'success': success,
            'unread_count': await get_unread_count()
        })
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def create_test_notification_handler(request):
    """Handle POST /api/notifications/test - For testing only"""
    try:
        # Parse request body
        data = await request.json()
        
        # Create notification
        notification_id = await add_notification(
            data.get('type', 'info'),
            data.get('message', 'Test notification'),
            data.get('data', None)
        )
        
        # Return JSON response
        return web.json_response({
            'success': True,
            'notification_id': notification_id,
            'unread_count': await get_unread_count()
        })
    except Exception as e:
        logger.error(f"Error creating test notification: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app):
    """Register notification routes with the web application"""
    # API routes
    app.router.add_get('/api/notifications', get_notifications_handler)
    app.router.add_get('/api/notifications/unread', get_unread_count_handler)
    app.router.add_post('/api/notifications/read/{id}', mark_read_handler)
    app.router.add_post('/api/notifications/read-all', mark_all_read_handler)
    app.router.add_delete('/api/notifications/{id}', delete_notification_handler)
    
    # Test routes (for development only)
    app.router.add_post('/api/notifications/test', create_test_notification_handler)
    
    return app