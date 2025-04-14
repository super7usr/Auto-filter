import re
from os import environ
import os
from Script import script
import pytz

def is_enabled(type, value):
    data = environ.get(type, str(value))
    if data.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif data.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        print(f'Error - {type} is invalid, exiting now')
        exit()

def is_valid_ip(ip):
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(ip_pattern, ip) is not None

# Bot information
API_ID = environ.get('API_ID', '')
if len(API_ID) == 0:
    print('Error - API_ID is missing, exiting now')
    exit()
else:
    API_ID = int(API_ID)
API_HASH = environ.get('API_HASH', '')
if len(API_HASH) == 0:
    print('Error - API_HASH is missing, exiting now')
    exit()
BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    print('Error - BOT_TOKEN is missing, exiting now')
    exit()
PORT = int(environ.get('PORT', '8383'))

# Add your images to "imgs" folder in this repo (https://github.com/HA-Bots/Auto-Filter-Bot/tree/main/imgs)
PICS = [os.path.join('imgs', file) for file in os.listdir('imgs')]

# Bot Admins
ADMINS = environ.get('ADMINS', '')
if len(ADMINS) == 0:
    print('Error - ADMINS is missing, exiting now')
    exit()
else:
    ADMINS = [int(admins) for admins in ADMINS.split()]

# Channels
INDEX_CHANNELS = [int(index_channels) if index_channels.startswith("-") else index_channels for index_channels in environ.get('INDEX_CHANNELS', '').split()]
if len(INDEX_CHANNELS) == 0:
    print('Info - INDEX_CHANNELS is empty')
LOG_CHANNEL = environ.get('LOG_CHANNEL', '')
if len(LOG_CHANNEL) == 0:
    print('Error - LOG_CHANNEL is missing, exiting now')
    exit()
else:
    LOG_CHANNEL = int(LOG_CHANNEL)
FORCE_SUB_CHANNELS = [int(fsub_channels) if fsub_channels.startswith("-") else fsub_channels for fsub_channels in environ.get('FORCE_SUB_CHANNELS', '').split()]
if len(FORCE_SUB_CHANNELS) == 0:
    print('Info - FORCE_SUB_CHANNELS is empty')
    
# support group
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', '0')
if len(SUPPORT_GROUP) == 0:
    print('Info - SUPPORT_GROUP is not set, using default')
    SUPPORT_GROUP = 0
else:
    try:
        SUPPORT_GROUP = int(SUPPORT_GROUP)
    except ValueError:
        print('Warning - Invalid SUPPORT_GROUP value, using default')
        SUPPORT_GROUP = 0

# Database information
DATABASE_URL = environ.get('DATABASE_URI', environ.get('DATABASE_URL', ""))
if len(DATABASE_URL) == 0:
    print('Error - DATABASE_URL is missing, exiting now')
    exit()

# Set DATABASE_URI for backwards compatibility
environ['DATABASE_URI'] = DATABASE_URL

# Determine which database to use
USE_POSTGRES = False
if DATABASE_URL.startswith(('postgres://', 'postgresql://')):
    print('Info - Using PostgreSQL database')
    USE_POSTGRES = True
elif DATABASE_URL.startswith(('mongodb://', 'mongodb+srv://')):
    print('Info - Using MongoDB database')
    USE_POSTGRES = False
else:
    print(f'Warning - Could not determine database type from URL: {DATABASE_URL}')
    print('Info - Defaulting to MongoDB')
    USE_POSTGRES = False

# Multi-MongoDB configuration
SECOND_DATABASE_URL = environ.get('SECOND_DATABASE_URL', "")
if len(SECOND_DATABASE_URL) == 0:
    print('Info - SECOND_DATABASE_URL is empty')
else:
    print('Info - SECOND_DATABASE_URL is configured')

# Additional MongoDB URLs as JSON array or single URL string
MULTI_MONGODB_URLS = environ.get('MULTI_MONGODB_URLS', "")
if len(MULTI_MONGODB_URLS) == 0:
    print('Info - No additional MongoDB URLs configured (MULTI_MONGODB_URLS is empty)')
else:
    import json
    try:
        # Try to parse as JSON array
        json.loads(MULTI_MONGODB_URLS)
        print('Info - Additional MongoDB URLs configured via MULTI_MONGODB_URLS')
    except json.JSONDecodeError:
        if MULTI_MONGODB_URLS.startswith(('mongodb://', 'mongodb+srv://')):
            # Single URL string
            print('Info - Additional MongoDB URL configured via MULTI_MONGODB_URLS')
        else:
            print('Warning - MULTI_MONGODB_URLS is not a valid JSON array or MongoDB URL')

DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Files')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/renish_rgi_bot')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/M0VIES_CHANNEL')
FILMS_LINK = environ.get('FILMS_LINK', 'https://movies.koyeb.app/')
TUTORIAL = environ.get("TUTORIAL", "https://t.me/")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/")

# Bot settings
TIME_ZONE = pytz.timezone(environ.get("TIME_ZONE", 'Asia/Colombo'))
DELETE_TIME = int(environ.get('DELETE_TIME', 300)) # Add time in seconds
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
MAX_BTN = int(environ.get('MAX_BTN', 5))
MAX_BUTTONS = MAX_BTN
LANGUAGES = [language.lower() for language in environ.get('LANGUAGES', 'hindi english telugu tamil kannada malayalam marathi punjabi').split()]
QUALITY = [quality.lower() for quality in environ.get('QUALITY', '360p 480p 720p 1080p 2160p').split()]
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE)
FILE_CAPTION = environ.get("FILE_CAPTION", script.FILE_CAPTION)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 0)) # Add time in seconds
WELCOME_TEXT = environ.get("WELCOME_TEXT", script.WELCOME_TEXT)
INDEX_EXTENSIONS = [extensions.lower() for extensions in environ.get('INDEX_EXTENSIONS', 'mp4 mkv').split()]
PM_FILE_DELETE_TIME = int(environ.get('PM_FILE_DELETE_TIME', '300'))

# boolean settings
USE_CAPTION_FILTER = is_enabled('USE_CAPTION_FILTER', True)
IS_VERIFY = is_enabled('IS_VERIFY', False)
AUTO_DELETE = is_enabled('AUTO_DELETE', True)
WELCOME = is_enabled('WELCOME', True)
PROTECT_CONTENT = is_enabled('PROTECT_CONTENT', False)
LONG_IMDB_DESCRIPTION = is_enabled("LONG_IMDB_DESCRIPTION", False)
LINK_MODE = is_enabled("LINK_MODE", True)
AUTO_FILTER = is_enabled('AUTO_FILTER', True)
IMDB = is_enabled('IMDB', False)
SPELL_CHECK = is_enabled("SPELL_CHECK", True)
SHORTLINK = is_enabled('SHORTLINK', False)

# for stream
IS_STREAM = is_enabled('IS_STREAM', True)
BIN_CHANNEL = environ.get("BIN_CHANNEL", "")
if len(BIN_CHANNEL) == 0:
    print('Error - BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)
URL = environ.get("URL", "")
if len(URL) == 0:
    print('Error - URL is missing, exiting now')
    exit()
else:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    elif is_valid_ip(URL):
        URL = f'http://{URL}/'
    else:
        print('Error - URL is not valid, exiting now')
        exit()

#start command reactions and sticker
REACTIONS = [reactions for reactions in environ.get('REACTIONS', '🤝 😇 🤗 😍 👍 🎅 😐 🥰 🤩 😱 🤣 😘 👏 😛 😈 🎉 ⚡️ 🫡 🤓 😎 🏆 🔥 🤭 🌚 🆒 👻 😁').split()]  # Multiple reactions can be used separated by space
STICKERS = [sticker for sticker in environ.get('STICKERS', 'CAACAgIAAxkBAAEN4ctnu1NdZUe21tiqF1CjLCZW8rJ28QACmQwAAj9UAUrPkwx5a8EilDYE CAACAgIAAxkBAAEN1pBntL9sz1tuP_qo0bCdLj_xQa28ngACxgEAAhZCawpKI9T0ydt5RzYE').split()]  # Multiple sticker can be used separated by space, use @idstickerbot for get sticker id

