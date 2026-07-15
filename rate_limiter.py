"""
Rate Limiting Middleware
Simple sliding-window rate limiter using in-memory storage.
For production with multiple instances, replace with Redis-backed limiter.
"""

import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from config import settings

logger = logging.getLogger(__name__)

# Sliding window storage: {key: [(timestamp, count)]}
_request_log: dict = defaultdict(list)

# Cleanup threshold — purge old entries every N requests
_CLEANUP_INTERVAL = 1000
_request_counter = 0


def _get_client_key(request: Request) -> str:
    """Extract client identifier from request."""
    # Try to get user_id from auth header (for per-user limiting)
    # Fallback to IP address
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _cleanup_old_entries(window_seconds: int = 60):
    """Remove expired entries to prevent memory leak."""
    cutoff = time.time() - window_seconds
    keys_to_delete = []
    for key, timestamps in _request_log.items():
        _request_log[key] = [t for t in timestamps if t > cutoff]
        if not _request_log[key]:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del _request_log[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with configurable limits per minute."""

    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.limit = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute window

    async def dispatch(self, request: Request, call_next):
        global _request_counter

        # Skip rate limiting for health checks
        if request.url.path in ("/", "/cors-test", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_key = _get_client_key(request)
        now = time.time()

        # Periodic cleanup
        _request_counter += 1
        if _request_counter % _CLEANUP_INTERVAL == 0:
            _cleanup_old_entries(self.window)

        # Count requests in current window
        cutoff = now - self.window
        _request_log[client_key] = [t for t in _request_log[client_key] if t > cutoff]
        request_count = len(_request_log[client_key])

        if request_count >= self.limit:
            logger.warning("Rate limit exceeded for %s: %d/%d", client_key, request_count, self.limit)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "retry_after_seconds": int(self.window - (now - _request_log[client_key][0]))
                }
            )

        # Record this request
        _request_log[client_key].append(now)

        return await call_next(request)
