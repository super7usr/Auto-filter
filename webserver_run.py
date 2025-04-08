import os
import sys
import time
import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set default ADMINS if not present
if not os.environ.get('ADMINS'):
    os.environ['ADMINS'] = '1927155351'  # Using the provided admin ID
    print("Info - Setting default ADMINS value")

# Print the start message
print(f"Starting Web Server at {datetime.datetime.now()}")

# Initialize variables
if not os.environ.get('API_ID'):
    print("Warning - API_ID not found, web server may have limited functionality")
if not os.environ.get('API_HASH'):
    print("Warning - API_HASH not found, web server may have limited functionality")
if not os.environ.get('BOT_TOKEN'):
    print("Warning - BOT_TOKEN not found, web server may have limited functionality")
    
# Set default values for other required variables if missing
if not os.environ.get('LOG_CHANNEL'):
    os.environ['LOG_CHANNEL'] = '-1001927155351'
    print("Info - Setting default LOG_CHANNEL value")
if not os.environ.get('BIN_CHANNEL'):
    os.environ['BIN_CHANNEL'] = '-1001927155351'
    print("Info - Setting default BIN_CHANNEL value")

# Run the web server
async def main():
    try:
        # Use the correct port (5000) instead of the default 8080
        os.environ['PORT'] = '5000'
        
        from web import web_app
        from aiohttp import web
        
        host = '0.0.0.0'  # Make sure it's accessible externally
        port = 5000
        
        print(f"Starting web server on {host}:{port}...")
        
        # Run the aiohttp web app
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        # Keep the server running
        print("Web server is now running")
        while True:
            await asyncio.sleep(3600)  # Keep it alive
            
    except KeyboardInterrupt:
        print("\nWeb server stopped by user.")
    except Exception as e:
        import traceback
        print(f"Error starting web server: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())