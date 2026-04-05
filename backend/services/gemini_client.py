"""
Optimized Gemini AI client with proper async support and caching.
"""
import asyncio
import hashlib
import logging
from functools import lru_cache
from typing import Dict
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# In-memory cache for AI responses (production should use Redis)
_response_cache: Dict[str, str] = {}
MAX_CACHE_SIZE = 1000


class GeminiAPIError(Exception):
    """Raised when the AI API returns an error."""
    pass


class GeminiTimeoutError(Exception):
    """Raised when the AI API does not respond within the timeout."""
    pass


@lru_cache(maxsize=1)
def _get_configured_model():
    """Get configured Gemini model (cached)."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(
            "gemini-1.5-flash",  # Using faster flash model
            generation_config={
                "max_output_tokens": 500,
                "temperature": 0.3,  # Lower for consistency
                "top_p": 0.8,
                "top_k": 40,
            }
        )
    except Exception as e:
        logger.error(f"Failed to configure Gemini model: {e}")
        raise GeminiAPIError(f"Model configuration failed: {str(e)}")


def _get_cache_key(system_prompt: str, user_prompt: str) -> str:
    """Generate cache key from prompts."""
    combined = f"{system_prompt}||{user_prompt}"
    return hashlib.md5(combined.encode()).hexdigest()


def _manage_cache_size():
    """Remove oldest entries if cache is too large."""
    if len(_response_cache) > MAX_CACHE_SIZE:
        # Remove 20% of oldest entries
        to_remove = len(_response_cache) // 5
        for key in list(_response_cache.keys())[:to_remove]:
            del _response_cache[key]


async def generate_content(
    system_prompt: str, 
    user_prompt: str, 
    timeout: int = 30,
    use_cache: bool = True
) -> str:
    """
    Call Gemini API asynchronously with caching and error handling.
    
    Args:
        system_prompt: System instructions for the AI
        user_prompt: User query/request
        timeout: Maximum seconds to wait for response
        use_cache: Whether to use cached responses
        
    Returns:
        str: AI-generated response text
        
    Raises:
        GeminiTimeoutError: If API doesn't respond within timeout
        GeminiAPIError: On any API-level error
    """
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(system_prompt, user_prompt)
        if cache_key in _response_cache:
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return _response_cache[cache_key]
    
    try:
        # Get model and generate content
        model = _get_configured_model()
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Run in thread pool to avoid blocking
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, combined_prompt),
            timeout=timeout
        )
        
        if not response or not response.text:
            raise GeminiAPIError("Empty response from Gemini API")
        
        # Cache the response
        if use_cache:
            _manage_cache_size()
            _response_cache[cache_key] = response.text
            logger.debug(f"Cached response for key: {cache_key[:8]}...")
        
        return response.text
        
    except asyncio.TimeoutError:
        logger.error(f"Gemini API timeout after {timeout}s")
        raise GeminiTimeoutError(f"Gemini API did not respond within {timeout} seconds")
        
    except GeminiAPIError:
        raise
        
    except Exception as e:
        logger.error(f"Unexpected Gemini API error: {e}")
        raise GeminiAPIError(f"Unexpected error: {str(e)}")


def clear_cache():
    """Clear the response cache. Useful for testing or memory management."""
    global _response_cache
    _response_cache.clear()
    logger.info("Gemini response cache cleared")
