import math
import secrets
import mimetypes
import os
import logging
import json
from info import BIN_CHANNEL
from utils import temp
from aiohttp import web
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch
# Commented out as it's causing SQLAlchemy dependency issues
# from web.utils.movie_utils import get_recent_movies
from web.utils.file_properties import get_file_ids

# Configure logger
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    try:
        # Create sample movies data for testing
        sample_movies = [
            {
                'movie_name': 'The Shawshank Redemption',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '9.3', 'year': '1994'},
                'media_id': 'sample_media_id_1'
            },
            {
                'movie_name': 'The Godfather',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '9.2', 'year': '1972'},
                'media_id': 'sample_media_id_2'
            },
            {
                'movie_name': 'The Dark Knight',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '9.0', 'year': '2008'},
                'media_id': 'sample_media_id_3'
            },
            {
                'movie_name': 'Pulp Fiction',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '8.9', 'year': '1994'},
                'media_id': 'sample_media_id_4'
            },
            {
                'movie_name': 'The Lord of the Rings: The Return of the King',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '9.0', 'year': '2003'},
                'media_id': 'sample_media_id_5'
            },
            {
                'movie_name': 'Inception',
                'poster': '/imgs/no-poster.svg',
                'imdb_data': {'rating': '8.8', 'year': '2010'},
                'media_id': 'sample_media_id_6'
            }
        ]
        
        # Read the template file
        with open('web/template/homepage.html', 'r') as file:
            html = file.read()
        
        # Convert movie data to JSON for template
        movies_json = json.dumps([{
            'title': movie.get('movie_name', ''),
            'poster': movie.get('poster', ''),
            'imdb_rating': movie.get('imdb_data', {}).get('rating', ''),
            'year': movie.get('imdb_data', {}).get('year', ''),
            'message_id': movie.get('media_id', '')
        } for movie in sample_movies], default=str)
        
        # Replace placeholder in template with actual movie data
        html = html.replace('const RECENT_MOVIES = [];', f'const RECENT_MOVIES = {movies_json};')
        
        return web.Response(text=html, content_type='text/html')
    
    except Exception as e:
        logger.error(f"Error in homepage handler: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fallback to just serving the template without movie data
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

@routes.get("/api/recent-movies", allow_head=True)
async def get_recent_movies_api(request):
    try:
        # Create some sample movies for testing purposes
        # In a real-world scenario, you'd fetch these from your database
        sample_movies = [
            {
                'id': '1',
                'file_name': 'The Shawshank Redemption 1994 1080p BluRay.mp4',
                'file_size': 1524000000,
                'file_id': 'sample_file_id_1',
                'poster_url': '/imgs/no-poster.svg',
                'year': '1994'
            },
            {
                'id': '2',
                'file_name': 'The Godfather 1972 720p.mkv',
                'file_size': 1250000000,
                'file_id': 'sample_file_id_2',
                'poster_url': '/imgs/no-poster.svg',
                'year': '1972'
            },
            {
                'id': '3',
                'file_name': 'The Dark Knight 2008 4K HDR.mp4',
                'file_size': 2800000000,
                'file_id': 'sample_file_id_3',
                'poster_url': '/imgs/no-poster.svg',
                'year': '2008'
            },
            {
                'id': '4',
                'file_name': 'Pulp Fiction 1994 Blu-Ray.mp4',
                'file_size': 1800000000,
                'file_id': 'sample_file_id_4',
                'poster_url': '/imgs/no-poster.svg',
                'year': '1994'
            },
            {
                'id': '5',
                'file_name': 'The Lord of the Rings The Return of the King 2003 Extended.mp4',
                'file_size': 3200000000,
                'file_id': 'sample_file_id_5',
                'poster_url': '/imgs/no-poster.svg',
                'year': '2003'
            },
            {
                'id': '6',
                'file_name': 'Inception 2010 1080p.mp4',
                'file_size': 1950000000,
                'file_id': 'sample_file_id_6',
                'poster_url': '/imgs/no-poster.svg',
                'year': '2010'
            }
        ]
        
        # In a production environment, you would process files from the database
        # and extract metadata like title, year, etc.
        
        return web.json_response({'movies': sample_movies})
    except Exception as e:
        logger.error(f"Error in recent movies API: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return web.json_response({'error': str(e), 'movies': []}, status=500)

@routes.get("/telegram/{id}", allow_head=True)
async def telegram_movie_handler(request):
    """
    Handle requests to /telegram/{id} and show a page with "Get it on Telegram" button
    """
    try:
        movie_id = request.match_info.get('id')
        
        # For sample purposes, we'll use a fixed list of sample movies
        # In a real app, you would look up the movie by ID in your database
        sample_movies = {
            '1': {'title': 'The Shawshank Redemption', 'poster': '/imgs/no-poster.svg', 'year': '1994'},
            '2': {'title': 'The Godfather', 'poster': '/imgs/no-poster.svg', 'year': '1972'},
            '3': {'title': 'The Dark Knight', 'poster': '/imgs/no-poster.svg', 'year': '2008'},
            '4': {'title': 'Pulp Fiction', 'poster': '/imgs/no-poster.svg', 'year': '1994'},
            '5': {'title': 'The Lord of the Rings: The Return of the King', 'poster': '/imgs/no-poster.svg', 'year': '2003'},
            '6': {'title': 'Inception', 'poster': '/imgs/no-poster.svg', 'year': '2010'},
        }
        
        # Find the movie in our sample data
        movie = sample_movies.get(movie_id, {'title': 'Unknown Movie', 'poster': '/imgs/no-poster.svg', 'year': ''})
        
        # Read the template file
        with open('web/template/get_telegram.html', 'r') as file:
            html = file.read()
        
        # Fill in the template with movie data
        # The template expects: title (in head), title (in content), poster URL, alt text
        movie_title = f"{movie['title']} ({movie['year']})" if movie['year'] else movie['title']
        html = html % (
            f"Get {movie_title} on Telegram",  # Title in head
            movie_title,                      # Title in content
            movie['poster'],                  # Poster URL 
            movie['title']                    # Alt text for poster
        )
        
        return web.Response(text=html, content_type='text/html')
    
    except Exception as e:
        logger.error(f"Error in telegram movie handler: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Serve error page
        error_html = """
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - Movie Not Found</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
            <style>
                :root {
                    --primary-gradient: linear-gradient(45deg, #0d253f, #1d3557, #2b4a7a);
                    --accent-color: #0088cc;
                }
                body {
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--primary-gradient);
                    background-size: 200% 200%;
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
                    background: rgba(15, 23, 42, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }
                .error-icon {
                    font-size: 4rem;
                    color: var(--accent-color);
                    margin-bottom: 20px;
                }
                .back-btn {
                    display: inline-block;
                    margin-top: 20px;
                    background: var(--accent-color);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 30px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                }
                .back-btn:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 6px 15px rgba(0, 136, 204, 0.4);
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <i class="fas fa-exclamation-circle error-icon"></i>
                <h1>Movie Not Found</h1>
                <p>Sorry, we couldn't find the movie you were looking for.</p>
                <a href="/" class="back-btn">
                    <i class="fas fa-home"></i> Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')

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

