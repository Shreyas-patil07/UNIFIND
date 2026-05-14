# ============================================================================
# UNIFIND Backend - Makefile
# ============================================================================
# Common deployment and development tasks
# ============================================================================

.PHONY: help install install-prod install-dev validate test lint format security clean docker-build docker-run docker-stop docker-clean deploy-render deploy-heroku

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose
IMAGE_NAME := unifind-backend
IMAGE_TAG := latest

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================================================
# Help
# ============================================================================

help: ## Show this help message
	@echo "$(BLUE)UNIFIND Backend - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Installation
# ============================================================================

install: ## Install all dependencies (development)
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-prod: ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-prod.txt
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: install ## Install development dependencies (alias for install)

# ============================================================================
# Validation & Testing
# ============================================================================

validate: ## Run startup validation
	@echo "$(BLUE)Running startup validation...$(NC)"
	$(PYTHON) scripts/startup_validation.py
	@echo "$(GREEN)✓ Validation passed$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-quick: ## Run tests without coverage
	@echo "$(BLUE)Running quick tests...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)✓ Tests completed$(NC)"

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Run linters (ruff, flake8)
	@echo "$(BLUE)Running linters...$(NC)"
	ruff check app/
	flake8 app/
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code (black, isort)
	@echo "$(BLUE)Formatting code...$(NC)"
	black app/
	isort app/
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without changes
	@echo "$(BLUE)Checking code format...$(NC)"
	black --check app/
	isort --check-only app/
	@echo "$(GREEN)✓ Format check completed$(NC)"

# ============================================================================
# Security
# ============================================================================

security: ## Run security checks (bandit, safety)
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r app/ -ll
	safety check --json
	@echo "$(GREEN)✓ Security checks completed$(NC)"

security-scan: security ## Alias for security

# ============================================================================
# Development
# ============================================================================

dev: ## Run development server with auto-reload
	@echo "$(BLUE)Starting development server...$(NC)"
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

run: ## Run production server locally
	@echo "$(BLUE)Starting production server...$(NC)"
	gunicorn app.main:app \
		--worker-class uvicorn.workers.UvicornWorker \
		--workers 4 \
		--bind 0.0.0.0:8000 \
		--timeout 120 \
		--log-level info

# ============================================================================
# Docker
# ============================================================================

docker-build: ## Build Docker image (production)
	@echo "$(BLUE)Building Docker image...$(NC)"
	$(DOCKER) build --target production -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "$(GREEN)✓ Docker image built: $(IMAGE_NAME):$(IMAGE_TAG)$(NC)"

docker-build-dev: ## Build Docker image (development)
	@echo "$(BLUE)Building development Docker image...$(NC)"
	$(DOCKER) build --target development -t $(IMAGE_NAME):dev .
	@echo "$(GREEN)✓ Docker image built: $(IMAGE_NAME):dev$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	$(DOCKER) run -d \
		--name $(IMAGE_NAME) \
		-p 8000:8000 \
		--env-file .env \
		--restart unless-stopped \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "$(GREEN)✓ Container started: $(IMAGE_NAME)$(NC)"
	@echo "$(YELLOW)View logs: make docker-logs$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	$(DOCKER) stop $(IMAGE_NAME) || true
	$(DOCKER) rm $(IMAGE_NAME) || true
	@echo "$(GREEN)✓ Container stopped$(NC)"

docker-logs: ## View Docker container logs
	$(DOCKER) logs -f $(IMAGE_NAME)

docker-shell: ## Open shell in running container
	$(DOCKER) exec -it $(IMAGE_NAME) /bin/bash

docker-clean: ## Remove Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	$(DOCKER) stop $(IMAGE_NAME) || true
	$(DOCKER) rm $(IMAGE_NAME) || true
	$(DOCKER) rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	$(DOCKER) rmi $(IMAGE_NAME):dev || true
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

# ============================================================================
# Docker Compose
# ============================================================================

compose-up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"

compose-down: ## Stop services with docker-compose
	@echo "$(BLUE)Stopping services with docker-compose...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

compose-logs: ## View docker-compose logs
	$(DOCKER_COMPOSE) logs -f

compose-build: ## Build services with docker-compose
	@echo "$(BLUE)Building services with docker-compose...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Services built$(NC)"

compose-restart: ## Restart services with docker-compose
	@echo "$(BLUE)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

# ============================================================================
# Deployment
# ============================================================================

deploy-render: ## Deploy to Render (requires git push)
	@echo "$(BLUE)Deploying to Render...$(NC)"
	@echo "$(YELLOW)Ensure all changes are committed$(NC)"
	git push origin main
	@echo "$(GREEN)✓ Pushed to main branch. Render will auto-deploy.$(NC)"

deploy-heroku: ## Deploy to Heroku
	@echo "$(BLUE)Deploying to Heroku...$(NC)"
	@echo "$(YELLOW)Ensure all changes are committed$(NC)"
	git push heroku main
	@echo "$(GREEN)✓ Deployed to Heroku$(NC)"

# ============================================================================
# Cleanup
# ============================================================================

clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-all: clean docker-clean ## Clean everything including Docker resources

# ============================================================================
# CI/CD
# ============================================================================

ci: format-check lint security test ## Run all CI checks

pre-commit: format lint ## Run pre-commit checks

pre-push: ci ## Run pre-push checks

# ============================================================================
# Database (if needed)
# ============================================================================

# db-migrate: ## Run database migrations
# 	@echo "$(BLUE)Running database migrations...$(NC)"
# 	# Add migration command here
# 	@echo "$(GREEN)✓ Migrations completed$(NC)"

# ============================================================================
# Utilities
# ============================================================================

env-example: ## Create .env from .env.example
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env created. Please edit with your values.$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env already exists$(NC)"; \
	fi

check-env: ## Check if required environment variables are set
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@$(PYTHON) -c "import os; from dotenv import load_dotenv; load_dotenv(); \
		required = ['FIREBASE_PROJECT_ID', 'GEMINI_API_KEY', 'CLOUDINARY_CLOUD_NAME']; \
		missing = [v for v in required if not os.getenv(v)]; \
		print('✓ All required variables set' if not missing else f'✗ Missing: {missing}')"

version: ## Show version information
	@echo "$(BLUE)UNIFIND Backend$(NC)"
	@echo "Version: 2.1.0"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Docker: $$($(DOCKER) --version)"

# ============================================================================
# Production Checklist
# ============================================================================

prod-check: ## Run production readiness checks
	@echo "$(BLUE)Running production readiness checks...$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Environment Configuration$(NC)"
	@make check-env
	@echo ""
	@echo "$(YELLOW)2. Startup Validation$(NC)"
	@make validate
	@echo ""
	@echo "$(YELLOW)3. Security Checks$(NC)"
	@make security
	@echo ""
	@echo "$(YELLOW)4. Code Quality$(NC)"
	@make lint
	@echo ""
	@echo "$(YELLOW)5. Tests$(NC)"
	@make test-quick
	@echo ""
	@echo "$(GREEN)✓ Production readiness checks completed$(NC)"
