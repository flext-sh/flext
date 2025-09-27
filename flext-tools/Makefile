# FLEXT Tools - Development Utilities Makefile
# =============================================
# Project-specific commands for flext-tools
# Extends the standardized build system

# Include the standardized build system
include Makefile.build

.PHONY: help test test-unit test-integration coverage validate
.PHONY: dev-setup validate-setup

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# 🎯 PROJECT-SPECIFIC HELP
# ============================================================================

help: ## Show project-specific help
	@echo "$(CYAN)🎯 FLEXT Tools - Development Utilities Commands$(RESET)"
	@echo "$(CYAN)===============================================$(RESET)"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(RESET)"
	@grep -E '^(test|coverage)[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-20s$(RESET) %s\\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development Commands:$(RESET)"
	@grep -E '^(dev|validate)[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-20s$(RESET) %s\\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Standard Commands (std-*):$(RESET)"
	@echo "Use 'make std-help' to see all standardized commands"

# ============================================================================
# 🧪 TESTING
# ============================================================================

test: ## Run all tests
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	@poetry run pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	@poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	@poetry run pytest tests/integration/ -v

coverage: ## Run tests with coverage report
	@echo "$(BLUE)📊 Running tests with coverage...$(RESET)"
	@poetry run pytest --cov=flext_tools --cov-report=term-missing --cov-report=html

coverage-html: coverage ## Open coverage HTML report
	@echo "$(BLUE)🌐 Opening coverage report...$(RESET)"
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

dev-setup: std-install-dev ## Complete development setup
	@echo "$(BLUE)🚀 Setting up development environment...$(RESET)"
	@poetry install --all-extras
	@echo "$(GREEN)✅ Development environment ready$(RESET)"

# ============================================================================
# QUALITY GATES (MANDATORY - ZERO TOLERANCE)
# ============================================================================

.PHONY: validate
validate: lint type-check security test ## Run all quality gates (MANDATORY ORDER)

.PHONY: check
check: lint type-check ## Quick health check

.PHONY: lint
lint: ## Run linting (ZERO TOLERANCE)
	@echo "$(BLUE)🔍 Running linting...$(RESET)"
	@poetry run ruff check .

.PHONY: type-check
type-check: ## Run type checking with Pyrefly (ZERO TOLERANCE)
	@echo "$(BLUE)🔍 Running type checking...$(RESET)"
	@PYTHONPATH=src poetry run pyrefly check .

.PHONY: security
security: ## Run security scanning
	@echo "$(BLUE)🔒 Running security scans...$(RESET)"
	@poetry run bandit -r src/
	@poetry run pip-audit

.PHONY: test
test: ## Run tests with coverage (MANDATORY)
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	@poetry run pytest --cov=flext_tools --cov-report=term-missing --cov-fail-under=75

.PHONY: format
format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	@poetry run ruff format .

.PHONY: fix
fix: ## Auto-fix issues
	@echo "$(BLUE)🔧 Auto-fixing issues...$(RESET)"
	@poetry run ruff check . --fix
	@poetry run ruff format .

validate-setup: std-validate-setup ## Validate project and dependencies
	@echo "$(BLUE)🔍 Validating project setup...$(RESET)"
	@test -f pytest.ini || { echo "$(RED)❌ pytest.ini missing$(RESET)"; exit 1; }
	@test -d tests/unit || { echo "$(YELLOW)⚠️  tests/unit/ missing$(RESET)"; }
	@echo "$(GREEN)✅ Project validation passed$(RESET)"

# ============================================================================
# 🔄 CONTINUOUS INTEGRATION
# ============================================================================

ci-test: ## Run tests in CI mode
	@echo "$(BLUE)🤖 Running tests in CI mode...$(RESET)"
	@poetry run pytest \
		--cov=flext_tools \
		--cov-report=xml \
		--cov-report=term \
		--junit-xml=reports/junit.xml \
		--maxfail=5 \
		-v

ci-lint: ## Run linting in CI mode
	@echo "$(BLUE)🤖 Running linting in CI mode...$(RESET)"
	@poetry run ruff check . --output-format=github

# ============================================================================
# 🛠️ UTILITIES
# ============================================================================

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)👀 Running tests in watch mode...$(RESET)"
	@poetry run ptw tests/ -- -x --tb=short

test-failed: ## Re-run only failed tests
	@echo "$(BLUE)🔄 Re-running failed tests...$(RESET)"
	@poetry run pytest --lf -x

# ============================================================================
# 🎯 COMMON ALIASES
# ============================================================================

t: test ## Alias for test
tu: test-unit ## Alias for test-unit
ti: test-integration ## Alias for test-integration
c: coverage ## Alias for coverage
l: std-lint ## Alias for lint
f: std-format ## Alias for format