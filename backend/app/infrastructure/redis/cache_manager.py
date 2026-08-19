"""
Redis Cache Manager
Provides caching utilities for frequently accessed data like contacts, templates, campaigns.
Implements cache-aside pattern with TTL-based expiration.
"""
import json
import logging
from typing import Any, Optional, Generic, TypeVar
from datetime import timedelta

import redis
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheManager:
    """Synchronous and asynchronous Redis cache manager."""
    
    def __init__(self, redis_url: str = settings.REDIS_URL):
        """Initialize cache manager with Redis connection."""
        self.redis_url = redis_url
        self._sync_client: Optional[redis.Redis] = None
        self._async_client: Optional[aioredis.Redis] = None
    
    @property
    def sync_client(self) -> redis.Redis:
        """Get synchronous Redis client (lazy initialization)."""
        if self._sync_client is None:
            self._sync_client = redis.from_url(self.redis_url, decode_responses=True)
        return self._sync_client
    
    async def get_async_client(self) -> aioredis.Redis:
        """Get asynchronous Redis client (lazy initialization)."""
        if self._async_client is None:
            self._async_client = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._async_client
    
    # ─── Synchronous Operations ─────────────────────────────────────────────────
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = self.sync_client.get(key)
            if value is None:
                return default
            return json.loads(value)
        except Exception as exc:
            logger.warning(f"Cache get error for key {key}: {exc}")
            return default
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)."""
        try:
            self.sync_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as exc:
            logger.warning(f"Cache set error for key {key}: {exc}")
            return False
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys from cache."""
        try:
            return self.sync_client.delete(*keys)
        except Exception as exc:
            logger.warning(f"Cache delete error: {exc}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self.sync_client.exists(key) > 0
        except Exception as exc:
            logger.warning(f"Cache exists error for key {key}: {exc}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            keys = self.sync_client.keys(pattern)
            if keys:
                return self.sync_client.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning(f"Cache clear pattern error for {pattern}: {exc}")
            return 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache."""
        try:
            return self.sync_client.incrby(key, amount)
        except Exception as exc:
            logger.warning(f"Cache increment error for key {key}: {exc}")
            return 0
    
    def append_list(self, key: str, value: Any, ttl: int = 3600) -> int:
        """Append value to a list in cache."""
        try:
            # For consistency, store as JSON in list
            result = self.sync_client.rpush(key, json.dumps(value))
            self.sync_client.expire(key, ttl)
            return result
        except Exception as exc:
            logger.warning(f"Cache append_list error for key {key}: {exc}")
            return 0
    
    def get_list(self, key: str) -> list:
        """Get all values from a list in cache."""
        try:
            values = self.sync_client.lrange(key, 0, -1)
            return [json.loads(v) for v in values]
        except Exception as exc:
            logger.warning(f"Cache get_list error for key {key}: {exc}")
            return []
    
    # ─── Asynchronous Operations ────────────────────────────────────────────────
    
    async def aget(self, key: str, default: Any = None) -> Any:
        """Get value from cache (async)."""
        try:
            client = await self.get_async_client()
            value = await client.get(key)
            if value is None:
                return default
            return json.loads(value)
        except Exception as exc:
            logger.warning(f"Cache aget error for key {key}: {exc}")
            return default
    
    async def aset(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (async)."""
        try:
            client = await self.get_async_client()
            await client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as exc:
            logger.warning(f"Cache aset error for key {key}: {exc}")
            return False
    
    async def adelete(self, *keys: str) -> int:
        """Delete one or more keys from cache (async)."""
        try:
            client = await self.get_async_client()
            return await client.delete(*keys)
        except Exception as exc:
            logger.warning(f"Cache adelete error: {exc}")
            return 0
    
    async def aexists(self, key: str) -> bool:
        """Check if key exists in cache (async)."""
        try:
            client = await self.get_async_client()
            return await client.exists(key) > 0
        except Exception as exc:
            logger.warning(f"Cache aexists error for key {key}: {exc}")
            return False
    
    async def aclear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern (async)."""
        try:
            client = await self.get_async_client()
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning(f"Cache aclear_pattern error for {pattern}: {exc}")
            return 0
    
    # ─── Cache Key Patterns ─────────────────────────────────────────────────────
    
    @staticmethod
    def make_key(*parts: str) -> str:
        """Generate cache key from parts."""
        return ":".join(parts)
    
    # Common cache key patterns
    CONTACT_KEY = "contact:{user_id}:{contact_id}"
    TEMPLATE_KEY = "template:{user_id}:{template_id}"
    CAMPAIGN_KEY = "campaign:{user_id}:{campaign_id}"
    MAILING_LIST_KEY = "list:{user_id}:{list_id}"
    SEGMENT_KEY = "segment:{user_id}:{segment_id}"
    USER_KEY = "user:{user_id}"
    USER_TEMPLATES_KEY = "user:{user_id}:templates"
    USER_CAMPAIGNS_KEY = "user:{user_id}:campaigns"
    
    # Default TTLs (in seconds)
    TTL_SHORT = 300  # 5 minutes for volatile data
    TTL_MEDIUM = 1800  # 30 minutes for standard data
    TTL_LONG = 3600  # 1 hour for stable data
    TTL_VERY_LONG = 86400  # 1 day for reference data


# Global cache manager instance
cache_manager = CacheManager()


# ─── Decorator for caching function results ────────────────────────────────────

def cached(ttl: int = CacheManager.TTL_MEDIUM):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=300)
        async def get_user_campaigns(user_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            key_parts = [func.__name__] + [str(arg) for arg in args]
            cache_key = CacheManager.make_key(*key_parts)
            
            # Try to get from cache
            cached_value = await cache_manager.aget(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Cache miss, call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.aset(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            return result
        
        return wrapper
    return decorator
