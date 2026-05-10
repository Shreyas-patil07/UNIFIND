.PHONY: help install test lint format clean docker-build docker-run dev

help:
	@echo "UNIFIND Backend - Available Commands"
	@echo "===================================="
	@echo "install       - Install dependencies"
	@echo "test          - Run tests with coverage"
	@echo "test-unit     - Run unit tests only"
	@echo "test-integration - Run integration tests only"
	@echo "lint          - Run all linters"
	@echo "format        - Format code with black and isort"
	@echo "security      - Run security scans"
	@echo "clean         - Remove cache and build files"
	@echo "docker-build  - Build Docker image"
	@echo "docker-run    - Run Docker container"
	@echo "dev           - Run development server"
	@echo "prod          - Run production server"

install:
	pip install -r requirements.txt

test:
	pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=60 \
		-v

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

lint:
	@echo "Running Ruff..."
	ruff check .
	@echo "Running Black..."
	black --check .
	@echo "Running isort..."
	isort --check-only .
	@echo "Running Flake8..."
	flake8 app/ --max-line-length=100

format:
	@echo "Formatting with Black..."
	black .
	@echo "Sorting imports with isort..."
	isort .
	@echo "Auto-fixing with Ruff..."
	ruff check --fix .

security:
	@echo "Running Bandit security scan..."
	bandit -r app/ -f screen
	@echo "Running Safety dependency check..."
	safety check --file requirements.txt

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "Clean complete!"

docker-build:
	docker build -t unifind-backend:latest .

docker-run:
	docker run -d \
		--name unifind-backend \
		-p 8000:8000 \
		--env-file .env \
		unifind-backend:latest

docker-stop:
	docker stop unifind-backend
	docker rm unifind-backend

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

prod:
	gunicorn app.main:app \
		--worker-class uvicorn.workers.UvicornWorker \
		--workers 4 \
		--bind 0.0.0.0:8000 \
		--timeout 120 \
		--access-logfile - \
		--error-logfile -
