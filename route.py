import re
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from utils import temp
from info import BIN_CHANNEL, URL
from web.utils.custom_dl import ByteStreamer
from web.utils.render_template import media_watch, get_error_page
from web.utils.file_properties import get_hash

# Configure logger
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "running"})

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        
        if not temp.BOT:
            return web.Response(
                status=503,
                text="Bot service unavailable",
                content_type="text/plain"
            )
            
        return web.Response(text=await media_watch(id), content_type='text/html')
    except Exception as e:
        logger.error(f"Error in stream_handler: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - Video Not Found</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
            <style>
                .error-container {{
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                    padding: 2rem;
                }}
                .error-icon {{
                    font-size: 5rem;
                    margin-bottom: 2rem;
                    color: #dc3545;
                }}
                .error-message {{
                    max-width: 600px;
                }}
                .back-btn {{
                    margin-top: 2rem;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">❌</div>
                <div class="error-message">
                    <h1>Video Not Found</h1>
                    <p class="lead">The video you requested could not be loaded.</p>
                    <p>The file might have been removed or there could be a temporary issue with our streaming service.</p>
                </div>
                <a href="/" class="btn btn-primary back-btn">Go to Homepage</a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_media_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        
        return await media_streamer(request, id, secure_hash)
    except Exception as e:
        logger.error(f"Error in stream_media_handler: {e}")
        return web.Response(status=404, text="File not found")

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    try:
        range_header = request.headers.get("Range", 0)
        
        if not temp.BOT:
            return web.Response(
                status=503,
                text="Bot service unavailable",
                content_type="text/plain"
            )
            
        # Get the message from BIN_CHANNEL
        message = await temp.BOT.get_messages(BIN_CHANNEL, id)
        if not message:
            return web.Response(status=404, text="File not found")
            
        # Verify hash
        file_hash = get_hash(message)
        if file_hash != secure_hash:
            logger.warning(f"Invalid hash: expected {file_hash}, got {secure_hash}")
            return web.Response(status=403, text="Invalid hash")
            
        # Initialize ByteStreamer
        streamer = ByteStreamer(temp.BOT)
        
        # Get file properties
        file_id = await streamer.get_file_properties(id)
        file_size = file_id.file_size
        
        # Handle range request
        if range_header:
            from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            from_bytes = request.http_range.start or 0
            until_bytes = (request.http_range.stop or file_size) - 1
            
        # Validate range
        if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
            return web.Response(
                status=416,
                body="416: Range not satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"},
            )
            
        # Calculate chunk size and offsets
        chunk_size = 1024 * 1024  # 1MB chunks
        until_bytes = min(until_bytes, file_size - 1)
        
        offset = from_bytes - (from_bytes % chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = until_bytes % chunk_size + 1
        
        req_length = until_bytes - from_bytes + 1
        part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
        
        # Get file stream
        body = streamer.yield_file(
            file_id, offset, first_part_cut, last_part_cut, part_count, chunk_size
        )
        
        # Determine content type and filename
        mime_type = file_id.mime_type
        file_name = file_id.file_name
        disposition = "attachment"
        
        if mime_type:
            if not file_name:
                try:
                    file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
                except (IndexError, AttributeError):
                    file_name = f"{secrets.token_hex(2)}.unknown"
        else:
            if file_name:
                mime_type = mimetypes.guess_type(file_id.file_name)[0]
            else:
                mime_type = "application/octet-stream"
                file_name = f"{secrets.token_hex(2)}.unknown"
                
        return web.Response(
            status=206 if range_header else 200,
            body=body,
            headers={
                "Content-Type": f"{mime_type}",
                "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                "Content-Length": str(req_length),
                "Content-Disposition": f'{disposition}; filename="{file_name}"',
                "Accept-Ranges": "bytes",
            },
        )
    except Exception as e:
        logger.error(f"Error in media_streamer: {e}")
        return web.Response(status=500, text=f"Server error: {str(e)}")