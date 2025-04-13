# Credit - adarsh-goel

from aiohttp import web
from web.stream_routes import routes
from web.utils.session_middleware import setup_session_middleware
from web.utils.admin_utils import setup_jinja

# Initialize the web application
web_app = web.Application()

# Setup middleware
web_app = setup_session_middleware(web_app)

# Setup Jinja2 templates
setup_jinja(web_app)

# Add routes
web_app.add_routes(routes)
