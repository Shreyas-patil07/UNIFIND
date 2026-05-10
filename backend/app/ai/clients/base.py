"""
Abstract base class for AI provider clients.
This enables easy switching between AI providers (Gemini, OpenAI, Claude, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL = "local"


class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass


class AITimeoutError(AIClientError):
    """Raised when AI API times out."""
    pass


class AIRateLimitError(AIClientError):
    """Raised when AI API rate limit is exceeded."""
    pass


class AIInvalidRequestError(AIClientError):
    """Raised when request is invalid."""
    pass


class BaseAIClient(ABC):
    """
    Abstract base class for AI provider clients.
    All AI providers must implement this interface.
    """
    
    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Return the provider type."""
        pass
    
    @abstractmethod
    async def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: int = 30,
        temperature: float = 0.3,
        max_tokens: int = 500,
        use_cache: bool = True
    ) -> str:
        """
        Generate content from prompts.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User query/request
            timeout: Maximum seconds to wait for response
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            use_cache: Whether to use cached responses
            
        Returns:
            str: AI-generated response text
            
        Raises:
            AITimeoutError: If API doesn't respond within timeout
            AIRateLimitError: If rate limit is exceeded
            AIInvalidRequestError: If request is invalid
            AIClientError: On any other API-level error
        """
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: int = 30,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User query/request
            timeout: Maximum seconds to wait for response
            use_cache: Whether to use cached responses
            
        Returns:
            dict: Parsed JSON response
            
        Raises:
            AITimeoutError: If API doesn't respond within timeout
            AIRateLimitError: If rate limit is exceeded
            AIInvalidRequestError: If request is invalid or response isn't valid JSON
            AIClientError: On any other API-level error
        """
        pass
    
    @abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            model: Optional specific embedding model to use
            
        Returns:
            List of embedding vectors
            
        Raises:
            AIClientError: On any API-level error
        """
        pass
    
    @abstractmethod
    def clear_cache(self):
        """Clear the response cache."""
        pass
    
    @abstractmethod
    def get_current_model(self) -> str:
        """Get the currently active model name."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the AI service is available.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        pass


class AIClientConfig:
    """Configuration for AI clients."""
    
    def __init__(
        self,
        api_key: str,
        default_model: Optional[str] = None,
        default_temperature: float = 0.3,
        default_max_tokens: int = 500,
        default_timeout: int = 30,
        enable_caching: bool = True,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.default_timeout = default_timeout
        self.enable_caching = enable_caching
        self.max_retries = max_retries
