"""
Authentication utilities for JWT tokens, password hashing, etc.
"""

import logging
logger = logging.getLogger(__name__)

import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from config import settings

# JWT Configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password against stored hash - supports both bcrypt and legacy format"""
    try:
        # Check if it's a bcrypt hash (starts with $2b$)
        if stored_password.startswith('$2b$'):
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
        
        # Legacy format with salt:hash
        salt, pwd_hash = stored_password.split(':')
        return pwd_hash == hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    except Exception as e:
        logger.debug("Password verification error: %s", e)
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("❌ Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug("JWT validation error: %s", e)
        return None
    except Exception as e:
        logger.debug("Token verification error: %s", e)
        return None

def generate_reset_token() -> str:
    """Generate password reset token"""
    return secrets.token_urlsafe(32)

def generate_verification_token() -> str:
    """Generate email verification token"""
    return secrets.token_urlsafe(32)
