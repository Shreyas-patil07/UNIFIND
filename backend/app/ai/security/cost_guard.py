"""
Cost Guard - Control AI API costs and enforce budgets.

Features:
- Token counting and estimation
- Per-user daily token budgets
- Per-request token limits
- Cost estimation and logging
- Circuit breaker for budget exhaustion
"""

import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Token budgets (configurable via environment)
DAILY_TOKEN_BUDGET_PER_USER = 50000  # 50k tokens per user per day
REQUEST_TOKEN_LIMIT = 2000  # 2k tokens per request
SYSTEM_DAILY_BUDGET = 1000000  # 1M tokens per day system-wide

# Cost estimation (approximate, based on Gemini pricing)
# Note: Most Gemini models are FREE TIER with no cost
COST_PER_1K_TOKENS = 0.0  # Free tier
COST_PER_1K_TOKENS_PAID = 0.001  # If using paid tier: $0.001 per 1k tokens

# In-memory budget tracking (production should use Redis)
_user_token_usage: Dict[str, Dict[str, int]] = {}  # {user_id: {date: token_count}}
_system_token_usage: Dict[str, int] = {}  # {date: token_count}


class CostLimitError(Exception):
    """Raised when cost/token budget is exceeded."""

    pass


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses a simple heuristic: ~4 characters per token (GPT-style tokenization).
    For production, use tiktoken or similar library.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Simple estimation: 4 chars per token
    # This is conservative (overestimates) which is safer for budgeting
    estimated = len(text) // 4

    # Add some overhead for special tokens
    estimated += 10

    return max(1, estimated)


def estimate_tokens_accurate(text: str) -> int:
    """
    Accurate token counting using tiktoken (if available).

    Falls back to estimate_tokens if tiktoken not installed.

    Args:
        text: Input text

    Returns:
        Token count
    """
    try:
        import tiktoken

        # Use cl100k_base encoding (GPT-4, GPT-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)

    except ImportError:
        logger.debug("tiktoken not available, using simple estimation")
        return estimate_tokens(text)
    except Exception as e:
        logger.warning(f"Error in accurate token counting: {e}, falling back to estimation")
        return estimate_tokens(text)


def get_current_date() -> str:
    """Get current date as string (YYYY-MM-DD)."""
    return time.strftime("%Y-%m-%d")


def get_user_token_usage(user_id: str, date: Optional[str] = None) -> int:
    """
    Get token usage for a user on a specific date.

    Args:
        user_id: User ID
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Token count used
    """
    if date is None:
        date = get_current_date()

    if user_id not in _user_token_usage:
        return 0

    return _user_token_usage[user_id].get(date, 0)


def get_system_token_usage(date: Optional[str] = None) -> int:
    """
    Get system-wide token usage for a specific date.

    Args:
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Token count used
    """
    if date is None:
        date = get_current_date()

    return _system_token_usage.get(date, 0)


def record_token_usage(user_id: str, token_count: int, date: Optional[str] = None):
    """
    Record token usage for a user.

    Args:
        user_id: User ID
        token_count: Number of tokens used
        date: Date string (YYYY-MM-DD), defaults to today
    """
    if date is None:
        date = get_current_date()

    # Record user usage
    if user_id not in _user_token_usage:
        _user_token_usage[user_id] = {}

    _user_token_usage[user_id][date] = _user_token_usage[user_id].get(date, 0) + token_count

    # Record system usage
    _system_token_usage[date] = _system_token_usage.get(date, 0) + token_count

    logger.debug(f"Recorded {token_count} tokens for user {user_id} on {date}")


def check_token_budget(
    user_id: str, estimated_tokens: int, raise_on_exceed: bool = True
) -> bool:
    """
    Check if user has sufficient token budget.

    Args:
        user_id: User ID
        estimated_tokens: Estimated tokens for the request
        raise_on_exceed: If True, raise CostLimitError on budget exceed

    Returns:
        True if within budget, False otherwise

    Raises:
        CostLimitError: If budget exceeded and raise_on_exceed=True
    """
    date = get_current_date()

    # Check request limit
    if estimated_tokens > REQUEST_TOKEN_LIMIT:
        msg = (
            f"Request exceeds token limit: {estimated_tokens} > {REQUEST_TOKEN_LIMIT}. "
            f"Please shorten your query."
        )
        logger.warning(f"Token limit exceeded for user {user_id}: {msg}")
        if raise_on_exceed:
            raise CostLimitError(msg)
        return False

    # Check user daily budget
    current_usage = get_user_token_usage(user_id, date)
    if current_usage + estimated_tokens > DAILY_TOKEN_BUDGET_PER_USER:
        remaining = max(0, DAILY_TOKEN_BUDGET_PER_USER - current_usage)
        msg = (
            f"Daily token budget exceeded. Used: {current_usage}/{DAILY_TOKEN_BUDGET_PER_USER}. "
            f"Remaining: {remaining}. Resets tomorrow."
        )
        logger.warning(f"Daily budget exceeded for user {user_id}: {msg}")
        if raise_on_exceed:
            raise CostLimitError(msg)
        return False

    # Check system daily budget
    system_usage = get_system_token_usage(date)
    if system_usage + estimated_tokens > SYSTEM_DAILY_BUDGET:
        msg = (
            f"System-wide daily budget exceeded. "
            f"Used: {system_usage}/{SYSTEM_DAILY_BUDGET}. "
            f"Please try again later."
        )
        logger.error(f"System budget exceeded: {msg}")
        if raise_on_exceed:
            raise CostLimitError(msg)
        return False

    return True


def estimate_cost(token_count: int, use_paid_tier: bool = False) -> float:
    """
    Estimate cost for token usage.

    Args:
        token_count: Number of tokens
        use_paid_tier: If True, use paid tier pricing

    Returns:
        Estimated cost in USD
    """
    if use_paid_tier:
        return (token_count / 1000) * COST_PER_1K_TOKENS_PAID
    else:
        return 0.0  # Free tier


def get_budget_status(user_id: str) -> Dict[str, any]:
    """
    Get budget status for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary with budget information
    """
    date = get_current_date()
    current_usage = get_user_token_usage(user_id, date)
    remaining = max(0, DAILY_TOKEN_BUDGET_PER_USER - current_usage)
    percentage_used = (current_usage / DAILY_TOKEN_BUDGET_PER_USER) * 100

    return {
        "user_id": user_id,
        "date": date,
        "tokens_used": current_usage,
        "tokens_remaining": remaining,
        "daily_limit": DAILY_TOKEN_BUDGET_PER_USER,
        "percentage_used": round(percentage_used, 2),
        "estimated_cost": estimate_cost(current_usage),
    }


def get_system_budget_status() -> Dict[str, any]:
    """
    Get system-wide budget status.

    Returns:
        Dictionary with system budget information
    """
    date = get_current_date()
    current_usage = get_system_token_usage(date)
    remaining = max(0, SYSTEM_DAILY_BUDGET - current_usage)
    percentage_used = (current_usage / SYSTEM_DAILY_BUDGET) * 100

    return {
        "date": date,
        "tokens_used": current_usage,
        "tokens_remaining": remaining,
        "daily_limit": SYSTEM_DAILY_BUDGET,
        "percentage_used": round(percentage_used, 2),
        "estimated_cost": estimate_cost(current_usage),
    }


def reset_user_budget(user_id: str, date: Optional[str] = None):
    """
    Reset token budget for a user (admin function).

    Args:
        user_id: User ID
        date: Date to reset, defaults to today
    """
    if date is None:
        date = get_current_date()

    if user_id in _user_token_usage and date in _user_token_usage[user_id]:
        del _user_token_usage[user_id][date]
        logger.info(f"Reset token budget for user {user_id} on {date}")


def cleanup_old_usage_data(days_to_keep: int = 7):
    """
    Clean up old usage data to prevent memory bloat.

    Args:
        days_to_keep: Number of days of data to keep
    """
    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

    # Clean user usage data
    for user_id in list(_user_token_usage.keys()):
        dates_to_remove = []
        for date in _user_token_usage[user_id].keys():
            try:
                date_time = time.mktime(time.strptime(date, "%Y-%m-%d"))
                if date_time < cutoff_time:
                    dates_to_remove.append(date)
            except Exception:
                continue

        for date in dates_to_remove:
            del _user_token_usage[user_id][date]

        # Remove user entry if no dates left
        if not _user_token_usage[user_id]:
            del _user_token_usage[user_id]

    # Clean system usage data
    dates_to_remove = []
    for date in _system_token_usage.keys():
        try:
            date_time = time.mktime(time.strptime(date, "%Y-%m-%d"))
            if date_time < cutoff_time:
                dates_to_remove.append(date)
        except Exception:
            continue

    for date in dates_to_remove:
        del _system_token_usage[date]

    logger.info(f"Cleaned up usage data older than {days_to_keep} days")


# Initialize cleanup on module load
cleanup_old_usage_data()
