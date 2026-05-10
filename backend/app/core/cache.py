"""
Production-ready caching layer with Redis support and in-memory fallback.
Provides a unified interface for caching across the application.
"""
import json
import logging
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import asyncio

logger = logging.getLogger(__name__)

# In-memory cache as fallback (production should use Redis)
_memory_cache: dict[str, tuple[Any, float]] = {}
MAX_MEMORY_CACHE_SIZE = 1000

# Redis client (will be initialized if Redis is available)
_redis_client: Optional[Any] = None


def init_redis(redis_url: Optional[str] = None):
    """
    Initialize Redis client if URL is provided.
    Falls back to in-memory cache if Redis is unavailable.
    """
    global _redis_client
    
    if not redis_url:
        logger.info("No Redis URL provided, using in-memory cache")
        return
    
    try:
        import redis.asyncio as redis
        _redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        logger.info("Redis client initialized successfully")
    except ImportError:
        logger.warning("redis package not installed, using in-memory cache")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}, using in-memory cache")


def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # Hash complex objects
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
    
    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        else:
            key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")
    
    return ":".join(key_parts)


def _manage_memory_cache_size():
    """Remove oldest entries if memory cache is too large."""
    if len(_memory_cache) > MAX_MEMORY_CACHE_SIZE:
        # Remove 20% of oldest entries
        to_remove = len(_memory_cache) // 5
        for key in list(_memory_cache.keys())[:to_remove]:
            del _memory_cache[key]


class CacheService:
    """
    Unified caching service with Redis and in-memory fallback.
    Automatically handles serialization and TTL.
    """
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Get value from cache.
        Tries Redis first, falls back to memory cache.
        """
        # Try Redis first
        if _redis_client:
            try:
                value = await _redis_client.get(key)
                if value:
                    logger.debug(f"Redis cache hit: {key}")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}, falling back to memory")
        
        # Fallback to memory cache
        if key in _memory_cache:
            value, expiry = _memory_cache[key]
            import time
            if time.time() < expiry:
                logger.debug(f"Memory cache hit: {key}")
                return value
            else:
                # Expired
                del _memory_cache[key]
        
        logger.debug(f"Cache miss: {key}")
        return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL (in seconds).
        Stores in both Redis and memory cache.
        """
        serialized = json.dumps(value, default=str)
        
        # Try Redis
        if _redis_client:
            try:
                await _redis_client.setex(key, ttl, serialized)
                logger.debug(f"Cached in Redis: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Always store in memory as fallback
        import time
        _manage_memory_cache_size()
        _memory_cache[key] = (value, time.time() + ttl)
        logger.debug(f"Cached in memory: {key} (TTL: {ttl}s)")
    
    @staticmethod
    async def delete(key: str):
        """Delete value from cache."""
        # Delete from Redis
        if _redis_client:
            try:
                await _redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # Delete from memory
        _memory_cache.pop(key, None)
        logger.debug(f"Deleted from cache: {key}")
    
    @staticmethod
    async def clear_pattern(pattern: str):
        """
        Clear all keys matching pattern (e.g., "user:*").
        Note: Pattern matching only works with Redis.
        """
        if _redis_client:
            try:
                keys = await _redis_client.keys(pattern)
                if keys:
                    await _redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
            except Exception as e:
                logger.warning(f"Redis pattern delete error: {e}")
        
        # For memory cache, clear all (pattern matching is expensive)
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys_to_delete = [k for k in _memory_cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del _memory_cache[key]
            logger.info(f"Cleared {len(keys_to_delete)} keys from memory cache")
    
    @staticmethod
    async def clear_all():
        """Clear entire cache."""
        if _redis_client:
            try:
                await _redis_client.flushdb()
                logger.info("Cleared Redis cache")
            except Exception as e:
                logger.warning(f"Redis flush error: {e}")
        
        _memory_cache.clear()
        logger.info("Cleared memory cache")


def cached(prefix: str, ttl: int = 300):
    """
    Decorator for caching function results.
    
    Usage:
        @cached("user_profile", ttl=300)
        async def get_user_profile(user_id: str):
            # expensive operation
            return profile
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await CacheService.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if result is not None:
                await CacheService.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Cache TTL constants (in seconds)
class CacheTTL:
    """Standard cache TTL values for different data types."""
    USER_PROFILE = 300  # 5 minutes
    PRODUCT_LISTING = 120  # 2 minutes
    PRODUCT_LIST = 60  # 1 minute
    AI_RESPONSE = 3600  # 1 hour
    SEARCH_RESULTS = 600  # 10 minutes
    STATIC_DATA = 86400  # 24 hours
    SHORT_LIVED = 30  # 30 seconds


# Convenience functions
async def cache_user_profile(user_id: str, profile: dict):
    """Cache user profile."""
    await CacheService.set(f"user:profile:{user_id}", profile, CacheTTL.USER_PROFILE)


async def get_cached_user_profile(user_id: str) -> Optional[dict]:
    """Get cached user profile."""
    return await CacheService.get(f"user:profile:{user_id}")


async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user."""
    await CacheService.clear_pattern(f"user:*:{user_id}")
    await CacheService.clear_pattern(f"user:{user_id}:*")


async def cache_product(product_id: str, product: dict):
    """Cache product."""
    await CacheService.set(f"product:{product_id}", product, CacheTTL.PRODUCT_LISTING)


async def get_cached_product(product_id: str) -> Optional[dict]:
    """Get cached product."""
    return await CacheService.get(f"product:{product_id}")


async def invalidate_product_cache(product_id: str):
    """Invalidate cache for a product."""
    await CacheService.delete(f"product:{product_id}")


async def invalidate_seller_products_cache(seller_id: str):
    """Invalidate all product caches for a seller."""
    await CacheService.clear_pattern(f"products:seller:{seller_id}*")
