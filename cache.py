"""
Redis caching layer for high-performance data access
"""
import json
import redis.asyncio as redis
from typing import Any, Optional, Union
from config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection with connection pooling"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True
            )
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL):
        """Set cached value with TTL"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete cached value"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get user session data"""
        return await self.get(f"session:{user_id}")
    
    async def set_user_session(self, user_id: str, session_data: dict):
        """Set user session data"""
        return await self.set(f"session:{user_id}", session_data, settings.SESSION_TTL)
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all user-related cache"""
        patterns = [
            f"user:{user_id}",
            f"session:{user_id}",
            f"jobs:{user_id}:*",
            f"applications:{user_id}:*"
        ]
        for pattern in patterns:
            await self.delete(pattern)

# Global cache instance
cache = CacheManager()