"""
Request ID Middleware
Adds a unique X-Request-ID header to every request/response for distributed tracing.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attaches a unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
