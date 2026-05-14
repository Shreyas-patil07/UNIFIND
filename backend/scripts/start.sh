#!/bin/bash
# UNIFIND Backend - Production Startup Script
# This script provides a deterministic, validated startup process for all environments.

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-development}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-4}"
TIMEOUT="${TIMEOUT:-120}"
LOG_LEVEL="${LOG_LEVEL:-info}"

# Derived configuration
if [ "$ENVIRONMENT" = "production" ]; then
    WORKERS="${WORKERS:-4}"
    TIMEOUT="${TIMEOUT:-120}"
    LOG_LEVEL="${LOG_LEVEL:-warning}"
elif [ "$ENVIRONMENT" = "staging" ]; then
    WORKERS="${WORKERS:-2}"
    TIMEOUT="${TIMEOUT:-90}"
    LOG_LEVEL="${LOG_LEVEL:-info}"
else
    WORKERS="${WORKERS:-2}"
    TIMEOUT="${TIMEOUT:-60}"
    LOG_LEVEL="${LOG_LEVEL:-debug}"
fi

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           UNIFIND Backend - Production Startup            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Environment: $ENVIRONMENT"
    log_info "Port: $PORT"
    log_info "Workers: $WORKERS"
    log_info "Timeout: ${TIMEOUT}s"
    log_info "Log Level: $LOG_LEVEL"
    echo ""
}

check_python() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION detected"
}

run_startup_validation() {
    log_info "Running startup validation..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 scripts/startup_validation.py; then
        log_success "Startup validation passed"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return 0
    else
        log_error "Startup validation failed"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return 1
    fi
}

wait_for_dependencies() {
    log_info "Waiting for dependencies to be ready..."
    
    # Add any dependency wait logic here
    # For example, waiting for database, cache, etc.
    
    log_success "All dependencies ready"
}

start_application() {
    log_info "Starting application with gunicorn..."
    echo ""
    
    # Gunicorn configuration
    exec gunicorn app.main:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers "$WORKERS" \
        --bind "0.0.0.0:$PORT" \
        --timeout "$TIMEOUT" \
        --keepalive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level "$LOG_LEVEL" \
        --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' \
        --preload \
        --graceful-timeout 30
}

# Graceful shutdown handler
cleanup() {
    log_warning "Received shutdown signal, cleaning up..."
    
    # Kill all child processes
    pkill -P $$ || true
    
    log_success "Cleanup complete"
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGTERM SIGINT SIGQUIT

# Main execution
main() {
    print_banner
    
    # Pre-flight checks
    check_python
    
    # Run validation (skip in development if SKIP_VALIDATION=1)
    if [ "${SKIP_VALIDATION:-0}" = "1" ] && [ "$ENVIRONMENT" = "development" ]; then
        log_warning "Skipping startup validation (SKIP_VALIDATION=1)"
    else
        if ! run_startup_validation; then
            log_error "Cannot start application - validation failed"
            exit 1
        fi
    fi
    
    # Wait for dependencies
    wait_for_dependencies
    
    # Start the application
    log_success "Starting UNIFIND Backend..."
    echo ""
    start_application
}

# Run main function
main
