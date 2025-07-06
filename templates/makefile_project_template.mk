# =============================================================================
# FLEXT PROJECT MAKEFILE TEMPLATE
# Standardized build automation for FLEXT project modules
# AUTO-GENERATED - DO NOT MODIFY MANUALLY
# =============================================================================

.PHONY: help install install-dev test lint build clean format type-check security
.PHONY: dev docs docs-serve watch coverage release-check
.PHONY: workspace-status workspace-install workspace-test workspace-lint workspace-clean

# =============================================================================
# CONFIGURATION AND DETECTION
# =============================================================================

# Project detection
SHELL := /bin/bash
PROJECT_NAME := $(shell basename $(CURDIR))
PROJECT_ROOT := $(CURDIR)

# Workspace coordination
FLEXT_ROOT ?= $(shell if [ -f "../Makefile" ] && grep -q "FLEXT Enhanced Workspace" "../Makefile" 2>/dev/null; then echo "$(CURDIR)/.."; else echo ""; fi)
ifneq ($(FLEXT_ROOT),)
    include $(FLEXT_ROOT)/templates/common_flext.mk
endif

# Python environment detection
PYTHON := $(shell which python3.13 || which python3 || which python)
PIP := $(shell which pip3 || which pip)

# Project type detection
HAS_PYPROJECT := $(shell test -f "pyproject.toml" && echo "true" || echo "false")
HAS_POETRY := $(shell test -f "poetry.lock" && echo "true" || echo "false")
HAS_REQUIREMENTS := $(shell test -f "requirements.txt" && echo "true" || echo "false")
HAS_TESTS := $(shell test -d "tests" && echo "true" || echo "false")
HAS_SRC := $(shell test -d "src" && echo "true" || echo "false")
HAS_MAKEFILE_LOCK := $(shell test -f ".makefile.lock" && echo "true" || echo "false")

# Technology detection
IS_PYTHON := $(shell test -f "pyproject.toml" -o -f "setup.py" -o -f "requirements.txt" && echo "true" || echo "false")
IS_GO := $(shell test -f "go.mod" && echo "true" || echo "false")
IS_LEGACY := $(shell echo "$(PROJECT_NAME)" | grep -q "^flx-" && echo "true" || echo "false")
IS_ENTERPRISE := $(shell echo "$(PROJECT_NAME)" | grep -qE "(algar|gruponos)" && echo "true" || echo "false")

# Colors for output
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# Determine project category for specialized handling
ifeq ($(IS_LEGACY),true)
    PROJECT_CATEGORY := LEGACY
else ifeq ($(IS_ENTERPRISE),true)
    PROJECT_CATEGORY := ENTERPRISE
else
    PROJECT_CATEGORY := FLEXT
endif

# =============================================================================
# HELP SYSTEM
# =============================================================================

help: ## Show this help message
	@echo "$(BOLD)$(CYAN)🚀 $(PROJECT_NAME) - $(PROJECT_CATEGORY) Project$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📊 Project Information:$(RESET)"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Type: $(PROJECT_CATEGORY)"
	@echo "  Python: $(HAS_PYPROJECT) | Poetry: $(HAS_POETRY) | Tests: $(HAS_TESTS)"
ifneq ($(FLEXT_ROOT),)
	@echo "  $(GREEN)✅ FLEXT Workspace: $(FLEXT_ROOT)$(RESET)"
	$(call workspace-help-header)
else
	@echo "  $(YELLOW)⚠ Standalone Mode$(RESET)"
	$(call standalone-help-header)
endif
	@echo ""
	@echo "$(BOLD)$(GREEN)🎯 Primary Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(help|install|test|lint|build|clean|format)$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)$(BLUE)🔧 Development Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(dev|docs|watch|coverage|type-check|security)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
ifneq ($(FLEXT_ROOT),)
	@echo "$(BOLD)$(MAGENTA)🔗 Workspace Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep 'workspace-' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(MAGENTA)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
endif
	@echo "$(BOLD)$(YELLOW)💡 Tips:$(RESET)"
	@echo "  • Use 'make install-dev' for development setup"
	@echo "  • Use 'make test' to run all tests"
	@echo "  • Use 'make format' to auto-format code"
ifneq ($(FLEXT_ROOT),)
	@echo "  • Use 'workspace-*' commands for coordinated operations"
endif

# =============================================================================
# INSTALLATION TARGETS
# =============================================================================

install: ## Install package in development mode
	@echo "$(BOLD)$(CYAN)📦 Installing $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call install-with-workspace,$(MAKE) _install-local)
else
	@$(MAKE) _install-local
endif

_install-local:
	@echo "$(CYAN)Installing dependencies locally...$(RESET)"
ifeq ($(HAS_POETRY),true)
	@poetry install
else ifeq ($(HAS_PYPROJECT),true)
	@$(PIP) install -e .
else ifeq ($(HAS_REQUIREMENTS),true)
	@$(PIP) install -r requirements.txt
else
	@echo "$(YELLOW)⚠ No package configuration found$(RESET)"
endif

install-dev: ## Install development dependencies
	@echo "$(BOLD)$(CYAN)🛠️ Installing development dependencies for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call install-dev-with-workspace,$(MAKE) _install-dev-local)
else
	@$(MAKE) _install-dev-local
endif

_install-dev-local:
	@echo "$(CYAN)Installing dev dependencies locally...$(RESET)"
ifeq ($(HAS_POETRY),true)
	@poetry install --with dev,test,security,build
else ifeq ($(HAS_PYPROJECT),true)
	@$(PIP) install -e ".[dev,test,security,build]" 2>/dev/null || $(PIP) install -e ".[dev]" 2>/dev/null || $(PIP) install -e .
else
	@echo "$(YELLOW)⚠ No dev dependencies configuration$(RESET)"
endif

# =============================================================================
# TESTING TARGETS
# =============================================================================

test: ## Run all tests
	@echo "$(BOLD)$(CYAN)🧪 Running tests for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call test-with-workspace,$(MAKE) _test-local)
else
	@$(MAKE) _test-local
endif

_test-local:
ifeq ($(HAS_TESTS),true)
	@echo "$(CYAN)Running tests locally...$(RESET)"
ifeq ($(HAS_POETRY),true)
	@poetry run pytest tests/ -v
else
	@$(PYTHON) -m pytest tests/ -v
endif
else
	@echo "$(YELLOW)⚠ No tests directory found$(RESET)"
endif

test-fast: ## Run fast tests only (exclude slow markers)
	@echo "$(BOLD)$(CYAN)⚡ Running fast tests for $(PROJECT_NAME)...$(RESET)"
ifeq ($(HAS_TESTS),true)
ifeq ($(HAS_POETRY),true)
	@poetry run pytest tests/ -v -m "not slow"
else
	@$(PYTHON) -m pytest tests/ -v -m "not slow"
endif
else
	@echo "$(YELLOW)⚠ No tests directory found$(RESET)"
endif

coverage: ## Run tests with coverage report
	@echo "$(BOLD)$(CYAN)📊 Running coverage analysis for $(PROJECT_NAME)...$(RESET)"
ifeq ($(HAS_TESTS),true)
	@mkdir -p reports
ifeq ($(HAS_POETRY),true)
	@poetry run pytest tests/ --cov=src --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-report=term-missing
else
	@$(PYTHON) -m pytest tests/ --cov=src --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-report=term-missing
endif
	@echo "$(GREEN)✅ Coverage report generated in reports/coverage/$(RESET)"
else
	@echo "$(YELLOW)⚠ No tests directory found$(RESET)"
endif

# =============================================================================
# CODE QUALITY TARGETS
# =============================================================================

lint: ## Run linting checks
	@echo "$(BOLD)$(CYAN)🔍 Running linting for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call lint-with-workspace,$(MAKE) _lint-local)
else
	@$(MAKE) _lint-local
endif

_lint-local:
	@echo "$(CYAN)Running linting locally...$(RESET)"
ifeq ($(IS_PYTHON),true)
ifeq ($(HAS_POETRY),true)
	@poetry run ruff check . || echo "$(YELLOW)⚠ Ruff not available$(RESET)"
else
	@$(PYTHON) -m ruff check . || echo "$(YELLOW)⚠ Ruff not available$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ Not a Python project$(RESET)"
endif

format: ## Format code automatically
	@echo "$(BOLD)$(CYAN)🎨 Formatting code for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call format-with-workspace,$(MAKE) _format-local)
else
	@$(MAKE) _format-local
endif

_format-local:
	@echo "$(CYAN)Formatting code locally...$(RESET)"
ifeq ($(IS_PYTHON),true)
ifeq ($(HAS_POETRY),true)
	@poetry run ruff format . || echo "$(YELLOW)⚠ Ruff not available$(RESET)"
	@poetry run black . || echo "$(YELLOW)⚠ Black not available$(RESET)"
	@poetry run isort . || echo "$(YELLOW)⚠ isort not available$(RESET)"
else
	@$(PYTHON) -m ruff format . || echo "$(YELLOW)⚠ Ruff not available$(RESET)"
	@$(PYTHON) -m black . || echo "$(YELLOW)⚠ Black not available$(RESET)"
	@$(PYTHON) -m isort . || echo "$(YELLOW)⚠ isort not available$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ Not a Python project$(RESET)"
endif

type-check: ## Run type checking
	@echo "$(BOLD)$(CYAN)🏷️ Running type checking for $(PROJECT_NAME)...$(RESET)"
ifeq ($(IS_PYTHON),true)
ifeq ($(HAS_SRC),true)
ifeq ($(HAS_POETRY),true)
	@poetry run mypy src/ --ignore-missing-imports || echo "$(YELLOW)⚠ mypy not available$(RESET)"
else
	@$(PYTHON) -m mypy src/ --ignore-missing-imports || echo "$(YELLOW)⚠ mypy not available$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ No src directory found$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ Not a Python project$(RESET)"
endif

security: ## Run security checks
	@echo "$(BOLD)$(CYAN)🔒 Running security checks for $(PROJECT_NAME)...$(RESET)"
ifeq ($(IS_PYTHON),true)
	@mkdir -p reports
ifeq ($(HAS_SRC),true)
ifeq ($(HAS_POETRY),true)
	@poetry run bandit -r src/ -f json -o reports/security.json || echo "$(YELLOW)⚠ bandit not available$(RESET)"
	@poetry run safety check || echo "$(YELLOW)⚠ safety not available$(RESET)"
else
	@$(PYTHON) -m bandit -r src/ -f json -o reports/security.json || echo "$(YELLOW)⚠ bandit not available$(RESET)"
	@$(PYTHON) -m safety check || echo "$(YELLOW)⚠ safety not available$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ No src directory found$(RESET)"
endif
else
	@echo "$(YELLOW)⚠ Not a Python project$(RESET)"
endif

# =============================================================================
# BUILD TARGETS
# =============================================================================

build: ## Build distribution packages
	@echo "$(BOLD)$(CYAN)🏗️ Building $(PROJECT_NAME)...$(RESET)"
ifeq ($(IS_PYTHON),true)
	@mkdir -p dist
ifeq ($(HAS_POETRY),true)
	@poetry build
else ifeq ($(HAS_PYPROJECT),true)
	@$(PYTHON) -m build .
else
	@echo "$(YELLOW)⚠ No build configuration found$(RESET)"
endif
else ifeq ($(IS_GO),true)
	@echo "$(CYAN)Building Go project...$(RESET)"
	@go build -o bin/$(PROJECT_NAME) .
else
	@echo "$(YELLOW)⚠ Unknown project type for building$(RESET)"
endif

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

clean: ## Clean build artifacts and cache files
	@echo "$(BOLD)$(CYAN)🧹 Cleaning $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call clean-with-workspace,$(MAKE) _clean-local)
else
	@$(MAKE) _clean-local
endif

_clean-local:
	@echo "$(CYAN)Cleaning locally...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@rm -rf bin/ 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(RESET)"

clean-all: clean ## Clean everything including virtual environments
	@echo "$(BOLD)$(RED)🗑️ Deep cleaning $(PROJECT_NAME)...$(RESET)"
	@rm -rf .venv/ 2>/dev/null || true
	@rm -rf node_modules/ 2>/dev/null || true
	@echo "$(GREEN)✅ Deep clean complete$(RESET)"

# =============================================================================
# DEVELOPMENT TARGETS
# =============================================================================

dev: install-dev ## Set up development environment
	@echo "$(BOLD)$(GREEN)🚀 Development environment ready for $(PROJECT_NAME)!$(RESET)"
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"
	@echo "$(GREEN)✅ Ready for development$(RESET)"

watch: ## Watch files and run tests on changes (requires entr)
	@echo "$(BOLD)$(CYAN)👀 Watching files for $(PROJECT_NAME)...$(RESET)"
ifeq ($(HAS_TESTS),true)
	@echo "$(CYAN)Press Ctrl+C to stop watching$(RESET)"
	@find src tests -name "*.py" | entr -c make test-fast || echo "$(YELLOW)⚠ entr not available$(RESET)"
else
	@echo "$(YELLOW)⚠ No tests directory found$(RESET)"
endif

docs: ## Generate documentation
	@echo "$(BOLD)$(CYAN)📚 Generating documentation for $(PROJECT_NAME)...$(RESET)"
	@if [ -f "mkdocs.yml" ]; then \
		echo "$(CYAN)Building MkDocs documentation...$(RESET)"; \
		mkdocs build || echo "$(YELLOW)⚠ MkDocs not available$(RESET)"; \
	elif [ -f "docs/conf.py" ]; then \
		echo "$(CYAN)Building Sphinx documentation...$(RESET)"; \
		cd docs && make html || echo "$(YELLOW)⚠ Sphinx not available$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ No documentation configuration found$(RESET)"; \
	fi

docs-serve: ## Serve documentation locally
	@echo "$(BOLD)$(CYAN)📖 Serving documentation for $(PROJECT_NAME)...$(RESET)"
	@if [ -f "mkdocs.yml" ]; then \
		echo "$(CYAN)Serving MkDocs at http://localhost:8000$(RESET)"; \
		mkdocs serve || echo "$(YELLOW)⚠ MkDocs not available$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ MkDocs configuration not found$(RESET)"; \
	fi

# =============================================================================
# QUALITY PIPELINE TARGETS
# =============================================================================

quality: ## Run complete quality pipeline
	@echo "$(BOLD)$(MAGENTA)🏆 Running quality pipeline for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call quality-check,$(MAKE) _lint-local)
else
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) security
endif
	@echo "$(BOLD)$(GREEN)✅ Quality pipeline complete$(RESET)"

commit-pipeline: ## Run pre-commit checks
	@echo "$(BOLD)$(MAGENTA)🚀 Running commit pipeline for $(PROJECT_NAME)...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call commit-pipeline,$(MAKE) _lint-local,$(MAKE) _test-local)
else
	@$(MAKE) quality
	@$(MAKE) test
endif
	@echo "$(BOLD)$(GREEN)✅ Ready for commit!$(RESET)"

release-check: ## Check if project is ready for release
	@echo "$(BOLD)$(MAGENTA)🔍 Checking release readiness for $(PROJECT_NAME)...$(RESET)"
	@$(MAKE) quality
	@$(MAKE) test
	@$(MAKE) build
	@echo "$(BOLD)$(GREEN)✅ Release checks passed$(RESET)"

# =============================================================================
# WORKSPACE COORDINATION TARGETS
# =============================================================================

ifneq ($(FLEXT_ROOT),)

workspace-status: ## Show workspace coordination status
	@echo "$(BOLD)$(BLUE)📊 Workspace Status for $(PROJECT_NAME)$(RESET)"
	@echo "FLEXT Root: $(FLEXT_ROOT)"
	@echo "Project Category: $(PROJECT_CATEGORY)"
	@echo "Python Project: $(IS_PYTHON)"
	@echo "Has Poetry: $(HAS_POETRY)"
	@echo "Has Tests: $(HAS_TESTS)"
	@echo "Has Source: $(HAS_SRC)"
	@echo "$(GREEN)✅ Workspace coordination enabled$(RESET)"

workspace-install: ## Install via workspace coordination
	$(call install-with-workspace,$(MAKE) _install-local)

workspace-test: ## Test via workspace coordination
	$(call test-with-workspace,$(MAKE) _test-local)

workspace-lint: ## Lint via workspace coordination
	$(call lint-with-workspace,$(MAKE) _lint-local)

workspace-clean: ## Clean via workspace coordination
	$(call clean-with-workspace,$(MAKE) _clean-local)

workspace-quality: ## Quality checks via workspace coordination
	$(call quality-check,$(MAKE) _lint-local)

workspace-commit: ## Commit pipeline via workspace coordination
	$(call commit-pipeline,$(MAKE) _lint-local,$(MAKE) _test-local)

else

workspace-status: ## Show workspace status (standalone mode)
	@echo "$(BOLD)$(YELLOW)⚠ Standalone Mode for $(PROJECT_NAME)$(RESET)"
	@echo "FLEXT workspace not detected"
	@echo "Running in local mode only"

endif

# =============================================================================
# PROJECT CATEGORY SPECIFIC TARGETS
# =============================================================================

ifeq ($(PROJECT_CATEGORY),LEGACY)

legacy-update: ## Update legacy project dependencies
	@echo "$(BOLD)$(YELLOW)🔄 Updating legacy project $(PROJECT_NAME)...$(RESET)"
	@echo "$(YELLOW)Checking for modern equivalents...$(RESET)"
ifneq ($(FLEXT_ROOT),)
	$(call validate-dependencies)
endif

legacy-migrate: ## Show migration path to modern FLEXT
	@echo "$(BOLD)$(YELLOW)📋 Migration path for $(PROJECT_NAME):$(RESET)"
	@echo "$(YELLOW)1. Update dependencies to use flext-core$(RESET)"
	@echo "$(YELLOW)2. Migrate to modern pyproject.toml$(RESET)"
	@echo "$(YELLOW)3. Update imports to new modules$(RESET)"
	@echo "$(YELLOW)4. Run tests and validate$(RESET)"

endif

ifeq ($(PROJECT_CATEGORY),ENTERPRISE)

enterprise-validate: ## Validate enterprise configuration
	@echo "$(BOLD)$(BLUE)🏢 Validating enterprise configuration for $(PROJECT_NAME)...$(RESET)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ Environment configuration found$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ No .env file found$(RESET)"; \
	fi
	@if [ -f "config.json" ]; then \
		echo "$(GREEN)✅ Enterprise config found$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ No config.json found$(RESET)"; \
	fi

enterprise-deploy: ## Prepare for enterprise deployment
	@echo "$(BOLD)$(BLUE)🚀 Preparing $(PROJECT_NAME) for enterprise deployment...$(RESET)"
	@$(MAKE) release-check
	@echo "$(BLUE)Creating deployment artifacts...$(RESET)"
	@echo "$(GREEN)✅ Ready for enterprise deployment$(RESET)"

endif

# =============================================================================
# INFORMATION AND DEBUGGING
# =============================================================================

info: ## Show detailed project information
	@echo "$(BOLD)$(CYAN)📋 Project Information: $(PROJECT_NAME)$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(RESET)"
	@echo "Name: $(PROJECT_NAME)"
	@echo "Root: $(PROJECT_ROOT)"
	@echo "Category: $(PROJECT_CATEGORY)"
	@echo "Python: $(PYTHON)"
	@echo ""
	@echo "$(BOLD)Detection Results:$(RESET)"
	@echo "  Python Project: $(IS_PYTHON)"
	@echo "  Go Project: $(IS_GO)"
	@echo "  Legacy Project: $(IS_LEGACY)"
	@echo "  Enterprise: $(IS_ENTERPRISE)"
	@echo ""
	@echo "$(BOLD)Configuration Files:$(RESET)"
	@echo "  pyproject.toml: $(HAS_PYPROJECT)"
	@echo "  poetry.lock: $(HAS_POETRY)"
	@echo "  requirements.txt: $(HAS_REQUIREMENTS)"
	@echo "  tests/: $(HAS_TESTS)"
	@echo "  src/: $(HAS_SRC)"
	@echo ""
ifneq ($(FLEXT_ROOT),)
	@echo "$(BOLD)$(GREEN)Workspace Integration:$(RESET)"
	@echo "  FLEXT Root: $(FLEXT_ROOT)"
	@echo "  Coordination: ✅ Enabled"
else
	@echo "$(BOLD)$(YELLOW)Workspace Integration:$(RESET)"
	@echo "  Status: ⚠ Standalone Mode"
endif

debug-make: ## Debug Makefile variables and detection
	@echo "$(BOLD)$(RED)🐛 Makefile Debug Information$(RESET)"
	@echo "SHELL: $(SHELL)"
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PROJECT_ROOT: $(PROJECT_ROOT)"
	@echo "FLEXT_ROOT: $(FLEXT_ROOT)"
	@echo "PYTHON: $(PYTHON)"
	@echo "PIP: $(PIP)"
	@echo ""
	@echo "Detection Variables:"
	@echo "  HAS_PYPROJECT: $(HAS_PYPROJECT)"
	@echo "  HAS_POETRY: $(HAS_POETRY)"
	@echo "  HAS_REQUIREMENTS: $(HAS_REQUIREMENTS)"
	@echo "  HAS_TESTS: $(HAS_TESTS)"
	@echo "  HAS_SRC: $(HAS_SRC)"
	@echo "  IS_PYTHON: $(IS_PYTHON)"
	@echo "  IS_GO: $(IS_GO)"
	@echo "  IS_LEGACY: $(IS_LEGACY)"
	@echo "  IS_ENTERPRISE: $(IS_ENTERPRISE)"
	@echo "  PROJECT_CATEGORY: $(PROJECT_CATEGORY)"

# Default target
.DEFAULT_GOAL := help
