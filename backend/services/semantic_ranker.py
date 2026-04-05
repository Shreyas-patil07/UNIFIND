import json
import re

from services.gemini_client import generate_content

SYSTEM_PROMPT = "You are a semantic search engine. Rank items based on relevance to user need."


async def rank_listings(query: str, intent: dict, listings: list[dict]) -> list[dict]:
    """
    Rank listings against the user query and extracted intent using Gemini.

    Returns a list of RankedResult dicts sorted descending by match_score.
    Each dict is guaranteed to have: id, match_score (int 0-100), reason (str).

    Raises:
        ValueError: if the Gemini response cannot be parsed as a JSON array.
    """
    intent_json = json.dumps(intent, ensure_ascii=False)
    listings_json = json.dumps(listings, ensure_ascii=False)

    user_prompt = (
        f"User query: {query}\n"
        f"Extracted intent: {intent_json}\n"
        f"Listings: {listings_json}\n"
        "Return ONLY a JSON array of objects with keys: id, match_score (0-100), reason."
    )

    raw = await generate_content(SYSTEM_PROMPT, user_prompt)

    # Attempt direct JSON parse first
    results = _parse_json_array(raw)

    # Apply defaults for missing fields
    for item in results:
        if "match_score" not in item:
            item["match_score"] = 0
        if "reason" not in item:
            item["reason"] = "No reason provided"

    # Sort descending by match_score
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    return results


def _parse_json_array(text: str) -> list:
    """Parse a JSON array from text, falling back to regex substring extraction."""
    # Try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback: extract first [...] substring
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Semantic ranker could not extract a valid JSON array from the Gemini response"
    )
