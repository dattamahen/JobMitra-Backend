import logging

logger = logging.getLogger(__name__)

from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings

class GoogleAuthService:
    def __init__(self):
        self.client_ids = list(filter(None, [
            settings.GOOGLE_CLIENT_ID,
            settings.GOOGLE_ANDROID_CLIENT_ID
        ]))
        logger.info("GoogleAuthService init: %d client_id(s) loaded. WEB=%s ANDROID=%s",
            len(self.client_ids),
            bool(settings.GOOGLE_CLIENT_ID),
            bool(settings.GOOGLE_ANDROID_CLIENT_ID)
        )
        
    def verify_google_token(self, credential: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        if not self.client_ids:
            logger.error("No Google client IDs configured — set GOOGLE_CLIENT_ID and GOOGLE_ANDROID_CLIENT_ID env vars")
            return None
        for client_id in self.client_ids:
            try:
                idinfo = id_token.verify_oauth2_token(
                    credential,
                    requests.Request(),
                    client_id
                )
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    continue
                return {
                    'google_id': idinfo['sub'],
                    'email': idinfo['email'],
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                    'full_name': idinfo.get('name', ''),
                    'picture': idinfo.get('picture', ''),
                    'email_verified': idinfo.get('email_verified', False)
                }
            except ValueError as e:
                logger.debug("Token verification failed for client_id %s: %s", client_id, e)
                continue
            except Exception as e:
                logger.error("Error verifying Google token: %s", e)
                continue
        return None
    
    def create_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        
        secret_key = settings.JWT_SECRET_KEY
        return jwt.encode(payload, secret_key, algorithm='HS256')