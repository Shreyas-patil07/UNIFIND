# UNIFIND Backend - Scripts Directory

This directory contains operational scripts for deployment, validation, and maintenance.

---

## Scripts Overview

### 1. startup_validation.py

**Purpose:** Comprehensive startup validation before accepting production traffic.

**What it checks:**
- Python version (3.11+)
- Required packages installed
- Environment variables present and valid
- Firebase connection working
- Gemini API accessible
- Cloudinary configured
- Production security settings

**Usage:**
```bash
# Run validation
python scripts/startup_validation.py

# Exit codes:
# 0 - All checks passed
# 1 - Critical check failed
# 2 - Configuration error
```

**When to use:**
- Before deploying to production
- After changing environment variables
- When troubleshooting startup issues
- In CI/CD pipelines

**Skip in development:**
```bash
export SKIP_VALIDATION=1
```

---

### 2. start.sh

**Purpose:** Production-grade startup script with validation and graceful shutdown.

**What it does:**
1. Prints startup banner
2. Checks Python version
3. Runs startup validation (optional)
4. Waits for dependencies
5. Starts gunicorn with optimal settings
6. Handles graceful shutdown

**Usage:**
```bash
# Make executable
chmod +x scripts/start.sh

# Run with defaults
./scripts/start.sh

# Run with custom settings
ENVIRONMENT=production WORKERS=8 ./scripts/start.sh

# Skip validation (development)
SKIP_VALIDATION=1 ./scripts/start.sh
```

**Environment variables:**
- `ENVIRONMENT` - Application environment (default: development)
- `PORT` - Server port (default: 8000)
- `WORKERS` - Number of workers (default: 4)
- `TIMEOUT` - Request timeout (default: 120)
- `LOG_LEVEL` - Logging level (default: info)
- `SKIP_VALIDATION` - Skip validation (default: 0)

**When to use:**
- Production deployments
- Systemd services
- Manual server starts
- Testing production configuration

---

## Adding New Scripts

### Guidelines

1. **Use descriptive names** - `validate_config.py`, not `check.py`
2. **Add shebang** - `#!/usr/bin/env python3` or `#!/bin/bash`
3. **Make executable** - `chmod +x script.sh`
4. **Document usage** - Add docstring or comments
5. **Handle errors** - Exit with appropriate codes
6. **Log output** - Use structured logging

### Template (Python)

```python
#!/usr/bin/env python3
"""
Script description here.

Usage:
    python scripts/my_script.py [options]

Exit Codes:
    0 - Success
    1 - Error
"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    try:
        # Your code here
        logger.info("Script completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Template (Bash)

```bash
#!/bin/bash
# Script description here
#
# Usage:
#   ./scripts/my_script.sh [options]
#
# Exit Codes:
#   0 - Success
#   1 - Error

set -e  # Exit on error
set -u  # Exit on undefined variable

# Functions
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Main
main() {
    log_info "Starting script..."
    
    # Your code here
    
    log_info "Script completed successfully"
}

# Run
main "$@"
```

---

## Common Patterns

### Exit Codes

Use standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Dependency error
- `126` - Command not executable
- `127` - Command not found
- `130` - Terminated by Ctrl+C

### Logging

Use structured logging:
```python
logger.info("Operation started", extra={'operation': 'deploy'})
logger.warning("Slow response", extra={'duration': 5.2})
logger.error("Operation failed", extra={'error': str(e)})
```

### Error Handling

Always handle errors gracefully:
```python
try:
    # Operation
    pass
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    return 1
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return 2
```

### Environment Variables

Load from .env file:
```python
from dotenv import load_dotenv
import os

load_dotenv()
value = os.getenv('VARIABLE_NAME', 'default_value')
```

---

## Testing Scripts

### Manual Testing

```bash
# Test success case
python scripts/startup_validation.py
echo $?  # Should be 0

# Test failure case (missing env var)
unset FIREBASE_PROJECT_ID
python scripts/startup_validation.py
echo $?  # Should be 1
```

### Automated Testing

```python
# tests/test_scripts.py
import subprocess

def test_startup_validation_success():
    result = subprocess.run(
        ['python', 'scripts/startup_validation.py'],
        capture_output=True
    )
    assert result.returncode == 0

def test_startup_validation_failure():
    result = subprocess.run(
        ['python', 'scripts/startup_validation.py'],
        capture_output=True,
        env={'PATH': os.environ['PATH']}  # Empty env
    )
    assert result.returncode != 0
```

---

## Maintenance

### Regular Tasks

1. **Review logs** - Check for warnings or errors
2. **Update dependencies** - Keep scripts compatible
3. **Test changes** - Verify scripts work after updates
4. **Document changes** - Update this README

### Deprecation

When deprecating a script:
1. Add deprecation warning
2. Update documentation
3. Provide migration path
4. Remove after grace period

Example:
```python
import warnings
warnings.warn(
    "This script is deprecated. Use new_script.py instead.",
    DeprecationWarning
)
```

---

## Troubleshooting

### Script Won't Execute

```bash
# Check if executable
ls -la scripts/start.sh

# Make executable
chmod +x scripts/start.sh

# Check shebang
head -1 scripts/start.sh
```

### Import Errors

```bash
# Add parent directory to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or in script:
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Environment Variables Not Loaded

```bash
# Verify .env exists
ls -la .env

# Load manually
source .env  # Bash
set -a; source .env; set +a  # Export all

# Or in Python
from dotenv import load_dotenv
load_dotenv()
```

---

## Best Practices

1. **Idempotent** - Scripts should be safe to run multiple times
2. **Atomic** - Either complete fully or fail cleanly
3. **Logged** - All operations should be logged
4. **Tested** - Scripts should have tests
5. **Documented** - Usage and behavior documented
6. **Versioned** - Track changes in git
7. **Reviewed** - Code review before merging

---

## Security

### Secrets

Never hardcode secrets:
```python
# ❌ Bad
API_KEY = "sk-1234567890"

# ✅ Good
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY not set")
```

### Input Validation

Always validate input:
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### File Permissions

Set appropriate permissions:
```bash
# Scripts: executable by owner
chmod 750 scripts/*.sh

# Config files: readable by owner only
chmod 600 .env
```

---

## Future Scripts

Planned scripts for future implementation:

1. **backup.py** - Backup Firestore data
2. **restore.py** - Restore from backup
3. **migrate.py** - Database migrations
4. **health_check.py** - Comprehensive health check
5. **performance_test.py** - Load testing
6. **security_scan.py** - Security audit
7. **cleanup.py** - Clean old data
8. **report.py** - Generate reports

---

## Contributing

When adding new scripts:

1. Follow templates above
2. Add documentation
3. Add tests
4. Update this README
5. Submit PR with description

---

## Support

For issues with scripts:

1. Check script documentation
2. Review logs
3. Test manually
4. Check GitHub issues
5. Contact DevOps team

---

**End of Scripts Documentation**
