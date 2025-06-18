# Makefile for flx-oracle-oic
# FLX Oracle Integration Cloud Adapter with Unified CLI - strict PEP8 compliance

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

# FLX CLI specific commands
cli-help: ## Show CLI help
	poetry run flx-oracle-oic --help

cli-tap: ## Test TAP functionality via CLI
	poetry run flx-oracle-oic tap discover --config config.json

cli-target: ## Test Target functionality via CLI
	poetry run flx-oracle-oic target validate --config config.json

cli-ext: ## Test Extension functionality via CLI
	poetry run flx-oracle-oic ext monitor health --config config.json

cli-adapter: ## Test FLX Adapter functionality
	poetry run flx-oracle-oic adapter health --config config.json

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
	docker build -t flx-oracle-oic:latest .

docker-run: ## Run in Docker container
	docker run --rm -v $(PWD)/config.json:/app/config.json flx-oracle-oic:latest --help

# Documentation
docs: ## Generate documentation
	poetry run sphinx-build -b html docs/ docs/_build/html

docs-serve: ## Serve documentation locally
	poetry run python -m http.server 8000 --directory docs/_build/html

# Performance
profile: ## Profile the CLI performance
	poetry run python -m cProfile -o profile.stats -m flx_oracle_oic.cli --help
	poetry run python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Integration testing with all components
test-integration-full: ## Test integration with all OIC components
	@echo "Testing TAP integration..."
	poetry run flx-oracle-oic tap discover --config config.json || true
	@echo "Testing Target integration..."
	poetry run flx-oracle-oic target validate --config config.json || true
	@echo "Testing Extension integration..."
	poetry run flx-oracle-oic ext monitor health --config config.json || true
	@echo "Testing Adapter integration..."
	poetry run flx-oracle-oic adapter health --config config.json || true
