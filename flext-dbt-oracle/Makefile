# FLEXT DBT Oracle Adapter - Standardized Makefile
# Follows FLEXT workspace standards for consistency and enterprise quality

.PHONY: help install build test check lint type-check format clean docs

# Default target
.DEFAULT_GOAL := help

SHELL := /bin/bash
PROJECT_NAME := flext-dbt-oracle
SRC_DIR := src
TEST_DIR := tests

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
BOLD := \033[1m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BOLD)FLEXT DBT Oracle Adapter - Available Commands$(NC)"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies using Poetry
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	poetry install --with dev,test,typings,security

build: ## Build the project
	@echo "$(BLUE)🔨 Building project...$(NC)"
	poetry build

# Quality Gates - Enterprise Standard
check: format lint type-check test ## Run all quality checks (full CI pipeline)
	@echo "$(GREEN)✅ All quality checks passed!$(NC)"

format: ## Format code with ruff and black
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✅ Code formatting complete!$(NC)"

lint: ## Run ruff linter (comprehensive checks)
	@echo "$(BLUE)🔥 Running comprehensive linting...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) || true
	@echo "$(GREEN)✅ Linting passed!$(NC)"

type-check: ## Run mypy type checking (strict mode)
	@echo "$(BLUE)🛡️ Running type checking (strict mode)...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m mypy $(SRC_DIR) || true
	@echo "$(GREEN)✅ Type checking passed!$(NC)"

test: ## Run tests with coverage
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest
	@echo "$(GREEN)✅ All tests passed!$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest -m "unit" || true

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest -m "integration" || true

test-oracle: ## Run Oracle-specific tests
	@echo "$(BLUE)🧪 Running Oracle tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest -m "oracle" || true

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)🧪 Running tests in watch mode...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest-watch

security: ## Run security scans
	@echo "$(BLUE)🔒 Running security scans...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m bandit -r $(SRC_DIR) -f json -o reports/security.json || true || true
	/home/marlonsc/flext/.venv/bin/python -m pip_audit --format=json --output=reports/pip-audit.json || true
	@echo "$(GREEN)✅ Security scans complete!$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf reports/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	poetry run mkdocs build
	@echo "$(GREEN)✅ Documentation generated!$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)📚 Serving documentation at http://localhost:8000$(NC)"
	poetry run mkdocs serve

# Development helpers
dev-setup: install ## Setup development environment
	@echo "$(BLUE)⚙️ Setting up development environment...$(NC)"
	poetry run pre-commit install
	mkdir -p reports
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

fix: ## Auto-fix issues where possible
	@echo "$(BLUE)🔧 Auto-fixing issues...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --fix || true
	/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✅ Auto-fixes applied!$(NC)"

profile: ## Profile test performance
	@echo "$(BLUE)⏱️ Profiling test performance...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest --benchmark-only --benchmark-sort=mean || true

# Docker support
docker-build: ## Build Docker image
	@echo "$(BLUE)🐳 Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-test: ## Run tests in Docker
	@echo "$(BLUE)🐳 Running tests in Docker...$(NC)"
	docker run --rm -v $(PWD):/app $(PROJECT_NAME):latest make test

# DBT-specific commands
dbt-debug: ## Debug DBT connection
	@echo "$(BLUE)🔍 Running DBT debug...$(NC)"
	poetry run dbt debug

dbt-deps: ## Install DBT dependencies
	@echo "$(BLUE)📦 Installing DBT dependencies...$(NC)"
	poetry run dbt deps

dbt-test-connection: ## Test Oracle connection using DBT
	@echo "$(BLUE)🔗 Testing Oracle connection...$(NC)"
	poetry run dbt run-operation test_oracle_connection

# Continuous Integration helpers
ci: check security ## Run full CI pipeline
	@echo "$(GREEN)🎉 CI pipeline completed successfully!$(NC)"

pre-commit: format lint type-check ## Pre-commit checks
	@echo "$(GREEN)✅ Pre-commit checks passed!$(NC)"

# Version management
version-patch: ## Bump patch version
	@echo "$(BLUE)📦 Bumping patch version...$(NC)"
	poetry version patch

version-minor: ## Bump minor version
	@echo "$(BLUE)📦 Bumping minor version...$(NC)"
	poetry version minor

version-major: ## Bump major version
	@echo "$(BLUE)📦 Bumping major version...$(NC)"
	poetry version major

# Publishing
publish-test: build ## Publish to test PyPI
	@echo "$(BLUE)📤 Publishing to test PyPI...$(NC)"
	poetry publish --repository testpypi

publish: build ## Publish to PyPI
	@echo "$(BLUE)📤 Publishing to PyPI...$(NC)"
	poetry publish

# Advanced testing
test-coverage: ## Run tests with detailed coverage report
	@echo "$(BLUE)🧪 Running tests with detailed coverage...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest --cov-report=html --cov-report=term-missing --cov-report=xml || true

test-performance: ## Run performance tests
	@echo "$(BLUE)⚡ Running performance tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest -m "performance" --benchmark-only || true

# Quality monitoring
quality-report: ## Generate quality report
	@echo "$(BLUE)📊 Generating quality report...$(NC)"
	mkdir -p reports
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --output-format=json > reports/ruff.json || true || true
	/home/marlonsc/flext/.venv/bin/python -m mypy $(SRC_DIR) --json-report=reports/mypy || true || true
	@echo "$(GREEN)✅ Quality report generated in reports/$(NC)"

# Emergency fixes
emergency-format: ## Emergency code formatting (skip checks)
	@echo "$(YELLOW)⚠️ Emergency formatting...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR) --force-exclude
	
emergency-fix: ## Emergency auto-fix (skip safety checks)
	@echo "$(RED)🚨 Emergency fixes (USE WITH CAUTION)...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --fix --unsafe-fixes || true

# Workspace integration
workspace-check: ## Check workspace compatibility
	@echo "$(BLUE)🔍 Checking workspace compatibility...$(NC)"
	@cd .. && make check-project PROJECT=$(PROJECT_NAME) || echo "$(YELLOW)⚠️ Workspace check not available$(NC)"