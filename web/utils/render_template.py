
from info import BIN_CHANNEL, URL
from utils import temp
from web.utils.custom_dl import TGCustomYield
import urllib.parse
import aiofiles
import os

async def media_watch(message_id):
    try:
        if not temp.BOT:
            # If bot instance not available, return error message
            return """
            <!DOCTYPE html>
            <html lang="en" data-bs-theme="dark">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Stream Error</title>
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
                    <h1 class="error-title">Bot Unavailable</h1>
                    <p class="error-message">The Telegram bot service is currently offline. Please try again later when the bot is running.</p>
                    <a href="/" class="back-button">
                        <i class="fas fa-home"></i> Back to Home
                    </a>
                </div>
            </body>
            </html>
            """
            
        # Get message information from Telegram
        try:
            if temp.BOT:
                media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
                if not media_msg:
                    raise ValueError(f"No message found with ID: {message_id}")
            else:
                # Return error if BOT is not available
                raise ValueError("Bot is not available")
        except Exception as msg_error:
            print(f"Error retrieving message {message_id}: {str(msg_error)}")
            return get_error_page(f"Could not retrieve message with ID {message_id}. The file may have been deleted or is unavailable.", "File Not Found")
        
        try:
            file_properties = await TGCustomYield().generate_file_properties(media_msg)
            if not file_properties:
                raise ValueError("Could not generate file properties")
                
            file_name, mime_type = file_properties.file_name, file_properties.mime_type
        except Exception as prop_error:
            print(f"Error generating file properties: {str(prop_error)}")
            return get_error_page("Could not process the requested file. The file may be corrupted or in an unsupported format.", "File Processing Error")
        
        # Build the watch URL format
        stream_url = f"{URL}watch/{message_id}"
        download_url = f"{URL}download/{message_id}/{file_name}"
        
        tag = mime_type.split('/')[0].strip()
        if tag == 'video':
            # Check which template file exists and use it
            template_path = 'web/template/watch_new.html'
            if not os.path.exists(template_path):
                template_path = 'watch_new.html'
                
            try:
                async with aiofiles.open(template_path) as r:
                    heading = 'Watch - {}'.format(file_name)
                    template = await r.read()
                    # Replace the video tag placeholder with the appropriate HTML5 video tag
                    if tag == 'video':
                        # Create HTML5 video tag with multiple sources for compatibility
                        video_tag = f'''
                        <video class="player" controls crossorigin playsinline>
                            <source src="{stream_url}" type="{mime_type}">
                            <!-- Fallback message -->
                            <p>Your browser doesn't support HTML5 video. Here is a <a href="{download_url}">link to download the video</a> instead.</p>
                        </video>
                        '''
                        template = template.replace('<tag src="%s" class="player"></tag>', video_tag)
                    # Format the template with title and filename
                    html = template % (heading, file_name)
                    return html
            except Exception as template_error:
                print(f"Error loading watch template: {str(template_error)}")
                return get_error_page("Could not load the video player template. Please try again later.", "Template Error")
        else:
            return get_error_page("This file is not a streamable video file.", "Unsupported Media Type")
    except Exception as e:
        print(f"Unexpected error in media_watch: {str(e)}")
        return get_error_page("We encountered an unexpected error while trying to stream this file. Please try again later.", "Stream Error")

def get_error_page(error_message, error_title="Stream Error"):
    """Generate a standardized error page with the given message and title"""
    return f"""
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{error_title}</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            :root {{
                --primary-gradient: linear-gradient(45deg, #0d253f, #1d3557, #2b4a7a);
                --accent-color: #ff5e00;
                --accent-glow: 0 0 10px rgba(255, 94, 0, 0.6);
            }}
            body {{
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
                margin: 0;
            }}
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .error-container {{
                max-width: 600px;
                width: 90%;
                text-align: center;
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
                animation: fadeIn 0.5s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .error-icon {{
                font-size: 5rem;
                color: var(--accent-color);
                margin-bottom: 20px;
                text-shadow: var(--accent-glow);
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
                100% {{ transform: scale(1); }}
            }}
            .error-title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #ff5e00, #ff9e00);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .error-message {{
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 30px;
                color: rgba(255, 255, 255, 0.9);
            }}
            .back-button {{
                background: linear-gradient(45deg, #0088cc, #00aaff);
                border: none;
                color: white;
                padding: 12px 28px;
                border-radius: 30px;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 136, 204, 0.4);
            }}
            .back-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0, 136, 204, 0.6);
                background: linear-gradient(45deg, #0099ff, #33bbff);
            }}
            .suggestion-list {{
                margin-top: 30px;
                text-align: left;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
            }}
            .suggestion-list h3 {{
                font-size: 1.3rem;
                margin-bottom: 15px;
                color: rgba(255, 255, 255, 0.9);
            }}
            .suggestion-list ul {{
                padding-left: 20px;
            }}
            .suggestion-list li {{
                margin-bottom: 10px;
                color: rgba(255, 255, 255, 0.8);
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <i class="fas fa-exclamation-triangle error-icon"></i>
            <h1 class="error-title">{error_title}</h1>
            <p class="error-message">{error_message}</p>
            <a href="/" class="back-button">
                <i class="fas fa-home"></i> Back to Home
            </a>
            
            <div class="suggestion-list">
                <h3>Suggestions:</h3>
                <ul>
                    <li>Try refreshing the page</li>
                    <li>Check your internet connection</li>
                    <li>Try a different browser</li>
                    <li>Use the download option instead of streaming</li>
                    <li>Search for a different version of the content</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

async def render_page(template_name, **context):
    """
    Renders an HTML template with the given context variables
    Args:
        template_name: Name of the template file in the web/template directory
        context: Keyword arguments to pass to the template
    Returns:
        Rendered HTML string
    """
    try:
        import os
        import aiofiles
        
        # Try to find the template in web/template directory
        template_path = os.path.join('web/template', template_name)
        
        # If not found, try fallback locations
        if not os.path.exists(template_path):
            template_path = template_name
            
            # If still not found, try without directory
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template {template_name} not found")
        
        # Read the template file
        async with aiofiles.open(template_path, 'r') as f:
            template_content = await f.read()
            
        # Basic template variable replacement
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            template_content = template_content.replace(placeholder, str(value))
            
        return template_content
    except Exception as e:
        print(f"Error rendering template {template_name}: {str(e)}")
        return get_error_page(f"Failed to render page template: {str(e)}", "Template Error")
