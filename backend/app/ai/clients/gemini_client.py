"""
Gemini AI client implementation with proper async support and caching.
Implements the BaseAIClient interface for provider abstraction.

Available Free Tier Models (as of May 2026):
============================================

FALLBACK MODELS (automatically tried in order):
- gemini-3.1-flash-lite: Most cost-efficient, optimized for high-volume tasks
- gemini-3.1-flash-lite-preview: Preview version of flash-lite
- gemini-3-flash-preview: Most intelligent model built for speed
- gemini-2.5-flash: Hybrid reasoning with 1M token context window
- gemini-2.5-flash-lite: Smallest and most cost-effective
- gemini-2.5-flash-lite-preview-09-2025: Latest flash-lite preview
- gemini-2.5-pro: State-of-the-art, excels at coding and reasoning
- gemini-1.5-flash: Legacy fast model
- gemini-1.5-pro: Legacy capable model
- gemini-1.0-pro: Legacy stable fallback

Note: All models in this file are FREE TIER with no input/output token costs.
See GOOGLE_FREE_TIER_MODELS.md for detailed documentation.
"""
import asyncio
import hashlib
import logging
import json
import re
from functools import lru_cache
from typing import Dict, List, Optional, Any
import google.generativeai as genai

from app.ai.clients.base import (
    BaseAIClient,
    AIProvider,
    AIClientError,
    AITimeoutError,
    AIRateLimitError,
    AIInvalidRequestError,
    AIClientConfig
)

logger = logging.getLogger(__name__)

# In-memory cache for AI responses (production should use Redis)
_response_cache: Dict[str, str] = {}
MAX_CACHE_SIZE = 1000

# Model fallback list - will try each model in order if rate limited
# Updated with all free tier Gemini API models (as of May 2026)
MODEL_FALLBACK_LIST: List[str] = [
    # Gemini 3.1 Series (Latest)
    "gemini-3.1-flash-lite",                    # Most cost-efficient, high-volume tasks
    "gemini-3.1-flash-lite-preview",            # Preview of flash-lite
    
    # Gemini 3 Series
    "gemini-3-flash-preview",                   # Most intelligent, built for speed
    
    # Gemini 2.5 Series (Stable & Recommended)
    "gemini-2.5-flash",                         # Hybrid reasoning, 1M context window
    "gemini-2.5-flash-lite",                    # Smallest, most cost-effective
    "gemini-2.5-flash-lite-preview-09-2025",    # Latest flash-lite preview
    "gemini-2.5-pro",                           # State-of-the-art, excels at coding
    
    # Legacy models (for backward compatibility)
    "gemini-1.5-flash",                         # Fast and efficient (legacy)
    "gemini-1.5-pro",                           # More capable (legacy)
    "gemini-1.0-pro",                           # Stable fallback (legacy)
]

# Track current model index
_current_model_index = 0


class GeminiClient(BaseAIClient):
    """
    Google Gemini AI client implementation.
    Supports automatic model fallback on rate limits.
    """
    
    def __init__(self, config: AIClientConfig):
        """Initialize Gemini client with configuration."""
        self.config = config
        self._response_cache: Dict[str, str] = {}
        self._max_cache_size = 1000
        
        # Configure Gemini API
        genai.configure(api_key=config.api_key)
        
        logger.info(f"Gemini client initialized with model: {self.get_current_model()}")
    
    @property
    def provider(self) -> AIProvider:
        """Return the provider type."""
        return AIProvider.GEMINI


@lru_cache(maxsize=10)
def _get_configured_model(model_name: str = None):
    """Get configured Gemini model (cached)."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use provided model or get from fallback list
        if model_name is None:
            model_name = MODEL_FALLBACK_LIST[_current_model_index]
        
        logger.info(f"Configuring model: {model_name}")
        
        return genai.GenerativeModel(
            model_name,
            generation_config={
                "max_output_tokens": 500,
                "temperature": 0.3,  # Lower for consistency
                "top_p": 0.8,
                "top_k": 40,
            }
        )
    except Exception as e:
        logger.error(f"Failed to configure Gemini model {model_name}: {e}")
        raise GeminiAPIError(f"Model configuration failed: {str(e)}")


def _is_rate_limit_error(error_message: str) -> bool:
    """Check if error is a rate limit error."""
    rate_limit_indicators = [
        "rate limit",
        "quota exceeded",
        "429",
        "resource exhausted",
        "too many requests"
    ]
    error_lower = str(error_message).lower()
    return any(indicator in error_lower for indicator in rate_limit_indicators)


def _switch_to_next_model() -> str:
    """Switch to the next model in the fallback list."""
    global _current_model_index
    _current_model_index = (_current_model_index + 1) % len(MODEL_FALLBACK_LIST)
    new_model = MODEL_FALLBACK_LIST[_current_model_index]
    logger.warning(f"Switching to fallback model: {new_model}")
    
    # Clear the cache to force new model configuration
    _get_configured_model.cache_clear()
    
    return new_model


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
    use_cache: bool = True,
    max_retries: int = 3
) -> str:
    """
    Call Gemini API asynchronously with caching, error handling, and model fallback.
    
    Args:
        system_prompt: System instructions for the AI
        user_prompt: User query/request
        timeout: Maximum seconds to wait for response
        use_cache: Whether to use cached responses
        max_retries: Maximum number of model fallback attempts
        
    Returns:
        str: AI-generated response text
        
    Raises:
        GeminiTimeoutError: If API doesn't respond within timeout
        GeminiAPIError: On any API-level error after all retries
    """
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(system_prompt, user_prompt)
        if cache_key in _response_cache:
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return _response_cache[cache_key]
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Get model and generate content
            current_model = MODEL_FALLBACK_LIST[_current_model_index]
            model = _get_configured_model(current_model)
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            logger.debug(f"Attempt {attempt + 1}/{max_retries} with model: {current_model}")
            
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
            error_msg = str(e)
            logger.error(f"Gemini API error on attempt {attempt + 1}: {error_msg}")
            last_error = e
            
            # Check if it's a rate limit error
            if _is_rate_limit_error(error_msg):
                if attempt < max_retries - 1:
                    new_model = _switch_to_next_model()
                    logger.info(f"Rate limit detected, switching to {new_model}")
                    continue
                else:
                    logger.error("All model fallbacks exhausted due to rate limits")
                    raise GeminiAPIError(f"Rate limit exceeded on all available models")
            else:
                # Non-rate-limit error, raise immediately
                raise GeminiAPIError(f"Unexpected error: {error_msg}")
    
    # If we get here, all retries failed
    raise GeminiAPIError(f"Failed after {max_retries} attempts. Last error: {str(last_error)}")


def clear_cache():
    """Clear the response cache. Useful for testing or memory management."""
    global _response_cache
    _response_cache.clear()
    logger.info("Gemini response cache cleared")


def get_current_model() -> str:
    """Get the currently active model name."""
    return MODEL_FALLBACK_LIST[_current_model_index]


def reset_model_index():
    """Reset to the first model in the fallback list."""
    global _current_model_index
    _current_model_index = 0
    _get_configured_model.cache_clear()
    logger.info(f"Reset to primary model: {MODEL_FALLBACK_LIST[0]}")
