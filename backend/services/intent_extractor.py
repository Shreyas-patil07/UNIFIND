import json
import re

from services.gemini_client import generate_content

SYSTEM_PROMPT = "You are an AI that extracts structured data from student marketplace queries."

REQUIRED_KEYS = {"category", "subject", "semester", "max_price", "condition", "intent_summary"}


def _build_user_prompt(query: str) -> str:
    return (
        "Extract and return ONLY a JSON object with these exact keys:\n"
        "- category: product category (e.g., 'Electronics', 'Books', 'Stationery', 'Furniture', 'Other')\n"
        "- subject: specific subject or item type (e.g., 'Laptop', 'Physics Textbook', 'Calculator')\n"
        "- semester: semester number if mentioned (e.g., '1', '2', '3', etc.) or 'Not specified'\n"
        "- max_price: maximum price as a number if mentioned, or null\n"
        "- condition: preferred condition ('New', 'Like New', 'Good', 'Fair', 'Any')\n"
        "- intent_summary: brief summary of what the user wants\n\n"
        f"User query: {query}\n\n"
        "Return ONLY valid JSON. Use 'Not specified' for missing text fields, null for missing numbers."
    )


def _parse_json(text: str) -> dict:
    """Try direct JSON parse, then fall back to regex substring extraction."""
    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Substring extraction via regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"Intent extraction failed: could not parse a valid JSON object from Gemini response. "
        f"Raw response: {text!r}"
    )


async def extract_intent(query: str) -> dict:
    """
    Call the Gemini API to extract structured intent from a natural-language query.

    Returns a dict with keys: category, subject, semester, max_price, condition, intent_summary.
    Raises ValueError if the response cannot be parsed as JSON.
    """
    user_prompt = _build_user_prompt(query)
    raw = await generate_content(SYSTEM_PROMPT, user_prompt)
    parsed = _parse_json(raw)
    
    # Apply defaults for missing or None values
    parsed.setdefault("category", "Other")
    parsed.setdefault("subject", "Not specified")
    parsed.setdefault("semester", "Not specified")
    parsed.setdefault("condition", "Any")
    parsed.setdefault("intent_summary", query)
    
    # Replace None with defaults
    if parsed["category"] is None:
        parsed["category"] = "Other"
    if parsed["subject"] is None:
        parsed["subject"] = "Not specified"
    if parsed["semester"] is None:
        parsed["semester"] = "Not specified"
    if parsed["condition"] is None:
        parsed["condition"] = "Any"
    if parsed["intent_summary"] is None:
        parsed["intent_summary"] = query
    
    return parsed
