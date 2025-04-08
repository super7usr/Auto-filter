import math
import secrets
import mimetypes
from info import BIN_CHANNEL
from utils import temp
from aiohttp import web
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text="Movie Series Bot - Media Streaming Server", content_type='text/html')

@routes.get("/movie")
async def movie_search(request):
    query = request.query.get('q', '')
    if not query:
        return web.Response(text="<h1>Please provide a search query</h1>", content_type='text/html')

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results for: {query}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .search-header {{
                background-color: #3a1c71;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .result-item {{
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .result-title {{
                color: #3a1c71;
                margin-top: 0;
            }}
            .bot-link {{
                display: inline-block;
                background-color: #3a1c71;
                color: white;
                padding: 10px 15px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .bot-link:hover {{
                background-color: #d76d77;
            }}
        </style>
    </head>
    <body>
        <div class="search-header">
            <h1>Search Results for: {query}</h1>
        </div>

        <p>Here are the search results for your query. To get direct file links, please use our Telegram bot:</p>

        <div class="result-item">
            <h2 class="result-title">Use our Telegram Bot</h2>
            <p>For better search results and direct access to movie files, use our Telegram bot.</p>
            <p>Just search for "{query}" in our bot to get instant results!</p>
            <a href="https://t.me/{temp.U_NAME}" class="bot-link">Open Telegram Bot</a>
        </div>

        <div class="result-item">
            <h2 class="result-title">Why use our Telegram Bot?</h2>
            <ul>
                <li>Faster search results</li>
                <li>Direct download links</li>
                <li>High-quality streaming options</li>
                <li>Multiple language and quality options</li>
                <li>Regular updates with new content</li>
            </ul>
        </div>
    </body>
    </html>
    """

    return web.Response(text=html, content_type='text/html')

@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = request.match_info["message_id"]
        return await media_watch(message_id)
    except Exception:
        return web.Response(status=404, text="404: File not found")

@routes.get("/download/{message_id:\d+}/{file_name}")
async def download_handler(request):
    try:
        return await media_download(request, int(request.match_info["message_id"]))
    except Exception:
        return web.Response(status=404, text="404: File not found")

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
                <p class="footer-text">© 2025 HA Bots | All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


@routes.get("/watch/{message_id}/{file_name}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except Exception as e:
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
        return await media_download(request, message_id)
    except Exception as e:
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


async def media_download(request, message_id: int):
    range_header = request.headers.get('Range', 0)
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_size = file_properties.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = request.http_range.stop or file_size - 1

    req_length = until_bytes - from_bytes

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