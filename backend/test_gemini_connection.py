"""Quick test script to verify Gemini API connection"""
import asyncio
from services.gemini_client import generate_content, GeminiAPIError, GeminiTimeoutError

async def test_gemini():
    try:
        print("Testing Gemini API connection...")
        response = await generate_content(
            "You are a helpful assistant.",
            "Say 'Hello, Gemini is working!' in one sentence."
        )
        print(f"✓ Success! Response: {response}")
        return True
    except GeminiTimeoutError as e:
        print(f"✗ Timeout Error: {e}")
        return False
    except GeminiAPIError as e:
        print(f"✗ API Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini())
    exit(0 if result else 1)
