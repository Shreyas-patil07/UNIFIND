"""
AI Security Module - Production-grade security for AI integrations.

This module provides comprehensive security measures for AI/LLM integrations:
- Input sanitization and validation
- Output validation and schema enforcement
- Cost control and rate limiting
- Error handling and fallback mechanisms
"""

from app.ai.security.cost_guard import check_token_budget, estimate_tokens
from app.ai.security.error_handler import (
    AICostLimitError,
    AISecurityError,
    AIValidationError,
    handle_ai_error,
    retry_with_backoff,
)
from app.ai.security.input_validator import sanitize_user_input, validate_query_input
from app.ai.security.output_validator import (
    validate_intent_output,
    validate_ranking_output,
)

__all__ = [
    # Input validation
    "sanitize_user_input",
    "validate_query_input",
    # Output validation
    "validate_intent_output",
    "validate_ranking_output",
    # Cost control
    "check_token_budget",
    "estimate_tokens",
    # Error handling
    "handle_ai_error",
    "retry_with_backoff",
    "AISecurityError",
    "AIValidationError",
    "AICostLimitError",
]
