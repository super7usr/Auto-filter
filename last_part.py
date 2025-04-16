
import logging
import math
import mimetypes
import secrets
from aiohttp import web
from info import BIN_CHANNEL
from utils import temp
from web.utils.custom_dl import TGCustomYield
from web.utils.render_template import media_watch, render_page

# Define routes object if not already defined
try:
    routes
except NameError:
    from aiohttp import web
    routes = web.RouteTableDef()

@routes.get("/watch/{message_id}")
async def watch_handler_redirect(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except Exception as e:
        error_html = """
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Not Found</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {
                    --primary-gradient: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b);
                    --accent-color: #ff5e00;
                }

                body {
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--primary-gradient);
                    background-size: 400% 400%;
                    animation: gradient 15s ease infinite;
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                }

                @keyframes gradient {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }

                .error-container {
                    max-width: 500px;
                    text-align: center;
                    background: rgba(15, 23, 42, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }

                .error-icon {
                    font-size: 5rem;
                    color: var(--accent-color);
                    margin-bottom: 20px;
                }

                .error-title {
                    font-size: 2rem;
                    margin-bottom: 20px;
                }

                .error-message {
                    margin-bottom: 30px;
                    color: rgba(255, 255, 255, 0.8);
                }

                .back-button {
                    background: linear-gradient(45deg, #0088cc, #00aaff);
                    border: none;
                    color: white;
                    padding: 12px 25px;
                    border-radius: 30px;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                }

                .back-button:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(0, 136, 204, 0.4);
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <i class="fas fa-exclamation-triangle error-icon"></i>
                <h1 class="error-title">File Not Found</h1>
                <p class="error-message">The media file you're looking for doesn't exist or has been removed.</p>
                <a href="/" class="back-button">
                    <i class="fas fa-home"></i> Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')

@routes.get("/watch")
async def watch_query_handler(request):
    try:
        # Get message_id and hash from query params
        message_id = int(request.query.get('message_id', 0))
        hash_value = request.query.get('hash', '')
        
        if not message_id or not hash_value:
            raise ValueError("Missing required parameters: message_id and hash")
            
        # Use the render_page function which handles hash verification
        from web.utils.render_template import render_page
        return web.Response(text=await render_page(message_id, hash_value), content_type='text/html')
    except Exception as e:
        logging.error(f"Error in watch_query_handler: {str(e)}")
        error_html = f"""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - Movie Series Bot</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {{
                    --primary-gradient: linear-gradient(45deg, #0a1e3c, #0d47a1, #1976d2);
                    --accent-color: #1e88e5;
                }}

                body {{
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--primary-gradient);
                    background-size: 400% 400%;
                    animation: gradient 15s ease infinite;
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                }}

                @keyframes gradient {{
                    0% {{ background-position: 0% 50%; }}
                    50% {{ background-position: 100% 50%; }}
                    100% {{ background-position: 0% 50%; }}
                }}

                .error-container {{
                    max-width: 500px;
                    text-align: center;
                    background: rgba(15, 23, 42, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }}

                .error-icon {{
                    font-size: 5rem;
                    color: var(--accent-color);
                    margin-bottom: 20px;
                }}

                .error-title {{
                    font-size: 2rem;
                    margin-bottom: 20px;
                }}

                .error-message {{
                    margin-bottom: 30px;
                    color: rgba(255, 255, 255, 0.8);
                }}

                .error-details {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 8px;
                    font-family: monospace;
                    font-size: 0.9rem;
                    overflow-x: auto;
                    color: #f1c40f;
                }}

                .back-button {{
                    background: linear-gradient(45deg, #0088cc, #00aaff);
                    border: none;
                    color: white;
                    padding: 12px 25px;
                    border-radius: 30px;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                }}

                .back-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(0, 136, 204, 0.4);
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <i class="fas fa-exclamation-triangle error-icon"></i>
                <h1 class="error-title">Error</h1>
                <p class="error-message">There was an error processing your request.</p>
                <div class="error-details">
                    {str(e)}
                </div>
                <a href="/" class="back-button">
                    <i class="fas fa-home"></i> Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')

# Original download handler replaced with a combined version below

@routes.get("/{message_id:\d+}/{file_name}")
async def download_get_handler(request):
    try:
        return await media_download(request, int(request.match_info["message_id"]))
    except Exception:
        return web.Response(status=404, text="404: File not found")
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Movie Series Bot - Media Streaming Server</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b);
                --secondary-gradient: linear-gradient(135deg, #667eea, #764ba2);
                --card-bg: rgba(25, 25, 30, 0.8);
                --text-glow: 0 0 10px rgba(255, 255, 255, 0.7);
                --card-glow: 0 0 15px rgba(114, 9, 183, 0.7);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }

            body {
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background: var(--primary-gradient);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                color: var(--bs-light);
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .container {
                max-width: 900px;
                text-align: center;
                padding: 2rem;
            }

            .logo-container {
                margin-bottom: 2rem;
                position: relative;
            }

            .logo-icon {
                font-size: 5rem;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
                animation: pulse 2s infinite;
                text-shadow: var(--text-glow);
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }

            .bot-title {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: var(--text-glow);
            }

            .subtitle {
                font-size: 1.3rem;
                margin-bottom: 2.5rem;
                color: rgba(255, 255, 255, 0.9);
            }

            .card {
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 2.5rem;
                margin-bottom: 2.5rem;
                box-shadow: var(--box-shadow);
                transition: all 0.3s ease;
                transform: translateY(0);
            }

            .card:hover {
                box-shadow: var(--card-glow);
                transform: translateY(-5px);
            }

            .feature-list {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 1.5rem;
                margin-bottom: 2rem;
                text-align: left;
            }

            .feature-item {
                flex: 1 1 250px;
                background: rgba(255, 255, 255, 0.05);
                padding: 1.5rem;
                border-radius: 12px;
                display: flex;
                align-items: flex-start;
                transition: all 0.3s ease;
            }

            .feature-item:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-3px);
            }

            .feature-icon {
                font-size: 1.8rem;
                margin-right: 1rem;
                color: #ffaf7b;
            }

            .feature-text h4 {
                margin-top: 0;
                color: white;
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
            }

            .feature-text p {
                margin: 0;
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
            }

            .btn-telegram {
                background: linear-gradient(45deg, #0088cc, #00aaff);
                border: none;
                border-radius: 30px;
                padding: 0.8rem 2rem;
                font-size: 1.2rem;
                font-weight: 600;
                color: white;
                box-shadow: 0 4px 15px rgba(0, 136, 204, 0.4);
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 10px;
            }

            .btn-telegram:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 136, 204, 0.6);
                background: linear-gradient(45deg, #0077b3, #0099e6);
                color: white;
            }

            .footer {
                margin-top: 2rem;
                padding: 1rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                width: 100%;
                text-align: center;
            }

            .footer-text {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
            }

            @media (max-width: 768px) {
                .bot-title {
                    font-size: 2.5rem;
                }
                .feature-list {
                    flex-direction: column;
                    align-items: center;
                }
                .feature-item {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-container">
                <i class="fas fa-film logo-icon"></i>
                <h1 class="bot-title">Movie Series Bot</h1>
                <p class="subtitle">Your ultimate media streaming companion</p>
            </div>

            <div class="card">
                <div class="feature-list">
                    <div class="feature-item">
                        <i class="fas fa-search feature-icon"></i>
                        <div class="feature-text">
                            <h4>Smart Filtering</h4>
                            <p>Advanced auto-filtering system to quickly find the content you're looking for.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-play-circle feature-icon"></i>
                        <div class="feature-text">
                            <h4>HD Streaming</h4>
                            <p>High-quality streaming experience with our optimized media player.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-download feature-icon"></i>
                        <div class="feature-text">
                            <h4>Easy Downloads</h4>
                            <p>Download your favorite content with just a few clicks.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-bolt feature-icon"></i>
                        <div class="feature-text">
                            <h4>Lightning Fast</h4>
                            <p>Optimized for speed and performance with minimal loading times.</p>
                        </div>
                    </div>
                </div>

                <div class="d-grid gap-2 justify-content-center">
                    <a href="https://t.me/HA_Bots" class="btn-telegram">
                        <i class="fab fa-telegram-plane"></i> Join us on Telegram
                    </a>
                </div>
            </div>

            <div class="footer">
                <p class="footer-text">Â© 2025 HA Bots | All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


@routes.get("/stream_video/{message_id}")
async def watch_video_handler(request):
    """Handle video streaming requests using the new format: /watch/{message_id}/video?hash={hash}"""
    try:
        message_id = int(request.match_info['message_id'])
        
        # Get the hash from query params, required for secure access
        hash_value = request.query.get('hash')
        if not hash_value:
            raise ValueError("Missing hash parameter")
            
        # Use the render_page function which handles hash verification
        from web.utils.render_template import render_page
        return web.Response(text=await render_page(message_id, hash_value), content_type='text/html')
    except Exception as e:
        logging.error(f"Error in watch_video_handler: {str(e)}")
        # Use the standardized error page from render_template
        from web.utils.render_template import get_error_page
        error_html = get_error_page(
            "We couldn't load the video you requested. The file might have been removed or there could be a temporary issue with our streaming service.",
            "Video Streaming Error"
        )
        return web.Response(text=error_html, content_type='text/html')

@routes.get("/watch/{message_id}/{file_name}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        
        # Get the hash from query params, required for secure access
        hash_value = request.query.get('hash')
        if not hash_value:
            raise ValueError("Missing hash parameter")
            
        # Use the render_page function which handles hash verification
        from web.utils.render_template import render_page
        return web.Response(text=await render_page(message_id, hash_value), content_type='text/html')
    except Exception as e:
        logging.error(f"Error in watch_handler: {str(e)}")
        error_html = f"""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - Movie Series Bot</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {{
                    --primary-gradient: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b);
                    --accent-color: #ff5e00;
                }}

                body {{
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--primary-gradient);
                    background-size: 400% 400%;
                    animation: gradient 15s ease infinite;
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                }}

                @keyframes gradient {{
                    0% {{ background-position: 0% 50%; }}
                    50% {{ background-position: 100% 50%; }}
                    100% {{ background-position: 0% 50%; }}
                }}

                .error-container {{
                    max-width: 500px;
                    text-align: center;
                    background: rgba(15, 23, 42, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }}

                .error-icon {{
                    font-size: 5rem;
                    color: var(--accent-color);
                    margin-bottom: 20px;
                }}

                .error-title {{
                    font-size: 2rem;
                    margin-bottom: 20px;
                }}

                .error-message {{
                    margin-bottom: 30px;
                    color: rgba(255, 255, 255, 0.8);
                }}

                .back-button {{
                    background: linear-gradient(45deg, #0088cc, #00aaff);
                    border: none;
                    color: white;
                    padding: 12px 25px;
                    border-radius: 30px;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                }}

                .back-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(0, 136, 204, 0.4);
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <i class="fas fa-exclamation-triangle error-icon"></i>
                <h1 class="error-title">Oops! Something went wrong</h1>
                <p class="error-message">We couldn't load the media you requested. The file might have been removed or there could be a temporary issue with our streaming service.</p>
                <a href="/" class="back-button">
                    <i class="fas fa-home"></i> Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')

@routes.get("/download/{message_id:\d+}/{file_name}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        
        # Get the hash from query params, required for secure access
        hash_value = request.query.get('hash')
        if not hash_value:
            raise ValueError("Missing hash parameter")
            
        # Verify hash before allowing download
        # Get message for hash verification
        if not temp.BOT:
            raise ValueError("Bot service unavailable")
            
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        if not media_msg:
            raise ValueError(f"No message found with ID: {message_id}")
            
        # Get hash for the message
        from web.utils.file_properties import get_hash
        expected_hash = get_hash(media_msg)
        
        # Verify hash matches
        if hash_value != expected_hash:
            logging.warning(f"Invalid hash: provided {hash_value}, expected {expected_hash}")
            raise ValueError("Invalid hash for requested file")
            
        # Continue with download
        return await media_download(request, message_id)
    except Exception as e:
        logging.error(f"Error in download_handler: {str(e)}")
        error_html = """
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Download Error - Movie Series Bot</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {
                    --primary-gradient: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b);
                    --accent-color: #ff5e00;
                }

                body {
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--primary-gradient);
                    background-size: 400% 400%;
                    animation: gradient 15s ease infinite;
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                }

                @keyframes gradient {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }

                .error-container {
                    max-width: 500px;
                    text-align: center;
                    background: rgba(15, 23, 42, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }

                .error-icon {
                    font-size: 5rem;
                    color: var(--accent-color);
                    margin-bottom: 20px;
                }

                .error-title {
                    font-size: 2rem;
                    margin-bottom: 20px;
                }

                .error-message {
                    margin-bottom: 30px;
                    color: rgba(255, 255, 255, 0.8);
                }

                .back-button {
                    background: linear-gradient(45deg, #0088cc, #00aaff);
                    border: none;
                    color: white;
                    padding: 12px 25px;
                    border-radius: 30px;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                }

                .back-button:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(0, 136, 204, 0.4);
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <i class="fas fa-download error-icon"></i>
                <h1 class="error-title">Download Failed</h1>
                <p class="error-message">We couldn't download the media you requested. The file might have been removed or there could be a temporary issue with our download service.</p>
                <a href="/" class="back-button">
                    <i class="fas fa-home"></i> Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')


async def chunk_size(length):
    """Calculate chunk size for efficient streaming"""
    if length > 104857600:  # 100 MB
        return 1048576  # 1 MB
    if length > 10485760:  # 10 MB
        return 524288  # 512 KB
    return 262144  # 256 KB

async def offset_fix(offset, chunk_size):
    """Calculate offset for chunks"""
    offset -= offset % chunk_size
    return offset

async def media_download(request, message_id: int):
    try:
        range_header = request.headers.get('Range', 0)
        
        # Safely get the message
        if not temp.BOT:
            return web.Response(
                status=503,
                text="Bot service unavailable",
                content_type="text/plain"
            )
            
        try:
            media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
            if not media_msg:
                return web.Response(
                    status=404, 
                    text="File not found", 
                    content_type="text/plain"
                )
        except Exception as e:
            print(f"Error retrieving message: {str(e)}")
            return web.Response(
                status=404, 
                text="File not found or access denied", 
                content_type="text/plain"
            )
            
        # Safely get file properties
        try:
            file_properties = await TGCustomYield().generate_file_properties(media_msg)
            if not file_properties:
                return web.Response(
                    status=500, 
                    text="Could not process file properties", 
                    content_type="text/plain"
                )
            file_size = file_properties.file_size
        except Exception as e:
            print(f"Error generating file properties: {str(e)}")
            return web.Response(
                status=500, 
                text="Failed to process file", 
                content_type="text/plain"
            )

        # Process range headers
        try:
            if range_header:
                from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
                from_bytes = int(from_bytes)
                until_bytes = int(until_bytes) if until_bytes else file_size - 1
            else:
                from_bytes = request.http_range.start or 0
                until_bytes = request.http_range.stop or file_size - 1

            # Validate range
            if from_bytes < 0 or until_bytes >= file_size or from_bytes > until_bytes:
                return web.Response(
                    status=416,  # Range Not Satisfiable
                    text=f"Invalid range. File size: {file_size}",
                    content_type="text/plain"
                )
                
            req_length = until_bytes - from_bytes
        except Exception as e:
            print(f"Error processing range headers: {str(e)}")
            from_bytes = 0
            until_bytes = file_size - 1
            req_length = until_bytes - from_bytes

        # Process file and prepare response
        try:
            new_chunk_size = await chunk_size(req_length)
            offset = await offset_fix(from_bytes, new_chunk_size)
            first_part_cut = from_bytes - offset
            last_part_cut = (until_bytes % new_chunk_size) + 1
            part_count = math.ceil(req_length / new_chunk_size)
            body = TGCustomYield().yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count,
                                          new_chunk_size)

            file_name = file_properties.file_name if file_properties.file_name \
                else f"{secrets.token_hex(2)}.jpeg"
            mime_type = file_properties.mime_type if file_properties.mime_type \
                else f"{mimetypes.guess_type(file_name)}"

            return_resp = web.Response(
                status=206 if range_header else 200,
                body=body,
                headers={
                    "Content-Type": mime_type,
                    "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                    "Content-Disposition": f'attachment; filename="{file_name}"',
                    "Accept-Ranges": "bytes",
                }
            )

            if return_resp.status == 200:
                return_resp.headers.add("Content-Length", str(file_size))

            return return_resp
            
        except Exception as e:
            print(f"Error preparing file download: {str(e)}")
            return web.Response(
                status=500,
                text="An error occurred while preparing the file download",
                content_type="text/plain"
            )
    except Exception as e:
        print(f"Unexpected error in media_download: {str(e)}")
        return web.Response(
            status=500,
            text="An unexpected error occurred",
            content_type="text/plain"
        )

