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
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch
from web.utils.admin_utils import admin_auth_required, get_session, set_session, clear_session, is_valid_admin, get_mock_activities, get_random_percentage_increase, get_formatted_date

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
    
    query = request.query.get('q', '')
    if not query:
        return web.Response(text="<h1>Please provide a search query</h1>", content_type='text/html')
    
    # Search for files
    files, next_offset, total_results = await get_search_results(query, max_results=20)
    
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
    
    try:
        # Simple validation (using admin ID as username)
        admin_id = int(username)
        
        # In a real application, you would hash and check the password
        # For this simple example, we're just checking if the admin ID is valid
        # and using a basic validation that password is not empty
        if is_valid_admin(admin_id) and password and len(password) >= 4:
            # Set authenticated session
            await set_session(request, 'authenticated', True)
            await set_session(request, 'admin_id', admin_id)
            return web.HTTPFound('/admin')
        else:
            return web.HTTPFound('/admin/login?error=Invalid+credentials')
    except (ValueError, TypeError):
        return web.HTTPFound('/admin/login?error=Invalid+admin+ID+format')

@routes.get("/admin/logout")
async def admin_logout(request):
    """Log out the admin user"""
    await clear_session(request)
    return web.HTTPFound('/admin/login')

@routes.get("/admin")
@admin_auth_required
async def admin_dashboard(request):
    """Render the admin dashboard"""
    # Get statistics data
    total_users = 0  # Replace with actual user count from database
    total_chats = 0  # Replace with actual chat count from database
    total_files = 0  # Replace with actual file count from database
    daily_searches = 0  # Replace with actual search count from database
    
    # For a real implementation, these would come from the database
    user_percent_increase = get_random_percentage_increase()
    chat_percent_increase = get_random_percentage_increase()
    file_percent_increase = get_random_percentage_increase()
    search_percent_increase = get_random_percentage_increase()
    
    # Get recent activities
    activities = get_mock_activities()
    
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
    return web.Response(text="Admin Settings Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/broadcast")
@admin_auth_required
async def admin_broadcast(request):
    """Render the admin broadcast page"""
    return web.Response(text="Admin Broadcast Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/index")
@admin_auth_required
async def admin_index(request):
    """Render the admin index page"""
    return web.Response(text="Admin Index Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/backup")
@admin_auth_required
async def admin_backup(request):
    """Render the admin backup page"""
    return web.Response(text="Admin Backup Page - Not Implemented Yet", content_type='text/html')

@routes.get("/admin/restart")
@admin_auth_required
async def admin_restart(request):
    """Render the admin restart page"""
    return web.Response(text="Admin Restart Page - Not Implemented Yet", content_type='text/html')
