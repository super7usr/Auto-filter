import base64
import json
from aiohttp import web
from cryptography import fernet
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionMiddleware:
    """Session middleware for aiohttp web application"""
    
    def __init__(self, secret_key=None):
        if secret_key is None:
            # Use environment variable or generate a new key
            secret_key = os.environ.get('SESSION_SECRET', fernet.Fernet.generate_key().decode())
        
        # Ensure the key is properly formatted for Fernet
        if not isinstance(secret_key, bytes):
            try:
                # Pad the key if needed
                padded_key = secret_key
                if len(padded_key) < 32:
                    padded_key = padded_key.ljust(32, '0')
                # Use first 32 bytes of key for Fernet
                fernet_key = base64.urlsafe_b64encode(padded_key[:32].encode())
                self.fernet = fernet.Fernet(fernet_key)
            except Exception as e:
                logger.error(f"Error initializing session encryption: {e}")
                # Fallback to a new key
                self.fernet = fernet.Fernet(fernet.Fernet.generate_key())
        else:
            self.fernet = fernet.Fernet(secret_key)
    
    @web.middleware
    async def middleware(self, request, handler):
        # Get session from cookie
        request['session'] = self.load_session(request)
        
        # Handle the request
        response = await handler(request)
        
        # Save session to cookie after the request is handled
        self.save_session(request, response)
        
        return response
    
    def load_session(self, request):
        """Load session data from cookie"""
        session_cookie = request.cookies.get('session')
        if not session_cookie:
            return {}
        
        try:
            # Decrypt and decode the cookie value
            decrypted = self.fernet.decrypt(session_cookie.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Error decoding session: {e}")
            return {}
    
    def save_session(self, request, response):
        """Save session data to cookie"""
        session = request.get('session', {})
        
        if not session:
            # Clear the cookie if the session is empty
            response.del_cookie('session')
            return
        
        try:
            # Encode and encrypt the session data
            session_json = json.dumps(session)
            encrypted = self.fernet.encrypt(session_json.encode())
            
            # Set the cookie (secure, httponly, etc.)
            response.set_cookie(
                'session', 
                encrypted.decode(), 
                httponly=True, 
                max_age=3600,  # 1 hour
                secure=False,  # Set to True for HTTPS
                samesite='Lax'
            )
        except Exception as e:
            logger.error(f"Error encoding session: {e}")

def setup_session_middleware(app):
    """Add session middleware to the application"""
    middleware = SessionMiddleware()
    app.middlewares.append(middleware.middleware)
    return app