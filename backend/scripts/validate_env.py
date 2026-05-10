#!/usr/bin/env python3
"""
Environment validation script for UNIFIND backend.
Validates all required environment variables before startup.
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple


# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def check_env_var(name: str, required: bool = True, validate_fn=None) -> Tuple[bool, str]:
    """
    Check if environment variable exists and optionally validate it.
    
    Args:
        name: Environment variable name
        required: Whether the variable is required
        validate_fn: Optional validation function
    
    Returns:
        Tuple of (is_valid, message)
    """
    value = os.getenv(name)
    
    if value is None or value.strip() == "":
        if required:
            return False, f"Missing required variable: {name}"
        else:
            return True, f"Optional variable not set: {name}"
    
    # Run custom validation if provided
    if validate_fn:
        try:
            validate_fn(value)
        except ValueError as e:
            return False, f"Invalid {name}: {str(e)}"
    
    return True, f"{name} is set"


def validate_firebase_key(value: str):
    """Validate Firebase private key format."""
    if not value.startswith("-----BEGIN PRIVATE KEY-----"):
        raise ValueError("Must start with '-----BEGIN PRIVATE KEY-----'")
    if not value.endswith("-----END PRIVATE KEY-----\n"):
        if not value.endswith("-----END PRIVATE KEY-----"):
            raise ValueError("Must end with '-----END PRIVATE KEY-----'")


def validate_email(value: str):
    """Basic email validation."""
    if "@" not in value or "." not in value:
        raise ValueError("Invalid email format")


def validate_cors_origins(value: str):
    """Validate CORS origins."""
    if not value or value.strip() == "":
        raise ValueError("Cannot be empty")
    
    # Check for wildcard in production
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production" and "*" in value:
        raise ValueError("Wildcard (*) not allowed in production")


def validate_environment(value: str):
    """Validate environment value."""
    valid_envs = ["development", "staging", "production", "test"]
    if value not in valid_envs:
        raise ValueError(f"Must be one of: {', '.join(valid_envs)}")


def main():
    """Run environment validation."""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}UNIFIND Backend - Environment Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print(f"{YELLOW}⚠ Warning: .env file not found at {env_file}{RESET}")
        print(f"{YELLOW}  Make sure environment variables are set via other means{RESET}\n")
    else:
        print(f"{GREEN}✓ .env file found{RESET}\n")
    
    # Define required variables with optional validators
    checks = [
        # Environment
        ("ENVIRONMENT", True, validate_environment),
        
        # Firebase
        ("FIREBASE_PROJECT_ID", True, None),
        ("FIREBASE_PRIVATE_KEY_ID", True, None),
        ("FIREBASE_PRIVATE_KEY", True, validate_firebase_key),
        ("FIREBASE_CLIENT_EMAIL", True, validate_email),
        ("FIREBASE_CLIENT_ID", True, None),
        ("FIREBASE_CLIENT_CERT_URL", True, None),
        
        # CORS
        ("CORS_ORIGINS", True, validate_cors_origins),
        
        # Gemini AI
        ("GEMINI_API_KEY", True, None),
        
        # Cloudinary
        ("CLOUDINARY_CLOUD_NAME", True, None),
        ("CLOUDINARY_API_KEY", True, None),
        ("CLOUDINARY_API_SECRET", True, None),
        
        # Email
        ("GMAIL_USER", True, validate_email),
        ("GMAIL_APP_PASSWORD", True, None),
    ]
    
    results = []
    errors = []
    warnings = []
    
    # Run checks
    for name, required, validator in checks:
        is_valid, message = check_env_var(name, required, validator)
        results.append((name, is_valid, message))
        
        if not is_valid:
            if required:
                errors.append(message)
            else:
                warnings.append(message)
    
    # Display results
    print(f"{BLUE}Validation Results:{RESET}\n")
    
    for name, is_valid, message in results:
        if is_valid:
            # Mask sensitive values
            value = os.getenv(name, "")
            if any(s in name.lower() for s in ["key", "secret", "password", "token"]):
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            
            print(f"{GREEN}✓{RESET} {name}: {display_value}")
        else:
            print(f"{RED}✗{RESET} {message}")
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary:{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for _, is_valid, _ in results if is_valid)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for warning in warnings:
            print(f"  • {warning}")
    
    # Production-specific checks
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        print(f"\n{BLUE}Production Checks:{RESET}")
        
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            origins = [o.strip() for o in cors_origins.split(",")]
            non_https = [o for o in origins if not o.startswith("https://") and not o.startswith("http://localhost")]
            
            if non_https:
                print(f"{YELLOW}⚠ Non-HTTPS origins in production:{RESET}")
                for origin in non_https:
                    print(f"  • {origin}")
                warnings.append("Non-HTTPS origins in production")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if errors:
        print(f"{RED}❌ Validation failed! Please fix the errors above.{RESET}")
        return 1
    elif warnings:
        print(f"{YELLOW}⚠ Validation passed with warnings.{RESET}")
        return 0
    else:
        print(f"{GREEN}✅ All validations passed!{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
