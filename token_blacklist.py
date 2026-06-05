"""
Token Blacklist Service
Invalidates JWT tokens on logout to prevent reuse.

For single-instance deployment: uses in-memory set.
For multi-instance (K8s/ECS): replace with Redis SET + TTL.
"""

import time
import logging
from typing import Set
from config import settings

logger = logging.getLogger(__name__)

# In-memory blacklist: {token_hash: expiry_timestamp}
_blacklist: dict = {}

# Cleanup interval
_CLEANUP_INTERVAL = 300  # 5 minutes
_last_cleanup = time.time()


def blacklist_token(token: str, expires_in_seconds: int = None) -> None:
    """Add a token to the blacklist."""
    global _last_cleanup

    if expires_in_seconds is None:
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Store hash of token (not full token) to save memory
    token_key = _hash_token(token)
    _blacklist[token_key] = time.time() + expires_in_seconds

    # Periodic cleanup of expired entries
    now = time.time()
    if now - _last_cleanup > _CLEANUP_INTERVAL:
        _cleanup_expired()
        _last_cleanup = now


def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted."""
    token_key = _hash_token(token)
    expiry = _blacklist.get(token_key)
    if expiry is None:
        return False
    if time.time() > expiry:
        # Token expired from blacklist, remove it
        del _blacklist[token_key]
        return False
    return True


def _hash_token(token: str) -> str:
    """Hash token to save memory — only need last 16 chars for uniqueness."""
    return token[-16:]


def _cleanup_expired() -> None:
    """Remove expired entries from blacklist."""
    now = time.time()
    expired_keys = [k for k, v in _blacklist.items() if now > v]
    for key in expired_keys:
        del _blacklist[key]
    if expired_keys:
        logger.debug("Cleaned up %d expired blacklist entries", len(expired_keys))
