
#!/usr/bin/env python
# Web server entrypoint file
import sys
import os
import time
import datetime
import aiohttp
from aiohttp import web
import asyncio
from info import PORT

# Import the web routes
from web import web_app

# Print the start message
print(f"Starting Web Server at {datetime.datetime.now()}")

# Run the web server
if __name__ == "__main__":
    try:
        web.run_app(web_app, host="0.0.0.0", port=PORT)
    except Exception as e:
        import traceback
        print(f"Error starting web server: {e}")
        traceback.print_exc()
