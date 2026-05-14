"""
Output Validator - Validate and sanitize AI outputs.

Protects against:
- Malformed JSON
- Schema violations
- Type errors
- Hallucinated fields
- XSS in AI-generated text
- Out-of-bounds values
"""

import logging
import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class OutputValidationError(ValueError):
    """Raised when output validation fails."""

    pass


# ============================================================================
# Pydantic Schemas for AI Outputs
# ============================================================================


class IntentExtractionOutput(BaseModel):
    """Schema for intent extraction output."""

    category: str = Field(..., description="Product category")
    subject: str = Field(..., description="Specific item or subject")
    semester: str = Field(..., description="Academic semester if applicable")
    max_price: float | None = Field(None, description="Maximum price", ge=0, le=1000000)
    condition: str = Field(..., description="Desired condition")
    intent_summary: str = Field(..., description="Brief summary of intent")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is from allowed list."""
        allowed_categories = [
            "Electronics",
            "Books",
            "Stationery",
            "Furniture",
            "Clothing",
            "Sports",
            "Other",
        ]
        if v not in allowed_categories:
            logger.warning(f"Invalid category '{v}', defaulting to 'Other'")
            return "Other"
        return v

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: str) -> str:
        """Validate condition is from allowed list."""
        allowed_conditions = ["New", "Like New", "Good", "Fair", "Any"]
        if v not in allowed_conditions:
            logger.warning(f"Invalid condition '{v}', defaulting to 'Any'")
            return "Any"
        return v

    @field_validator("semester")
    @classmethod
    def validate_semester(cls, v: str) -> str:
        """Validate semester format."""
        if v == "Not specified":
            return v
        # Check if it's a valid semester number (1-8)
        if v.isdigit() and 1 <= int(v) <= 8:
            return v
        logger.warning(f"Invalid semester '{v}', defaulting to 'Not specified'")
        return "Not specified"

    @field_validator("subject", "intent_summary")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize text fields to prevent XSS."""
        # Remove HTML tags
        v = re.sub(r"<[^>]+>", "", v)
        # Remove script content
        v = re.sub(r"<script[^>]*>.*?</script>", "", v, flags=re.DOTALL | re.IGNORECASE)
        # Limit length
        if len(v) > 500:
            v = v[:500]
        return v.strip()


class RankedItem(BaseModel):
    """Schema for a single ranked item."""

    id: str = Field(..., description="Item ID")
    match_score: int = Field(..., description="Match score", ge=0, le=100)
    reason: str = Field(..., description="Reason for ranking")

    @field_validator("match_score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        """Ensure score is within bounds."""
        if v < 0:
            return 0
        if v > 100:
            return 100
        return v

    @field_validator("reason")
    @classmethod
    def sanitize_reason(cls, v: str) -> str:
        """Sanitize reason text."""
        # Remove HTML tags
        v = re.sub(r"<[^>]+>", "", v)
        # Limit length
        if len(v) > 300:
            v = v[:300]
        if not v or len(v.strip()) == 0:
            return "No reason provided"
        return v.strip()


class SemanticRankingOutput(BaseModel):
    """Schema for semantic ranking output."""

    results: List[RankedItem] = Field(..., description="List of ranked items")

    @field_validator("results")
    @classmethod
    def validate_results(cls, v: List[RankedItem]) -> List[RankedItem]:
        """Validate results list."""
        if not v:
            logger.warning("Empty results list")
            return []

        # Remove duplicates by ID
        seen_ids = set()
        unique_results = []
        for item in v:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)
            else:
                logger.warning(f"Duplicate item ID removed: {item.id}")

        # Sort by match_score descending
        unique_results.sort(key=lambda x: x.match_score, reverse=True)

        # Limit to top 50
        if len(unique_results) > 50:
            logger.info(f"Truncating results from {len(unique_results)} to 50")
            unique_results = unique_results[:50]

        return unique_results


# ============================================================================
# Validation Functions
# ============================================================================


def validate_intent_output(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate intent extraction output against schema.

    Args:
        raw_output: Raw output from AI

    Returns:
        Validated and sanitized output

    Raises:
        OutputValidationError: If validation fails
    """
    try:
        # Validate against schema
        validated = IntentExtractionOutput(**raw_output)

        # Convert to dict
        result = validated.model_dump()

        logger.debug(f"Intent output validated: {result.get('category')}")
        return result

    except Exception as e:
        logger.error(f"Intent output validation failed: {e}")
        logger.error(f"Raw output: {raw_output}")

        # Return safe defaults
        logger.warning("Returning default intent output due to validation failure")
        return {
            "category": "Other",
            "subject": "Not specified",
            "semester": "Not specified",
            "max_price": None,
            "condition": "Any",
            "intent_summary": "Unable to extract intent",
        }


def validate_ranking_output(raw_output: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate semantic ranking output against schema.

    Args:
        raw_output: Raw output from AI (list of ranked items)

    Returns:
        Validated and sanitized output

    Raises:
        OutputValidationError: If validation fails
    """
    try:
        # Wrap in container for validation
        validated = SemanticRankingOutput(results=raw_output)

        # Convert to list of dicts
        result = [item.model_dump() for item in validated.results]

        logger.debug(f"Ranking output validated: {len(result)} items")
        return result

    except Exception as e:
        logger.error(f"Ranking output validation failed: {e}")
        logger.error(f"Raw output sample: {raw_output[:2] if raw_output else 'empty'}")

        # Try to salvage what we can
        salvaged = []
        for item in raw_output:
            try:
                validated_item = RankedItem(**item)
                salvaged.append(validated_item.model_dump())
            except Exception:
                logger.warning(f"Skipping invalid item: {item}")
                continue

        if salvaged:
            logger.warning(f"Salvaged {len(salvaged)} items from {len(raw_output)} total")
            return salvaged

        # Return empty list if nothing can be salvaged
        logger.warning("Returning empty ranking output due to validation failure")
        return []


def sanitize_ai_text(text: str, max_length: int = 500) -> str:
    """
    Sanitize AI-generated text to prevent XSS and other attacks.

    Args:
        text: AI-generated text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove script tags and content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove style tags and content
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove event handlers
    text = re.sub(r"on\w+\s*=\s*[\"'][^\"']*[\"']", "", text, flags=re.IGNORECASE)

    # Remove javascript: protocol
    text = re.sub(r"javascript\s*:", "", text, flags=re.IGNORECASE)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def validate_numeric_field(
    value: Any, field_name: str, min_value: float = 0, max_value: float = 1000000
) -> float | None:
    """
    Validate a numeric field from AI output.

    Args:
        value: Value to validate
        field_name: Name of the field (for logging)
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Validated numeric value or None
    """
    if value is None:
        return None

    try:
        # Convert to float
        numeric_value = float(value)

        # Check bounds
        if numeric_value < min_value:
            logger.warning(
                f"{field_name} below minimum ({numeric_value} < {min_value}), setting to {min_value}"
            )
            return min_value

        if numeric_value > max_value:
            logger.warning(
                f"{field_name} above maximum ({numeric_value} > {max_value}), setting to {max_value}"
            )
            return max_value

        return numeric_value

    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid {field_name} value: {value} ({e}), returning None")
        return None


def detect_hallucinated_fields(output: Dict[str, Any], expected_fields: List[str]) -> List[str]:
    """
    Detect unexpected fields in AI output (potential hallucination).

    Args:
        output: AI output dictionary
        expected_fields: List of expected field names

    Returns:
        List of unexpected field names
    """
    unexpected = []

    for key in output.keys():
        if key not in expected_fields:
            unexpected.append(key)
            logger.warning(f"Unexpected field in AI output: {key}")

    return unexpected


def validate_enum_field(value: str, allowed_values: List[str], default: str) -> str:
    """
    Validate an enum field from AI output.

    Args:
        value: Value to validate
        allowed_values: List of allowed values
        default: Default value if validation fails

    Returns:
        Validated value or default
    """
    if not value or not isinstance(value, str):
        logger.warning(f"Invalid enum value: {value}, using default: {default}")
        return default

    if value not in allowed_values:
        logger.warning(
            f"Enum value '{value}' not in allowed values {allowed_values}, using default: {default}"
        )
        return default

    return value


def get_output_stats(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get statistics about AI output.

    Args:
        output: AI output dictionary

    Returns:
        Dictionary with stats
    """
    stats = {
        "field_count": len(output),
        "has_null_values": any(v is None for v in output.values()),
        "text_fields": sum(1 for v in output.values() if isinstance(v, str)),
        "numeric_fields": sum(1 for v in output.values() if isinstance(v, (int, float))),
        "list_fields": sum(1 for v in output.values() if isinstance(v, list)),
    }

    return stats
