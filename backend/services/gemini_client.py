import asyncio
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)


class GeminiAPIError(Exception):
    """Raised when the AI API returns an error."""
    pass


class GeminiTimeoutError(Exception):
    """Raised when the AI API does not respond within the timeout."""
    pass


def _get_api_key() -> str:
    """Get Gemini API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not set in the environment. Please add it to backend/.env")
    return api_key


def _call_gemini_sync(system_prompt: str, user_prompt: str) -> str:
    """Synchronous Gemini API call."""
    try:
        api_key = _get_api_key()
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Combine system and user prompts
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(combined_prompt)
        
        if not response.text:
            raise GeminiAPIError("Empty response from Gemini API")
            
        return response.text
        
    except GeminiAPIError:
        raise
    except Exception as e:
        raise GeminiAPIError(f"Gemini API error: {str(e)}")


async def generate_content(
    system_prompt: str, user_prompt: str, timeout: int = 30
) -> str:
    """
    Call Gemini API asynchronously and return the response text.
    
    Raises:
        GeminiTimeoutError: if the API does not respond within timeout seconds
        GeminiAPIError: on any API-level error
    """
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(_call_gemini_sync, system_prompt, user_prompt),
            timeout=timeout,
        )
        return response
        
    except asyncio.TimeoutError:
        raise GeminiTimeoutError(f"Gemini API did not respond within {timeout} seconds")
    except GeminiAPIError:
        raise
    except Exception as e:
        raise GeminiAPIError(f"Unexpected error calling Gemini API: {str(e)}")
