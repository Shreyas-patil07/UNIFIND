import json
import re

from services.gemini_client import generate_content

SYSTEM_PROMPT = """You are a precise data extraction AI for a student marketplace. Your ONLY job is to extract structured information from queries and return valid JSON.

CRITICAL RULES:
1. You MUST return ONLY a valid JSON object, nothing else
2. Do NOT include any explanatory text before or after the JSON
3. Do NOT use markdown code blocks
4. Extract information accurately from the user's query"""

REQUIRED_KEYS = {"category", "subject", "semester", "max_price", "condition", "intent_summary"}


def _build_user_prompt(query: str) -> str:
    return (
        "TASK: Extract structured data from the user query below.\n\n"
        "REQUIRED OUTPUT FORMAT - Return ONLY this JSON structure (no extra text):\n"
        "{\n"
        '  "category": "string",\n'
        '  "subject": "string",\n'
        '  "semester": "string",\n'
        '  "max_price": number or null,\n'
        '  "condition": "string",\n'
        '  "intent_summary": "string"\n'
        "}\n\n"
        "FIELD INSTRUCTIONS:\n"
        "1. category: Choose ONE from: 'Electronics', 'Books', 'Stationery', 'Furniture', 'Clothing', 'Sports', 'Other'\n"
        "   - If user mentions laptop/phone/calculator → 'Electronics'\n"
        "   - If user mentions textbook/novel/notes → 'Books'\n"
        "   - If user mentions pen/notebook/folder → 'Stationery'\n"
        "   - If user mentions desk/chair/table → 'Furniture'\n"
        "   - Otherwise → 'Other'\n\n"
        "2. subject: The SPECIFIC item they want (e.g., 'Laptop', 'Calculator', 'Physics Textbook', 'Desk')\n"
        "   - Be specific: 'Calculator' not 'Electronics'\n"
        "   - Use the exact item name from the query\n\n"
        "3. semester: If mentioned, extract the number (e.g., '1', '2', '3', '4', '5', '6', '7', '8')\n"
        "   - If NOT mentioned → 'Not specified'\n"
        "   - Examples: '3rd semester' → '3', 'first year' → '1', 'final year' → '8'\n\n"
        "4. max_price: Extract the maximum price as a NUMBER (no currency symbols)\n"
        "   - 'under 50000' → 50000\n"
        "   - 'around 30k' → 30000\n"
        "   - 'budget 25000' → 25000\n"
        "   - If NO price mentioned → null\n\n"
        "5. condition: Choose ONE from: 'New', 'Like New', 'Good', 'Fair', 'Any'\n"
        "   - If they say 'new' or 'brand new' → 'New'\n"
        "   - If they say 'excellent' or 'barely used' → 'Like New'\n"
        "   - If they say 'good' or 'working' → 'Good'\n"
        "   - If they say 'used' or 'old' → 'Fair'\n"
        "   - If NOT mentioned → 'Any'\n\n"
        "6. intent_summary: Write a 1-sentence summary of what they want\n"
        "   - Example: 'User wants a laptop for coding under 50000 rupees'\n\n"
        f"USER QUERY: {query}\n\n"
        "REMEMBER: Return ONLY the JSON object, no other text. Start with {{ and end with }}"
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
