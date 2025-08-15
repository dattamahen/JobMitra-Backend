"""
Rate limiting middleware for API protection
"""
import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from cache import cache
from config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc"]:
            return await call_next(request)
        
        # Get user identifier (IP or user_id from token)
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if not await self.is_allowed(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute allowed"
                }
            )
        
        return await call_next(request)
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user_id from Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                from auth_utils import verify_token
                token = auth_header.replace("Bearer ", "")
                payload = verify_token(token)
                if payload and payload.get("user_id"):
                    return f"user:{payload['user_id']}"
            except:
                pass
        
        # Fallback to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        current_time = int(time.time())
        window_start = current_time - 60  # 1-minute window
        
        key = f"rate_limit:{client_id}"
        
        try:
            # Get current request count
            requests = await cache.get(key) or []
            
            # Filter requests within current window
            recent_requests = [req_time for req_time in requests if req_time > window_start]
            
            # Check if limit exceeded
            if len(recent_requests) >= settings.RATE_LIMIT_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for {client_id}")
                return False
            
            # Add current request
            recent_requests.append(current_time)
            
            # Update cache
            await cache.set(key, recent_requests, 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request if rate limiting fails
            return True