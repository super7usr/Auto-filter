import os
import aiohttp_jinja2
import jinja2
import datetime
import logging
from aiohttp import web
from functools import wraps
from info import ADMINS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Jinja2 templates
def setup_jinja(app):
    """Setup Jinja2 template engine for admin pages"""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_path))

# Admin authentication utilities
def admin_auth_required(func):
    """Decorator to require admin authentication"""
    @wraps(func)
    async def wrapper(request):
        session = await get_session(request)
        
        if not session.get('authenticated') or not session.get('admin_id'):
            return web.HTTPFound('/admin/login')
        
        # Verify that the admin ID is valid
        admin_id = session.get('admin_id')
        if not is_valid_admin(admin_id):
            # Clear the invalid session
            await clear_session(request)
            return web.HTTPFound('/admin/login?error=Invalid+admin+credentials')
            
        return await func(request)
    return wrapper

async def get_session(request):
    """Get the current session or create a new one"""
    session = request.get('session', {})
    return session

async def set_session(request, key, value):
    """Set a session value"""
    if not hasattr(request, 'session'):
        request['session'] = {}
    request['session'][key] = value

async def clear_session(request):
    """Clear the session"""
    request['session'] = {}

def is_valid_admin(admin_id):
    """Check if the given ID is a valid admin ID"""
    if not admin_id:
        return False
    
    try:
        admin_id = int(admin_id)
        if admin_id in ADMINS:
            return True
    except (ValueError, TypeError):
        pass
    
    return False

# Data formatting utilities
def format_size(size_bytes):
    """Format bytes to human-readable size"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_random_percentage_increase():
    """Generate a random percentage increase for demo purposes"""
    # In production, this would be calculated from actual data
    import random
    return random.randint(2, 15)

def get_formatted_date():
    """Get current date formatted for display"""
    now = datetime.datetime.now()
    return now.strftime("%B %d, %Y %H:%M:%S")

# Mock data generators (will be replaced with actual data in production)
def get_mock_activities():
    """Generate mock activities for testing the admin panel"""
    return [
        {
            "icon": "fas fa-user-plus",
            "iconBg": "rgba(34, 197, 94, 0.2)",
            "iconColor": "#22c55e",
            "title": "New User Joined",
            "description": "User ID: 283947283 has joined the bot",
            "time": "2 minutes ago"
        },
        {
            "icon": "fas fa-file-alt",
            "iconBg": "rgba(14, 165, 233, 0.2)",
            "iconColor": "#0ea5e9",
            "title": "Files Indexed",
            "description": "15 new files indexed from channel @MovieChannel",
            "time": "1 hour ago"
        },
        {
            "icon": "fas fa-comments",
            "iconBg": "rgba(168, 85, 247, 0.2)",
            "iconColor": "#a855f7",
            "title": "New Group Added",
            "description": "Bot was added to 'Movies Discussion' group",
            "time": "3 hours ago"
        },
        {
            "icon": "fas fa-exclamation-triangle",
            "iconBg": "rgba(245, 158, 11, 0.2)",
            "iconColor": "#f59e0b",
            "title": "API Warning",
            "description": "High rate of API usage detected",
            "time": "5 hours ago"
        }
    ]