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
    files, next_offset, total_results = await get_search_results(query, max_results=12)
    
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
        <style>
            :root {{
                --primary-gradient: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b);
                --secondary-gradient: linear-gradient(135deg, #667eea, #764ba2);
                --card-bg: rgba(25, 25, 30, 0.8);
                --text-glow: 0 0 10px rgba(255, 255, 255, 0.7);
                --card-glow: 0 0 15px rgba(114, 9, 183, 0.7);
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }}
            
            body {{
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                background: var(--primary-gradient);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                color: var(--bs-light);
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .container {{
                max-width: 900px;
                width: 100%;
                margin: 20px auto;
                text-align: center;
            }}
            
            .search-header {{
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: var(--box-shadow);
                animation: fadeIn 0.5s ease-in-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .search-header h1 {{
                margin: 0;
                background: var(--secondary-gradient);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5rem;
                font-weight: 700;
            }}
            
            .search-title {{
                color: #fff;
                font-size: 1.3rem;
                margin: 20px 0;
                opacity: 0.9;
            }}
            
            .results-container {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .results-list {{
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                box-shadow: var(--box-shadow);
                text-align: left;
                transition: all 0.3s ease;
                animation: slideIn 0.5s ease-in-out;
                animation-fill-mode: both;
            }}
            
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateX(-20px); }}
                to {{ opacity: 1; transform: translateX(0); }}
            }}
            
            .results-list:hover {{
                box-shadow: var(--card-glow);
            }}
            
            .result-list-title {{
                margin-top: 0;
                margin-bottom: 20px;
                color: #fff;
                font-size: 1.5rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .result-icon {{
                color: #ffaf7b;
                font-size: 1.8rem;
            }}
            
            .file-item {{
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
                transition: all 0.3s ease;
                border-left: 4px solid #0088cc;
            }}
            
            .file-item:hover {{
                transform: translateY(-3px);
                background: rgba(0, 0, 0, 0.3);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .file-name {{
                font-weight: 500;
                color: #fff;
                margin-bottom: 5px;
                word-break: break-word;
            }}
            
            .file-size {{
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
                display: inline-block;
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 8px;
                border-radius: 4px;
                margin-right: 8px;
            }}
            
            .file-link {{
                display: block;
                color: inherit;
                text-decoration: none;
            }}
            
            .btn-telegram {{
                background: linear-gradient(45deg, #0088cc, #00aaff);
                border: none;
                border-radius: 30px;
                padding: 12px 25px;
                font-size: 1.1rem;
                font-weight: 600;
                color: white;
                box-shadow: 0 4px 15px rgba(0, 136, 204, 0.4);
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                margin-top: 10px;
            }}
            
            .btn-telegram:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 136, 204, 0.6);
                background: linear-gradient(45deg, #0077b3, #0099e6);
                color: white;
            }}
            
            .no-results {{
                padding: 40px 25px;
                text-align: center;
                color: rgba(255, 255, 255, 0.8);
            }}
            
            .no-results h3 {{
                margin-bottom: 20px;
                color: #fff;
            }}
            
            .home-link {{
                color: rgba(255, 255, 255, 0.7);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 5px;
                margin-top: 20px;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }}
            
            .home-link:hover {{
                color: white;
            }}
            
            .query-highlight {{
                background: linear-gradient(45deg, #ff9966, #ff5e62);
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: 500;
            }}
            
            @media (max-width: 768px) {{
                .search-header h1 {{
                    font-size: 2rem;
                }}
                .container {{
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="search-header">
                <h1>Search Results</h1>
                <p class="search-title">
                    <span class="query-highlight">📥 Found {total_results} results for: {query}</span>
                </p>
            </div>
            
            <div class="results-container">
            """
    
    if files:
        html += f"""
                <div class="results-list">
                    <h2 class="result-list-title">
                        <i class="fas fa-file-video result-icon"></i>
                        Available Files
                    </h2>
        """
        
        # Add file results
        for i, file in enumerate(files, start=1):
            # Get file details - clean up file name if needed
            file_name = file.file_name if hasattr(file, 'file_name') else file.get('file_name', 'Unknown')
            file_size = get_size(file.file_size if hasattr(file, 'file_size') else file.get('file_size', 0))
            file_id = file.file_id if hasattr(file, 'file_id') else file.get('file_id', '')
            
            # Create bot link with file_id
            bot_link = f"https://t.me/NEW_OLD_MOVIE_SERIES_bot?start=file_1927155351_{file_id}"
            
            html += f"""
                    <div class="file-item">
                        <a href="{bot_link}" class="file-link">
                            <div class="file-name">{i}. [{file_size}] {file_name}</div>
                        </a>
                    </div>
            """
        
        html += """
                    <a href="https://t.me/NEW_OLD_MOVIE_SERIES_bot" class="btn-telegram">
                        <i class="fab fa-telegram-plane"></i> More Results on Telegram
                    </a>
                </div>
        """
    else:
        html += """
                <div class="results-list">
                    <div class="no-results">
                        <h3><i class="fas fa-exclamation-circle"></i> No Results Found</h3>
                        <p>We couldn't find any files matching your search query.</p>
                        <p>Try different keywords or check our Telegram bot for more comprehensive results.</p>
                        <a href="https://t.me/NEW_OLD_MOVIE_SERIES_bot" class="btn-telegram">
                            <i class="fab fa-telegram-plane"></i> Search on Telegram
                        </a>
                    </div>
                </div>
        """
    
    html += """
                <div class="results-list">
                    <h2 class="result-list-title">
                        <i class="fas fa-info-circle result-icon"></i>
                        Get More Features
                    </h2>
                    <p>Use our Telegram bot for advanced features:</p>
                    <ul>
                        <li>Interactive previews with technical details</li>
                        <li>Visual quality tags (4K, 1080p, HDR, etc.)</li>
                        <li>Direct streaming and downloads</li>
                        <li>Plot summaries and IMDb information</li>
                    </ul>
                    <a href="/" class="home-link">
                        <i class="fas fa-arrow-left"></i> Back to Homepage
                    </a>
                </div>
            </div>
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
