"""
Optimized semantic ranking service for matching products to user intent.

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
from typing import Dict, List

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
from app.ai.security.input_validator import sanitize_user_input
from app.ai.security.output_validator import validate_ranking_output

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a product matching AI for a student marketplace.
Rank products by match quality (0-100 scale).

RULES:
1. Return ONLY a JSON array
2. No markdown, no explanations
3. Rank ALL products provided
4. Higher score = better match"""


async def rank_listings(
    query: str, intent: Dict, listings: List[Dict], user_id: str = "anonymous"
) -> List[Dict]:
    """
    Rank product listings against user query and intent.

    SECURITY HARDENED:
    - Input validation and sanitization
    - Token budget checking
    - Output schema validation
    - Retry with exponential backoff
    - Fallback on failure

    Args:
        query: Original user query
        intent: Extracted intent dictionary
        listings: List of product listings to rank
        user_id: User ID for cost tracking

    Returns:
        List[Dict]: Ranked results with id, match_score, reason
        Sorted by match_score descending

    Raises:
        ValueError: If ranking fails
        GeminiAPIError: If AI API fails
    """
    if not listings:
        return []

    try:
        # Step 1: Validate and sanitize input
        sanitized_query = sanitize_user_input(query, max_length=150, strict=False)
        logger.debug(f"Sanitized query for ranking: {sanitized_query[:50]}...")

        # Step 2: Optimize listings (reduce token usage)
        simplified_listings = [
            {
                "id": listing["id"],
                "title": listing["title"],
                "category": listing.get("category", ""),
                "price": listing.get("price", 0),
                "condition": listing.get("condition", ""),
                "description": listing.get("description", "")[:80],  # Limit to 80 chars
            }
            for listing in listings[:20]  # Limit to top 20 to save tokens
        ]

        # Optimize intent
        simplified_intent = {
            "category": intent.get("category", ""),
            "subject": intent.get("subject", ""),
            "max_price": intent.get("max_price"),
            "condition": intent.get("condition", ""),
        }

        # Step 3: Check token budget
        user_prompt = _build_ranking_prompt(sanitized_query, simplified_intent, simplified_listings)
        combined_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        estimated_tokens = estimate_tokens_accurate(combined_prompt)

        logger.debug(f"Estimated tokens for ranking: {estimated_tokens}")
        check_token_budget(user_id, estimated_tokens, raise_on_exceed=True)

        # Step 4: Call AI with retry
        async def _call_ai():
            return await generate_content(SYSTEM_PROMPT, user_prompt, timeout=25)

        raw_response = await retry_with_backoff(_call_ai, max_retries=3)

        # Step 5: Parse and validate output
        results = _parse_json_array(raw_response)
        validated_results = validate_ranking_output(results)

        # Step 6: Record token usage
        response_tokens = estimate_tokens_accurate(raw_response)
        total_tokens = estimated_tokens + response_tokens
        record_token_usage(user_id, total_tokens)

        logger.info(f"Ranked {len(validated_results)} listings (tokens: {total_tokens})")
        return validated_results

    except ValueError as e:
        # Input validation error - don't retry
        logger.error(f"Input validation failed: {e}")
        raise

    except GeminiAPIError as e:
        # AI API error - return empty results
        logger.error(f"Gemini API error during ranking: {e}")
        error_response = handle_ai_error(e, {"query": query[:50], "user_id": user_id})
        logger.warning("Returning empty ranking results due to AI error")
        return []

    except AIValidationError as e:
        # Output validation error - return empty results
        logger.error(f"Output validation failed: {e}")
        logger.warning("Returning empty ranking results due to validation error")
        return []

    except Exception as e:
        # Unexpected error - return empty results
        logger.error(f"Unexpected error in ranking: {e}", exc_info=True)
        logger.warning("Returning empty ranking results due to unexpected error")
        return []


def _build_ranking_prompt(query: str, intent: Dict, listings: List[Dict]) -> str:
    """Build optimized ranking prompt."""
    # Truncate query to save tokens
    query = query[:150] if len(query) > 150 else query

    intent_json = json.dumps(intent, ensure_ascii=False)
    listings_json = json.dumps(listings, ensure_ascii=False)

    return (
        f"QUERY: {query}\n"
        f"INTENT: {intent_json}\n"
        f"PRODUCTS: {listings_json}\n\n"
        "Rank products by match quality:\n"
        "- 90-100: Perfect match\n"
        "- 70-89: Good match\n"
        "- 50-69: Decent match\n"
        "- 30-49: Weak match\n"
        "- 0-29: Poor match\n\n"
        "Return JSON array:\n"
        '[{"id": "1", "match_score": 85, "reason": "brief explanation"}, ...]\n\n'
        "Return ONLY the JSON array with ALL products."
    )


def _parse_json_array(text: str) -> List[Dict]:
    """
    Parse JSON array from AI response.

    Args:
        text: Raw AI response

    Returns:
        list: Parsed JSON array

    Raises:
        ValueError: If array cannot be extracted
    """
    # Try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Extract array substring
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse JSON array from: {text[:200]}")
    raise ValueError("Could not extract valid JSON array from AI response")


def _apply_defaults(results: List[Dict]) -> List[Dict]:
    """Apply default values for missing fields."""
    for item in results:
        if "match_score" not in item or item["match_score"] is None:
            item["match_score"] = 0
        if "reason" not in item or not item["reason"]:
            item["reason"] = "No reason provided"
        # Ensure match_score is int
        item["match_score"] = int(item["match_score"])

    return results
