import json
import re

from services.gemini_client import generate_content

SYSTEM_PROMPT = """You are a product matching AI for a student marketplace. Your job is to rank products by how well they match what the user wants.

CRITICAL RULES:
1. You MUST return ONLY a valid JSON array, nothing else
2. Do NOT include any explanatory text before or after the JSON
3. Do NOT use markdown code blocks
4. Rank ALL products provided, even if they don't match well
5. Higher match_score means better match (0-100 scale)"""


async def rank_listings(query: str, intent: dict, listings: list[dict]) -> list[dict]:
    """
    Rank listings against the user query and extracted intent using Gemini.

    Returns a list of RankedResult dicts sorted descending by match_score.
    Each dict is guaranteed to have: id, match_score (int 0-100), reason (str).

    Raises:
        ValueError: if the Gemini response cannot be parsed as a JSON array.
    """
    # Optimize: Send only essential fields to reduce token usage
    simplified_listings = [
        {
            "id": l["id"],
            "title": l["title"],
            "category": l.get("category", ""),
            "price": l.get("price", 0),
            "condition": l.get("condition", ""),
            "description": l.get("description", "")[:100]  # Limit description to 100 chars
        }
        for l in listings
    ]
    
    # Optimize: Simplify intent to only relevant fields
    simplified_intent = {
        "category": intent.get("category", ""),
        "subject": intent.get("subject", ""),
        "max_price": intent.get("max_price"),
        "condition": intent.get("condition", "")
    }
    
    intent_json = json.dumps(simplified_intent, ensure_ascii=False)
    listings_json = json.dumps(simplified_listings, ensure_ascii=False)

    user_prompt = (
        "TASK: Rank these products based on how well they match the user's needs.\n\n"
        f"USER QUERY: {query[:200]}\n\n"  # Limit query length
        f"USER INTENT:\n{intent_json}\n\n"
        f"PRODUCTS:\n{listings_json}\n\n"
        "RANKING INSTRUCTIONS:\n"
        "1. Compare each product against the user's intent\n"
        "2. Consider: category match, item match, price fit, condition match\n"
        "3. Score 0-100: 90-100=perfect, 70-89=good, 50-69=decent, 30-49=weak, 0-29=poor\n"
        "4. Explain score briefly\n\n"
        "OUTPUT FORMAT (JSON array only):\n"
        '[{"id": "1", "match_score": 85, "reason": "brief explanation"}, ...]\n\n'
        "Return ONLY the JSON array with ALL products."
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
