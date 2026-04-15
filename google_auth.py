from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings

class GoogleAuthService:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        
    def verify_google_token(self, credential: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                credential, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
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
            print(f"Google token verification failed: {e}")
            return None
        except Exception as e:
            print(f"Error verifying Google token: {e}")
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