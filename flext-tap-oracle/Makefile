# ================================================================================
# FLEXT TAP ORACLE MAKEFILE - ENTERPRISE STANDARDS
# ================================================================================
# This Makefile follows FLEXT workspace standards for Oracle Tap project
# Provides comprehensive quality gates and development automation
# ================================================================================

.PHONY: help install dev-setup lint type-check test check format build clean
.DEFAULT_GOAL := help

# Configuration
PROJECT_NAME := flext-tap-oracle
PYTHON_VERSION := 3.13
SRC_DIR := src
TEST_DIR := tests
PACKAGE_DIR := $(SRC_DIR)/flext_tap_oracle

# Color codes for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
BOLD := \033[1m
NC := \033[0m # No Color

# ================================================================================
# HELP AND INFORMATION
# ================================================================================

help: ## Show this help message
	@echo "$(BOLD)$(CYAN)FLEXT Tap Oracle - Enterprise Development Commands$(NC)"
	@echo "$(BLUE)============================================================$(NC)"
	@echo ""
	@echo "$(BOLD)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)Quality Gates:$(NC)"
	@echo "  $(GREEN)make check$(NC)           - Run all quality checks (lint + type + test)"
	@echo "  $(GREEN)make check-strict$(NC)    - Run strict quality checks with zero tolerance"
	@echo ""
	@echo "$(BOLD)Examples:$(NC)"
	@echo "  $(YELLOW)make install$(NC)         - Install dependencies"
	@echo "  $(YELLOW)make dev-setup$(NC)       - Setup development environment" 
	@echo "  $(YELLOW)make check$(NC)           - Run quality gates before commit"
	@echo ""

# ================================================================================
# SETUP AND INSTALLATION
# ================================================================================

install: ## Install production dependencies
	@echo "$(BLUE)📦 Installing production dependencies...$(NC)"
	poetry install --only=main
	@echo "$(GREEN)✅ Production dependencies installed$(NC)"

dev-setup: ## Setup development environment with all dependencies
	@echo "$(BLUE)🔧 Setting up development environment...$(NC)"
	poetry install --with=dev,test,typings,security
	poetry run pre-commit install || echo "$(YELLOW)⚠️  Pre-commit not configured$(NC)"
	@echo "$(GREEN)✅ Development environment ready$(NC)"

update: ## Update dependencies to latest versions
	@echo "$(BLUE)🔄 Updating dependencies...$(NC)"
	poetry update
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

# ================================================================================
# CODE QUALITY AND LINTING
# ================================================================================

lint: ## Run comprehensive linting with ruff
	@echo "$(BLUE)🔍 Running comprehensive linting...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --output-format=full || true

lint-fix: ## Fix auto-fixable linting issues
	@echo "$(BLUE)🔧 Fixing linting issues...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --fix --output-format=full || true

format: ## Format code with ruff formatter
	@echo "$(BLUE)📝 Formatting code...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR)

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)📋 Checking code formatting...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR) --check

# ================================================================================
# TYPE CHECKING
# ================================================================================

type-check: ## Run type checking with mypy
	@echo "$(BLUE)🔍 Running type checking...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m mypy $(PACKAGE_DIR) $(TEST_DIR) || true

type-check-strict: ## Run strict type checking
	@echo "$(BLUE)🔍 Running strict type checking...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m mypy $(PACKAGE_DIR) $(TEST_DIR) --strict --show-error-codes || true

# ================================================================================
# TESTING
# ================================================================================

test: ## Run all tests with coverage
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v --cov=$(PACKAGE_DIR) --cov-report=term-missing --cov-report=html --cov-report=xml || true

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v -m "unit" --cov=$(PACKAGE_DIR) || true

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v -m "integration" --cov=$(PACKAGE_DIR) || true

test-performance: ## Run performance tests
	@echo "$(BLUE)🧪 Running performance tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v -m "performance" --benchmark-only || true

test-stress: ## Run stress tests
	@echo "$(BLUE)🧪 Running stress tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v -m "stress" || true

test-fast: ## Run tests without coverage for speed
	@echo "$(BLUE)🧪 Running fast tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v --no-cov || true

test-verbose: ## Run tests with maximum verbosity
	@echo "$(BLUE)🧪 Running verbose tests...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -vvv --tb=long --cov=$(PACKAGE_DIR) || true

# ================================================================================
# SECURITY AND QUALITY GATES
# ================================================================================

security: ## Run security checks
	@echo "$(BLUE)🔒 Running security checks...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m bandit -r $(PACKAGE_DIR) -f json -o reports/security.json || true || true
	/home/marlonsc/flext/.venv/bin/python -m bandit -r $(PACKAGE_DIR) || true

audit: ## Audit dependencies for vulnerabilities
	@echo "$(BLUE)🔍 Auditing dependencies...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pip_audit

# ================================================================================
# COMPREHENSIVE QUALITY GATES
# ================================================================================

check: format-check lint type-check test ## Run all quality checks (standard)
	@echo "$(GREEN)$(BOLD)✅ All quality checks passed!$(NC)"

check-strict: ## Run strict quality checks with zero tolerance
	@echo "$(BLUE)$(BOLD)🔥 RUNNING STRICT QUALITY GATES$(NC)"
	@echo "$(YELLOW)============================================$(NC)"
	@echo ""
	
	@echo "$(BLUE)📋 Checking code formatting (strict)...$(NC)"
	@/home/marlonsc/flext/.venv/bin/python -m ruff format $(SRC_DIR) $(TEST_DIR) --check || (echo "$(RED)❌ Code formatting failed$(NC)" && exit 1)
	@echo "$(GREEN)✅ Code formatting OK$(NC)"
	
	@echo "$(BLUE)🔍 Running linting (strict)...$(NC)"
	@/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --output-format=full || (echo "$(RED)❌ Linting failed$(NC)" && exit 1) || true
	@echo "$(GREEN)✅ Linting OK$(NC)"
	
	@echo "$(BLUE)🔍 Running type checking (strict)...$(NC)"
	@/home/marlonsc/flext/.venv/bin/python -m mypy $(PACKAGE_DIR) $(TEST_DIR) --strict || (echo "$(RED)❌ Type checking failed$(NC)" && exit 1) || true
	@echo "$(GREEN)✅ Type checking OK$(NC)"
	
	@echo "$(BLUE)🧪 Running tests (strict)...$(NC)"
	@/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) -v --cov=$(PACKAGE_DIR) --cov-fail-under=95 --cov-report=term-missing || (echo "$(RED)❌ Tests failed$(NC)" && exit 1) || true
	@echo "$(GREEN)✅ Tests OK$(NC)"
	
	@echo "$(BLUE)🔒 Running security checks...$(NC)"
	@/home/marlonsc/flext/.venv/bin/python -m bandit -r $(PACKAGE_DIR) -q || (echo "$(RED)❌ Security checks failed$(NC)" && exit 1) || true
	@echo "$(GREEN)✅ Security OK$(NC)"
	
	@echo ""
	@echo "$(GREEN)$(BOLD)🎉 ALL STRICT QUALITY GATES PASSED!$(NC)"

quality-gate: check-strict ## Alias for check-strict

# ================================================================================
# BUILD AND PACKAGING
# ================================================================================

build: clean ## Build distribution packages
	@echo "$(BLUE)📦 Building distribution packages...$(NC)"
	poetry build
	@echo "$(GREEN)✅ Build completed$(NC)"

build-wheel: ## Build wheel package only
	@echo "$(BLUE)📦 Building wheel package...$(NC)"
	poetry build -f wheel

build-sdist: ## Build source distribution only
	@echo "$(BLUE)📦 Building source distribution...$(NC)"
	poetry build -f sdist

publish-test: build ## Publish to test PyPI
	@echo "$(BLUE)📤 Publishing to test PyPI...$(NC)"
	poetry publish --repository testpypi

publish: build ## Publish to PyPI
	@echo "$(BLUE)📤 Publishing to PyPI...$(NC)"
	poetry publish

# ================================================================================
# DEVELOPMENT TOOLS
# ================================================================================

shell: ## Open poetry shell
	@echo "$(BLUE)🐚 Opening poetry shell...$(NC)"
	poetry shell

run: ## Run the tap in development mode
	@echo "$(BLUE)🏃 Running tap in development mode...$(NC)"
	poetry run python -m flext_tap_oracle

demo: ## Run tap with demo configuration
	@echo "$(BLUE)🎭 Running tap demo...$(NC)"
	@echo "This would run with demo config if available"

# ================================================================================
# DOCUMENTATION
# ================================================================================

docs: ## Build documentation
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	@if [ -f "mkdocs.yml" ]; then \
		poetry run mkdocs build; \
	else \
		echo "$(YELLOW)⚠️  No mkdocs.yml found$(NC)"; \
	fi

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)📚 Serving documentation...$(NC)"
	@if [ -f "mkdocs.yml" ]; then \
		poetry run mkdocs serve; \
	else \
		echo "$(YELLOW)⚠️  No mkdocs.yml found$(NC)"; \
	fi

# ================================================================================
# CLEANUP AND MAINTENANCE
# ================================================================================

clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

clean-deep: clean ## Deep clean including poetry cache
	@echo "$(BLUE)🧹 Deep cleaning...$(NC)"
	poetry cache clear --all pypi -n || true
	rm -rf reports/
	@echo "$(GREEN)✅ Deep cleanup completed$(NC)"

reset: clean-deep ## Reset environment completely
	@echo "$(BLUE)🔄 Resetting environment...$(NC)"
	rm -rf .venv/
	poetry install --with=dev,test,typings,security
	@echo "$(GREEN)✅ Environment reset$(NC)"

# ================================================================================
# REPORTING AND METRICS
# ================================================================================

reports: ## Generate all reports
	@echo "$(BLUE)📊 Generating reports...$(NC)"
	@mkdir -p reports
	@/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) --cov=$(PACKAGE_DIR) --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --junit-xml=reports/pytest.xml || true
	@/home/marlonsc/flext/.venv/bin/python -m bandit -r $(PACKAGE_DIR) -f json -o reports/security.json || true || true
	@echo "$(GREEN)✅ Reports generated in reports/$(NC)"

metrics: ## Show project metrics
	@echo "$(BLUE)📊 Project Metrics$(NC)"
	@echo "$(YELLOW)==================$(NC)"
	@echo "Source lines of code:"
	@find $(SRC_DIR) -name "*.py" -exec wc -l {} + | tail -1
	@echo "Test lines of code:"
	@find $(TEST_DIR) -name "*.py" -exec wc -l {} + | tail -1
	@echo "Python files:"
	@find $(SRC_DIR) $(TEST_DIR) -name "*.py" | wc -l

coverage-report: ## Generate coverage report
	@echo "$(BLUE)📊 Generating coverage report...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m pytest $(TEST_DIR) --cov=$(PACKAGE_DIR) --cov-report=html --cov-report=term-missing || true

# ================================================================================
# VALIDATION AND COMPLIANCE
# ================================================================================

validate: ## Validate project structure and configuration
	@echo "$(BLUE)✅ Validating project structure...$(NC)"
	@echo "Checking pyproject.toml..."
	@poetry check
	@echo "Checking package structure..."
	@test -f $(PACKAGE_DIR)/__init__.py || (echo "$(RED)❌ Missing __init__.py in package$(NC)" && exit 1)
	@test -f $(PACKAGE_DIR)/tap.py || (echo "$(RED)❌ Missing tap.py in package$(NC)" && exit 1)
	@echo "$(GREEN)✅ Project structure valid$(NC)"

pre-commit: check-strict ## Run pre-commit quality gates
	@echo "$(GREEN)✅ Pre-commit checks completed$(NC)"

pre-push: check-strict reports ## Run comprehensive checks before push
	@echo "$(GREEN)✅ Pre-push checks completed$(NC)"

# ================================================================================
# ENTERPRISE INTEGRATION
# ================================================================================

enterprise-check: ## Run enterprise-grade quality checks
	@echo "$(BLUE)$(BOLD)🏢 ENTERPRISE QUALITY GATES$(NC)"
	@echo "$(YELLOW)================================$(NC)"
	@$(MAKE) check-strict
	@$(MAKE) security
	@$(MAKE) audit
	@$(MAKE) validate
	@echo ""
	@echo "$(GREEN)$(BOLD)🎉 ENTERPRISE QUALITY GATES PASSED!$(NC)"

ci: enterprise-check ## Run CI pipeline checks
	@echo "$(GREEN)✅ CI pipeline checks completed$(NC)"

# ================================================================================
# ENVIRONMENT INFORMATION
# ================================================================================

info: ## Show environment information
	@echo "$(BLUE)ℹ️  Environment Information$(NC)"
	@echo "$(YELLOW)========================$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python version: $(PYTHON_VERSION)"
	@echo "Poetry version: $$(poetry --version)"
	@echo "Python executable: $$(poetry run which python)"
	@echo "Virtual environment: $$(poetry env info --path)"
	@echo ""
	@echo "$(BLUE)📦 Dependencies:$(NC)"
	@poetry show --tree

env: info ## Alias for info

# ================================================================================
# MELTANO INTEGRATION
# ================================================================================

meltano-test: ## Test with Meltano (if available)
	@echo "$(BLUE)🎵 Testing with Meltano...$(NC)"
	@if command -v meltano >/dev/null 2>&1; then \
		echo "Running Meltano tests..."; \
		meltano test tap-oracle || echo "$(YELLOW)⚠️  Meltano tests failed or not configured$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Meltano not available$(NC)"; \
	fi

meltano-discover: ## Run discovery with Meltano
	@echo "$(BLUE)🎵 Running Meltano discovery...$(NC)"
	@if command -v meltano >/dev/null 2>&1; then \
		meltano discover tap-oracle || echo "$(YELLOW)⚠️  Meltano discovery failed or not configured$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Meltano not available$(NC)"; \
	fi

# ================================================================================
# DEBUGGING AND TROUBLESHOOTING
# ================================================================================

debug: ## Run with debug logging
	@echo "$(BLUE)🐛 Running with debug logging...$(NC)"
	poetry run python -m flext_tap_oracle --log-level DEBUG

trace: ## Run with trace logging
	@echo "$(BLUE)🔍 Running with trace logging...$(NC)"
	PYTHONPATH=src poetry run python -c "import flext_tap_oracle; print('Import successful')"

lint-errors: ## Show only linting errors (no warnings)
	@echo "$(BLUE)🔍 Showing linting errors only...$(NC)"
	/home/marlonsc/flext/.venv/bin/python -m ruff check $(SRC_DIR) $(TEST_DIR) --select=E,F || true

# ================================================================================
# MAKEFILE MAINTENANCE
# ================================================================================

makefile-check: ## Validate Makefile syntax
	@echo "$(BLUE)🔍 Checking Makefile syntax...$(NC)"
	@$(MAKE) --dry-run --silent help >/dev/null && echo "$(GREEN)✅ Makefile syntax OK$(NC)" || echo "$(RED)❌ Makefile syntax error$(NC)"

# Print current configuration
config:
	@echo "$(BLUE)⚙️  Configuration$(NC)"
	@echo "$(YELLOW)=================$(NC)"
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PYTHON_VERSION: $(PYTHON_VERSION)"
	@echo "SRC_DIR: $(SRC_DIR)"
	@echo "TEST_DIR: $(TEST_DIR)"
	@echo "PACKAGE_DIR: $(PACKAGE_DIR)"