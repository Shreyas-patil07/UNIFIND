"""
Optimized intent extraction service for AI Need Board.
Extracts structured data from natural language queries.

SECURITY HARDENED:
- Input sanitization and validation
- Output schema validation
- Cost control and token budgeting
- Error handling with retries
- Fallback mechanisms
"""

import json
import logging
import re
from typing import Dict

from app.ai.clients.gemini_client import GeminiAPIError, generate_content
from app.ai.security.cost_guard import (
    check_token_budget,
    estimate_tokens_accurate,
    record_token_usage,
)
from app.ai.security.error_handler import (
    AIValidationError,
    create_fallback_response,
    handle_ai_error,
    retry_with_backoff,
)
from app.ai.security.input_validator import validate_query_input
from app.ai.security.output_validator import validate_intent_output

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise data extraction AI for a student marketplace. 
Extract structured information from queries and return ONLY valid JSON.

RULES:
1. Return ONLY a JSON object, no other text
2. Do NOT use markdown code blocks
3. Extract information accurately"""

REQUIRED_KEYS = {"category", "subject", "semester", "max_price", "condition", "intent_summary"}


def _build_user_prompt(query: str) -> str:
    """Build optimized user prompt for intent extraction."""
    # Truncate very long queries to save tokens
    query = query[:300] if len(query) > 300 else query

    return (
        "Extract data from this query and return JSON:\n\n"
        f"QUERY: {query}\n\n"
        "OUTPUT FORMAT (JSON only):\n"
        "{\n"
        '  "category": "Electronics|Books|Stationery|Furniture|Clothing|Sports|Other",\n'
        '  "subject": "specific item name",\n'
        '  "semester": "1-8 or Not specified",\n'
        '  "max_price": number or null,\n'
        '  "condition": "New|Like New|Good|Fair|Any",\n'
        '  "intent_summary": "brief summary"\n'
        "}\n\n"
        "CATEGORY MAPPING:\n"
        "- laptop/phone/calculator → Electronics\n"
        "- textbook/novel/notes → Books\n"
        "- pen/notebook → Stationery\n"
        "- desk/chair → Furniture\n\n"
        "Return ONLY the JSON object."
    )


def _parse_json(text: str) -> Dict:
    """
    Parse JSON from AI response with fallback extraction.

    Args:
        text: Raw AI response text

    Returns:
        dict: Parsed JSON object

    Raises:
        ValueError: If JSON cannot be extracted
    """
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract JSON substring
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse JSON from: {text[:200]}")
    raise ValueError("Could not extract valid JSON from AI response")


def _apply_defaults(parsed: Dict) -> Dict:
    """Apply default values for missing or None fields."""
    defaults = {
        "category": "Other",
        "subject": "Not specified",
        "semester": "Not specified",
        "max_price": None,
        "condition": "Any",
        "intent_summary": "User query",
    }

    for key, default_value in defaults.items():
        if key not in parsed or parsed[key] is None:
            parsed[key] = default_value

    return parsed


async def extract_intent(query: str, user_id: str = "anonymous") -> Dict:
    """
    Extract structured intent from natural language query.

    SECURITY HARDENED:
    - Input validation and sanitization
    - Token budget checking
    - Output schema validation
    - Retry with exponential backoff
    - Fallback on failure

    Args:
        query: Natural language query from user
        user_id: User ID for cost tracking

    Returns:
        dict: Structured intent with keys:
            - category: Product category
            - subject: Specific item
            - semester: Academic semester (if applicable)
            - max_price: Maximum price (if specified)
            - condition: Desired condition
            - intent_summary: Brief summary

    Raises:
        ValueError: If intent cannot be extracted
        GeminiAPIError: If AI API fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    try:
        # Step 1: Validate and sanitize input
        sanitized_query = validate_query_input(query)
        logger.debug(f"Sanitized query: {sanitized_query[:50]}...")

        # Step 2: Check token budget
        user_prompt = _build_user_prompt(sanitized_query)
        combined_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        estimated_tokens = estimate_tokens_accurate(combined_prompt)

        logger.debug(f"Estimated tokens: {estimated_tokens}")
        check_token_budget(user_id, estimated_tokens, raise_on_exceed=True)

        # Step 3: Call AI with retry
        async def _call_ai():
            return await generate_content(SYSTEM_PROMPT, user_prompt, timeout=20)

        raw_response = await retry_with_backoff(_call_ai, max_retries=3)

        # Step 4: Parse and validate output
        parsed = _parse_json(raw_response)
        validated = validate_intent_output(parsed)

        # Step 5: Record token usage
        response_tokens = estimate_tokens_accurate(raw_response)
        total_tokens = estimated_tokens + response_tokens
        record_token_usage(user_id, total_tokens)

        logger.info(
            f"Extracted intent: {validated.get('category')} - {validated.get('subject')} "
            f"(tokens: {total_tokens})"
        )
        return validated

    except ValueError as e:
        # Input validation error - don't retry
        logger.error(f"Input validation failed: {e}")
        raise

    except GeminiAPIError as e:
        # AI API error - return fallback
        logger.error(f"Gemini API error during intent extraction: {e}")
        error_response = handle_ai_error(e, {"query": query[:50], "user_id": user_id})
        fallback = create_fallback_response("intent", reason="AI service error")
        logger.warning("Returning fallback intent response")
        return fallback

    except AIValidationError as e:
        # Output validation error - return fallback
        logger.error(f"Output validation failed: {e}")
        fallback = create_fallback_response("intent", reason="Invalid AI output")
        logger.warning("Returning fallback intent response")
        return fallback

    except Exception as e:
        # Unexpected error - return fallback
        logger.error(f"Unexpected error in intent extraction: {e}", exc_info=True)
        fallback = create_fallback_response("intent", reason="Unexpected error")
        logger.warning("Returning fallback intent response")
        return fallback
