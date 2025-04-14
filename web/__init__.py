# Credit - adarsh-goel

import sys
import logging
from aiohttp import web
from web.stream_routes import routes as stream_routes
from web.utils.session_middleware import setup_session_middleware
from web.utils.admin_utils import setup_jinja

# Configure logger
logger = logging.getLogger(__name__)

# Initialize the web application
web_app = web.Application()

# Setup middleware
web_app = setup_session_middleware(web_app)

# Setup Jinja2 templates
setup_jinja(web_app)

# Add routes from stream_routes
web_app.add_routes(stream_routes)

# Add routes from new streaming implementation in route.py
try:
    # Import and initialize the routes from route.py
    sys.path.append('.')  # Add current directory to path
    from route import routes as route_routes
    
    # Add the routes from route.py
    web_app.add_routes(route_routes)
    
    logger.info("Added routes from route.py successfully")
except Exception as e:
    logger.error(f"Error adding routes from route.py: {e}")
    import traceback
    logger.error(traceback.format_exc())
    
# Add routes for MongoDB management
try:
    from web.routes.mongodb_routes import routes as mongodb_routes
    
    # Add the MongoDB management routes
    web_app.add_routes(mongodb_routes)
    
    logger.info("Added MongoDB management routes successfully")
except Exception as e:
    logger.error(f"Error adding MongoDB management routes: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Also add routes from last_part.py
try:
    # Import and initialize the routes from last_part.py
    sys.path.append('.')  # Add current directory to path
    from last_part import routes as last_part_routes
    
    # Add the routes from last_part.py
    web_app.add_routes(last_part_routes)
    
    logger.info("Added routes from last_part.py successfully")
except Exception as e:
    logger.error(f"Error adding routes from last_part.py: {e}")
    import traceback
    logger.error(traceback.format_exc())
    
# Add routes from first_part.py
try:
    # Import and initialize the routes from first_part.py
    sys.path.append('.')  # Add current directory to path
    from first_part import routes as first_part_routes
    
    # Add the routes from first_part.py
    web_app.add_routes(first_part_routes)
    
    logger.info("Added routes from first_part.py successfully")
except Exception as e:
    logger.error(f"Error adding routes from first_part.py: {e}")
    import traceback
    logger.error(traceback.format_exc())
    
# Add the dedicated streaming route handler
try:
    # Import our custom streaming handler setup function
    sys.path.append('.')  # Ensure path is set
    from stream_video_handler import setup_routes as setup_stream_video_routes
    
    # Register the streaming routes using the setup function
    setup_stream_video_routes(web_app)
    logger.info("Added streaming video routes successfully")
except Exception as e:
    logger.error(f"Error adding streaming video routes: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Add notification API routes
try:
    # Import our notification routes setup function
    from web.routes.notification_routes import setup_routes as setup_notification_routes
    
    # Register the notification routes
    setup_notification_routes(web_app)
    logger.info("Added notification API routes successfully")
except Exception as e:
    logger.error(f"Error adding notification API routes: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Initialize notification hooks
try:
    # Import and install notification hooks
    from web.utils.notification_hooks import install_notification_hooks
    
    # Install notification hooks for real-time notifications
    install_notification_hooks(web_app=web_app)
    logger.info("Notification hooks installed successfully")
except Exception as e:
    logger.error(f"Error installing notification hooks: {e}")
    import traceback
    logger.error(traceback.format_exc())
