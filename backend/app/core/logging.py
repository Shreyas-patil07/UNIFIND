"""
Logging configuration for UNIFIND backend with structured JSON logging.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from app.core.config import settings


class SensitiveDataFilter(logging.Filter):
    """Filter to scrub sensitive data from logs."""
    SENSITIVE_PATTERNS = [
        'password', 'token', 'api_key', 'secret', 'authorization',
        'credit_card', 'ssn', 'private_key', 'firebase_private_key'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                record.msg = "[REDACTED - Sensitive Data]"
                record.args = ()
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Outputs logs in JSON format for better parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """Standard text formatter for development."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add request ID to message if available
        request_id = getattr(record, 'request_id', None)
        if request_id:
            record.msg = f"[{request_id}] {record.msg}"
        
        return super().format(record)


def setup_logging() -> None:
    """
    Configure structured logging with sensitive data filtering.
    Uses JSON format in production, standard format in development.
    """
    # Determine log level
    log_level = logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Choose formatter based on environment
    if settings.ENVIRONMENT == "production":
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for environment: {settings.ENVIRONMENT}")
