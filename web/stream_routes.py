import math
import secrets
import mimetypes
import os
import aiohttp_jinja2
import time
import logging
from info import BIN_CHANNEL, ADMINS, PORT
from utils import temp, get_size
from aiohttp import web
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix, ByteStreamer
from web.utils.render_template import media_watch, get_error_page
from web.utils.file_properties import FileNotFound, get_hash
from web.utils.admin_utils import admin_auth_required, get_session, set_session, clear_session, is_valid_admin, get_mock_activities, get_random_percentage_increase, get_formatted_date
from database.file_mapping import get_message_id_from_file_id, get_file_id_from_message_id

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    with open('web/template/homepage.html', 'r') as file:
        html = file.read()
    return web.Response(text=html, content_type='text/html')

@routes.get("/imgs/{file_path:.*}", allow_head=True)
async def img_file_handler(request):
    file_path = request.match_info.get('file_path')
    full_path = f"imgs/{file_path}"
    
    if os.path.exists(full_path):
        with open(full_path, 'rb') as file:
            content = file.read()
        
        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            content_type = 'application/octet-stream'
            
        return web.Response(body=content, content_type=content_type)
    else:
        return web.Response(text="Image not found", status=404)

@routes.get("/static/{file_path:.*}", allow_head=True)
async def static_file_handler(request):
    file_path = request.match_info.get('file_path')
    full_path = f"web/static/{file_path}"
    
    if os.path.exists(full_path):
        with open(full_path, 'rb') as file:
            content = file.read()
        
        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            content_type = 'application/octet-stream'
            
        return web.Response(body=content, content_type=content_type)
    else:
        return web.Response(text="File not found", status=404)

@routes.get("/old", allow_head=True)
async def old_root_route_handler(request):
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Movie Series Bot - Media Streaming Server</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --accent-gradient: linear-gradient(45deg, #00c6ff, #92dfff);
                --cinema-orange: #ff8c42;
                --cinema-accent: linear-gradient(135deg, #ff8c42, #ffbc80);
                --card-bg: rgba(9, 22, 52, 0.85);
                --text-glow: 0 0 10px rgba(0, 198, 255, 0.7);
                --card-glow: 0 0 25px rgba(0, 114, 255, 0.6);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }

            body {
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background-color: #091634;
                background-image: url('/imgs/img1.jpg');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
                color: var(--bs-light);
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                position: relative;
                overflow-x: hidden;
            }
            
            body::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(to bottom, 
                    rgba(9, 22, 52, 0.85), 
                    rgba(15, 52, 96, 0.8), 
                    rgba(22, 78, 135, 0.75));
                z-index: -1;
            }
            
            /* Animated particles */
            .particles {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                pointer-events: none;
            }
            
            .particle {
                position: absolute;
                width: 6px;
                height: 6px;
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                animation: float 15s linear infinite;
            }
            
            @keyframes float {
                0% {
                    transform: translateY(0) translateX(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-1000px) translateX(100px) rotate(360deg);
                    opacity: 0;
                }
            }

            .container {
                max-width: 1000px;
                text-align: center;
                padding: 2.5rem;
                z-index: 1;
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
                animation: fadeInUp 1s ease-out;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .logo-container {
                margin-bottom: 2.5rem;
                position: relative;
            }
            
            .logo-backdrop {
                position: absolute;
                width: 120px;
                height: 120px;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -70%);
                background: var(--accent-gradient);
                border-radius: 50%;
                filter: blur(20px);
                opacity: 0.6;
                z-index: -1;
                animation: pulse 3s infinite;
            }

            .logo-icon {
                font-size: 6rem;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
                animation: pulse 3s infinite;
                text-shadow: var(--text-glow);
                filter: drop-shadow(0 0 10px rgba(255, 114, 94, 0.5));
                position: relative;
            }
            
            .logo-icon::after {
                content: '';
                position: absolute;
                width: 100%;
                height: 10px;
                bottom: -10px;
                left: 0;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                animation: shine 3s infinite;
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%); }
                50% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }

            @keyframes pulse {
                0% { transform: scale(1); filter: brightness(1); }
                50% { transform: scale(1.08); filter: brightness(1.2); }
                100% { transform: scale(1); filter: brightness(1); }
            }

            .bot-title {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: var(--text-glow);
                position: relative;
                display: inline-block;
                letter-spacing: 2px;
                animation: textShadowPulse 3s infinite;
            }
            
            @keyframes textShadowPulse {
                0% {
                    text-shadow: 0 0 5px rgba(142, 84, 233, 0.5);
                }
                50% {
                    text-shadow: 0 0 15px rgba(233, 64, 87, 0.8), 0 0 30px rgba(242, 113, 33, 0.4);
                }
                100% {
                    text-shadow: 0 0 5px rgba(142, 84, 233, 0.5);
                }
            }

            .subtitle {
                font-size: 1.5rem;
                margin-bottom: 2.5rem;
                color: rgba(255, 255, 255, 0.95);
                font-weight: 400;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
                animation: fadeIn 1.5s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
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

            .search-container {
                width: 100%;
                max-width: 600px;
                margin: 0 auto 2rem auto;
            }

            .search-form {
                display: flex;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
                padding: 5px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }

            .search-input {
                flex-grow: 1;
                background: transparent;
                border: none;
                color: white;
                padding: 15px 20px;
                font-size: 1.1rem;
                outline: none;
            }

            .search-input::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }

            .search-button {
                background: linear-gradient(45deg, #0088cc, #00aaff);
                border: none;
                border-radius: 30px;
                padding: 10px 25px;
                font-size: 1rem;
                font-weight: 600;
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .search-button:hover {
                background: linear-gradient(45deg, #007bb8, #0099e6);
                transform: scale(1.05);
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

            <div class="search-container">
                <form action="/movie" method="get" class="search-form">
                    <input type="text" name="q" placeholder="Search for movies, series, or shows..." class="search-input" required>
                    <button type="submit" class="search-button">
                        <i class="fas fa-search"></i> Search
                    </button>
                </form>
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
                    <a href="https://t.me/NEW_OLD_MOVIE_SERIES_bot" class="btn-telegram">
                        <i class="fab fa-telegram-plane"></i> Use our Telegram Bot
                    </a>
                </div>
            </div>

            <div class="footer">
                <p class="footer-text">© 2025 Movie Series Bot | All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@routes.get("/movie")
async def movie_search(request):
    from database.ia_filterdb import get_search_results
    from utils import get_size
    from info import URL
    from web.utils.ads_handler import inject_ads_into_results
    
    query = request.query.get('q', '')
    if not query:
        return web.Response(text="<h1>Please provide a search query</h1>", content_type='text/html')
    
    # Search for files
    files, next_offset, total_results = await get_search_results(query, max_results=20)
    
    # Inject ads into results if ads are enabled
    has_ads = False
    if files:
        files, has_ads = await inject_ads_into_results(files)
    
    search_query = query.replace(" ", "+")
    web_search_url = f"{URL}movie?q={search_query}"
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results for: {query}</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap">
        <style>
            :root {{
                --primary-dark: #0a0e17;
                --primary-bg: #031633;
                --theme-blue: #0066cc;
                --theme-blue-hover: #0055b3;
                --accent-color: #0066cc;
                --text-color: #ffffff;
                --text-secondary: rgba(255, 255, 255, 0.7);
                --card-bg: rgba(15, 23, 42, 0.6);
                --card-border: rgba(255, 255, 255, 0.08);
                --card-hover: rgba(17, 25, 45, 0.9);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                --cta-gradient: linear-gradient(90deg, #0066cc, #0055b3);
                --header-height: 70px;
                --content-max-width: 1800px;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Montserrat', sans-serif;
                background-color: var(--primary-bg);
                background-image: url('/imgs/img1.jpg');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: var(--text-color);
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }}
            
            body::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    to bottom,
                    rgba(10, 14, 23, 0.9) 0%,
                    rgba(10, 14, 23, 0.8) 30%,
                    rgba(10, 14, 23, 0.7) 60%,
                    rgba(10, 14, 23, 0.95) 100%
                );
                z-index: -1;
            }}
            
            /* Header Section */
            header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: var(--header-height);
                padding: 0 40px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: linear-gradient(180deg, rgba(0, 0, 0, 0.7) 0%, transparent 100%);
                z-index: 100;
                transition: background-color 0.3s ease;
            }}
            
            header.scrolled {{
                background-color: var(--primary-dark);
            }}
            
            .logo-container {{
                display: flex;
                align-items: center;
            }}
            
            .logo {{
                font-size: 24px;
                font-weight: 700;
                color: var(--theme-blue);
                text-decoration: none;
                text-transform: uppercase;
                letter-spacing: 1px;
                display: flex;
                align-items: center;
            }}
            
            .logo i {{
                margin-right: 10px;
                font-size: 26px;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .search-toggle {{
                background: none;
                border: none;
                color: var(--text-color);
                font-size: 20px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .search-toggle:hover {{
                color: var(--theme-blue);
                transform: scale(1.1);
            }}
            
            .login-btn {{
                background: var(--theme-blue);
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
            }}
            
            .login-btn:hover {{
                background: var(--theme-blue-hover);
                transform: translateY(-2px);
            }}
            
            /* Main Content */
            .main-content {{
                padding-top: calc(var(--header-height) + 30px);
                padding-bottom: 50px;
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding-left: 20px;
                padding-right: 20px;
            }}
            
            .search-header {{
                text-align: center;
                margin-bottom: 40px;
                animation: fadeIn 0.5s ease-in-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .search-title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #ffffff, #d9d9d9);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .search-subtitle {{
                color: var(--text-secondary);
                font-size: 1.1rem;
                margin-bottom: 25px;
            }}
            
            .query-highlight {{
                color: var(--theme-blue);
                font-weight: 600;
            }}
            
            .results-container {{
                background: var(--card-bg);
                border-radius: 10px;
                padding: 30px;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: var(--box-shadow);
                border: 1px solid var(--card-border);
                animation: fadeIn 0.7s ease-in-out;
            }}
            
            .results-header {{
                display: flex;
                align-items: center;
                margin-bottom: 25px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 15px;
            }}
            
            .results-icon {{
                font-size: 24px;
                margin-right: 15px;
                color: var(--theme-blue);
            }}
            
            .results-title {{
                font-size: 1.5rem;
                font-weight: 600;
                color: var(--text-color);
                margin: 0;
            }}
            
            .results-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 20px;
            }}
            
            .file-card {{
                background: rgba(26, 32, 44, 0.4);
                border-radius: 8px;
                overflow: hidden;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            
            .file-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
                border-color: rgba(255, 255, 255, 0.1);
            }}
            
            .file-link {{
                text-decoration: none;
                color: var(--text-color);
                display: block;
                padding: 16px;
            }}
            
            .file-size {{
                display: inline-block;
                background: var(--theme-blue);
                color: white;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .file-name {{
                font-size: 1rem;
                line-height: 1.4;
                overflow: hidden;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                margin-bottom: 10px;
            }}
            
            .file-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.85rem;
                color: var(--text-secondary);
            }}
            
            .file-action {{
                display: flex;
                align-items: center;
                gap: 5px;
                color: var(--theme-blue);
                font-weight: 500;
            }}
            
            .no-results {{
                text-align: center;
                padding: 40px 0;
            }}
            
            .no-results-icon {{
                font-size: 4rem;
                color: var(--text-secondary);
                margin-bottom: 20px;
                opacity: 0.8;
            }}
            
            .no-results-title {{
                font-size: 1.8rem;
                margin-bottom: 15px;
                color: var(--text-color);
            }}
            
            .no-results-text {{
                color: var(--text-secondary);
                font-size: 1.1rem;
                max-width: 600px;
                margin: 0 auto 30px;
                line-height: 1.6;
            }}
            
            .search-suggestion {{
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .search-suggestion h4 {{
                font-size: 1.1rem;
                margin-bottom: 10px;
                color: var(--text-color);
            }}
            
            .search-suggestion ul {{
                list-style-type: none;
                padding-left: 10px;
            }}
            
            .search-suggestion li {{
                margin-bottom: 8px;
                color: var(--text-secondary);
                position: relative;
                padding-left: 20px;
            }}
            
            .search-suggestion li::before {{
                content: '•';
                color: var(--theme-blue);
                position: absolute;
                left: 0;
                top: 0;
                font-size: 1.2rem;
            }}
            
            .back-btn {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: none;
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: var(--text-color);
                padding: 10px 20px;
                border-radius: 4px;
                margin-top: 30px;
                font-weight: 500;
                transition: all 0.2s ease;
                text-decoration: none;
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }}
            
            .telegram-btn {{
                display: inline-flex;
                align-items: center;
                gap: 10px;
                background: var(--theme-blue);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 4px;
                margin-top: 30px;
                font-weight: 600;
                transition: all 0.2s ease;
                text-decoration: none;
            }}
            
            .telegram-btn:hover {{
                background: var(--theme-blue-hover);
                transform: translateY(-2px);
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                header {{
                    padding: 0 20px;
                }}
                
                .search-title {{
                    font-size: 2rem;
                }}
                
                .results-grid {{
                    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
                }}
            }}
            
            @media (max-width: 480px) {{
                .search-title {{
                    font-size: 1.8rem;
                }}
                
                .results-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .results-container {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <header id="header">
            <div class="logo-container">
                <a href="/" class="logo">
                    <i class="fas fa-film"></i>
                    <span>MovieBot</span>
                </a>
            </div>
            <div class="header-actions">
                <button id="search-toggle" class="search-toggle">
                    <i class="fas fa-search"></i>
                </button>
                <a href="https://t.me/NEW_OLD_MOVIE_SERIES_bot" class="login-btn">
                    <i class="fab fa-telegram-plane"></i> Open Bot
                </a>
            </div>
        </header>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="search-header">
                <h1 class="search-title">Search Results</h1>
                <p class="search-subtitle">
                    Found <span class="query-highlight">{total_results} results</span> for: "<span class="query-highlight">{query}</span>"
                </p>
            </div>
            
            <!-- Results Container -->
            <div class="results-container">
    """
    
    if files:
        html += f"""
                <div class="results-header">
                    <i class="fas fa-film results-icon"></i>
                    <h2 class="results-title">Available Files</h2>
                </div>
                
                <div class="results-grid">
        """
        
        # Add file results
        for i, file in enumerate(files, start=1):
            # Get file details - clean up file name if needed
            file_name = file.file_name if hasattr(file, 'file_name') else file.get('file_name', 'Unknown')
            file_size = get_size(file.file_size if hasattr(file, 'file_size') else file.get('file_size', 0))
            file_id = file.file_id if hasattr(file, 'file_id') else file.get('file_id', '')
            
            # Create bot link with file_id
            bot_link = f"https://t.me/NEW_OLD_MOVIE_SERIES_bot?start=file_1_{file_id}"
            
            html += f"""
                    <div class="file-card">
                        <a href="{bot_link}" class="file-link">
                            <span class="file-size">{file_size}</span>
                            <div class="file-name">{file_name}</div>
                            <div class="file-meta">
                                <span>File #{i}</span>
                                <span class="file-action">
                                    <i class="fas fa-external-link-alt"></i> Get
                                </span>
                            </div>
                        </a>
                    </div>
            """
        
        html += """
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://t.me/NEW_OLD_MOVIE_SERIES_bot" class="telegram-btn">
                        <i class="fab fa-telegram-plane"></i> More Results on Telegram
                    </a>
                </div>
        """
    else:
        # No results found
        html += """
                <div class="no-results">
                    <i class="fas fa-search-minus no-results-icon"></i>
                    <h3 class="no-results-title">No Results Found</h3>
                    <p class="no-results-text">
                        We couldn't find any matches for your search. Please try different keywords or check your spelling.
                    </p>
                    
                    <div class="search-suggestion">
                        <h4>Search Tips:</h4>
                        <ul>
                            <li>Check the spelling of your search term</li>
                            <li>Try using fewer or different keywords</li>
                            <li>Try searching for a related item</li>
                            <li>Use more general terms</li>
                        </ul>
                    </div>
                </div>
        """
    
    # Close HTML tags
    html += """
            </div>
            
            <div style="text-align: center;">
                <a href="/" class="back-btn">
                    <i class="fas fa-arrow-left"></i> Back to Home
                </a>
            </div>
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Header scroll effect
                const header = document.getElementById('header');
                window.addEventListener('scroll', function() {
                    if (window.scrollY > 50) {
                        header.classList.add('scrolled');
                    } else {
                        header.classList.remove('scrolled');
                    }
                });
                
                // Trigger scrolled state initially if page is not at the top
                if (window.scrollY > 50) {
                    header.classList.add('scrolled');
                }
            });
        </script>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')
@routes.get("/watch/{file_or_message_id}")
async def watch_handler_redirect(request):
    try:
        id_param = request.match_info['file_or_message_id']
        
        # Check for streaming parameter (indicates request from search results)
        is_streaming = request.query.get("stream", "false").lower() == "true"
        
        # Check if the ID is numeric (likely a message_id)
        if id_param.isdigit():
            message_id = int(id_param)
            return web.Response(text=await media_watch(message_id), content_type='text/html')
        else:
            # It's a file_id from the database, we need to find its message_id
            logging.info(f"Looking up message_id for file_id: {id_param}")
            
            # Use our mapping utility to find the message_id
            message_id = await get_message_id_from_file_id(id_param)
            
            if message_id:
                logging.info(f"Found message_id {message_id} for file_id {id_param}")
                return web.Response(text=await media_watch(message_id), content_type='text/html')
            else:
                # If we couldn't find a message_id, show an error
                error_message = "Could not find this file in our streaming system. Please try accessing it through the Telegram bot."
                logging.warning(f"No message_id found for file_id: {id_param}")
                return web.Response(text=get_error_page(error_message, "File Not Found"), content_type='text/html')
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
                    --primary-gradient: linear-gradient(45deg, #0d253f, #1d3557, #2b4a7a);
                    --accent-color: #3498db;
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
    """
    Improved media download function using ByteStreamer for efficient streaming
    with proper range request handling for better compatibility with media players.
    """
    try:
        range_header = request.headers.get('Range', 0)
        
        # Safely get the message
        if not temp.BOT:
            return web.Response(
                status=503,
                text="Bot service unavailable",
                content_type="text/plain"
            )
            
        # Initialize the ByteStreamer
        byte_streamer = ByteStreamer(temp.BOT)
        
        try:
            # Get file properties with the improved method
            file_id = await byte_streamer.get_file_properties(message_id)
            
            # Get secure hash for verification
            secure_hash = file_id.unique_id[:6]
            
            # Get request hash if provided
            req_hash = request.rel_url.query.get("hash")
            if req_hash and req_hash != secure_hash:
                logging.warning(f"Invalid hash: {req_hash} != {secure_hash}")
                return web.Response(
                    status=403,
                    text="Invalid file hash",
                    content_type="text/plain"
                )
                
        except FileNotFound as e:
            logging.error(f"File not found: {e}")
            return web.Response(
                status=404, 
                text="File not found", 
                content_type="text/plain"
            )
        except Exception as e:
            logging.error(f"Error retrieving file properties: {e}")
            return web.Response(
                status=500, 
                text="Error retrieving file", 
                content_type="text/plain"
            )
            
        # Get the file size
        file_size = file_id.file_size
        if not file_size:
            logging.error(f"Error: File size is 0 for message {message_id}")
            return web.Response(
                status=404, 
                text="Invalid file", 
                content_type="text/plain"
            )
        
        # Handle range requests
        from_bytes = 0
        until_bytes = 0
        
        if range_header:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            # If no range header, serve the full file
            from_bytes = 0
            until_bytes = file_size - 1

        # Validate range
        if (until_bytes >= file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
            return web.Response(
                status=416,
                text="Range not satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"},
                content_type="text/plain"
            )
        
        # Calculate streaming parameters
        chunk_size = 1024 * 1024  # 1 MB chunk size
        until_bytes = min(until_bytes, file_size - 1)
        
        offset = from_bytes - (from_bytes % chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = (until_bytes % chunk_size) + 1
        
        req_length = until_bytes - from_bytes + 1
        part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
        
        # Determine MIME type and filename
        mime_type = file_id.mime_type
        file_name = file_id.file_name
        
        if not mime_type:
            # Try to guess MIME type from filename
            if file_name:
                mime_type = mimetypes.guess_type(file_name)[0]
            
            # Default to octet-stream if we still don't have a MIME type
            if not mime_type:
                mime_type = "application/octet-stream"
                if not file_name:
                    file_name = f"{secrets.token_hex(2)}.unknown"
        
        # Determine content disposition
        disposition = "attachment"
        if mime_type and mime_type.startswith(('video/', 'audio/', 'image/')):
            disposition = "inline"  # For media files, use inline disposition for browser playback
        
        # Create response headers
        headers = {
            "Content-Type": mime_type,
            "Accept-Ranges": "bytes",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"'
        }
        
        if range_header:
            headers["Content-Range"] = f"bytes {from_bytes}-{until_bytes}/{file_size}"
            status_code = 206  # Partial Content
        else:
            status_code = 200  # OK
        
        # Get the file generator
        body = byte_streamer.yield_file(
            file_id,
            offset,
            first_part_cut,
            last_part_cut,
            part_count,
            chunk_size
        )
        
        # Return the streamresponse with the generator
        return web.Response(
            status=status_code,
            body=body,
            headers=headers
        )
    except Exception as e:
        logging.error(f"Unexpected error in media_download: {str(e)}")
        return web.Response(
            status=500,
            text=f"Internal Server Error: {str(e)}",
            content_type="text/plain"
        )

# Admin Dashboard Routes
@routes.get("/admin/login")
async def admin_login_get(request):
    """Render the admin login page"""
    context = {}
    
    # Check if there's an error parameter
    error = request.query.get('error')
    if error:
        context['error'] = error
    
    # Check if already logged in
    session = await get_session(request)
    if session.get('authenticated') and is_valid_admin(session.get('admin_id')):
        return web.HTTPFound('/admin')
    
    with open('web/template/admin_login.html', 'r') as file:
        html = file.read()
        
    # Replace error placeholder if needed
    if 'error' in context:
        html = html.replace('{% if error %}', '').replace('{% endif %}', '')
        html = html.replace('{{ error }}', context['error'])
    else:
        # Remove the error block
        start_index = html.find('{% if error %}')
        end_index = html.find('{% endif %}') + len('{% endif %}')
        if start_index != -1 and end_index != -1:
            html = html[:start_index] + html[end_index:]
    
    return web.Response(text=html, content_type='text/html')

@routes.post("/admin/login")
async def admin_login_post(request):
    """Process admin login"""
    data = await request.post()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # Check for hardcoded "renish" username and password
    if username == "renish" and password == "renish":
        # Set authenticated session
        await set_session(request, 'authenticated', True)
        # Use a default admin ID (can be any value from ADMINS list)
        await set_session(request, 'admin_id', ADMINS[0] if ADMINS else 1)
        logger.info("Admin logged in with hardcoded credentials")
        return web.HTTPFound('/admin')
    
    # Fallback to the original admin ID-based authentication
    try:
        # Try to parse admin ID
        admin_id = int(username)
        
        # Check if valid admin and password
        if is_valid_admin(admin_id) and password and len(password) >= 4:
            # Set authenticated session
            await set_session(request, 'authenticated', True)
            await set_session(request, 'admin_id', admin_id)
            return web.HTTPFound('/admin')
        else:
            return web.HTTPFound('/admin/login?error=Invalid+credentials')
    except (ValueError, TypeError):
        return web.HTTPFound('/admin/login?error=Invalid+credentials')

@routes.get("/admin/logout")
async def admin_logout(request):
    """Log out the admin user"""
    await clear_session(request)
    return web.HTTPFound('/admin/login')

@routes.get("/admin")
@admin_auth_required
async def admin_dashboard(request):
    """Render the admin dashboard"""
    from database.users_chats_db import db
    from database.ia_filterdb import Media, using_postgres
    import time
    
    # Get real statistics data from database
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    
    # Get file count from Media collection
    if using_postgres:
        total_files = await Media.count_documents()
    else:
        # For MongoDB
        from database.ia_filterdb import instance
        total_files = await instance.db[Media.collection.name].count_documents({})
    
    # Use basic growth metrics for now (can be enhanced with time series data later)
    user_percent_increase = 5  # Default sensible value
    chat_percent_increase = 3  # Default sensible value
    file_percent_increase = 4  # Default sensible value
    
    # We'll use a sensible default value for searches
    # In production, this would come from a log analysis or dedicated stats collection
    daily_searches = total_files // 10 if total_files > 0 else 0
    search_percent_increase = 2  # Default sensible value
    
    # Get recent activities from database, if possible, or use empty list
    activities = []
    
    # Build activities list from recent database events
    try:
        # Get recent user joins
        from database.users_chats_db import db
        recent_users = db.col.find().sort([('_id', -1)]).limit(3)
        
        async for user in recent_users:
            activities.append({
                "icon": "fas fa-user-plus",
                "iconBg": "rgba(34, 197, 94, 0.2)",
                "iconColor": "#22c55e",
                "title": "New User Joined",
                "description": f"User ID: {user.get('id')} has joined the bot",
                "time": "Recently"
            })
            
        # Get recent chat additions
        recent_chats = db.grp.find().sort([('_id', -1)]).limit(3)
        
        async for chat in recent_chats:
            activities.append({
                "icon": "fas fa-comments",
                "iconBg": "rgba(168, 85, 247, 0.2)",
                "iconColor": "#a855f7",
                "title": "New Group Added",
                "description": f"Bot was added to '{chat.get('title')}' group",
                "time": "Recently"
            })
    except Exception as e:
        import logging
        logging.error(f"Error getting recent activities: {e}")
        # Add a generic activity if we can't get real ones
        activities.append({
            "icon": "fas fa-info-circle",
            "iconBg": "rgba(14, 165, 233, 0.2)",
            "iconColor": "#0ea5e9",
            "title": "System Status",
            "description": "Dashboard is operational",
            "time": "Just now"
        })
    
    # Load the template
    with open('web/template/admin_dashboard.html', 'r') as file:
        html = file.read()
    
    # Replace placeholders with actual data
    replacements = {
        '{{ total_users }}': str(total_users),
        '{{ user_percent_increase }}': str(user_percent_increase),
        '{{ total_chats }}': str(total_chats),
        '{{ chat_percent_increase }}': str(chat_percent_increase),
        '{{ total_files }}': str(total_files),
        '{{ file_percent_increase }}': str(file_percent_increase),
        '{{ daily_searches }}': str(daily_searches),
        '{{ search_percent_increase }}': str(search_percent_increase),
    }
    
    for key, value in replacements.items():
        html = html.replace(key, value)
    
    # Handle activities list
    if activities:
        activities_html = ""
        for activity in activities:
            activity_item = f"""
            <li class="activity-item">
                <div class="activity-icon" style="background-color: {activity['iconBg']}; color: {activity['iconColor']};">
                    <i class="{activity['icon']}"></i>
                </div>
                <div class="activity-content">
                    <h4 class="activity-title">{activity['title']}</h4>
                    <p class="activity-description">{activity['description']}</p>
                    <span class="activity-time">{activity['time']}</span>
                </div>
            </li>
            """
            activities_html += activity_item
        
        # Replace the activities placeholder with actual items
        html = html.replace("{% for activity in activities %}", "")
        html = html.replace("{% endfor %}", "")
        # Find the activity-item placeholder and replace it
        start = html.find('<li class="activity-item">')
        end = html.find('</li>', start) + len('</li>')
        if start != -1 and end != -1:
            html = html[:start] + activities_html + html[end:]
    
    return web.Response(text=html, content_type='text/html')

# Additional admin routes (these are stubs for now)
@routes.get("/admin/users")
@admin_auth_required
async def admin_users(request):
    """Render the admin users page"""
    return web.Response(text="Admin Users Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/files")
@admin_auth_required
async def admin_files(request):
    """Render the admin files page"""
    return web.Response(text="Admin Files Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/chats")
@admin_auth_required
async def admin_chats(request):
    """Render the admin chats page"""
    return web.Response(text="Admin Chats Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/logs")
@admin_auth_required
async def admin_logs(request):
    """Render the admin logs page"""
    return web.Response(text="Admin Logs Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/settings")
@admin_auth_required
async def admin_settings(request):
    """Render the admin settings page"""
    # Import ads_db here to avoid circular imports
    from database.ads_db import ads_db
    
    # Get current ad settings
    ads_settings = await ads_db.get_ads_settings()
    
    # Check for any flash messages from the session
    session = await get_session(request)
    success_message = session.get('success_message')
    error_message = session.get('error_message')
    
    # Clear flash messages after use
    if 'success_message' in session:
        await set_session(request, 'success_message', None)
    if 'error_message' in session:
        await set_session(request, 'error_message', None)
    
    # Load the template
    with open('web/template/admin_settings.html', 'r') as file:
        html = file.read()
    
    # Replace placeholders with actual data
    replacements = {
        '{{ ads_settings.ads_code }}': ads_settings.get('ads_code', ''),
        '{{ ads_settings.frequency }}': str(ads_settings.get('frequency', 5)),
        '{{ ads_settings.enabled }}': str(ads_settings.get('enabled', False)).lower(),
        '{{ ads_settings.detect_adblock }}': str(ads_settings.get('detect_adblock', True)).lower(),
        '{{ ads_settings.adblock_message }}': ads_settings.get('adblock_message', ''),
    }
    
    # Replace placeholders
    for key, value in replacements.items():
        html = html.replace(key, value)
    
    # Handle success and error messages
    if success_message:
        html = html.replace('{% if success_message %}', '')
        html = html.replace('{% endif %}', '', 1)
        html = html.replace('{{ success_message }}', success_message)
    else:
        # Remove success message block
        start = html.find('{% if success_message %}')
        end = html.find('{% endif %}', start) + len('{% endif %}')
        if start != -1 and end != -1:
            html = html[:start] + html[end:]
    
    if error_message:
        html = html.replace('{% if error_message %}', '')
        html = html.replace('{% endif %}', '', 1)
        html = html.replace('{{ error_message }}', error_message)
    else:
        # Remove error message block
        start = html.find('{% if error_message %}')
        end = html.find('{% endif %}', start) + len('{% endif %}')
        if start != -1 and end != -1:
            html = html[:start] + html[end:]
    
    return web.Response(text=html, content_type='text/html')

@routes.get("/admin/broadcast")
@admin_auth_required
async def admin_broadcast(request):
    """Render the admin broadcast page"""
    # Create a simple broadcast form
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Broadcast Message | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --text-glow: 0 0 10px rgba(0, 198, 255, 0.7);
                --card-glow: 0 0 25px rgba(0, 114, 255, 0.6);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .container {
                max-width: 800px;
                padding: 2rem;
            }
            
            .card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .form-control {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 8px;
            }
            
            .form-control:focus {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(0, 198, 255, 0.5);
                box-shadow: 0 0 15px rgba(0, 198, 255, 0.3);
                color: white;
            }
            
            .btn-primary {
                background: linear-gradient(45deg, #0072ff, #00c6ff);
                border: none;
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-primary:hover {
                background: linear-gradient(45deg, #0066e8, #00b4f0);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            .header-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .back-link {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                color: rgba(255, 255, 255, 0.7);
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .back-link:hover {
                color: white;
                transform: translateX(-3px);
            }
            
            .broadcast-options {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .form-check {
                padding: 1rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                transition: all 0.3s ease;
            }
            
            .form-check:hover {
                background: rgba(255, 255, 255, 0.08);
            }
            
            .form-check-input:checked {
                background-color: #0072ff;
                border-color: #0072ff;
            }
            
            .alert {
                border-radius: 8px;
                padding: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="header-actions">
                <a href="/admin" class="back-link">
                    <i class="fas fa-arrow-left"></i>
                    Back to Dashboard
                </a>
                <h2>Broadcast Message</h2>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Send Message to All Users</h3>
                    
                    <form action="/admin/broadcast/send" method="POST">
                        <div class="mb-3">
                            <label for="message" class="form-label">Message Content</label>
                            <textarea class="form-control" id="message" name="message" rows="6" required placeholder="Enter your broadcast message here..."></textarea>
                            <small class="form-text text-muted">The message will be sent to all users who have interacted with your bot.</small>
                        </div>
                        
                        <div class="broadcast-options">
                            <div class="form-check flex-grow-1">
                                <input class="form-check-input" type="radio" name="broadcast_type" id="users" value="users" checked>
                                <label class="form-check-label d-block" for="users">
                                    <span class="d-block fw-bold mb-1">Users Only</span>
                                    <small class="text-muted">Send to individual users who have started the bot</small>
                                </label>
                            </div>
                            
                            <div class="form-check flex-grow-1">
                                <input class="form-check-input" type="radio" name="broadcast_type" id="groups" value="groups">
                                <label class="form-check-label d-block" for="groups">
                                    <span class="d-block fw-bold mb-1">Groups Only</span>
                                    <small class="text-muted">Send to all groups where the bot is added</small>
                                </label>
                            </div>
                            
                            <div class="form-check flex-grow-1">
                                <input class="form-check-input" type="radio" name="broadcast_type" id="both" value="both">
                                <label class="form-check-label d-block" for="both">
                                    <span class="d-block fw-bold mb-1">Both</span>
                                    <small class="text-muted">Send to all users and groups</small>
                                </label>
                            </div>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="pin_message" name="pin_message" value="1">
                            <label class="form-check-label" for="pin_message">Pin message after sending</label>
                        </div>
                        
                        <div class="d-flex justify-content-between">
                            <a href="/admin" class="btn btn-secondary">Cancel</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-paper-plane me-2"></i>
                                Send Broadcast
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <strong>Note:</strong> Broadcasting to a large number of users or groups may take some time. The process will continue in the background after you submit.
            </div>
        </div>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')

@routes.post("/admin/settings/update-ads")
@admin_auth_required
async def admin_update_ads_settings(request):
    """Update ad settings"""
    from database.ads_db import ads_db
    
    try:
        # Get form data
        data = await request.post()
        
        # Process form data
        ads_code = data.get('ads_code', '').strip()
        frequency = int(data.get('frequency', 5))
        enabled = data.get('enable_ads') == 'on'
        detect_adblock = data.get('detect_adblock') == 'on'
        adblock_message = data.get('adblock_message', '').strip()
        
        # Update database
        await ads_db.update_ads_settings(
            ads_code=ads_code,
            frequency=frequency,
            enabled=enabled,
            detect_adblock=detect_adblock,
            adblock_message=adblock_message
        )
        
        # Set success message in session
        await set_session(request, 'success_message', 'Advertisement settings updated successfully!')
        
        # Redirect to settings page
        return web.HTTPFound('/admin/settings')
        
    except Exception as e:
        # Log the error
        import logging
        logging.error(f"Error updating ad settings: {e}")
        
        # Set error message in session
        await set_session(request, 'error_message', f'Error updating settings: {str(e)}')
        
        # Redirect to settings page
        return web.HTTPFound('/admin/settings')

@routes.post("/admin/broadcast/send")
@admin_auth_required
async def admin_broadcast_send(request):
    """Process the broadcast form submission"""
    from utils import broadcast_messages, groups_broadcast_messages
    
    try:
        # Get form data
        data = await request.post()
        message_text = data.get('message', '').strip()
        broadcast_type = data.get('broadcast_type', 'users')
        pin_message = data.get('pin_message') == '1'
        
        if not message_text:
            return web.Response(
                text="Error: Message cannot be empty",
                content_type='text/html'
            )
        
        # Start background task for broadcasting
        import asyncio
        
        if broadcast_type in ['users', 'both']:
            # Broadcast to users
            asyncio.create_task(broadcast_to_users(message_text, pin_message))
            
        if broadcast_type in ['groups', 'both']:
            # Broadcast to groups
            asyncio.create_task(broadcast_to_groups(message_text, pin_message))
        
        # Return success message
        html = """
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Broadcast Initiated | Admin Dashboard</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {
                    --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                    --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                    --card-bg: rgba(9, 22, 52, 0.85);
                    --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                }
                
                body {
                    min-height: 100vh;
                    background-color: #091634;
                    color: var(--bs-light);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .container {
                    max-width: 600px;
                    padding: 2rem;
                }
                
                .success-card {
                    background: var(--card-bg);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: var(--box-shadow);
                    padding: 2rem;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }
                
                .success-icon {
                    font-size: 4rem;
                    margin-bottom: 1.5rem;
                    color: #4ade80;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% {
                        transform: scale(1);
                        opacity: 1;
                    }
                    50% {
                        transform: scale(1.1);
                        opacity: 0.8;
                    }
                    100% {
                        transform: scale(1);
                        opacity: 1;
                    }
                }
                
                .success-title {
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                }
                
                .success-message {
                    font-size: 1.1rem;
                    color: rgba(255, 255, 255, 0.8);
                    margin-bottom: 2rem;
                }
                
                .btn-primary {
                    background: linear-gradient(45deg, #0072ff, #00c6ff);
                    border: none;
                    font-weight: 600;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }
                
                .btn-primary:hover {
                    background: linear-gradient(45deg, #0066e8, #00b4f0);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
                }
                
                .bg-glow {
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(ellipse at center, rgba(0, 198, 255, 0.2) 0%, rgba(9, 22, 52, 0) 70%);
                    z-index: -1;
                    animation: rotate 30s linear infinite;
                }
                
                @keyframes rotate {
                    0% {
                        transform: rotate(0deg);
                    }
                    100% {
                        transform: rotate(360deg);
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-card">
                    <div class="bg-glow"></div>
                    <i class="fas fa-paper-plane success-icon"></i>
                    <h1 class="success-title">Broadcast Initiated</h1>
                    <p class="success-message">Your message is now being sent to all """
        
        if broadcast_type == 'users':
            html += "users."
        elif broadcast_type == 'groups':
            html += "groups."
        else:
            html += "users and groups."
        
        html += """</p>
                    <p>This process will continue in the background and may take some time to complete depending on the number of recipients.</p>
                    <a href="/admin" class="btn btn-primary mt-3">
                        <i class="fas fa-arrow-left me-2"></i>
                        Return to Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return web.Response(
            text=html,
            content_type='text/html'
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error in broadcast: {e}")
        return web.Response(
            text=f"Error: {str(e)}",
            content_type='text/html'
        )

async def broadcast_to_users(message, pin=False):
    """Background task to broadcast message to all users"""
    from utils import broadcast_messages
    from database.users_chats_db import db
    import logging
    
    try:
        # Get bot instance
        from bot import Bot
        bot = Bot().bot
        
        # Get all users
        users = await db.get_all_users()
        
        # Call the broadcast function for each user
        async for user in users:
            try:
                user_id = user['id']
                await broadcast_messages(user_id, message, pin)
            except Exception as e:
                logging.error(f"Error broadcasting to user {user.get('id')}: {e}")
        
    except Exception as e:
        logging.error(f"Error in broadcast_to_users: {e}")

async def broadcast_to_groups(message, pin=False):
    """Background task to broadcast message to all groups"""
    from utils import groups_broadcast_messages
    from database.users_chats_db import db
    import logging
    
    try:
        # Get bot instance
        from bot import Bot
        bot = Bot().bot
        
        # Get all groups
        chats = await db.get_all_chats()
        
        # Call the broadcast function for each group
        async for chat in chats:
            try:
                chat_id = chat['id']
                await groups_broadcast_messages(chat_id, message, pin)
            except Exception as e:
                logging.error(f"Error broadcasting to chat {chat.get('id')}: {e}")
        
    except Exception as e:
        logging.error(f"Error in broadcast_to_groups: {e}")

@routes.get("/admin/index")
@admin_auth_required
async def admin_index(request):
    """Render the admin index page"""
    return web.Response(text="Admin Index Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/backup")
@admin_auth_required
async def admin_backup(request):
    """Render the admin backup page"""
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Backup | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --text-glow: 0 0 10px rgba(0, 198, 255, 0.7);
                --card-glow: 0 0 25px rgba(0, 114, 255, 0.6);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .container {
                max-width: 800px;
                padding: 2rem;
            }
            
            .card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .btn-primary {
                background: linear-gradient(45deg, #0072ff, #00c6ff);
                border: none;
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-primary:hover {
                background: linear-gradient(45deg, #0066e8, #00b4f0);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            .header-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .back-link {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                color: rgba(255, 255, 255, 0.7);
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .back-link:hover {
                color: white;
                transform: translateX(-3px);
            }
            
            .backup-option {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }
            
            .backup-option:hover {
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }
            
            .backup-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .backup-description {
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 1rem;
            }
            
            .backup-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .alert {
                border-radius: 8px;
                padding: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="header-actions">
                <a href="/admin" class="back-link">
                    <i class="fas fa-arrow-left"></i>
                    Back to Dashboard
                </a>
                <h2>Create Backup</h2>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Backup Options</h3>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="backup-option text-center">
                                <i class="fas fa-database backup-icon"></i>
                                <h4 class="backup-title">Database Backup</h4>
                                <p class="backup-description">Create a backup of all database collections including users, files, and settings.</p>
                                <a href="/admin/backup/database" class="btn btn-primary">
                                    <i class="fas fa-download me-2"></i>
                                    Create Database Backup
                                </a>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="backup-option text-center">
                                <i class="fas fa-code backup-icon"></i>
                                <h4 class="backup-title">Code Backup</h4>
                                <p class="backup-description">Create a backup of the bot's source code and configuration files.</p>
                                <a href="/admin/backup/code" class="btn btn-primary">
                                    <i class="fas fa-file-archive me-2"></i>
                                    Create Code Backup
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="alert alert-info mt-4">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Note:</strong> Backups will be created and downloaded to your device. For security, backups are not stored on the server.
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')

@routes.get("/admin/backup/code")
@admin_auth_required
async def admin_backup_code(request):
    """Create and send a code backup"""
    import os
    import zipfile
    import io
    import datetime
    
    try:
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            # Walk through the project directory and add files to the zip
            for root, _, files in os.walk('.'):
                for file in files:
                    # Skip certain directories and file types
                    if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.venv', 'node_modules']):
                        continue
                    
                    # Skip certain file types
                    if file.endswith(('.pyc', '.pyo', '.zip', '.tar.gz', '.db', '.sqlite3')):
                        continue
                    
                    # Add the file to the zip
                    file_path = os.path.join(root, file)
                    # Add the file with a relative path inside the zip
                    zip_file.write(file_path, file_path)
        
        # Seek to the beginning of the buffer
        zip_buffer.seek(0)
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"code_backup_{timestamp}.zip"
        
        # Create response with the zip file
        response = web.Response(
            body=zip_buffer.getvalue(),
            content_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Error creating code backup: {e}")
        return web.Response(text=f"Error creating backup: {str(e)}", content_type='text/html')

@routes.get("/admin/backup/database")
@admin_auth_required
async def admin_backup_database(request):
    """Create and send a database backup"""
    import json
    import io
    import zipfile
    import datetime
    from database.users_chats_db import db
    
    try:
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            # Backup users collection
            users = await db.get_all_users()
            users_list = [user async for user in users]
            users_json = json.dumps(users_list, indent=2, default=str)
            zip_file.writestr('users.json', users_json)
            
            # Backup chats collection
            chats = await db.get_all_chats()
            chats_list = [chat async for chat in chats]
            chats_json = json.dumps(chats_list, indent=2, default=str)
            zip_file.writestr('chats.json', chats_json)
            
            # Get Media collection backup if possible
            try:
                from database.ia_filterdb import Media, instance
                if hasattr(instance, 'db') and hasattr(Media, 'collection'):
                    media_collection = instance.db[Media.collection.name]
                    media_cursor = media_collection.find({})
                    media_list = []
                    
                    async for doc in media_cursor:
                        # Convert ObjectId to string for JSON serialization
                        if '_id' in doc:
                            doc['_id'] = str(doc['_id'])
                        media_list.append(doc)
                    
                    media_json = json.dumps(media_list, indent=2, default=str)
                    zip_file.writestr('media.json', media_json)
            except Exception as e:
                import logging
                logging.error(f"Error backing up media collection: {e}")
                # Continue with the backup even if media fails
                zip_file.writestr('media_backup_error.txt', f"Error backing up media collection: {str(e)}")
        
        # Seek to the beginning of the buffer
        zip_buffer.seek(0)
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_backup_{timestamp}.zip"
        
        # Create response with the zip file
        response = web.Response(
            body=zip_buffer.getvalue(),
            content_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Error creating database backup: {e}")
        return web.Response(text=f"Error creating database backup: {str(e)}", content_type='text/html')

@routes.get("/admin/restart")
@admin_auth_required
async def admin_restart(request):
    """Render the admin restart page"""
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Restart System | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --danger-gradient: linear-gradient(45deg, #f43f5e, #ef4444);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .container {
                max-width: 800px;
                padding: 2rem;
            }
            
            .card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .btn-primary {
                background: linear-gradient(45deg, #0072ff, #00c6ff);
                border: none;
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-primary:hover {
                background: linear-gradient(45deg, #0066e8, #00b4f0);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
            }
            
            .btn-danger {
                background: var(--danger-gradient);
                border: none;
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-danger:hover {
                background: linear-gradient(45deg, #e11d48, #dc2626);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            .header-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .back-link {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                color: rgba(255, 255, 255, 0.7);
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .back-link:hover {
                color: white;
                transform: translateX(-3px);
            }
            
            .restart-option {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }
            
            .restart-option:hover {
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }
            
            .restart-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .restart-description {
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 1rem;
            }
            
            .restart-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            
            .icon-blue {
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .icon-red {
                background: var(--danger-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .alert {
                border-radius: 8px;
                padding: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="header-actions">
                <a href="/admin" class="back-link">
                    <i class="fas fa-arrow-left"></i>
                    Back to Dashboard
                </a>
                <h2>System Restart</h2>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Restart Options</h3>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="restart-option text-center">
                                <i class="fas fa-sync restart-icon icon-blue"></i>
                                <h4 class="restart-title">Restart Bot Only</h4>
                                <p class="restart-description">Restart only the Telegram bot service while keeping the web server running.</p>
                                <a href="/admin/restart/bot" class="btn btn-primary">
                                    <i class="fas fa-robot me-2"></i>
                                    Restart Bot
                                </a>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="restart-option text-center">
                                <i class="fas fa-globe restart-icon icon-blue"></i>
                                <h4 class="restart-title">Restart Web Server</h4>
                                <p class="restart-description">Restart only the web server service while keeping the bot running.</p>
                                <a href="/admin/restart/web" class="btn btn-primary">
                                    <i class="fas fa-server me-2"></i>
                                    Restart Web Server
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="restart-option text-center mt-4">
                        <i class="fas fa-power-off restart-icon icon-red"></i>
                        <h4 class="restart-title">Restart Entire System</h4>
                        <p class="restart-description">Restart both the Telegram bot and web server services. The system will be temporarily unavailable.</p>
                        <a href="/admin/restart/full" class="btn btn-danger">
                            <i class="fas fa-redo-alt me-2"></i>
                            Restart Entire System
                        </a>
                    </div>
                    
                    <div class="alert alert-warning mt-4">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Warning:</strong> Restarting services may cause temporary disruption. Users may not be able to use the bot or website during the restart process.
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')

@routes.get("/admin/restart/bot")
@admin_auth_required
async def admin_restart_bot(request):
    """Restart only the Telegram bot service"""
    import asyncio
    import sys
    import os
    
    # Create response page first
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Restarting Bot | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <meta http-equiv="refresh" content="10;url=/admin">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                max-width: 600px;
                padding: 2rem;
            }
            
            .restart-card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 2rem;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .spinner {
                width: 4rem;
                height: 4rem;
                margin-bottom: 1.5rem;
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-left-color: #00c6ff;
                border-radius: 50%;
                display: inline-block;
                animation: spinner 1s linear infinite;
            }
            
            @keyframes spinner {
                to {transform: rotate(360deg);}
            }
            
            .restart-title {
                font-size: 1.75rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            
            .restart-message {
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 2rem;
            }
            
            .bg-glow {
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(ellipse at center, rgba(0, 198, 255, 0.2) 0%, rgba(9, 22, 52, 0) 70%);
                z-index: -1;
                animation: rotate 30s linear infinite;
            }
            
            @keyframes rotate {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }
            
            .countdown {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.6);
                margin-top: 2rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="restart-card">
                <div class="bg-glow"></div>
                <div class="spinner"></div>
                <h1 class="restart-title">Restarting Bot</h1>
                <p class="restart-message">The Telegram bot service is being restarted. This may take a few moments.</p>
                <p>You will be redirected to the dashboard automatically when the process is complete.</p>
                <div class="countdown">Redirecting in 10 seconds...</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Schedule the bot restart
    asyncio.create_task(restart_bot_service())
    
    return web.Response(text=html, content_type='text/html')

@routes.get("/admin/restart/web")
@admin_auth_required
async def admin_restart_web(request):
    """Restart only the web server service"""
    import asyncio
    import sys
    import os
    
    # Create response page first
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Restarting Web Server | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                max-width: 600px;
                padding: 2rem;
            }
            
            .restart-card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 2rem;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .spinner {
                width: 4rem;
                height: 4rem;
                margin-bottom: 1.5rem;
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-left-color: #00c6ff;
                border-radius: 50%;
                display: inline-block;
                animation: spinner 1s linear infinite;
            }
            
            @keyframes spinner {
                to {transform: rotate(360deg);}
            }
            
            .restart-title {
                font-size: 1.75rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            
            .restart-message {
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 2rem;
            }
            
            .bg-glow {
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(ellipse at center, rgba(0, 198, 255, 0.2) 0%, rgba(9, 22, 52, 0) 70%);
                z-index: -1;
                animation: rotate 30s linear infinite;
            }
            
            @keyframes rotate {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }
            
            .warning {
                font-size: 0.9rem;
                color: #fcd34d;
                margin-top: 2rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="restart-card">
                <div class="bg-glow"></div>
                <div class="spinner"></div>
                <h1 class="restart-title">Restarting Web Server</h1>
                <p class="restart-message">The web server is being restarted. You will need to reload the page in a few moments.</p>
                <p class="warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    You will need to reload the page manually or navigate back to the admin dashboard after about 10 seconds.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Schedule the web server restart
    asyncio.create_task(restart_web_service())
    
    return web.Response(text=html, content_type='text/html')

@routes.get("/admin/restart/full")
@admin_auth_required
async def admin_restart_full(request):
    """Restart the entire system"""
    import asyncio
    import sys
    import os
    
    # Create response page first
    html = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Restarting System | Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {
                --primary-gradient: linear-gradient(45deg, #091634, #0f3460, #164e87);
                --secondary-gradient: linear-gradient(135deg, #00c6ff, #0072ff);
                --card-bg: rgba(9, 22, 52, 0.85);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            
            body {
                min-height: 100vh;
                background-color: #091634;
                color: var(--bs-light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                max-width: 600px;
                padding: 2rem;
            }
            
            .restart-card {
                background: var(--card-bg);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: var(--box-shadow);
                padding: 2rem;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .spinner {
                width: 4rem;
                height: 4rem;
                margin-bottom: 1.5rem;
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-left-color: #ef4444;
                border-radius: 50%;
                display: inline-block;
                animation: spinner 1s linear infinite;
            }
            
            @keyframes spinner {
                to {transform: rotate(360deg);}
            }
            
            .restart-title {
                font-size: 1.75rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: #ef4444;
            }
            
            .restart-message {
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 2rem;
            }
            
            .bg-glow {
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(ellipse at center, rgba(239, 68, 68, 0.2) 0%, rgba(9, 22, 52, 0) 70%);
                z-index: -1;
                animation: rotate 30s linear infinite;
            }
            
            @keyframes rotate {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }
            
            .warning {
                font-size: 0.9rem;
                color: #fcd34d;
                margin-top: 2rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="restart-card">
                <div class="bg-glow"></div>
                <div class="spinner"></div>
                <h1 class="restart-title">Full System Restart</h1>
                <p class="restart-message">The entire system is being restarted. This may take a minute to complete.</p>
                <p>You will need to navigate back to the website after the restart is complete.</p>
                <p class="warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Please wait at least 30 seconds before attempting to reconnect.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Schedule the full system restart
    asyncio.create_task(restart_full_system())
    
    return web.Response(text=html, content_type='text/html')

async def restart_bot_service():
    """Restart only the Telegram bot"""
    import logging
    import asyncio
    import os
    import signal
    import subprocess
    
    try:
        logging.info("Bot restart requested by admin")
        
        # Give time for the response to be sent
        await asyncio.sleep(1)
        
        # Find the bot process
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and any('bot.py' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                    # Kill the bot process
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    logging.info(f"Terminated bot process with PID {proc.info['pid']}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Wait a moment before restarting
        await asyncio.sleep(2)
        
        # Start the bot again
        subprocess.Popen(['python', 'bot.py'])
        logging.info("Bot restarted successfully")
        
    except Exception as e:
        logging.error(f"Error restarting bot: {e}")

async def restart_web_service():
    """Restart only the web server"""
    import logging
    import asyncio
    import os
    import signal
    import sys
    
    try:
        logging.info("Web server restart requested by admin")
        
        # Give time for the response to be sent
        await asyncio.sleep(1)
        
        # The web server will be restarted by executing a shutdown
        # The web service manager will restart it automatically
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Error restarting web server: {e}")

async def restart_full_system():
    """Restart the entire system"""
    import logging
    import asyncio
    import os
    import signal
    import sys
    import subprocess
    
    try:
        logging.info("Full system restart requested by admin")
        
        # Give time for the response to be sent
        await asyncio.sleep(1)
        
        # Kill the bot process
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and any('bot.py' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                    # Kill the bot process
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    logging.info(f"Terminated bot process with PID {proc.info['pid']}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Restart the entire system by triggering a full exit
        # The service manager will restart everything
        await asyncio.sleep(1)
        os.system('nohup bash -c "sleep 2 && python run_bot_web.py" > /dev/null 2>&1 &')
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Error restarting system: {e}")
