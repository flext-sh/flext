# Makefile for tap-oracle-oic
# Oracle Integration Cloud Singer TAP with strict PEP8 compliance

.PHONY: help install install-dev clean lint format type-check test test-cov test-unit test-integration test-e2e security audit build publish pre-commit check all ci-check

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install all dependencies including development
	poetry install

# Code quality and formatting (strict PEP8)
format: ## Format code with black, isort, and ruff
	poetry run black src/ tests/ --line-length 88 --target-version py39
	poetry run isort src/ tests/ --profile black --line-length 88
	poetry run ruff format src/ tests/

lint: ## Run all linters (ruff, black check, isort check)
	poetry run ruff check src/ tests/ --fix
	poetry run black src/ tests/ --check --line-length 88 --target-version py39
	poetry run isort src/ tests/ --check-only --profile black --line-length 88

type-check: ## Run mypy type checking
	poetry run mypy src/ --strict --warn-unreachable --warn-redundant-casts --warn-unused-ignores

# Testing
test: ## Run all tests
	poetry run pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term --cov-fail-under=80

test-unit: ## Run unit tests only
	poetry run pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests only
	poetry run pytest tests/integration/ -v --tb=short

test-e2e: ## Run end-to-end tests
	SKIP_LIVE_TESTS=true poetry run pytest tests/test_e2e_complete.py -v --tb=short

# Security
security: ## Run security checks
	poetry run bandit -r src/ -f json || true
	poetry run safety check

audit: ## Audit dependencies for vulnerabilities
	poetry audit

# Build and publish
build: ## Build package
	poetry build

publish: ## Publish to PyPI (requires auth)
	poetry publish

# Development tools
clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit: ## Run pre-commit hooks
	poetry run pre-commit run --all-files

# Singer TAP specific
discover: ## Run Singer discovery
	poetry run tap-oracle-oic --config config.json --discover

catalog: ## Generate catalog
	poetry run tap-oracle-oic --config config.json --discover > catalog.json

sync: ## Run sync with catalog
	poetry run tap-oracle-oic --config config.json --catalog catalog.json

generate-config: ## Generate config.json from .env
	python generate_config.py

# Comprehensive checks
check: format lint type-check test ## Run all quality checks
	@echo "✅ All checks passed!"

all: clean install-dev check build ## Full development setup and validation

ci-check: install-dev lint type-check test-cov security ## CI/CD pipeline checks
	@echo "✅ CI checks completed!"

# Docker support
docker-build: ## Build Docker image
	docker build -t tap-oracle-oic:latest .

docker-run: ## Run in Docker container
	docker run --rm -v $(PWD)/config.json:/app/config.json tap-oracle-oic:latest --discover

# Documentation
docs: ## Generate documentation
	poetry run sphinx-build -b html docs/ docs/_build/html

docs-serve: ## Serve documentation locally
	poetry run python -m http.server 8000 --directory docs/_build/html

# Performance
profile: ## Profile the tap performance
	poetry run python -m cProfile -o profile.stats -m tap_oracle_oic --config config.json --discover
	poetry run python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
