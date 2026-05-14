"""
Input Validator - Sanitize and validate user inputs before AI processing.

Protects against:
- Prompt injection attacks
- XSS attacks
- SQL injection
- Command injection
- Oversized inputs
- Malicious patterns
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Maximum input lengths
MAX_QUERY_LENGTH = 500
MAX_DESCRIPTION_LENGTH = 300
MAX_TITLE_LENGTH = 200

# Suspicious patterns that may indicate prompt injection
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions?",
    r"disregard\s+(previous|above|all)\s+instructions?",
    r"forget\s+(previous|above|all)\s+instructions?",
    r"new\s+instructions?:",
    r"system\s*:",
    r"assistant\s*:",
    r"you\s+are\s+now",
    r"act\s+as\s+a",
    r"pretend\s+to\s+be",
    r"roleplay\s+as",
    r"<\s*script",
    r"javascript\s*:",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"subprocess",
    r"os\.system",
    r"DROP\s+TABLE",
    r"DELETE\s+FROM",
    r"INSERT\s+INTO",
    r"UPDATE\s+.*\s+SET",
    r"UNION\s+SELECT",
    r"--\s*$",  # SQL comment
    r"/\*.*\*/",  # Multi-line comment
    r"<\s*iframe",
    r"<\s*embed",
    r"<\s*object",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
]

# Compile patterns for performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS]


class InputValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """
    Detect potential prompt injection attempts.

    Args:
        text: Input text to check

    Returns:
        Tuple of (is_suspicious, matched_patterns)
    """
    matched_patterns = []

    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            matched_patterns.append(pattern.pattern)

    is_suspicious = len(matched_patterns) > 0

    if is_suspicious:
        logger.warning(
            f"Potential prompt injection detected. Matched patterns: {matched_patterns[:3]}"
        )

    return is_suspicious, matched_patterns


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags and dangerous characters.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
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

    return text


def sanitize_special_chars(text: str) -> str:
    """
    Sanitize special characters that could be used in attacks.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove control characters except newline, tab, carriage return
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t\r")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Truncated text
    """
    if len(text) > max_length:
        logger.info(f"Truncating text from {len(text)} to {max_length} characters")
        return text[:max_length]
    return text


def sanitize_user_input(
    text: str,
    max_length: int = MAX_QUERY_LENGTH,
    allow_html: bool = False,
    strict: bool = True,
) -> str:
    """
    Sanitize user input for AI processing.

    Args:
        text: Raw user input
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags
        strict: If True, raise error on suspicious patterns

    Returns:
        Sanitized text

    Raises:
        InputValidationError: If input is invalid or suspicious (strict mode)
    """
    if not text or not isinstance(text, str):
        raise InputValidationError("Input must be a non-empty string")

    # Check for prompt injection
    is_suspicious, matched_patterns = detect_prompt_injection(text)

    if is_suspicious and strict:
        logger.error(f"Blocked suspicious input. Patterns: {matched_patterns}")
        raise InputValidationError(
            "Input contains suspicious patterns. Please rephrase your query."
        )

    # Remove HTML if not allowed
    if not allow_html:
        text = sanitize_html(text)

    # Sanitize special characters
    text = sanitize_special_chars(text)

    # Truncate to max length
    text = truncate_text(text, max_length)

    # Final validation
    if not text or len(text.strip()) == 0:
        raise InputValidationError("Input is empty after sanitization")

    return text


def validate_query_input(query: str) -> str:
    """
    Validate and sanitize a search query.

    Args:
        query: User search query

    Returns:
        Sanitized query

    Raises:
        InputValidationError: If query is invalid
    """
    try:
        sanitized = sanitize_user_input(
            query, max_length=MAX_QUERY_LENGTH, allow_html=False, strict=True
        )

        # Additional query-specific validation
        if len(sanitized) < 3:
            raise InputValidationError("Query must be at least 3 characters long")

        # Check for excessive repetition (spam detection)
        words = sanitized.lower().split()
        if len(words) > 0:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # If any word appears more than 50% of the time, it's suspicious
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.5:
                logger.warning(f"Excessive word repetition detected in query: {query[:50]}")
                raise InputValidationError("Query contains excessive repetition")

        return sanitized

    except InputValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating query: {e}")
        raise InputValidationError(f"Query validation failed: {str(e)}")


def validate_description_input(description: str) -> str:
    """
    Validate and sanitize a product description.

    Args:
        description: Product description

    Returns:
        Sanitized description

    Raises:
        InputValidationError: If description is invalid
    """
    try:
        sanitized = sanitize_user_input(
            description, max_length=MAX_DESCRIPTION_LENGTH, allow_html=False, strict=False
        )

        return sanitized

    except InputValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating description: {e}")
        raise InputValidationError(f"Description validation failed: {str(e)}")


def validate_batch_inputs(inputs: List[str], max_length: int = MAX_QUERY_LENGTH) -> List[str]:
    """
    Validate and sanitize a batch of inputs.

    Args:
        inputs: List of input strings
        max_length: Maximum length per input

    Returns:
        List of sanitized inputs

    Raises:
        InputValidationError: If any input is invalid
    """
    if not inputs or not isinstance(inputs, list):
        raise InputValidationError("Inputs must be a non-empty list")

    if len(inputs) > 100:
        raise InputValidationError("Too many inputs. Maximum 100 allowed.")

    sanitized_inputs = []

    for i, text in enumerate(inputs):
        try:
            sanitized = sanitize_user_input(text, max_length=max_length, strict=False)
            sanitized_inputs.append(sanitized)
        except InputValidationError as e:
            logger.warning(f"Input {i} failed validation: {e}")
            # Skip invalid inputs in batch processing
            continue

    if not sanitized_inputs:
        raise InputValidationError("All inputs failed validation")

    return sanitized_inputs


def get_input_stats(text: str) -> Dict[str, int]:
    """
    Get statistics about input text.

    Args:
        text: Input text

    Returns:
        Dictionary with stats (length, words, lines, etc.)
    """
    return {
        "length": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
        "unique_words": len(set(text.lower().split())),
        "has_html": bool(re.search(r"<[^>]+>", text)),
        "has_urls": bool(re.search(r"https?://", text)),
    }
